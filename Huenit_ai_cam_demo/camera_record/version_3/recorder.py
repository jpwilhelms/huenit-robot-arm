import time
from threading import Thread

import cv2
import numpy as np
from loguru import logger

from buffer_queue import ThreadSafeBufferOfSizeOne
from record_util import send_event


class Recorder(Thread):
    is_running = False

    def __init__(self, queue: ThreadSafeBufferOfSizeOne, desire_fps=24):
        super().__init__()
        self.queue = queue
        self.desire_fps = desire_fps

    def set_record_file_path(self, file_path):
        self.record_file_path = file_path

    def set_stop(self):
        self.is_running = False

    def run(self):
        self.is_running = True
        print("Recording thread Start.")
        to_js_dict = {
            "name": "Stream_Device_Record",
            "sender": "python",
            "succes": True,
            "param": {"status": "ready"},
        }
        send_event(to_js_dict)

        out = None
        start_time = time.time()
        before_image = ""
        last_time = ""
        init_flag = True
        while self.is_running:
            image: bytes = self.queue.get()

            if before_image == image or not image:
                time.sleep(0.02)
                continue

            before_image = image

            # Decode the JPEG bytes into an OpenCV matrix
            img_np = np.frombuffer(image, dtype=np.uint8)
            img_cv: np.ndarray = cv2.imdecode(img_np, cv2.IMREAD_COLOR)

            if out is None:
                height, width, channels = img_cv.shape

                logger.info(f"image width : width={width}, height={height}")
                out = cv2.VideoWriter(
                    self.record_file_path,
                    cv2.VideoWriter_fourcc(*"H264"),
                    self.desire_fps,
                    (width, height),
                )

            # Write the frame to disk
            end_time = end_time = time.time()
            frame_duation = end_time - start_time
            frame_per_second = int(self.desire_fps * frame_duation)
            logger.info(
                f"start_time={start_time}, end_time={end_time}, frame_duation={frame_duation}, frame_per_second={frame_per_second}"
            )
            to_js_dict = {
                "name": "Stream_Device_Record",
                "sender": "python",
                "succes": True,
                "param": {"status": "in-progress", "time": f"{start_time}"},
            }

            if init_flag:
                to_js_dict["param"]["status"] = "start"
                send_event(to_js_dict)
                init_flag = False
            else:
                send_event(to_js_dict)

            last_time = end_time

            for i in range(frame_per_second):
                out.write(img_cv)
            # cv2.imshow("Frame", img_cv)
            import uuid, os

            # path = os.path.join(os.getcwd(), 'images', str(uuid.uuid1()))
            path = os.path.join(
                "/Users/paul/Code_files/SUPERNOVA_MARKUP/src/Luban/resources/huenit_py/src/python_protocol_cores/camera_record/version_3/images",
                f"{str(uuid.uuid1())}.jpg",
            )
            # cv2.imwrite(path, img_cv)

            # if cv2.waitKey(1) & 0xFF == ord("q"):
            #     break
            start_time = end_time

        out.release()
        # logger.info("Record thread exit ")
        logger.info("Recording Thread exit.")
        to_js_dict = {
            "name": "Stream_Device_Record",
            "sender": "python",
            "succes": True,
            "param": {"status": "done", "time": f"{last_time}"},
        }
        send_event(to_js_dict)
