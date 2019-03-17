### Quick guide
Longer explanation [here](https://github.com/remiprev/teamocil)

#### Usage

```bash
$ teamocil [options] [layout-name]
```

* `--list`: Lists all available layouts in `~/.teamocil`
* `--here`: Uses the current window as the layout’s first window
* `--edit`: Opens the layout file with `$EDITOR` instead of executing it
* `--show`: Shows the layout content instead of executing it
* `--layout`: Takes a custom file path to a YAML layout file instead of `[layout-name]`

#### Custom window layout
* even-horizontal
* even-vertical
* main-horizontal
* main-vertical
* tiled

#### Simple three pane window

```yaml
windows:
  - name: sample-three-panes
    root: ~/Code/sample/www
    layout: main-vertical
    panes:
      - vim
      - commands:
        - git pull
        - git status
      - rails server
        focus: true
```

```
.------------------.------------------.
| (0)              | (1)              |
|                  |                  |
|                  |                  |
|                  |                  |
|                  |------------------|
|                  | (2) <focus here  |
|                  |                  |
|                  |                  |
|                  |                  |
'------------------'------------------'
```
