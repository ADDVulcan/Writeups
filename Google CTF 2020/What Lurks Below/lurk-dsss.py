#!/usr/bin/env python3

import numpy
import scipy.signal
from bitstring import Bits

chip_sequence = 0x800cb441d49370b8386cba0e36c0949acef422d30c15f189768137cedee1ddab4267ce10054d878f788c415861e992f56a1b66324deaeb7fea56f6cf19b6162b

samples = numpy.fromfile('challenge.cfile', dtype=numpy.complex64)
chips = (numpy.array(Bits(bin(chip_sequence))) * 2) - 1
correlation = scipy.signal.correlate(samples, chips)

# The input signal is a single synthesized file, so we can depend on a fixed
# chip rate and phase.  Take the imaginary part of the correlation every 512
# samples (the chip sequence length).
data = Bits((correlation[511::512].imag > 0) * 1)

print(data)
output = open('lurk.png', 'wb')
output.write(data.tobytes())
output.close()
print('wrote output to lurk.png')
