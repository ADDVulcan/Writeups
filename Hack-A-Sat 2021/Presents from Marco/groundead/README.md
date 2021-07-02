# Groundead

### Presents from Marco

_80 points, 52 Solves_

Active ADDVulcan players:
<li> recingSnake
<li> alvarop
<li> WillC
<li> worm
<li> supersat
<li> DoughSk8er
<li> miek
<li> skipcod3

## Challenge Description

The server executable for the challenge was provided as a download link, this was saved as `challenge`.

## Ticket

Correctly exploiting the server would present a flag in the form:

```
flag{yankee661660oscar2:___a bunch of unguessable stuff___}
```

Don't share your ticket with other teams.

## Connecting

Connect to the challenge on:

```
unfair-cookie.satellitesabove.me:5001
```

Using netcat, you might run:

```
nc unfair-cookie.satellitesabove.me 5001
```

## Solving

Your team's flag for this challenge will look something like:
flag{yankee661660oscar2:___a bunch of unguessable stuff___}

## Write up by racingSnake

### Initial Analysis

The downloaded file was examined:

    $ file challenge
    challenge: ELF 64-bit LSB pie executable, x86-64, version 1 (SYSV), dynamically linked, interpreter /lib64/ld-linux-x86-64.so.2, BuildID[sha1]=f2a424febdfd563d6730087e3a439da905bc9a7f, for GNU/Linux 3.2.0, not stripped

This shows that it is a Linux 64 bit executable with symbols still present.

