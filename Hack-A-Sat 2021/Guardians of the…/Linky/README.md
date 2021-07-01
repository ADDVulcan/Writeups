# Linky

### Guardians of the…

*96 points, 41 solves*

Active ADDVulcan players:
- miek
- martling
- mossmann
- dtechshield

## Challenge Description

Years have passed since our satellite was designed, and the Systems Engineers didn't do a great job with the documentation. Partial information was left behind in the user documentation and we don't know what power level we should configure the Telemetry transmitter to ensure we have 10 dB of Eb/No margin over the minimum required for BER (4.4 dB) .

### Ticket

Present this ticket when connecting to the challenge:
```
ticket{golf947225golf2:XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX}
```
Don't share your ticket with other teams.

### Connecting

Connect to the challenge on:
```
wild-wish.satellitesabove.me:5022
```

Using netcat, you might run:
```
nc wild-wish.satellitesabove.me 5022
```

### Solving

Your team's flag for this challenge will look something like:
```
flag{golf947225golf2:___a bunch of unguessable stuff___} 
```

## Writeup by mossmann

The server prompted for the ticket and then presented a link budget exercise that at first appeared to include a great deal of superfluous information.

```
$ nc wild-wish.satellitesabove.me 5022
Ticket please:
ticket{golf947225golf2:XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX}
 _     _       _
| |   (_)_ __ | | ___   _
| |   | | '_ \| |/ / | | |
| |___| | | | |   <| |_| |
|_____|_|_| |_|_|\_\\__, |
                    |___/
    .-.
   (;;;)
    \_|
      \ _.--l--._
     . \    |     `.
   .` `.\   |    .` `.
 .`     `\  |  .`     `.
/ __      \.|.`      __ \/
|   ''--._ \V  _.--''   |
|        _ (") _        |
| __..--'   ^   '--..__ |
\         .`|`.         /-.)
 `.     .`  |  `.     .`
   `. .`    |    `. .`
     `._    |    _.`|
         `--l--`  | |
                  | |
                  | |
                  | |
         o        | |     o
          )    o  | |    (
         \|/  (   | |   \|/
             \|/  | | o  WWwwwW
                o | |  )
        WWwwWww ( | | \|/
               \|/WWwwWWwW


Our satellite has launched, but the user documentation and Critical Design Review package
for the Telemetry link are missing a few key details. Fill in the details to configure
the Telemetry Transmitter and solve the challenge.


Here's the information we have captured

************** Global Parameters *****************
Frequency (Hz): 12100000000.0
Wavelength (m): 0.025
Data Rate (bps): 10000000.0
************* Transmit Parameters ****************
Transmit Line Losses (dB): -1
Transmit Half-power Beamwidth (deg): 26.30
Transmit Antenna Gain (dBi): 16.23
Transmit Pointing Error (deg): 10.00
Transmit Pointing Loss (dB): -1.74
*************** Path Parameters ******************
Path Length (km): 2831
Polarization Loss (dB): -0.5
Atmospheric Loss (dB): -2.1
Ionospheric Loss (dB): -0.1
************** Receive Parameters ****************
Receive Antenna Diameter (m): 5.3
Receive Antenna Efficiency: 0.55
Receive Pointing Error (deg): 0.2
Receive System Noise Temperature (K): 522
Receive Line Loss (antenna to LNA) (dB): -2
Receive Demodulator Implementation Loss (dB): -2
Required Eb/No for BER (dB): 4.4

Calculate and provide the recieve antenna gain in dBi:
```

### Gain

