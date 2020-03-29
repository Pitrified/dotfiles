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
* `<prefix> t` to show a clock
* `<prefix> ?` to show the help

#### Copy
Info:
* https://www.rushiagr.com/blog/2016/06/16/everything-you-need-to-know-about-tmux-copy-pasting-ubuntu/
* https://www.freecodecamp.org/news/tmux-in-practice-integration-with-system-clipboard-bcd72c62ff7b/
* https://github.com/tmux-plugins/tmux-yank

Internal tmux buffer, works in vanilla tmux
* `<prefix> [` or mouse wheel scroll to enter scroll mode with arrow or page keys 
* `Ctrl-SPACE` to start copying
* `Alt-w` or `Ctrl-w` to copy
* `<prefix> ]` to paste

Goes to system clipboard with tmux-yank installed
* hold down Shift while selecting with the mouse (even not in scroll mode)
* `Ctrl-Shift-c` to copy
* `Ctrl-Shift-v` to paste

With these vim keybind and tmux yank
```
setw -g mode-keys vi
bind P paste-buffer
bind-key -T copy-mode-vi v send-keys -X begin-selection
bind-key -T copy-mode-vi y send-keys -X copy-selection
bind-key -T copy-mode-vi r send-keys -X rectangle-toggle
```
* `<prefix> [` or mouse wheel scroll to enter scroll mode with arrow or page keys 
* `v` to enter visual selection, `V` line selection
* `r` to toggle rectangle selection
* `ENTER` to copy to tmux clipboard
* `y` to copy to system clipboard