The file was set as executable and run:

    $ chmod 755 ./challenge

    $ ./challenge

         .-.                                                         -----------
       (;;;)                                                        /            '
        |_|                                  ,-------,-|           |C>      )    |
          ' _.--l--._                       '      ,','|          /    || ,'     |
         .      |     `.                   '-----,','  |         (,    ||        ,
       .` `.    |    .` `.                 |     ||    |           -- ||||      |
     .`     `   |  .`     `.               |     ||    |           |||||||     _|
    ' __      `.|.`      __ `              |     ||    |______      `````|____/ |
    |   ''--._  V  _.--''   |              |     ||    |     ,|         _/_____/ |
    |        _ ( ) _        |              |     ||  ,'    ,' |        /          |
    | __..--'   ^   '--..__ | _           '|     ||,'    ,'   |       |            |
    '         .`|`.         '-.)        ,  |_____|'    ,'     |       /           | |
     `.     .`  |  `.     .`           , _____________,'      ,',_____|      |    | |
       `. .`    |    `. .`             |             |     ,','      |      |    | |
         `._    |    _.`|       -------|             |   ,','    ____|_____/    /  |
             `--l--`  | |     ;        |             | ,','  /  |              /   |
                      | |    ;         |_____________|','    |   -------------/   |
                   ---| |-------.                      |===========,'
                 /    ..       / |
                --------------   |
               |              | /
               |              |/
                --------------


    Ground Station ONLINE

    >

We are prompted for a Ground Station Command, so we enter some text:

    >hello

    That sequence of hex characters did not work. Try again.

Hexadecimal input is expected, so we try that:

    >00 00 00 00 00 00 00 00

    That sequence of hex characters did not work. Try again.

Clearly the input is being validated, so we reverse engineer the file.

### Reverse Engineering

Ghidra was used to analyse the `challenge` file in more detail. We see two functions of potential interest `getSatellitePacketBytes` and `processSatellitePacketBytes`. Within those functions we see calls being made to C++ library functions including "basic_string", "basic_stringstream", and "strtoul".

#### getSatellitePacketBytes

Input is read and discarded if it is less than two characters, this discards any lines if [Return] is pressed. Then the input is parsed as a sequence of hexadecimal octets. After three octet pairs a value of '7' is expected. If this does not match then a message (`That sequence of hex characters did not work. Try again.`) is output. If the '7' is found then the remaining input is parsed as hexadecimal octets.

We try that in our sample:
    0 0 0 0 0 0 7

    That sequence of hex characters did not work. Try again.

This is the same message as before, except that there is a delay before it is output suggesting that some progress was made.

#### processSatellitePacketBytes

Input is read from an input queue (assumed to be from the function above) until it is empty. Further down we see that there is a switch statement. If a byte value (assumed to be a `mode` indicator) of '8' is found then 'Emergency Mode is triggered' and the flag is revealed. The program flow only gets to the switch statement if some form of validity check is passed; we see this check at the end of the function. Prior to this validity check we see that the some bit fields are extracted from the data; these match the Space Packet Protocol: https://public.ccsds.org/Pubs/133x0b2e1.pdf, giving us some hint of the data structure being processed.

It is noted that this function has nested while loops allowing multiple packets to be processed. This seemed to contradict the queue being read until empty early on. However, timing delays between the two functions allow further input from `getSatellitePacketBytes` to be processed as additional messages.

More detailed analysis allows us to match the first three octet pairs to the Packet Primary Header. The next byte is used as the aforementioned `mode` octet which in the specification would be the Auxillary Data Field of the Secondary Header. Unfortunately this coincides with the 7th octet of the input, which as we saw in `getSatellitePacketBytes` must be '7'. Indeed, creating an apparently valid pair of packets gives:

    >8 0 0 1 0 1 7
    8 0 0 1 0 1 7

    Packet Version Number: 00000000
    Packet Type: 00000000
    Secondary Header Flag: 00000001
    Application Process Identifier: 00000000
    Sequence Flags: 00000000
    Packet Sequence Count or Packet Name: 00000001
    Packet Data Length: 00000002


    That sequence of hex characters did not work. Try again.

The above are debug messages output by this function. We also see the above message is output if this function does not successfully validate the packet header, or after all supplied packets have been processed.

### Exploit Strategy

Given that `getSatellitePacketBytes` forces the 7th octet to be '7' and that this is the 'mode' option that we need to be '8' we need to find a way of overcoming that. It is noted that the PacketDataLength is included in the Packet Primary Header so we investigate whether we could send two concatenated packets in one line of input with only the first one having the 'mode 7' enforced.

We know that we can take advantage of the timing to send multiple lines to the queue, how can we spoof the contents to trigger processing of an additional packet that bypasses the `mode` being forced to 7?

Further analysis of the code reveals:

1. Only the first 32 bytes of the input buffer are cleared to zeros for each input line by `getSatellitePacketBytes`.
2. The payload is scanned for 5 occurrences of the byte sequence "1acffc1d" by `processSatellitePacketBytes`.

We determined that a pair of messages could be sent, with the first message satisfying the expected payload data and the second one declaring a shorter packet length than the supplied data such that the remaining octets would be treated as a further packet.

### Final Exploit

Some tweaks were made to the exploit candidate to ensure that all of the checks on payload length, payload data contents and mode were satisfied. The final exploit input is as follows:

    >8 0 0 1 0 1a 7 1a cf fc 1d 1a cf fc 1d 1a cf fc 1d 1a cf fc 1d 1a cf fc 1d 0 0 0 0 0 8
    8 0 0 1 0 1a 7 1a cf fc 1d 1a cf fc 1d 1a cf fc 1d 1a cf fc 1d 1a cf fc 8 0 0 1 0 0 8


    Packet Version Number: 00000000
    Packet Type: 00000000
    Secondary Header Flag: 00000001
    Application Process Identifier: 00000000
    Sequence Flags: 00000000
    Packet Sequence Count or Packet Name: 00000001
    Packet Data Length: 0000001b


    Handling Test Telemetry


    Packet Version Number: 00000000
    Packet Type: 00000000
    Secondary Header Flag: 00000001
    Application Process Identifier: 00000000
    Sequence Flags: 00000000
    Packet Sequence Count or Packet Name: 00000001
    Packet Data Length: 00000001


    EMERGENCY_MODE: THE SPACECRAFT IS IN EMERGENCY_MODE
    You made it!
    Here's your flag:

Thank you for providing this challenge. It was great to practice our skills reverse engineering C++ code.
