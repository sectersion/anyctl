# USB-CDC <-> UART0 bridge — drag onto the MICROPY drive, then wire:
# GP0 (pin 1) = TX -> router RX   GP1 (pin 2) = RX <- router TX   GND = GND
# Never touch VBUS/5V. Baud 115200. Open the new COM port with console.py.
from machine import UART
import sys
from select import select

uart = UART(0, 115200, tx=0, rx=1, rxbuf=4096, timeout=0)
while True:
    r, _, _ = select([sys.stdin.buffer, uart], [], [], 0.05)
    if uart in r:
        d = uart.read()
        if d:
            sys.stdout.buffer.write(d)
            sys.stdout.buffer.flush()
    if sys.stdin.buffer in r:
        d = sys.stdin.buffer.read(1)
        if d:
            uart.write(d)
