# HAS 4 Quals Hyde Street
Hyde Street was a fun little JS/TS challenge where the goal was to get a given value returned after a bunch of mathematical operations luckily these only consisted of simple math operations (division, subtraction, addition in this case). The program that was given to us was written in C which makes it a little bit harder but not by much, here's an example
```C
#include <stdint.h>
#include <stdbool.h>

bool quick_maths(uint32_t run) {
run = run / 13;
run = run - 236;
run = run / 6;
run = run / 10;
run = run / 9;
run = run + 13651;
run = run - 214;
run = run - 45;
run = run / 7;
run = run + 1491;
return (run == 7513);
}
```

from the above code example we can see our target number we want to get is 7513, This shouldn't be hard to get because it's only addition subtraction and division.

## How to get what number we want to give quick_maths
first we want to take the number we want(in this case 75130 and plug it in and apply the inverse operation
```
run = 7513-1491 (6022)
run = 6022 * 7 (42154)
run = 42154 + 45 (42199)
run = 42199 + 214 (42413)
run = 42413 - 13651 (28762)
run = 28762 * 9 (258858)
run = 258858 * 10 (2588580)
run = 2588580 * 6 (15531480)
run = 15531480 + 236 (15531716)
finally, run = 15531716 * 13 (201912308)
```
So here we want to initate quick_maths with run being 201912308, if we ever want to double check our answer we can repeat the same steps, but starting from the top and not inversing the operation 

let's put this into some code now!

## Putting this into code

The first thing we want to do is start parsing the file given to us, since this challenge uses Deno we can read the file with Deno.readTextFile() and make a hacky C parser to tell both if we are in the quick_maths function, and what operations are being ran.

put together we get something like this
```js
//reading data
const data = await Deno.readTextFile("/chall/challs/generated.c");

// parsing into lines
const lines = data.split("\n");
let in_quick_maths = false;
let ops = []
let final;
//iterating through lines
for (let line of lines) {
    line = line.trim();
    //finding if we are in the function
    if (line == "bool quick_maths(uint32_t run) {") {
        in_quick_maths = true;
    } else if (line == "}") {
        in_quick_maths = false;
    } else if (in_quick_maths) {
    //getting the value to return to true
        if (line.startsWith("return")) {
            final = parseInt(line.match("\\d+")[0])
            break
        } else {
        //getting the operations
            const slice = line.replace(";", "").split(" ").slice(3, 5);
            const kind = slice[0]
            const value = parseInt(slice[1])
            ops.push([kind, value])
        }
    }
}
```
after this we have pretty much everything we need! we just need to implement the inverse operations we can do this like so

```js

const inverse_ops = {
    '+': '-',
    '-': '+',
    '/': '*',
}

let initial = final;

//reversing the operations
for (let op of ops.reverse()) {
    const kind = op[0]
    const value = op[1]
    if (kind == '+') {
        initial -= value
    } else if (kind == '-') {
        initial += value
    } else if (kind == '/') {
        initial *= value
    }
}
//send initial value to return true
console.log(initial)
```
after that we are all done! here is everything put together

```js
//reading data
const data = await Deno.readTextFile("/chall/challs/generated.c");

// parsing into lines
const lines = data.split("\n");
let in_quick_maths = false;
let ops = []
let final;
//iterating through lines
for (let line of lines) {
    line = line.trim();
    //finding if we are in the function
    if (line == "bool quick_maths(uint32_t run) {") {
        in_quick_maths = true;
    } else if (line == "}") {
        in_quick_maths = false;
    } else if (in_quick_maths) {
    //getting the value to return to true
        if (line.startsWith("return")) {
            final = parseInt(line.match("\\d+")[0])
            break
        } else {
        //getting the operations
            const slice = line.replace(";", "").split(" ").slice(3, 5);
            const kind = slice[0]
            const value = parseInt(slice[1])
            ops.push([kind, value])
        }
    }
}

const inverse_ops = {
    '+': '-',
    '-': '+',
    '/': '*',
}

let initial = final;

//reversing the operations
for (let op of ops.reverse()) {
    const kind = op[0]
    const value = op[1]
    if (kind == '+') {
        initial -= value
    } else if (kind == '-') {
        initial += value
    } else if (kind == '/') {
        initial *= value
    }
}
//send initial value to return true
console.log(initial)
```

