# gganada update 24.04.23
# gganada update 25.03.05 -> unused source (target_inner_scripts)
"""
Module used for communicating with the robot and controlling its motion via
UART.
"""
import _thread      # import needed to use Python threads

from machine import UART
from Maix import GPIO
from fpioa_manager import fm
import time
import math
fm.register(6, fm.fpioa.UART1_TX, force=True)
fm.register(7, fm.fpioa.UART1_RX, force=True)

uart = UART(UART.UART1, 115200, 8, 1, 0, timeout=1000, read_buf_len=4096)
# Two variables used by the robot movement thread
state = 0

commandQ = None

def checkConnection():
    """
    Check whether the robot is connected.
    Sends command M400 and waits up to 0.1 seconds for a response.
    Treats a missing response as disconnected and an "ok" response as connected.
    """
    command = "M400\n"
    uart.write(command.encode())
    strt = time.time()
    while True:
        if(time.time() - strt > 0.1):
            return False
        read_data = uart.read()
        if read_data:
            if read_data.decode('utf-8').find("ok") > -1:
                break
            else:
                pass
    return True

def sendCommand(command):
    """
    Internal helper used to send a command to the robot.

    :param command: string to send

    Sends the command and waits for a response.
    """
    uart.write(command.encode())
    while True:
        read_data = uart.read()
        if read_data:
            if read_data.decode('utf-8').find("ok") > -1:
                break
            else:
                pass
        time.sleep(0.00001)

def sendCommandNoReturn(command):
    """
    Internal helper used to send a command to the robot.

    :param command: string to send

    Sends the command without waiting for a response.
    """
    uart.write(command.encode())

def moveThread():
    """
    Thread worker that allows the next Python script to continue while the robot
    performs a movement. Started at the bottom of the module and used internally.
    """
    while True:
        global state

        if state == 0:      #
            global commandQ
            if commandQ != None:
                state = 1   # mark that motion is in progress
                sendCommand(commandQ)
                sendCommand("M400\n")
                commandQ = None # clear commandQ so the next loop knows nothing is pending
                state = 0   # motion finished, indicate idle state
        else:
            pass
        time.sleep(0.00001)
    
def isMoving():
    """
    Return whether the robot is currently in motion. Used by moveG0, moveG1, and
    moveThread.

    :return: state (boolean)
    """
    global state
    try:
        return state
    except:
        return 1

def checkXYZ(x,y,z):
    """
    Check whether the robot can perform a G0 move to the specified coordinates.

    :param x: float, target x coordinate
    :param y: float, target y coordinate
    :param z: float, target z coordinate

    :return: int, returns 1 if the pose is reachable, else 0
    """
    leng = math.sqrt(x*x + y*y)
    if(leng <=213.44 and z >=2.182):
        if(z<=9.066):
            if(not (leng > 61 + math.pow((55*55 -(z-30)**2),(0.5)))):
                # print('first err')
                return 0
        elif(z<=100.1):
            if(not (leng > math.pow((152**2-(z-147)**2),(0.5))+48)):
                # print('second err')
                return 0
        else:
            if(not (leng > math.pow((3600 - (z-148)**2),(0.5))+153.5)):
                # print('third err')
                return 0
    elif(leng <= 224.566 and z <=3.241):
        if(not (leng > math.pow((144**2 - (z+138)**2),(0.5))+81)):
            # print('fourth err')
            return 0
    else:
        if(not ((leng < (16500+100*z)/17) and ((leng-228)**2+(z+4)**2 <150**2))):
            # print('fifth err')
            return 0
    
    if( y <0):
        ix = (-1*y)/leng
        # print("ix: ",ix)
        if 0.98 < ix:
            return 0

    # print('cango')    
    return 1
    
def moveG0(x, y, z, wait = True): # new wait parameter: True blocks, False uses thread
    """
    Execute a G0 movement.

    :param x: float, target x coordinate
    :param y: float, target y coordinate
    :param z: float, target z coordinate
    :param wait: boolean, if True wait until the robot finishes moving

    A G0 move drives the robot as quickly as possible.
    """ 
    send = 0
    if(checkXYZ(x,y,z)==1):
        send = 1
    

    global commandQ
    command = "G0 X" + str(x) + " Y" + str(y) + " Z" + str(z) + "\n"
    
    time.sleep(0.00001)
    global state
    
    if state == 0 and send ==1:  # no motion in progress
        if wait == True:    # synchronous behavior
            state = 1
            sendCommand(command)
            sendCommand("M400\n")
            state = 0

        elif wait == False: # asynchronous behavior
            commandQ = command
    elif state == 1:           # already moving, do nothing
        send = 2
        pass
    time.sleep(0.00001)
    return send         # 1 if reachable and queued, 2 if busy, 0 if unreachable

