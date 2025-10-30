HOWTO: Getting Started with the Huenit AI Camera and Robot Arm
================================================================

This document explains how to run your first MicroPython programs on the Huenit AI camera, display simple output, and execute basic robot/suction motions. Everything below has been validated on the files in this repository; where something still needs deeper investigation it is called out explicitly.

Prerequisites
-------------

* Execute all commands from the repository root (this directory rooted at `/workspace/huenit-robot-arm`).
* The original Huenit MicroPython environment and helper scripts are part of the repo: no extra packages are required on the device itself.
* After every power cycle let the factory UI finish booting before sending commands. The camera UI always starts first; your custom `main.py` runs only after you hold BACK for ~2 s (or stop the UI manually via the REPL).

Repository Layout (selected files)
----------------------------------

* `camera_flash_dump/` – backup of the files that shipped on the device (`main.py`, `robot.py`, `RobotData*.json`, ...). Restore them to revert to factory behaviour.
* `Huenit_ai_cam_demo/host_camera_tool.py` – CLI helper for flashing/reading scripts. It talks to the device exactly like the original IDE.
* `Huenit_ai_cam_demo/micropython_scripts/`
  * `display_colors_main.py` – colour/rotation test (works reliably).
  * `display_circle_main.py` – shows the JPEG `circle.jpg` (see the pipeline below).
  * `camera_robot_bridge.py` – the stock streaming script from the Huenit IDE.

Communicate with the Camera (Raw REPL)
--------------------------------------

1. Connect the camera via USB.
2. Open a REPL session using your host Python (with `pyserial` installed):
   ```bash
   python3 - <<'PY'
   import serial, time
   ser = serial.Serial('/dev/ttyUSB0', 115200, timeout=0.5, write_timeout=1)
   for _ in range(10):
       ser.write(b'\x03'); time.sleep(0.05)  # break running script
   ser.write(b'\x02'); ser.write(b'\x03\x03')  # ensure normal REPL
   ser.read(ser.in_waiting or 0)
   ser.write(b'\x01')  # raw REPL
   print(ser.read(ser.in_waiting or 256))
   ser.close()
   PY
   ```
   When you see `raw REPL; CTRL-B to exit` you can push your own code.
3. Keep that helper handy – every upload below uses the same pattern (send script, `time.sleep(0.001)` after each `write`, then execute with `Ctrl+D`).

Flashing custom `main.py`
-------------------------

*Use this only when you want your script to start after every reboot.*

```bash
python3 Huenit_ai_cam_demo/host_camera_tool.py flash \
    --main Huenit_ai_cam_demo/micropython_scripts/display_colors_main.py \
    --robot camera_flash_dump/robot.py
```

Notes:

* The script often reboots the camera mid-transfer; `host_camera_tool.py` can time out after ~2 min even when flashing succeeded. Always verify by dumping `main.py` through the raw REPL (`help('modules')` → `import ubinascii`, `open('main.py','rb')`, etc.).
* To return to the stock behaviour run the same command with `--main camera_flash_dump/main.py`.

Display Quick Wins
------------------

### 1. Colour/Rotation Cycle (already proven)

`display_colors_main.py` cycles through rotations 0–3 and fills the screen with red/green/blue/black backgrounds. It also draws bold text outlines so you can confirm which rotation matches the physical orientation.

### 2. Show a JPEG (circle)

