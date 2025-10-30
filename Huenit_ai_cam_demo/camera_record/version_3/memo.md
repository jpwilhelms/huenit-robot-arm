
# Device Prerequisites
Configure only the REPL (UART) portion and write it to the device (boot.py).
```python

# Set the UART baudrate to 1,500,000 when the script starts for higher throughput.
from machine import UART
repl = UART.repl_uart()
repl.init(1500000, 8, None, 1, read_buf_len=4096, ide=False, from_ide=False)

```






# Python Program
## How to Run

#### Install the required libraries

```bash
pip install uvicorn opencv-python pyserial fastapi  VideoCapture
```

#### Launch the program

```bash
python .\main.py
```

## HTTP Video Streaming

Open the following URL in a browser to receive an MJPEG stream.

```
http://localhost:10600/video
```

## Recording

#### Start recording

Call the URL below to begin recording. Use the `file_name` parameter to select the output filename.

```
http://localhost:10600/record_start?file_name=test34.mp4
```

#### Stop recording

Invoke the next URL to stop recording.

```
http://localhost:10600/record_stop
```

#### decode
https://www.urldecoder.org/

#### Program write
Call the `/code_write` URL to execute the value of the `code` parameter on the device.

http://localhost:10300/code_write?code=import%20sensor%2C%20image%2C%20time%2C%20lcd%0Afrom%20machine%20import%20UART%0 Afrom%20binascii%20import%20hexlify%0A%0Alcd.init%28%29%20%20%20%20%20%20%20%20%20%20%2 0%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%23%20Init%20lcd%20display%0Alcd.clear %28lcd.RED%29%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%23%20Clear% 20lcd%20screen.%0A%0Asensor.reset%28dual_buff%3DTrue%29%20%23%20improve%20fps%0Asensor.reset %28%29%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%23% 20Reset%20and%20initialize%20the%20sensor.%0Asensor.set_pixformat%28sensor.RGB565%29%20%23%20S et%20pixel%20format%20to%20RGB565%20%28or%20GRAYSCALE%29%0Asensor.set_framesize%28sensor.Q VGA%29%20%20%20%23%20Set%20frame%20size%20to%20QVGA%20%28320x240%29%0Asensor.skip_fra mes%28time%20%3D%202000%29%20%20%20%20%20%23%20Wait%20for%20settings%20take%20effect.% 0Aclock%20%3D%20time.clock%28%29%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20 %23%20Create%20a%20clock%20object%20to%20track%20the%20FPS.%0Asend_len%2C%20count%2C%20e rr%20%3D%200%2C%200%2C%200%0A%0Awhile%28True%29%3A%0A%20%20%20%20clock.tick%28%29% 20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%23%20Update%20the% 20FPS%20clock.%0A%20%20%20%20img%20%3D%20sensor.snapshot%28%29%20%20%20%20%20%20%20 %20%20%23%20Take%20a%20picture%20and%20return%20the%20image.%0A%20%20%20%20lcd.display% 28img%29%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%23%20Display%20image%20 on%20lcd.%0A%20%20%20%20%23logger.info%28clock.fps%28%29%29%20%20%20%20%20%20%20%20% 20%20%20%20%20%20%23%20Note%3A%20CanMV%20Cam%20runs%20about%20half%20as%20fast%20w hen%20connected%23%23%20to%20the%20IDE.%20The%20FPS%20should%20increase%20once%20disconn ected.%0A%0A%0A%0A%0A%20%20%20%20img%20%3D%20img.compress%28quality%3D60%29%0A%20% 20%20%20img_bytes%20%3D%20img.to_bytes%28%29%0A%20%20%20%20repl.write%28img_bytes%29

import sensor, image, time, lcd
from machine import UART
from binascii import hexlify

lcd.init()                          # Init lcd display
lcd.clear(lcd.RED)                  # Clear lcd screen.

sensor.reset(dual_buff=True) # improve fps
sensor.reset()                      # Reset and initialize the sensor.
sensor.set_pixformat(sensor.RGB565) # Set pixel format to RGB565 (or GRAYSCALE)
sensor.set_framesize(sensor.QVGA)   # Set frame size to QVGA (320x240)
sensor.skip_frames(time = 2000)     # Wait for settings take effect.
clock = time.clock()                # Create a clock object to track the FPS.
send_len, count, err = 0, 0, 0

