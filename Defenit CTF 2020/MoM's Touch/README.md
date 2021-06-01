# Mom's Touch

## Challenge Description

The challenge provided a Linux executable that takes text input and tells you whether or not the input is the flag.

## Determining Flag Length

First the executable told me to check the length, so I wrote a `bash` one-liner to determine the flag length: 

```bash
flag=''; while echo ${flag} | ./momsTouch | grep -q 'Check the legnth'; do flag=${flag}A; done; echo ${flag}
```

With the correct length, the error message changed to "Try Again".

## Timing Attack FTW

I knew the first few characters of the flag, so I tried input with both correct and incorrect initial characters and found that `perf` revealed vulnerability to a timing attack. Then I executed the attack with another one-liner to reveal the flag one character at a time: 

```bash
flag=$(printf '_%.0s' {1..73}); for i in {1..73}; do flag=$(for j in {33..126}; do f=${flag/_/$(printf "%x" $j | xxd -p -r)}; echo -n $f; echo -n $f | perf stat -B -e instructions ./momsTouch 2>&1 | grep ins; done | sort -V -k2 | tail -1 | awk '{print $1}'); echo $flag; done
```

## Notes

There are some other great [writeups](https://ctftime.org/task/11845) of this challenge, but they all used static analysis techniques. I decided to write this up because I took a very different approach. Sometimes you can reverse engineer things just by observing their behavior!

This writeup was originally posted [on Twitter](https://twitter.com/michaelossmann/status/1270962888035819520).
