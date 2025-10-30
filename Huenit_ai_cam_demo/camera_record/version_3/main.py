from uvicorn import run
import serial
import time

import serial
from serial.tools import list_ports
import socket


def find_available_port(start_port=10600, max_attempts=10):
    for port in range(start_port, start_port + max_attempts):
        if is_port_free(port):
            print(f"Port {port} is available.")
            return port
    raise ValueError(
        f"No available ports in the range {start_port} to {start_port + max_attempts - 1}"
    )


def is_port_free(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            s.bind(("", port))
            s.listen(1)
            s.settimeout(0.1)
            try:
                conn, addr = s.accept()
                conn.close()
                return False  # If accept succeeds, the port is not free
            except socket.timeout:
                return True  # If accept times out, the port is likely free
        except socket.error:
            return False  # If bind/listen fails, the port is definitely not free


def scan_ports():
    ports = list(serial.tools.list_ports.comports())
    available_ports = [
        (
            port.device,
            port.description,
            port.vid,
            port.pid,
            port.manufacturer,
            port.serial_number,
        )
        for port in ports
    ]
    return available_ports


def get_my_device():
    port_list = scan_ports()
    for item in port_list:
        if "FTDI" in item:
            return (item[0], item[1])


def run_server(ser: serial.Serial = None):
    if ser is None:
        ser: serial.Serial = serial.Serial()
        ser.xonxoff = False
        ser.port = get_my_device()[0]
        ser.open()
        ser.baudrate = 115200

    ser.xonxoff = False
    ser.flushInput()  # Clear input buffer
    ser.flushOutput()  # Clear output buffer
    ser.write(b"\x03")
    time.sleep(0.01)
    ser.write(b"\x03")
    time.sleep(0.01)
    ser.write(b"\x03")
    time.sleep(0.01)

    ser.xonxoff = True
    code = 'import os\r\nfiles = os.listdir()\r\nwith open("/flash/stream_flag", "w") as f:\r\nf.write("true")\r\n\r\n\r\n\r\n\r\n'
    ser.write(code.encode("utf-8"))
    time.sleep(1)

    ser.dtr = False
    ser.rts = False
    time.sleep(0.2)
    ser.rts = True
    ser.rts = False
    time.sleep(0.2)
    ser.close()
    time.sleep(0.5)

    print("from sub main")
    import os

    print("pid =", os.getpid())
    target_port = find_available_port()
    print("allocated port =", target_port)
    run("server:app", host="0.0.0.0", port=target_port, reload=True)


if __name__ == "__main__":
    run_server()
