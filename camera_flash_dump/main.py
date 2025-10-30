# Based on the MicroPython examples located in
# Huenit robotics/resources/app/resources/huenit_py/src.
# This script runs directly on the Huenit AI camera. It initializes the image
# sensor, streams compressed JPEG frames over the REPL UART, and, if a robot
# arm is attached, tries to interact with it via G/M codes. Without an arm
# connected the script continues operating in camera-only mode.

import sensor
import image
import time
import lcd
from machine import UART
from Maix import GPIO
from fpioa_manager import fm

try:
    import robot  # originates from target_inner_scripts/robot.py
except ImportError as exc:
    robot = None
    print("robot_module_missing:", exc)


def init_uart_for_robot():
    # The robot arm is attached to the second UART.
    fm.register(6, fm.fpioa.UART1_TX, force=True)
    fm.register(7, fm.fpioa.UART1_RX, force=True)
    return UART(UART.UART1, 115200, 8, 1, 0, timeout=1000, read_buf_len=4096)


def init_camera():
    lcd.init()
    lcd.clear(lcd.BLACK)
    sensor.reset(dual_buff=True)
    sensor.set_pixformat(sensor.RGB565)
    sensor.set_framesize(sensor.QVGA)
    sensor.skip_frames(time=2000)


def ensure_robot_ready():
    if robot is None:
        return False
    try:
        if robot.checkConnection():
            print("robot_ready")
            # Ensure auto-reports are disabled.
            robot.sendCommand("M155 S0\n")
            return True
    except Exception as exc:
        print("robot_check_failed:", exc)
    print("robot_not_connected")
    return False


def main():
    uart_to_robot = init_uart_for_robot()
    init_camera()

    repl = UART.repl_uart()
    repl.init(1_500_000, 8, None, 1, read_buf_len=4096)

    clock = time.clock()
    robot_ready = ensure_robot_ready()
    last_robot_ping = time.ticks_ms()

    while True:
        clock.tick()
        img = sensor.snapshot()
        lcd.display(img)

        # Update the robot status once per second.
        if robot_ready and time.ticks_diff(time.ticks_ms(), last_robot_ping) > 1000:
            try:
                robot.sendCommandNoReturn("M400\n")
            except Exception as exc:
                robot_ready = False
                print("robot_lost:", exc)
            last_robot_ping = time.ticks_ms()

        # Compress the frame and stream it over the REPL UART.
        jpeg = img.compress(quality=60)
        repl.write(jpeg.to_bytes())


main()
