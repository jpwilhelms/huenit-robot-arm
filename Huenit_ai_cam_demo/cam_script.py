import sys
import serial.serialutil
import serial.tools.list_ports
import subprocess
from serial.serialutil import SerialException
from typing import Any, List
from huenit_util import *
from python_protocol_cores.ampy_samples.ampy.files import Files, DirectoryExistsError
from python_protocol_cores.ampy_samples.ampy.pyboard import Pyboard
import posixpath

import io
import contextlib
import threading
from queue import Queue, Empty
import time

print(sys.version)
pyEVENT_PLAY_CAMERA_CODE = "playCameraCode"
EVENT_PLAY_SAMPLE_CAMERA_CODE = "playSampleCameraCode"
EVENT_PLAY_MACHINE_CODE = "playMachineCode"
EVENT_PLAY_CAMERA_UPLOAD_CODE = "playCameraUploadCode"

filePath = "..."

envCliPath = get_ampy()

def getPort() -> List:
    ports = list(serial.tools.list_ports.comports())
    for port in ports:
        print(port.description)
        print(port.device)
    return ports

def scan_ports() -> Any:
    ports = list(serial.tools.list_ports.comports())
    available_ports = [(port.device, port.description, port.vid, port.pid, port.manufacturer, port.serial_number) for port in ports]
    return available_ports

def get_my_serial(port_list: List) -> str:
    result = 'None'
    for item in port_list:
        if item[-2] == 'FTDI':
            result = item[0]
            return result
    

def uploadCode(p_path, a_path, port, target_file_path, time_out) -> None:
    cliRun(p_path, a_path, port, time_out, ["put", target_file_path])


def showUsbFileList(p_path, a_path, port, time_out) -> None:
    # path = get_path("/flash")
    path = '/flash'
    cliRun(p_path, a_path, port, time_out, ["ls", path])

def deleteFile(p_path, a_path, port, target) -> None:
    path = get_path("/flash/"+target+".py")
    cliRun(p_path, a_path, port, ["rm", path])

def deleteMain(p_path, port) -> None:
    deleteFile(p_path, port, "main")

def playSampleCameraCode() -> None:
    ports = getPort()
    for port in ports:
        if is_huenit_usb(port):
            runScript(port, "default")
            

def runScript(p_path, a_path, port, target, time_out) -> None:
    cliRun(p_path, a_path, port, time_out, ["run", target])
    
def runThreadScript(p_path, port, target) -> None:
    cliThreadRun(p_path, port, ["run", target])

def resetScript(p_path, a_path, port, time_out) -> None:
    ### PATH
    cliRun(p_path, a_path, port, time_out, ["run", get_path(getcwd()+"/src/python_protocol_cores/ampy_samples/inter_remove.py")])

def interruptScript(p_path, a_path, port, time_out) -> None:
    cliRun(p_path, a_path, port, time_out, ["reset"])

def capture_print(func, *args,):
    # Create a buffer
    buffer = io.StringIO()

    # Redirect stdout to the buffer
    with contextlib.redirect_stdout(buffer):
        # Call the arbitrary function
        func(*args)

    # Retrieve the output from the buffer, strip trailing newline, and split by lines
    output = buffer.getvalue().rstrip().split('\n')

    return output

def cliRun(python_path: str, ampy_path: str, port: str, time_out: float, customCommand) -> None:    
    ampy = ampy_path
    try:
        command = ["--port", port, "--delay", "1"]+customCommand
        print('customCommand', customCommand)
        print('command', command)
        final_command = [python_path, ampy] + command
        print('final_command = ', final_command)
        
        r = subprocess.run(
                final_command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=time_out)
        out = (r.stdout).decode('utf-8')
        print(out)
    
    except subprocess.TimeoutExpired:
        erm = ("Time out! ... (in ampy protocol)")
        raise Exception(erm)
    
    except Exception as e:
        print(e)
        raise Exception('ampy run error')


