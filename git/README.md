# Git checker

## RATIONALE 

* Every repo in repos folders must be checked.
* Only add in the single list repos in different places.

## IDEAS / TODO 

* Use default parameters for bold/background color.
* Move echo_color in `~/dotfiles/bash/echo_color.bash`.
    This might create problems regarding the source order:
    if some topic gets sourced before bash and tries to use `echo_color`,
    the function will not be available.
* Use # to skip lines in the list file.
* Add local file to check.
* A verbose flag that prints git status output.

## INFO and RESEARCH

### Colors and a very nice structure

* https://gist.github.com/mzabriskie/6631607

### Check for git in different folder

* https://stackoverflow.com/a/24352829/2237151

### Check for correct parameters

* https://tldp.org/LDP/abs/html/complexfunct.html

### Iterate over array

```bash
for i in "${my_array[@]}"; do echo "$i"; done
```

### Load content of a file into an array

```bash
filecontent=( `cat "logfile" `)
for t in "${filecontent[@]}"; do echo "$t"; done
```

### Define hash tables in bash

* https://www.artificialworlds.net/blog/2012/10/17/bash-associative-array-examples/
* https://stackoverflow.com/questions/1494178/how-to-define-hash-tables-in-bash

### Check if file exists

* https://linuxize.com/post/bash-check-if-file-exists/

### Command options

* https://stackoverflow.com/a/29754866/2237151
* https://medium.com/@Drew_Stokes/bash-argument-parsing-54f3b81a6a8f

### Pull with password

* https://serverfault.com/a/912788

### Color in git output

* https://stackoverflow.com/a/27430972/2237151

### Open hyperlink from terminal

* https://unix.stackexchange.com/a/437585
* https://gist.github.com/egmontkob/eb114294efbcd5adb1944c9f3cb5feda
* https://purpleidea.com/blog/2018/06/29/hyperlinks-in-gnome-terminal/
