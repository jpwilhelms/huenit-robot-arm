import time
import lcd


def draw_frame(rotation):
    lcd.rotation(rotation)
    lcd.clear(lcd.BLACK)

    # Color combinations per rotation
    colors = [
        (lcd.RED, lcd.YELLOW),
        (lcd.GREEN, lcd.CYAN),
        (lcd.BLUE, lcd.WHITE),
        (lcd.BLACK, lcd.MAGENTA),
    ]
    bg, fg = colors[rotation % len(colors)]

    lcd.fill_rect(20, 60, 280, 50, bg)
    lcd.draw_rectangle(18, 58, 284, 54, fg)

    lcd.fill_rect(40, 140, 240, 50, fg)
    lcd.draw_rectangle(38, 138, 244, 54, bg)

    lcd.draw_line(20, 60, 300, 190, fg)
    lcd.draw_line(20, 190, 300, 60, fg)


def main():
    lcd.init()
    while True:
        for rot in range(4):
            draw_frame(rot)
            time.sleep_ms(1000)


main()