while(True):
    clock.tick()                    # Update the FPS clock.
    img = sensor.snapshot()         # Take a picture and return the image.
    lcd.display(img)                # Display image on lcd.
    #logger.info(clock.fps())              # Note: CanMV Cam runs about half as fast when connected## to the IDE. The FPS should increase once disconnected.




    img = img.compress(quality=60)
    img_bytes = img.to_bytes()
    repl.write(img_bytes)

http://localhost:10300/code_write?code=import%20sensor%2C%20image%2C%20time%2C%20lcd%0Afrom%20machine%20import%20UART%0Afrom%20binascii%20import%20hexlify%0A%0Alcd.init%28%29%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%23%20Init%20lcd%20display%0Alcd.clear%28lcd.RED%29%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%23%20Clear%20lcd%20screen.%0A%0Alcd.init%28freq%3D15000000%29%0Asensor.reset%28dual_buff%3DTrue%29%20%20%20%20%20%20%20%20%23%20improve%20fps%0Asensor.reset%28%29%0Asensor.set_pixformat%28sensor.RGB565%29%0Asensor.set_framesize%28sensor.QVGA%29%0Asensor.skip_frames%28time%20%3D%202000%29%20%0Asensor.set_windowing%28%28224%2C%20224%29%29%0Asensor.run%281%29%0Asensor.set_vflip%281%29%0Asensor.set_hmirror%281%29%0A%0Aclock%20%3D%20time.clock%28%29%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%23%20Create%20a%20clock%20object%20to%20track%20the%20FPS.%0Asend_len%2C%20count%2C%20err%20%3D%200%2C%200%2C%200%0A%0Awhile%28True%29%3A%0A%20%20%20%20clock.tick%28%29%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%23%20Update%20the%20FPS%20clock.%0A%20%20%20%20img%20%3D%20sensor.snapshot%28%29%20%20%20%20%20%20%20%20%20%23%20Take%20a%20picture%20and%20return%20the%20image.%0A%20%20%20%20lcd.display%28img%29%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%23%20Display%20image%20on%20lcd.%0A%20%20%20%20%23logger.info%28clock.fps%28%29%29%20%20%20%20%20%20%20%20%20%20%20%20%20%20%23%20Note%3A%20CanMV%20Cam%20runs%20about%20half%20as%20fast%20when%20connected%23%23%20to%20the%20IDE.%20The%20FPS%20should%20increase%20once%20disconnected.%0A%0A%20%20%20%20img%20%3D%20img.compress%28quality%3D60%29%0A%20%20%20%20img_bytes%20%3D%20img.to_bytes%28%29%0A%20%20%20%20repl.write%28img_bytes%29



import sensor, image, time, lcd
from machine import UART
from binascii import hexlify

repl = UART.repl_uart()

lcd.init()                          # Init lcd display
lcd.clear(lcd.RED)                  # Clear lcd screen.

lcd.init(freq=15000000)
sensor.reset(dual_buff=True)        # improve fps
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QVGA)
sensor.skip_frames(time = 2000) 
sensor.set_windowing((224, 224))
sensor.set_vflip(1)
sensor.set_hmirror(1)

clock = time.clock()                # Create a clock object to track the FPS.
send_len, count, err = 0, 0, 0

while(True):
    clock.tick()                    # Update the FPS clock.
    img = sensor.snapshot()         # Take a picture and return the image.
    lcd.display(img)                # Display image on lcd.
    #logger.info(clock.fps())              # Note: CanMV Cam runs about half as fast when connected## to the IDE. The FPS should increase once disconnected.

    img = img.compress(quality=60)
    img_bytes = img.to_bytes()
    repl.write(img_bytes)