We computed the antenna [area](https://duckduckgo.com/?q=area+of+a+circle) from its diameter and plugged numbers into a [web-based calculator](https://calculator.academy/antenna-gain-calculator/) to find that the receive antenna gain was 53.9 dBi (although this calculator did not display the units of the result!). I wasn't sure what precision would be required, so I entered 54 and found that it was accepted.

After accepting the answer, the server prompted us with another question. Perhaps the initial information was not as superfluous as we had supposed.

###  G/T

```
Calculate and provide the recieve antenna gain in dBi: 54

Good job.  You get to continue
Receive Antenna Gain (dBi): 54.00
Receive Half-power Beamwidth (deg): 0.33
Receive Pointing Error (deg): 0.2
Receive Pointing Loss (dB): -4.48

Okay, now we know the receive antenna gain.
Calculate and provide the ground terminal G/T (dB/K):
```

The second question asked for the ground station's [gain-to-noise-temperature](https://en.wikipedia.org/wiki/Antenna_gain-to-noise-temperature). Measuring or estimating G/T can be a fairly [complicated process](http://setileague.org/articles/g-t.htm). We tried using [some](https://www.satellite-calculations.com/Satellite/gtsys.htm) [calculators](https://www.satsig.net/link-budget.htm) but quickly became confused by the details.

The first number given to me by [one of the calculators](https://www.satellite-calculations.com/Satellite/gtsys.htm) wasn't accepted by the server, but I noticed that it was in the range mentioned by Wikipedia as "Achievable G/T" (20 to 30ish). Since an integer was accepted as an answer to the first question, I decided to try a brute force search for the second answer. My initial search for an integer answer did not yield a result, so I tried adding one decimal place and quickly found the solution.

```python
#!/usr/bin/env python3

from pwn import *

wrong = b'Wrong'
result = wrong

# expecting a number of 20-30ish based on https://en.wikipedia.org/wiki/Antenna_gain-to-noise-temperature
i = 20.0

while result[:5] == wrong:
    r = remote('wild-wish.satellitesabove.me', 5022)
    r.recvuntil('Ticket please:\n')
    r.send('ticket{golf947225golf2:XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX}\n')
    r.recvuntil('Calculate and provide the recieve antenna gain in dBi: ')
    r.send('54\n')
    r.recvuntil('Calculate and provide the ground terminal G/T (dB/K): ')
    r.send(f'{i:.1f}\n')
    result = r.recv()
    r.close()
    print(f'\n{i:.1f}: {result}\n')
    i += 0.1
```

```
...
24.6: b'Wrong answer! You lose.\n\nWrong! Maybe next time\n'

[+] Opening connection to wild-wish.satellitesabove.me on port 5022: Done
[*] Closed connection to wild-wish.satellitesabove.me port 5022

24.7: b'Wrong answer! You lose.\n\nWrong! Maybe next time\n'

[+] Opening connection to wild-wish.satellitesabove.me on port 5022: Done
[*] Closed connection to wild-wish.satellitesabove.me port 5022

24.8: b"\nNicely done.  Let's keep going.\n\nDetermine the transmit power (in W) to achieve 10dB of Eb/No margin (above minimum for BER): "
```

### Transmit Power

After accepting the second answer, the server prompted us with a third question.

```
Calculate and provide the ground terminal G/T (dB/K): 24.8

Nicely done.  Let's keep going.

Determine the transmit power (in W) to achieve 10dB of Eb/No margin (above minimum for BER):
```

Computation of the necessary transmit power depends on much of the information we know about the system, but in particular requires an understanding of the Eb/No (E<sub>b</sub>/N<sub>0</sub>) specification. We didn't really have that understanding, but the Internet helped. [This document](http://www.eletrica.ufpr.br/evelio/TE111/Eb_N0.pdf) seemed like a good example of a similar computation, so I tried to go through it.

I had to make a few assumptions about the modulation, bandwidth, and temperatures, but I was able to work through the example. Initially it gave me an implausibly high transmit power, so I decided to go through the process again in repeatable Python:


```python
#!/usr/bin/env python3
#
# based on http://www.eletrica.ufpr.br/evelio/TE111/Eb_N0.pdf

import math

# example parameters from Eb_N0.pdf
#required_EbNo = 11.1 #dB
#data_rate = 2000000.0 #bps
#distance = 100 #m
#wavelength = 0.122 #m
#margin_dB = 30 #dB
#tx_antenna_gain_dBi = 0
#rx_antenna_gain_dBi = 0
#other_loss_dB = 0
#noise_figure_dB = 7

required_EbNo = 4.4 #dB
data_rate = 10000000.0 #bps
distance = 2831000 #m
wavelength = 0.025 #m
margin_dB = 10
tx_antenna_gain_dBi = 16.23
rx_antenna_gain_dBi = 54
other_loss_dB = 1 + 1.74 + 0.5 + 2.1 + 0.1 + 4.48

# computed from noise temp 522 K, reference temp 290 K
# https://www.allaboutcircuits.com/tools/noise-figure-noise-temperature-calculator/
noise_figure_dB = 4.4716

# assuming temperature in Eb_N0.pdf
effective_temperature = 290 #K

# assuming DQPSK as in Eb_N0.pdf
rx_bandwidth = data_rate / 2

boltzman = 1.38065e-23 #J/K

carrier_to_noise_dB = required_EbNo + 10*math.log(data_rate / rx_bandwidth, 10)
noise_power = boltzman * effective_temperature * rx_bandwidth #W
noise_power_dBW = 10*math.log(noise_power, 10)
rx_noise_power_dBW = noise_power_dBW + noise_figure_dB
carrier_power_dBW = carrier_to_noise_dB + rx_noise_power_dBW

path_loss_dB = 22 + 20*math.log(distance/wavelength, 10)

tx_power_dBW = carrier_power_dBW + path_loss_dB + margin_dB - tx_antenna_gain_dBi - rx_antenna_gain_dBi + other_loss_dB

tx_power_W = 10**(tx_power_dBW/10)
print(f'transmit power: {tx_power_dBW} dBW ({tx_power_W} W)')
```

Having remembered to include the antenna gains(!), this time I got a plausible result of 5.8 W, but this answer was not accepted by the server. Adjusting my assumptions a bit yielded results of 6 W or so, so I decided to try another brute force search in that vicinity.

```python
#!/usr/bin/env python3

from pwn import *

wrong = b'Sorry'
result = wrong

# expecting answer to be roughly 6 W, so brute forcing 4+ W
i = 4.0

while result[:5] == wrong:
    r = remote('wild-wish.satellitesabove.me', 5022)
    r.recvuntil('Ticket please:\n')
    r.send('ticket{golf947225golf2:XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX}\n')
    r.recvuntil('Calculate and provide the recieve antenna gain in dBi: ')
    r.send('54\n')
    r.recvuntil('Calculate and provide the ground terminal G/T (dB/K): ')
    r.send('24.8\n')
    r.recvuntil('(above minimum for BER): ')
    r.send(f'{i:.1f}\n')
    result = r.recv()
    r.close()
    print(f'\n{i:.1f}: {result}\n')
    i += 0.1
```

The search found the answer when it reached 9.5. (I later confirmed that it accepted answers as high as 9.8.)

```
Determine the transmit power (in W) to achieve 10dB of Eb/No margin (above minimum for BER): 9.5

Winner Winner Chicken Dinner

************** Global Parameters *****************
Frequency (Hz): 12100000000.0
Wavelength (m): 0.025
Data Rate (bps): 10000000.0
************* Transmit Parameters ****************
Transmit Power (W): 9.5
Transmit Power (dBW): 9.78
Transmit Line Losses (dB): -1
Transmit Half-power Beamwidth (deg): 26.30
Transmit Antenna Gain (dBi): 16.23
Transmit Pointing Error (deg): 10.00
Transmit Pointing Loss (dB): -1.74
Transmit Effective Isotropic Radiated Power (EIRP)(dBW): 25.01
*************** Path Parameters ******************
Path Length (km): 2831
Polarization Loss (dB): -0.5
Atmospheric Loss (dB): -2.1
Ionospheric Loss (dB): -0.1
************** Receive Parameters ****************
Receive Antenna Diameter (m): 5.3
Receive Antenna Efficiency: 0.55
Receive Antenna Gain (dBi): 54.00
Receive Half-power Beamwidth (deg): 0.33
Receive Pointing Error (deg): 0.2
Receive Pointing Loss (dB): -4.48
Receive System Noise Temperature (K): 522
Receive Line Loss (antenna to LNA) (dB): -2
******************* Results **********************
RSSI (dBW): -162.59
G/T (dB/K): 24.80
S/No (dB-HZ): 86.34
Eb/No (dB): 16.34
Receive Demodulator Implementation Loss (dB): -2
Required Eb/No for BER (dB): 4.4
Margin(dB): 9.94

flag{golf947225golf2:GHqGXSQn5W7hlPAxgBdEaWGYeOdNYkRTfM6yb4u1VVv1BG2qHGczGxSe7YxEAg5iQzVYWC9qSz2yYMrw969VOKY}
```

I think that this challenge may have been very difficult to solve using only computation or only brute force, but we had success by using a combination of both techniques with the computation helping to identify search ranges.
