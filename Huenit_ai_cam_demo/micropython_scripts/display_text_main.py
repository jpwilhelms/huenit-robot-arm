import time
import lcd


def main():
    lcd.init()
    lcd.rotation(2)
    lcd.font(lcd.FONT_DejaVu40)
    lcd.clear(lcd.NAVY)
    lcd.draw_string(20, 90, "HELLO", lcd.YELLOW, lcd.NAVY)
    lcd.draw_string(20, 150, "HUENIT", lcd.CYAN, lcd.NAVY)
    while True:
        time.sleep_ms(500)


main()
