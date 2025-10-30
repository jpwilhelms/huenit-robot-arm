"""
Helper script that relies on the Python modules from
`Huenit robotics/resources/app/resources/huenit_py/src` to work with the
Huenit AI camera:

  - Flash MicroPython files (`robot.py`, `main.py`)
  - Read files from the device flash
  - Capture a JPEG frame via the high-speed REPL
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

# Ensure the original Huenit modules can be imported.
REPO_ROOT = Path(__file__).resolve().parents[1]
SDK_PATH = (
    REPO_ROOT
    / "Huenit robotics"
    / "resources"
    / "app"
    / "resources"
    / "huenit_py"
    / "src"
)
sys.path.insert(0, str(SDK_PATH))

SITE_PACKAGES_MAC = (
    REPO_ROOT
    / "Huenit robotics"
    / "resources"
    / "app"
    / "resources"
    / "huenit_py"
    / "huenit_env_mac"
    / "lib"
    / "python3.10"
    / "site-packages"
)
if SITE_PACKAGES_MAC.exists():
    sys.path.append(str(SITE_PACKAGES_MAC))

VERSION3_PATH = (
    SDK_PATH / "python_protocol_cores" / "camera_record" / "version_3"
)
if VERSION3_PATH.exists():
    sys.path.append(str(VERSION3_PATH))

from python_protocol_cores.cam_script import get_my_serial, scan_ports  # type: ignore # noqa: E402
from python_protocol_cores.ampy_samples.ampy.pyboard import (  # type: ignore # noqa: E402
    Pyboard,
    PyboardError,
)
from python_protocol_cores.ampy_samples.ampy.files import (  # type: ignore # noqa: E402
    Files,
)
from python_protocol_cores.camera_record.version_3.buffer_queue import (  # type: ignore # noqa: E402
    ThreadSafeBufferOfSizeOne,
)
from python_protocol_cores.camera_record.version_3.serial_reciever import (  # type: ignore # noqa: E402
    SerialReceiver,
)

_original_enter_raw = Pyboard.enter_raw_repl


def _enter_raw_with_ctrl_a(self):
    _original_enter_raw(self)
    try:
        self.serial.write(b"\x01")
        # consume until raw REPL banner (best effort)
        self.read_until(1, b"raw REPL; CTRL-B to exit\r\n", timeout=2)
    except Exception:
        # Banner not strictly required; continue anyway
        pass


Pyboard.enter_raw_repl = _enter_raw_with_ctrl_a

MICROPY_DIR = Path(__file__).resolve().parent / "micropython_scripts"
DEFAULT_MAIN = MICROPY_DIR / "camera_robot_bridge.py"
DEFAULT_ROBOT = MICROPY_DIR / "robot.py"


def _find_camera_port() -> str:
    port_list = scan_ports()
    if not port_list:
        raise RuntimeError("No serial device found.")
    preferred = get_my_serial(port_list)
    if preferred and preferred != "None":
        return preferred
    for device, description, *_rest in port_list:
        if description and "HUENIT" in description.upper():
            return device
    # Final fallback: return the first FTDI/USB port.
    device, *_ = port_list[0]
    return device


def _open_pyboard(port: str, baudrate: int = 115200) -> Pyboard:
    return Pyboard(device=port, baudrate=baudrate, rawdelay=0)


def flash_files(main_file: Path = DEFAULT_MAIN, robot_file: Path = DEFAULT_ROBOT) -> None:
    port = _find_camera_port()
    print(f"[flash] Using port {port}")
    pyb = _open_pyboard(port)
    files = Files(pyb)
    try:
        for local, remote in (
            (robot_file, "/flash/robot.py"),
            (main_file, "/flash/main.py"),
        ):
            data = local.read_bytes()
            print(f"[flash] Writing {remote} ({len(data)} bytes)")
            files.put_origin(remote, data, timeout=10)
        pyb.enter_raw_repl()
        try:
            pyb.exec_raw(b"import machine\nmachine.reset()")
            print("[flash] Soft reset triggered, new script active.")
        except PyboardError as exc:
            print(f"[flash] Reset command failed (likely due to reboot): {exc}")
    finally:
        pyb.close()


def read_file(remote_path: str) -> bytes:
    port = _find_camera_port()
    pyb = _open_pyboard(port)
    files = Files(pyb)
    try:
        data = files.get(remote_path)
        return data
    finally:
        pyb.close()


def capture_frame(output_path: Path, timeout: float = 10.0) -> Path:
    port = _find_camera_port()
    queue = ThreadSafeBufferOfSizeOne()
    receiver = SerialReceiver(queue, port, baurdrate=1_500_000)
    receiver.daemon = True
    receiver.start()
    print(f"[capture] Waiting for JPEG data on {port} ...")
    start = time.time()
    frame = None
    try:
        while time.time() - start < timeout:
            candidate = queue.get()
            if candidate:
                frame = candidate
                break
            time.sleep(0.1)
    finally:
        receiver.set_stop()
        receiver.join(timeout=2)
    if frame is None:
        raise TimeoutError("No image received - is the MicroPython script running?")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(frame)
    print(f"[capture] Frame stored in {output_path}")
    return output_path


def _cli() -> None:
    parser = argparse.ArgumentParser(description="Huenit AI-Cam helper")
    sub = parser.add_subparsers(dest="command", required=True)

    flash_cmd = sub.add_parser("flash", help="Transfer MicroPython files")
    flash_cmd.add_argument(
        "--main",
        type=Path,
        default=DEFAULT_MAIN,
        help="Path to main.py (default: camera_robot_bridge.py)",
    )
    flash_cmd.add_argument(
        "--robot",
        type=Path,
        default=DEFAULT_ROBOT,
        help="Path to robot.py (default: from target_inner_scripts)",
    )

    read_cmd = sub.add_parser("read", help="Download a file from flash")
    read_cmd.add_argument("remote", help="Remote path, e.g. /flash/main.py")
    read_cmd.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Optional path where the content should be stored",
    )

    capture_cmd = sub.add_parser("capture", help="Save a JPEG frame")
    capture_cmd.add_argument(
        "output",
        type=Path,
        nargs="?",
        default=Path("huenit_capture.jpg"),
        help="Destination path for the captured image",
    )

    args = parser.parse_args()

    if args.command == "flash":
        flash_files(args.main, args.robot)
    elif args.command == "read":
        data = read_file(args.remote)
        if args.output:
            args.output.write_bytes(data)
            print(f"[read] Saved content to {args.output}")
        else:
            sys.stdout.buffer.write(data)
    elif args.command == "capture":
        capture_frame(args.output)


if __name__ == "__main__":
    _cli()
