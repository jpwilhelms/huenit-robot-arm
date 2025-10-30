# main.py
import atexit
import time

from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from loguru import logger

from buffer_queue import ThreadSafeBufferOfSizeOne
from recorder import Recorder
from serial_reciever import SerialReceiver
import os, serial

from record_util import send_event

# Instantiate FastAPI
app = FastAPI()
queue: ThreadSafeBufferOfSizeOne = ThreadSafeBufferOfSizeOne()

import serial
from serial.tools import list_ports


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


SERIAL_PORT = get_my_device()[0]
serial_reciver = SerialReceiver(queue, SERIAL_PORT)
serial_reciver.daemon = True
serial_reciver.start()


# Recording thread instance
recorder = None


# Cleanup routine when the program exits
def exit_handler():
    logger.info("(from logger) Program exit..: exit_handler()")
    serial_reciver.set_stop()
    serial_reciver.join()


atexit.register(exit_handler)

previous_print_time = time.time()


# Stream images from the message queue
def video_streaming():  # -> Any:
    before_img = None
    global previous_print_time
    while True:
        # Pull frames from the queue and stream them as HTTP multipart JPEG
        img = queue.get()
        if img != before_img or img != None:
            before_img = img
            yield (
                b"\r\n--frame\r\n" b"Content-Type: image/jpeg\r\n\r\n" + img + b"\r\n"
            )
            time_now = time.time()
            if time_now - previous_print_time > 0.025:
                # print('now streaming in localhost ...')
                to_js_dict = {
                    "name": "Stream_Device_Video",
                    "sender": "python",
                    "succes": True,
                    "param": {"status": "in-progress"},
                }
                send_event(to_js_dict)
                previous_print_time = time_now
        else:
            time.sleep(0.02)


@app.get("/video")
async def video():
    # Use StreamingResponse to continuously send images
    return StreamingResponse(
        video_streaming(), media_type="multipart/x-mixed-replace; boundary=--frame"
    )


# code write test
@app.get("/code_write")
async def code_write(code):
    serial_reciver.write_code(code)


# Start recording
@app.get("/record_start")
async def record_start(file_name):
    logger.info("(from logger) Recording start.")
    global recorder
    if recorder:
        return {"result": "Now recording.", "file_name": recorder.record_file_path}

    else:
        recorder = Recorder(queue)
        recorder.daemon = True
        recorder.set_record_file_path(file_name)
        recorder.start()

        return {"result": "OK", "file_name": file_name}


# Stop recording
@app.get("/record_stop")
async def record_stop():
    # logger.info("Recording exit ")
    logger.info("(from logger) Recording exit.")
    global recorder
    if recorder:
        recorder.set_stop()
        current_record_file_path = recorder.record_file_path
        recorder.join()
        recorder = None
        return {"result": "OK", "file_name": current_record_file_path}
    else:
        return {"result": "Recording is not started..", "file_name": ""}


# Query recording status
@app.get("/record_status")
async def record_status():
    global recorder
    if recorder and recorder.is_alive():
        return {"result": "OK", "file_name": recorder.record_file_path}
    else:
        return {"result": "Recording is not started..", "file_name": ""}
