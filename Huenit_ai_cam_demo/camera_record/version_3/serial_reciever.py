import sys
import time
from queue import Queue
from threading import Event, Thread

import serial
from loguru import logger

from buffer_queue import ThreadSafeBufferOfSizeOne
from record_util import send_event


class SerialReceiver(Thread):
    """
    Connect to a serial port, receive JPEG image data, and push the decoded
    frames into the ThreadSafeBufferOfSizeOne queue.
    """

    ser = None
    is_running = False

    def __init__(self, queue: ThreadSafeBufferOfSizeOne, port, baurdrate=1500000):
        super().__init__()

        self.port = port
        self.baurdrate = baurdrate
        self.queue: ThreadSafeBufferOfSizeOne = queue

        self.is_running: Event = Event()  # signals start/stop
        self.is_running.clear()

        self.is_write_code: Event = Event()
        self.is_write_code.clear()

        self.connect_serial()

    def connect_serial(self):
        # Establish the serial connection
        to_js_dict = {
            "name": "Stream_Device_Serial_Connection",
            "sender": "python",
            "succes": True,
            "param": {"status": "ready"},
        }
        send_event(to_js_dict)
        self.ser: serial.Serial = serial.Serial()
        self.ser.xonxoff = True
        self.ser.port = self.port
        self.ser.baudrate = self.baurdrate
        self.ser.timeout = 1
        # self.ser.set_buffer_size(rx_szie=12800, tx_size=12800)
        self.ser.open()
        logger.info("(from logger) Serial connection completed.")
        to_js_dict = {
            "name": "Stream_Device_Serial_Connection",
            "sender": "python",
            "succes": True,
            "param": {"status": "done"},
        }
        send_event(to_js_dict)

    def close_serial(self):
        pass

    def disconnect_serial(self):
        # Tear down the serial connection
        if self.ser and self.ser.is_open:
            self.ser.close()

    def set_stop(self):
        # Flip the event so the thread shuts down
        self.is_running.clear()

    def run(self):
        image_data = b""
        start_marker = -1
        end_marker = -1

        self.is_running.set()
        # logger.info("Image receive start..")
        logger.info("(from logger) Image receive start..")
        to_js_dict = {
            "name": "Stream_Device_Image_Listener",
            "sender": "python",
            "succes": True,
            "param": {"status": "ready"},
        }
        send_event(to_js_dict)
        while self.is_running.is_set():
            while self.is_write_code.isSet():
                time.sleep(0.5)

            # Read data from the serial port
            data = self.ser.read(512)

            if not data:
                logger.info("wait image(data)...")
                to_js_dict = {
                    "name": "Stream_Device_Image_Listener",
                    "sender": "python",
                    "succes": True,
                    "param": {"status": "in-progress"},
                }
                send_event(to_js_dict)
                continue
            # else:
            #     logger.info(data[10:])

            # Append to the current image buffer
            image_data += data

            # Use the JPEG markers to split out a frame
            start_marker = image_data.find(b"\xff\xd8")  # JPEG start marker
            end_marker = image_data.rfind(b"\xff\xd9")  # JPEG end marker

            if start_marker != -1 and end_marker != -1 and end_marker > start_marker:
                # Extract the image
                image_data_jpeg = image_data[start_marker : end_marker + 2]

                # Push the image into the queue
                self.queue.add(image_data_jpeg)

                # Reset the buffer
                image_data = b""
                start_marker = -1
                end_marker = -1

        self.close_serial()
        # logger.info("Serial listener thread exit.")
        logger.info("(from logger) Serial listener thread exit.")
        to_js_dict = {
            "name": "Stream_Device_Image_Listener",
            "sender": "python",
            "succes": True,
            "param": {"status": "done"},
        }
        send_event(to_js_dict)

    def write_code(self, code):
        # Execute user-provided Python code on the device

        logger.info(f"write code:|{code}|")

        self.is_write_code.set()
        code_write_dict = {
            "name": "Stream_Device_Code_Write",
            "sender": "python",
            "succes": True,
            "param": {"status": "ready"},
        }
        send_event(code_write_dict)
        logger.info(self.ser.read_all())

        self.ser.xonxoff = True
        time.sleep(0.2)
        logger.info(self.ser.read_all())

        self.ser.write(b"\x03")  # ctrl-C twice: interrupt any running program
        logger.info(self.ser.read_all())
        time.sleep(0.1)

        self.ser.write(b"\x03")  # ctrl-C twice: interrupt any running program
        logger.info(self.ser.read_all())
        time.sleep(0.1)

        self.ser.xonxoff = False
        logger.info(self.ser.read_all())
        time.sleep(0.02)

        self.ser.write(b"\x01")  # # ctrl-A: enter raw REPL
        logger.info(self.ser.read_all())
        time.sleep(0.2)

        # TODO : read 2byte and OK
        while True:
            data = self.ser.read_all()
            if str(data).find("raw REPL"):
                time.sleep(0.2)
                break

        logger.info(f"code:|{code}|")
        self.ser.write(code.encode("utf-8"))
        time.sleep(0.2)
        self.ser.write(b"\x04")  # ETX
        logger.info(self.ser.read_all())

        while True:
            data = self.ser.read_all()
            logger.info(data)
            if data == b"":
                break
            time.sleep(0.5)

        logger.info("(from logger) Write code completed.")
        self.is_write_code.clear()
        code_write_dict = {
            "name": "Stream_Device_Code_Write",
            "sender": "python",
            "succes": True,
            "param": {"status": "done"},
        }
        send_event(code_write_dict)


if __name__ == "__main__":
    queue = Queue()
    t = SerialReceiver("COM7")
    t.daemon = True
    t.start()

    time.sleep(3)

    t.set_stop()
    t.join()