def moveG1(x, y, z, wait = True): # new wait parameter: True blocks, False uses thread
    """
    Execute a G1 movement.

    :param x: float, target x coordinate
    :param y: float, target y coordinate
    :param z: float, target z coordinate
    :param wait: boolean, if True wait until the robot finishes moving

    A G1 move drives the robot along a straight path.
    """ 
    send = 0
    if(checkXYZ(x,y,z)==1):
        send = 1
    

    global commandQ
    command = "G1 X" + str(x) + " Y" + str(y) + " Z" + str(z) + "\n"
    
    time.sleep(0.00001)
    global state
    
    if state == 0 and send ==1:  # no motion in progress
        if wait == True:    # synchronous behavior
            state = 1
            sendCommand(command)
            sendCommand("M400\n")
            state = 0

        elif wait == False: # asynchronous behavior
            commandQ = command
    elif state == 1:           # already moving, do nothing
        send = 2
        pass
    time.sleep(0.00001)
    return send         # 1 if reachable and queued, 2 if busy, 0 if unreachable

def pumpOn():
    command = "M1400 A1023" + "\n"
    sendCommand(command)

def pumpOnGripper():
    # Changing to A623 alters the suction strength
    command = "M1400 A623" + "\n"
    sendCommand(command)

def pumpOff():
    command = "M1400 A0" + "\n"
    sendCommand(command)

def pump(power):
    command = "M1400 A" + str(power) + "\n"
    sendCommand(command)

def valveOn():
    command = "M1401 A1" + "\n"
    sendCommand(command)

def valveOff():
    command = "M1401 A0" + "\n"
    sendCommand(command)

def suctionOn():
    """
    Turn on the robot suction module.
    """
    valveOff()
    pumpOn()

def suctionOff():
    """
    Turn off the robot suction module.
    """
    pumpOff()
    valveOn()
    time.sleep(0.3)
    valveOff()

def gripper(state):
    """
    Configure the robot gripper module.

    :param state: int, 0 - idle, 1 - open, 2 - close
    """
    if state == 0:
        pumpOff()
        valveOn()
        time.sleep(0.3)
        valveOff()
    elif state == 1:
        valveOff()
        pumpOnGripper()
    elif state == 2:
        valveOn()
        pumpOnGripper()

def set_current_position():
    sendCommand("M1500 B4\n")

def moveAngle(a,b,c):
    """
    Move the robot by providing axis angles.

    :param a: float, angle a
    :param b: float, angle b
    :param c: float, angle c
    """
    command = "M1005 A" + str(a) + " B" + str(b) + " C" + str(c) + "\n"
    sendCommand(command)
    sendCommand("M400\n")

def moveAngle_noM400(a,b,c):
    command = "M1005 A" + str(a) + " B" + str(b) + " C" + str(c) + "\n"
    sendCommand(command)

def moveZ0_M400(z):
    command = "G0 Z" + str(z) + "\n"
    sendCommand(command)
    sendCommand("M400\n")

def moveZ0(z):
    command = "G0 Z" + str(z) + "\n"
    sendCommand(command)

def extract_floats(text):
    """
    Extract floating point numbers from the robot response. Used internally.

    :param text: string, response from the robot

    :return: list(float), float values found in the text including +/- signs
    """

    floats = []
    current_number = ""

    for char in text:
        if char.isdigit() or char in ".+-":
            current_number += char
        else:
            if current_number:
                try:
                    floats.append(float(current_number))
                except ValueError:
                    pass  # Ignore invalid format
                current_number = ""

    if current_number:
        try:
            floats.append(float(current_number))
        except ValueError:
            pass

    return floats

def getLoc():
    """
    Retrieve the current position of the robot arm.

    :return: tuple (x(float), y(float), z(float)) containing the coordinates
    """
    uart.write("M1008 A3\n".encode())
    read_data = None
    while True:
        read_data = uart.read()
        if read_data:
            if read_data.decode('utf-8').find("ok") > -1:
                break
            else:
                pass
    return extract_floats(read_data.decode('utf-8'))

def getLocCanNull():
    """
    Retrieve the current position of the robot arm.

    :return: tuple (x(float), y(float), z(float)) or None if the query times out
    """
    uart.write("M1008 A3\n".encode())
    read_data = None
    cnTime = time.time()
    while True:
        read_data = uart.read()
        if(time.time() - cnTime > 0.01):
            return None
        if read_data:
            if read_data.decode('utf-8').find("ok") > -1:
                break
            else:
                if(time.time() - cnTime > 0.01):
                    return None

    return extract_floats(read_data.decode('utf-8'))



def getDeg():
    """
    Obtain the joint encoder angles.

    :return: tuple (a(float), b(float), c(float)) with encoder values
    """
    uart.write("M1008 A2\n")
    read_data = None
    while True:
        read_data = uart.read()
        if read_data:
            if read_data.decode('utf-8').find("ok") > -1:
                break
            else:
                pass
    return extract_floats(read_data.decode('utf-8'))

def freeMod():
    """
    Release motor torque so the user can move the robot freely.
    """
    sendCommand("M84\n")

def unsetFreeMod():
    """
    Apply motor torque so the user can no longer move the robot freely.
    """
    sendCommand("M17\n")

def moduleCheckAble(enable):
    """
    Enable or disable module status checking.
    """
    sendCommand("M1600 D" + str(enable) + "\n")

_thread.start_new_thread(moveThread,())