http://localhost:10300/code_write?code=import%20sensor%2C%20image%2C%20time%2C%20lcd%0Afrom%20machine%20import%20UART%0Afrom%20binascii%20import%20hexlify%0A%0Arepl%20%3D%20UART.repl_uart%28%29%0A%0Alcd.init%28%29%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%23%20Init%20lcd%20display%0Alcd.clear%28lcd.RED%29%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%23%20Clear%20lcd%20screen.%0A%0Alcd.init%28freq%3D15000000%29%0Asensor.reset%28dual_buff%3DTrue%29%20%20%20%20%20%20%20%20%23%20improve%20fps%0Asensor.reset%28%29%0Asensor.set_pixformat%28sensor.RGB565%29%0Asensor.set_framesize%28sensor.QVGA%29%0Asensor.skip_frames%28time%20%3D%202000%29%20%0Asensor.set_windowing%28%28224%2C%20224%29%29%0Asensor.set_vflip%281%29%0Asensor.set_hmirror%281%29%0A%0Aclock%20%3D%20time.clock%28%29%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%23%20Create%20a%20clock%20object%20to%20track%20the%20FPS.%0Asend_len%2C%20count%2C%20err%20%3D%200%2C%200%2C%200%0A%0Awhile%28True%29%3A%0A%20%20%20%20clock.tick%28%29%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%23%20Update%20the%20FPS%20clock.%0A%20%20%20%20img%20%3D%20sensor.snapshot%28%29%20%20%20%20%20%20%20%20%20%23%20Take%20a%20picture%20and%20return%20the%20image.%0A%20%20%20%20lcd.display%28img%29%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%23%20Display%20image%20on%20lcd.%0A%20%20%20%20%23logger.info%28clock.fps%28%29%29%20%20%20%20%20%20%20%20%20%20%20%20%20%20%23%20Note%3A%20CanMV%20Cam%20runs%20about%20half%20as%20fast%20when%20connected%23%23%20to%20the%20IDE.%20The%20FPS%20should%20increase%20once%20disconnected.%0A%0A%20%20%20%20img%20%3D%20img.compress%28quality%3D60%29%0A%20%20%20%20img_bytes%20%3D%20img.to_bytes%28%29%0A%20%20%20%20repl.write%28img_bytes%29


import sensor, image, time, lcd
from machine import UART
from binascii import hexlify

repl = UART.repl_uart()

lcd.init()                          # Init lcd display
lcd.clear(lcd.RED)                  # Clear lcd screen.

sensor.reset(dual_buff=True)        # improve fps
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QVGA)
sensor.skip_frames(time = 2000) 
sensor.set_windowing((224, 224))
sensor.set_vflip(1)
sensor.set_hmirror(1)

clock = time.clock()                # Create a clock object to track the FPS.
send_len, count, err = 0, 0, 0

while(True):
    clock.tick()                    # Update the FPS clock.
    img = sensor.snapshot()         # Take a picture and return the image.
    lcd.display(img)                # Display image on lcd.
    #logger.info(clock.fps())              # Note: CanMV Cam runs about half as fast when connected## to the IDE. The FPS should increase once disconnected.

    img = img.compress(quality=60)
    img_bytes = img.to_bytes()
    repl.write(img_bytes)

http://localhost:10600/code_write?code=import%20sensor%2C%20image%2C%20time%2C%20lcd%0Afrom%20machine%20import%20UART%0Afrom%20binascii%20import%20hexlify%0A%0Arepl%20%3D%20UART.repl_uart%28%29%0A%0Alcd.init%28%29%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%23%20Init%20lcd%20display%0Alcd.clear%28lcd.RED%29%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%23%20Clear%20lcd%20screen.%0A%0Asensor.reset%28dual_buff%3DTrue%29%20%20%20%20%20%20%20%20%23%20improve%20fps%0Asensor.set_pixformat%28sensor.RGB565%29%0Asensor.set_framesize%28sensor.QVGA%29%0Asensor.skip_frames%28time%20%3D%202000%29%20%0Asensor.set_windowing%28%28224%2C%20224%29%29%0Asensor.set_vflip%281%29%0Asensor.set_hmirror%281%29%0A%0Aclock%20%3D%20time.clock%28%29%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%23%20Create%20a%20clock%20object%20to%20track%20the%20FPS.%0Asend_len%2C%20count%2C%20err%20%3D%200%2C%200%2C%200%0A%0Awhile%28True%29%3A%0A%20%20%20%20clock.tick%28%29%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%23%20Update%20the%20FPS%20clock.%0A%20%20%20%20img%20%3D%20sensor.snapshot%28%29%20%20%20%20%20%20%20%20%20%23%20Take%20a%20picture%20and%20return%20the%20image.%0A%20%20%20%20lcd.display%28img%29%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%23%20Display%20image%20on%20lcd.%0A%20%20%20%20%23logger.info%28clock.fps%28%29%29%20%20%20%20%20%20%20%20%20%20%20%20%20%20%23%20Note%3A%20CanMV%20Cam%20runs%20about%20half%20as%20fast%20when%20connected%23%23%20to%20the%20IDE.%20The%20FPS%20should%20increase%20once%20disconnected.%0A%0A%20%20%20%20img%20%3D%20img.compress%28quality%3D60%29%0A%20%20%20%20img_bytes%20%3D%20img.to_bytes%28%29%0A%20%20%20%20repl.write%28img_bytes%29