Once `circle.jpg` is present on `/flash` (the repository ships a sample in its root; replace it with your own if you like) you can display it with:
   ```bash
   # Serial upload helper (run once to copy circle.jpg)
   python3 - <<'PY'
   import serial, time, binascii
   from pathlib import Path

   data = Path('circle.jpg').read_bytes()
   chunks = [binascii.hexlify(data[i:i+200]).decode() for i in range(0, len(data), 200)]

   ser = serial.Serial('/dev/ttyUSB0', 115200, timeout=0.5, write_timeout=1)
   for _ in range(10):
       ser.write(b'\x03'); time.sleep(0.05)
   ser.write(b'\x02'); ser.write(b'\x03\x03'); ser.read(ser.in_waiting or 0)
   ser.write(b'\x01')

   ser.write(b"import ubinascii\r\nf=open('circle.jpg','wb')\r\n"); ser.flush(); time.sleep(0.001)
   for chunk in chunks:
       ser.write(f"f.write(ubinascii.unhexlify('{chunk}'))\r\n".encode()); ser.flush(); time.sleep(0.001)
   ser.write(b"f.close()\r\nprint('WRITE_DONE')\r\n"); ser.flush(); time.sleep(0.001)
   ser.write(b'\x04'); time.sleep(1)
   ser.write(b'\x02'); ser.close()
   PY
   ```
   Afterwards display it with:
   ```bash
   python3 - <<'PY'
   import serial, time
   script = """
   import lcd, image, time
   lcd.init()
   img = image.Image('circle.jpg')
   while True:
       for rot in range(4):
           lcd.rotation(rot)
           lcd.clear(lcd.BLACK)
           lcd.display(img)
           time.sleep_ms(1000)
   """
   ser = serial.Serial('/dev/ttyUSB0', 115200, timeout=0.5, write_timeout=1)
   for _ in range(10):
       ser.write(b'\x03'); time.sleep(0.05)
   ser.write(b'\x02'); ser.write(b'\x03\x03'); ser.read(ser.in_waiting or 0)
   ser.write(b'\x01')
   ser.write(script.strip().replace('\n','\r\n').encode()); ser.flush(); time.sleep(0.001)
   ser.write(b'\r\n'); ser.flush(); time.sleep(0.001)
   ser.write(b'\x04'); ser.flush(); time.sleep(0.001)
   time.sleep(8)
   ser.write(b'\x02'); ser.close()
   PY
   ```

To keep the circle visible after every restart, flash `display_circle_main.py` as the `--main` file.

> **Still open:** Reliable large-text rendering via `lcd.draw_string()` is inconsistent on this firmware. For now, use colour fills, shapes, or pre-rendered bitmaps.

Robot Arm & Suction Basics
--------------------------

The MicroPython API is defined in `camera_flash_dump/robot.py` (copied from the device). Key functions:

```python
import robot, time
robot.checkConnection()            # returns True if the arm answers M400
robot.moveG0(100, 200, 50)         # fast move (G0)
robot.moveG1(120, 210, 30)         # linear move (G1)
robot.moveAngle(90, -60, 45)       # joint angles
robot.moveZ0(80)                   # move Z only
robot.suctionOn(); time.sleep(1); robot.suctionOff()
robot.gripper(1); robot.gripper(0) # 1=open, 0=release, 2=close
robot.suctionAngle(120, speed=60)  # rotate end effector ( <270° )
pos = robot.getLoc()               # returns [x, y, z]
angles = robot.getDeg()            # returns [a, b, c]
```

Recommendations:

* Always call `robot.checkConnection()` before issuing moves.
* Ensure the workspace is clear; there is no built-in collision avoidance.
* Use the macro files in `camera_flash_dump/RobotData*.json` as templates for sequencing motions and suction events.

Touchscreen Input
-----------------

MicroPython also exposes the touch controller:

```python
import touchscreen, time
touchscreen.init()
for _ in range(20):
    status, x, y = touchscreen.read()
    print(status, x, y)
    time.sleep_ms(100)
touchscreen.__del__()
```

Status constants: `STATUS_IDLE`, `STATUS_RELEASE`, `STATUS_PRESS`, `STATUS_MOVE`. Controllers supported: `NS2009`, `FT62XX`.

What Works vs. Needs Investigation
----------------------------------

| Feature                                      | Status                                       |
|----------------------------------------------|----------------------------------------------|
| Colour fills / rotation test (`lcd.clear`)    | ✅ Verified (`display_colors_main.py`).       |
| JPEG display (`circle.jpg` + `lcd.display`)   | ✅ Verified (`display_circle_main.py`).       |
| Text drawing via `lcd.draw_string`            | ⚠️ Inconsistent – characters appear pixelated. Prefer bitmaps or shapes until font handling is understood. |
| Robot motion (`moveG0`, `moveG1`, etc.)       | ✅ API available; test motions carefully with the real arm. |
| Suction / gripper (`suctionOn`, `gripper`)    | ✅ Works when the arm is connected.           |
| Touchscreen (`touchscreen.read`)              | ⚠️ API discovered, not yet validated in practice. |
| Factory UI coexistence                        | ⚠️ UI restarts on boot; custom `main.py` begins only after holding BACK ~2 s or stopping the UI via REPL. |

Next Steps
----------

* Wrap the working snippets into higher-level scripts (e.g. show camera status + move robot + prompt via touchscreen).
* Investigate font rendering or ship pre-rendered glyphs as bitmaps.
* Validate the touchscreen module in practice (debounce, coordinate mapping, integration with UI).
* Automate flashing with better timeout handling (or rely on direct raw REPL uploads).

Have fun experimenting – and keep backups of `camera_flash_dump/` whenever you change `main.py`.
