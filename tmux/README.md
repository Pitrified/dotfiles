### Quick guide
Longer explanation [here](https://nickjanetakis.com/blog/who-else-wants-to-boost-their-productivity-with-tmux)

#### Sessions
* `tmux new -s sessionname` creates a new session
* `tmux attach -t sessionname` reopens an existing session
* `tmux ls` lists open sessions
* `<prefix> d` to detatch from a session
* `tmux kill-session -t sessionname` deletes an existing session

#### Windows
Inside each session there can be 1 or more windows
* `<prefix> c` to create new window
* `<prefix> [np0-9]` to select one
* `<prefix> w` to list and select one
* `<prefix> f` to find one by name
* `<prefix> ,` to rename
* `exit` or `C-d` to close. Might be a good idea to unmap `C-d`

#### Panes
Split a window into independent terminals.
* `<prefix> o` to cycle through them
* `<prefix> q` to jump to numbered label that appear
* `<prefix> z` to zoom in and out of a pane
* `<prefix> q` to close

#### Misc
* `<prefix> [` to enter scroll mode with arrow or page keys 
* `Ctrl-Shift-c` to copy, hold down Shift while selecting with the mouse
* `Ctrl-Shift-v` to paste
* `<prefix> t` to show a clock
* `<prefix> ?` to show the help
