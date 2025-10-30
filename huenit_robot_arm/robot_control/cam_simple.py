import serial, time, sys

PORT = "/dev/ttyUSB0"   # adjust to your setup
BAUD = 115200           # typical for ampy; try 921600 if needed
CODE = b"print('HELLO_FROM_CAMERA')\r\n"

with serial.Serial(PORT, BAUD, timeout=1) as ser:
    time.sleep(0.2)
    ser.reset_input_buffer(); ser.reset_output_buffer()

    # Interrupt any program that might be running
    ser.write(b'\x03')         # Ctrl-C
    time.sleep(0.05)

    # Enter paste mode
    ser.write(b'\x05')         # Ctrl-E
    time.sleep(0.02)
    ser.write(CODE)
    time.sleep(0.02)
    ser.write(b'\x04')         # Ctrl-D = execute
    time.sleep(0.2)

    # Read the output
    out = ser.read(4096)
    sys.stdout.buffer.write(out)
