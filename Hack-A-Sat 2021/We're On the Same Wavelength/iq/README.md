# iq

### We're On the Same Wavelength

*22 points, 225 solves*

Active ADDVulcan Players:
- mossmann

## Challenge Description

Convert the provided series of transmit bits into in-phase quadrature samples.

### Ticket

Present this ticket when connecting to the challenge:
```
ticket{sierra788811india2:XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX}
```
Don't share your ticket with other teams.

### Connecting

Connect to the challenge on:
```
unique-permit.satellitesabove.me:5006
```

Using netcat, you might run:
```
nc unique-permit.satellitesabove.me 5006
```

### Solving

Your team's flag for this challenge will look something like:
```
flag{sierra788811india2:___a bunch of unguessable stuff___} 
```

## Writeup by mossmann

The server presented a QPSK modulation exercise requiring conversion of data bits into a stream of quadrature samples.

```
$ nc unique-permit.satellitesabove.me 5006
Ticket please:
ticket{sierra788811india2:XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX}
IQ Challenge
   QPSK Modulation
          Q
          |
    01    |     11
    o     |+1   o
          |
          |
    -1    |     +1
===================== I
          |
          |
    00    |     10
    o     |-1   o
          |
          |
Convert the provided series of transmit bits into QPSK I/Q samples
                  |Start here
                  v
Bits to transmit: 01000011 01110010 01101111 01101101 01110101 01101100 01100101 01101110 01110100 00001010
Provide as interleaved I/Q e.g. 1.0 -1.0 -1.0  1.0 ...
                                 I    Q    I    Q  ...
Input samples:
```

I solved this in Python and pasted the output into the `nc` session.

```python
#!/usr/bin/env python3

from bitstring import Bits

bits = Bits('0b01000011011100100110111101101101011101010110110001100101011011100111010000001010')

constellation=('-1.0 -1.0 ', '-1.0 1.0 ', '1.0 -1.0 ', '1.0 1.0 ')

print(''.join([constellation[dibit.int] for dibit in bits.cut(2)]))
```

```
Input samples: -1.0 1.0 -1.0 -1.0 -1.0 -1.0 1.0 1.0 -1.0 1.0 1.0 1.0 -1.0 -1.0 1.0 -1.0 -1.0 1.0 1.0 -1.0 1.0 1.0 1.0 1.0 -1.0 1.0 1.0 -1.0 1.0 1.0 -1.0 1.0 -1.0 1.0 1.0 1.0 -1.0 1.0 -1.0 1.0 -1.0 1.0 1.0 -1.0 1.0 1.0 -1.0 -1.0 -1.0 1.0 1.0 -1.0 -1.0 1.0 -1.0 1.0 -1.0 1.0 1.0 -1.0 1.0 1.0 1.0 -1.0 -1.0 1.0 1.0 1.0 -1.0 1.0 -1.0 -1.0 -1.0 -1.0 -1.0 -1.0 1.0 -1.0 1.0 -1.0
You got it! Here's your flag:
flag{sierra788811india2:GCTXc4Rx0CLs4xRaGZC7Kr5d9N3qTBfG8CkvLIoNpXloz0Sl2CLWsFgk_r4NxVQlQs7kpYCXKflqPbi7Nl4Y8SI}
```
