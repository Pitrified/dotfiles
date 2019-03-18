## TODO
256 color support, check for xterm-color and decide colorscheme accordingly

## Vim tips and tricks

* `g;` go to last place an edit was made
* `ab sht ShortHand` press `C-V`
* tabs gt gT
* marks and motion
* go to last modified text/last change
* in insert mode paste yanked text without leaving the insert mode `<C-r>0`
* If yanked text contains new line characters, `<C-r><C-p>0` will take care of fixing indentation issues.
* `<C-h>` " delete back one character (backspace)
* `<C-w>` " delete back one word
* `<C-u>` " delete back to start of line
* `<C-k>` " delete forward to end of line
* run normal mode across a range, visually select then `:normal somecommand`, accepts `.`
* `"ap` and `"add` to edit macros
* `autocmd BufWritePost $MYVIMRC source $MYVIMRC` to constantly reload vimrc while editing it
### Commands

[qua](https://github.com/VSCodeVim/Vim/blob/master/ROADMAP.md) ci sono comandi in lista

#### Left-right motions

| Command        | Description                                                                    |
| -------------- | ------------------------------------------------------------------------------ |
| g0             | to first character in screen line (differs from "0" when lines wrap)           |
| g^             | to first non-blank character in screen line (differs from "^" when lines wrap) |
| :1234: g\$     | to last character in screen line (differs from "\$" when lines wrap)           |
| gm             | to middle of the screen line                                                   |
| :1234: \|      | to column N (default: 1)                                                       |
| :1234: f{char} | to the Nth occurrence of {char} to the right                                   |
| :1234: F{char} | to the Nth occurrence of {char} to the left                                    |
| :1234: t{char} | till before the Nth occurrence of {char} to the right                          |
| :1234: T{char} | till before the Nth occurrence of {char} to the left                           |
| :1234: ;       | repeat the last "f", "F", "t", or "T" N times                                  |
| :1234: ,       | repeat the last "f", "F", "t", or "T" N times in opposite direction            |

#### Up-down motions

| Command   | Description                                                                               |
| --------- | ----------------------------------------------------------------------------------------- |
| :1234: G  | goto line N (default: last line), on the first non-blank character                        |
| :1234: gg | goto line N (default: first line), on the first non-blank character                       |
| :1234: %  | goto line N percentage down in the file; N must be given, otherwise it is the `%` command |
| :1234: gk | up N screen lines (differs from "k" when line wraps)                                      |
| :1234: gj | down N screen lines (differs from "j" when line wraps)                                    |

#### Scrolling
| Command       | Description                                    |
| ------------- | ---------------------------------------------- |
|CTRL-E | window N lines downwards (default: 1)          |
|CTRL-D | window N lines Downwards (default: 1/2 window) |
|CTRL-F | window N pages Forwards (downwards)            |
|CTRL-Y | window N lines upwards (default: 1)            |
|CTRL-U | window N lines Upwards (default: 1/2 window)   |
|CTRL-B | window N pages Backwards (upwards)             |
|z CR or zt    | redraw, current line at top of window          |
|z. or zz      | redraw, current line at center of window       |
|z- or zb      | redraw, current line at bottom of window       |

These only work when 'wrap' is off:

| Command   | Description |
| ------------------------- | --------- | 
zh | scroll screen N characters to the right       |
zl | scroll screen N characters to the left        |
zH | scroll screen half a screenwidth to the right |
zL | scroll screen half a screenwidth to the left  |

#### Marks and motions

| Command                                                     | Description                                        |
| ----------------------------------------------------------- | -------------------------------------------------- |
| m{a-zA-Z}                                                   | mark current position with mark {a-zA-Z}           |
| \`{a-z} | go to mark {a-z} within current file               |
| \`{A-Z} | go to mark {A-Z} in any file                       |
| \`{0-9} | go to the position where Vim was previously exited |
| \`\` | go to the position before the last jump                |
| \`" | go to the position when last editing this file         |
| \`[ | go to the start of the previously operated or put text |
| \`] | go to the end of the previously operated or put text   |
| \`< | go to the start of the (previous) Visual area          |
| \`> | go to the end of the (previous) Visual area            |
| \`. | go to the position of the last change in this file     |
| '.                                                          | go to the position of the last change in this file |
| :marks                                                      | print the active marks                             |
| :1234: CTRL-O                                               | go to Nth older position in jump list              |
| :1234: CTRL-I                                               | go to Nth newer position in jump list              |
| :ju[mps]                                                    | print the jump list                                |

#### Various motions

| Command             | Description                                                                                        |
| ------------------- | -------------------------------------------------------------------------------------------------- |
| :1234: H            | go to the Nth line in the window, on the first non-blank                                           |
| M                   | go to the middle line in the window, on the first non-blank                                        |
| :1234: L            | go to the Nth line from the bottom, on the first non-blank                                         |
#### Inserting text

| Command   | Description                                                   |
| --------- | ------------------------------------------------------------- |
| gI        | insert text in column 1 (N times)                             |
| gi        | insert at the end of the last change                          |


in Visual block mode:

| Command | Description|
| ------- | ------------------------------------------------------- |
| I       | insert the same text in front of all the selected lines |
| A       | append the same text after all the selected lines       |


#### Special keys in Insert mode

| Command                      | Description                                                        |
| ---------------------------- | ------------------------------------------------------------------ |
| CTRL-V {char}..              | insert character literally, or enter decimal byte value            |
| NL or CR or CTRL-M or CTRL-J | begin new line                                                     |
| CTRL-E                       | insert the character from below the cursor                         |
| CTRL-Y                       | insert the character from above the cursor                         |
| CTRL-A                       | insert previously inserted text                                    |
| CTRL-@                       | insert previously inserted text and stop Insert mode               |
| CTRL-R {0-9a-z%#:.-="}       | insert the contents of a register                                  |
| CTRL-N                       | insert next match of identifier before the cursor                  |
| CTRL-P                       | insert previous match of identifier before the cursor              |
| CTRL-X ...                   | complete the word before the cursor in various ways                |
| BS or CTRL-H                 | delete the character before the cursor                             |
| Del                          | delete the character under the cursor                              |
| CTRL-W                       | delete word before the cursor                                      |
| CTRL-U                       | delete all entered characters in the current line                  |
| CTRL-T                       | insert one shiftwidth of indent in front of the current line       |
| CTRL-D                       | delete one shiftwidth of indent in front of the current line       |
| 0 CTRL-D                     | delete all indent in the current line                              |
| ^ CTRL-D                     | delete all indent in the current line, restore indent in next line |


#### Copying and moving text

| Command          | Description                                            |
| ---------------- | ------------------------------------------------------ |
| "{char}          | use register {char} for the next delete, yank, or put  |
| "\* "+           | use register `*`,`+` to access system clipboard        |
| :reg             | show the contents of all registers                     |
| :reg {arg}       | show the contents of registers mentioned in {arg}      |
| ]p               | like p, but adjust indent to current line              |
| \[p              | like P, but adjust indent to current line              |
| gp               | like p, but leave cursor after the new text            |
| gP               | like P, but leave cursor after the new text            |

#### Visual mode

| Command | Description                                         |
| ------- | --------------------------------------------------- |
| o       | exchange cursor position with start of highlighting |
| gv      | start highlighting on previous visual area          |

#### Text objects (only in Visual mode or after an operator)

| Command    | Description                                                 |
| -----------| ----------------------------------------------------------- |
| a], a[     | select '[' ']' blocks                                       |
| i], i[     | select inner '[' ']' blocks                                 |
| ab, a(, a) | Select "a block" (from "[(" to "])")                        |
| ib, i), i( | Select "inner block" (from "[(" to "])")                    |
| a>, a<     | Select "a &lt;&gt; block"                                   |
| i>, i<     | Select "inner <> block"                                     |
| aB, a{, a} | Select "a Block" (from "[{" to "]}")                        |
| iB, i{, i} | Select "inner Block" (from "[{" to "]}")                    |
| at         | Select "a tag block" (from &lt;aaa&gt; to &lt;/aaa&gt;)     |
| it         | Select "inner tag block" (from &lt;aaa&gt; to &lt;/aaa&gt;) |

#### Repeating commands

| Command                           | Description                                                                                        |
| --------------------------------- | -------------------------------------------------------------------------------------------------- |
| q{a-z}                            | record typed characters into register {a-z}                                                        |
| q{A-Z}                            | record typed characters, appended to register {a-z}                                                |
| q                                 | stop recording                                                                                     |
| :1234: @{a-z}                     | execute the contents of register {a-z} (N times)                                                   |
| :1234: @@                         | repeat previous @{a-z} (N times)                                                                   |
| :@{a-z}                           | execute the contents of register {a-z} as an Ex command                                            |
| :@@                               | repeat previous :@{a-z}                                                                            |
| :[range]g[lobal]/{pattern}/[cmd]  | execute Ex command [cmd](default: ':p') on the lines within [range] where {pattern} matches        |
| :[range]g[lobal]!/{pattern}/[cmd] | execute Ex command [cmd](default: ':p') on the lines within [range] where {pattern} does NOT match |
| :so[urce] {file}                  | read Ex commands from {file}                                                                       |
| :so[urce]! {file}                 | read Vim commands from {file}                                                                      |

#### Multi-window commands

| Command           | Description                                                             |
| ----------------- | ----------------------------------------------------------------------- |
| :e[dit] {file}    | Edit {file}.                                                            |
| &lt;ctrl-w&gt; hl | Switching between windows.                                              |
| :new              | Create a new window horizontally and start editing an empty file in it. |
| :vne[w]           | Create a new window vertically and start editing an empty file in it.   |

#### Tabs

| Command                              | Description                                                                   |
| ------------------------------------ | ----------------------------------------------------------------------------- |
| :tabn[ext] :1234:                    | Go to next tab page or tab page {count}. The first tab page has number one.   |
| {count}gt | Same as above                                                                 |
| :tabp[revious] :1234:                | Go to the previous tab page. Wraps around from the first one to the last one. |
| :tabN[ext] :1234:                    | Same as above                                                                 |
| {count}&lt;C-PageUp&gt;, {count}gT   | Same as above                                                                 |
| :tabfir[st]                          | Go to the first tab page.                                                     |
| :tabl[ast]                           | Go to the last tab page.                                                      |
| :tabe[dit] {file}                    | Open a new tab page with an empty window, after the current tab page          |
| :[count]tabe[dit], :[count]tabnew    | Same as above                                                                 |
| :tabnew {file}                       | Open a new tab page with an empty window, after the current tab page          |
| :[count]tab {cmd}                    | Execute {cmd} and when it opens a new window open a new tab page instead.     |
| :tabc[lose][!] :1234:                | Close current tab page or close tab page {count}.                             |
| :tabo[nly][!]                        | Close all other tab pages.                                                    |
| :tabm[ove][n]                        | Move the current tab page to after tab page N.                                |
| :tabs                                | List the tab pages and the windows they contain.                              |


#### Fold commands

| Command                  | Description                                                                                                  |
| ------------------------ | ------------------------------------------------------------------------------------------------------------ |
| zf{motion} or {Visual}zf | Operator to create a fold.                                                                                   |
| zo                       | Open one fold under the cursor.When a count is given, that many folds deep will be opened.                   |
| zO                       | Open all folds under the cursor recursively.                                                                 |
| zc                       | Close one fold under the cursor. When a count is given, that many folds deep are closed.                     |
| zC                       | Close all folds under the cursor recursively.                                                                |
| za                       | When on a closed fold: open it. When on an open fold: close it and set 'foldenable'.                         |
| zA                       | When on a closed fold: open it recursively. When on an open fold: close it recursively and set 'foldenable'. |
| zm                       | Fold more: Subtract one from 'foldlevel'.                                                                    |
| zM                       | Close all folds: set 'foldlevel' to 0. 'foldenable' will be set.                                             |
| zr                       | Reduce folding: Add one to 'foldlevel'.                                                                      |
| zR                       | Open all folds. This sets 'foldlevel' to highest fold level.                                                 |
| zn                       | Fold none: reset 'foldenable'. All folds will be open.                                                       |
| zN                       | Fold normal: set 'foldenable'. All folds will be as they were before.                                        |
| [z                       | Move to the start of the current open fold.                                                                  |
| ]z                       | Move to the end of the current open fold.                                                                    |
| zj                       | Move downwards to the start of the next fold.                                                                |
| zk                       | Move upwards to the end of the previous fold.                                                                |

#### Text object motions

| Command    | Description                                            |
| ---------- | ------------------------------------------------------ |
| :1234: )   | N sentences forward                                    |
| :1234: (   | N sentences backward                                   |
| :1234: }   | N paragraphs forward                                   |
| :1234: {   | N paragraphs backward                                  |
| :1234: ]]  | N sections forward, at start of section                |
| :1234: \[\[  | N sections backward, at start of section               |
| :1234: ]\[  | N sections forward, at end of section                  |
| :1234: \[]  | N sections backward, at end of section                 |
| :1234: \[(  | N times back to unclosed '('                           |
| :1234: \[{  | N times back to unclosed '{'                           |
| :1234: ])  | N times forward to unclosed ')'                        |
| :1234: ]}  | N times forward to unclosed '}'                        |

```vimscript
" Easily create a new tab.
noremap <Leader>tN :tabnew<CR>
" Easily close a tab.
noremap <Leader>tc :tabclose<CR>
" Easily move a tab.
noremap <Leader>tm :tabmove<CR>
" Easily go to next tab.
noremap <Leader>tn :tabnext<CR>
" Easily go to previous tab.
noremap <Leader>tp :tabprevious<CR>
```

