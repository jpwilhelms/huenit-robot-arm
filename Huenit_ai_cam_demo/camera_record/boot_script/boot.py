from machine import UART
repl = UART.repl_uart()
repl.init(1500000, 8, None, 1, read_buf_len=4096)