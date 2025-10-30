import time
import lcd


def main():
    lcd.init()
    lcd.rotation(2)
    colors = [
        (lcd.RED, "RED"),
        (lcd.GREEN, "GREEN"),
        (lcd.BLUE, "BLUE"),
        (lcd.BLACK, "BLACK"),
    ]

    while True:
        for color, _ in colors:
            lcd.clear(color)
            time.sleep_ms(500)


main()
