import time
import lcd


def main():
    lcd.init()
    lcd.rotation(2)
    lcd.clear(lcd.BLACK)

    # Two bars as a simple "HELLO / HUENIT" display
    lcd.fill_rect(20, 80, 120, 40, lcd.YELLOW)
    lcd.fill_rect(20, 150, 160, 40, lcd.CYAN)

    # Add borders so the bars are clearly separated
    lcd.draw_rectangle(18, 78, 124, 44, lcd.RED)
    lcd.draw_rectangle(18, 148, 164, 44, lcd.BLUE)

    # Optional: diagonal lines for extra contrast
    lcd.draw_line(20, 80, 140, 120, lcd.RED)
    lcd.draw_line(20, 150, 180, 190, lcd.BLUE)

    while True:
        time.sleep_ms(500)


main()