import sensor, image, time, lcd
from machine import UART
from binascii import hexlify

repl = UART.repl_uart()

lcd.init()                          # Init lcd display
loading = image.Image(size=(lcd.width(), lcd.height()))
loading.draw_rectangle((0, 0, lcd.width(), lcd.height()), fill=True, color=(255, 0, 0))
info = "Loading cam sensor ..."
loading.draw_string(int(lcd.width()//2 - len(info) * 5), (lcd.height())//4, info, color=(255, 255, 255), scale=2, mono_space=0)
lcd.display(loading)

sensor.reset(dual_buff=True)        # improve fps
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QVGA)
sensor.skip_frames(time = 2000) 
sensor.set_windowing((224, 224))
sensor.set_vflip(1)
sensor.set_hmirror(1)

clock = time.clock()                # Create a clock object to track the FPS.
send_len, count, err = 0, 0, 0

while(True):
    clock.tick()                    # Update the FPS clock.
    img = sensor.snapshot()         # Take a picture and return the image.
    lcd.display(img)                # Display image on lcd.
    #logger.info(clock.fps())              # Note: CanMV Cam runs about half as fast when connected## to the IDE. The FPS should increase once disconnected.

    img = img.compress(quality=60)
    img_bytes = img.to_bytes()
    repl.write(img_bytes)

http://localhost:10600/code_write?code=import%20sensor%2C%20image%2C%20time%2C%20lcd%0Afrom%20machine%20import%20UART%0Afrom%20binascii%20import%20hexlify%0A%0Arepl%20%3D%20UART.repl_uart%28%29%0A%0Alcd.init%28%29%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%23%20Init%20lcd%20display%0Aloading%20%3D%20image.Image%28size%3D%28lcd.width%28%29%2C%20lcd.height%28%29%29%29%0Aloading.draw_rectangle%28%280%2C%200%2C%20lcd.width%28%29%2C%20lcd.height%28%29%29%2C%20fill%3DTrue%2C%20color%3D%28255%2C%200%2C%200%29%29%0Ainfo%20%3D%20%22Loading%20cam%20sensor%20...%22%0Aloading.draw_string%28int%28lcd.width%28%29%2F%2F2%20-%20len%28info%29%20%2A%205%29%2C%20%28lcd.height%28%29%29%2F%2F4%2C%20info%2C%20color%3D%28255%2C%20255%2C%20255%29%2C%20scale%3D2%2C%20mono_space%3D0%29%0Alcd.display%28loading%29%0A%0Asensor.reset%28dual_buff%3DTrue%29%20%20%20%20%20%20%20%20%23%20improve%20fps%0Asensor.set_pixformat%28sensor.RGB565%29%0Asensor.set_framesize%28sensor.QVGA%29%0Asensor.skip_frames%28time%20%3D%202000%29%20%0Asensor.set_windowing%28%28224%2C%20224%29%29%0Asensor.set_vflip%281%29%0Asensor.set_hmirror%281%29%0A%0Aclock%20%3D%20time.clock%28%29%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%23%20Create%20a%20clock%20object%20to%20track%20the%20FPS.%0Asend_len%2C%20count%2C%20err%20%3D%200%2C%200%2C%200%0A%0Awhile%28True%29%3A%0A%20%20%20%20clock.tick%28%29%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%23%20Update%20the%20FPS%20clock.%0A%20%20%20%20img%20%3D%20sensor.snapshot%28%29%20%20%20%20%20%20%20%20%20%23%20Take%20a%20picture%20and%20return%20the%20image.%0A%20%20%20%20lcd.display%28img%29%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%23%20Display%20image%20on%20lcd.%0A%20%20%20%20%23logger.info%28clock.fps%28%29%29%20%20%20%20%20%20%20%20%20%20%20%20%20%20%23%20Note%3A%20CanMV%20Cam%20runs%20about%20half%20as%20fast%20when%20connected%23%23%20to%20the%20IDE.%20The%20FPS%20should%20increase%20once%20disconnected.%0A%0A%20%20%20%20img%20%3D%20img.compress%28quality%3D60%29%0A%20%20%20%20img_bytes%20%3D%20img.to_bytes%28%29%0A%20%20%20%20repl.write%28img_bytes%29