def cliThreadRun(python_path: str, ampy_path: str, port: str, customCommand) -> None:
    ampy = ampy_path
    try:
        command = ["--port", port, "--delay", "1"]+customCommand
        print('customCommand', customCommand)
        print('command', command)
        final_command = [python_path, ampy] + command
        print('final_command = ', final_command)

        process = subprocess.Popen(final_command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        yield 'pid =' + str(process.pid)
        while True:
            output = process.stdout.readline().decode('utf-8')
            if output == '' and process.poll() is not None:
                break
            if output:
                yield output.strip()
        rc = process.poll()
    
    except subprocess.TimeoutExpired:
        erm = ("Time out! ... (in ampy protocol)")
        raise Exception(erm)
    
    except Exception as e:
        print(e)
        raise Exception('ampy run error')

import io, sys


class ContinuousIterator:
    def __init__(self, queue):
        self.queue = queue

    def __iter__(self):
        return self

    def __next__(self):
        try:
            return self.queue.get_nowait()
        except Empty:
            time.sleep(0.1)  
            return "No data return"  

        
def cliTestrun(local_file, output_queue, no_output=False, already_port_ser=None):
    try:
        _board = Pyboard(device='', already_port_ser=already_port_ser)
        board_files = Files(_board)
        
        print('Running board_files.run...')
        board_files.run(local_file, wait_output=not no_output, stream_output=not no_output ,output_queue=output_queue)
                
    except Exception as e:
        print('Error:', e)
        output_queue.put(f"Error: {str(e)}")
    finally:
        output_queue.put(None)  # exit signal

def hueCamRun(local_file, output_queue, no_output=False, already_port_ser=None):
    try:
        content = None
        with open(local_file, "r", encoding="UTF-8") as file:
            content = file.read()
        print("gganada hueCamScript: ", content)
        
        already_port_ser.write(b'\x05')
        time.sleep(0.01)
        
        already_port_ser.write(content.encode('utf-8'))
        
        time.sleep(0.01)
        already_port_ser.write(b'\x04')
        time.sleep(0.5)
        while True:
            time.sleep(0.3)
            message = already_port_ser.read(already_port_ser.in_waiting)
            try:
                decoded_message = message.decode('utf-8')
            except UnicodeDecodeError:
                decoded_message = message
            print("gganada updated", decoded_message, " ------------gganada end")
            
            if message:
                print("gganada Script debug: ", decoded_message, " ------------gganada end")
                output_queue.put(decoded_message)

    except Exception as e:
        print('Error:', e)
        output_queue.put(f"Error: {str(e)}")
    finally:
        output_queue.put(None)  # exit signal


def cliPut(local, remote=None, already_port_ser=None, timeout=None) -> None:
    _board = Pyboard(device='', already_port_ser=already_port_ser)
    board_files = Files(_board)
    if remote is None:
        remote = os.path.basename(os.path.abspath(local))

    if os.path.isdir(local):
        # Directory copy, create the directory and walk all children to copy
        # over the files.
        board_files = Files(_board)
        for parent, child_dirs, child_files in os.walk(local, followlinks=True):
            # Create board filesystem absolute path to parent directory.
            remote_parent = posixpath.normpath(
                posixpath.join(remote, os.path.relpath(parent, local))
            )
            try:
                board_files.mkdir(remote_parent)
            except DirectoryExistsError:
                pass
            # Loop through all the files and put them on the board too.
            for filename in child_files:
                with open(os.path.join(parent, filename), "rb") as infile:
                    remote_filename = posixpath.join(remote_parent, filename)
                    board_files.put_origin(remote_filename, infile.read(), timeout=timeout)

    else:
        with open(local, "rb") as infile:
            board_files = Files(_board)
            board_files.put_origin(remote, infile.read(), timeout=timeout)


# def line_generator(output_queue):
#     while True:
#         line = output_queue.get()
#         if line is None:  
#             break
#         yield line

def cliThreadRun_2(local_file, no_output=False, already_port_ser=None) -> None:
    output_queue = Queue()
    thread = threading.Thread(target=hueCamRun, 
                              kwargs={'local_file':local_file, 
                                      'output_queue': output_queue,
                                      'already_port_ser': already_port_ser})
    thread.start()
    return ContinuousIterator(output_queue)