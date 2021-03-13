# The quest for clickable links in terminal that open another terminal already cd'd in the right folder just as I want

## Process

### Open gnome-terminal in the right working directory

Not a problem:

```bash
/bin/gnome-terminal --working-directory /home/pmn/dotfiles/
```

A terminal pops up right where I want.

### Clickable links (hyperlinks) in the terminal

No worries mate:

```bash
echo -e '\e]8;;file:///home/pmn/dotfiles\aThis is a link\e]8;;\a'
```

By `Ctrl+Click`-ing on the link the file explorer gets opened in the right folder.

### Create a new schema for an app

In `~/.local/share/applications/mimeapps.list` add:

(Note that the use of this file is deprecated, `~/.config/mimeapps.list` should be used)

```
[Default Applications]
x-scheme-handler/mygnometerm=mygnometerm.desktop
```

In `~/.local/share/applications/mygnometerm.desktop` add:

```
[Desktop Entry]
Type=Application
Terminal=false
Name=My Gnome Terminal
Exec=/bin/gnome-terminal --working-directory %f
MimeType=x-scheme-handler/mygnometerm
```

Create the folder for the mime database:

```bash
mkdir -p ~/.local/share/mime/packages
```

Update the mime database:
```bash
update-mime-database ~/.local/share/mime
```

This **does** work: if I right-click on a folder in the file explorer and select `My Gnome Terminal` as the app to use, a terminal is opened already in the right folder.

## Research

### Open gnome in different folder

* https://stackoverflow.com/a/1098096/2237151

### URI for terminal

* https://github.com/neovim/neovim/issues/3278

### Open custom uri scheme

* https://stackoverflow.com/questions/42119708/call-custom-uri-scheme-eg-lightroom-myplugin-from-shell-terminal-app

### App uri

* https://unix.stackexchange.com/questions/38563/what-are-the-uris-starting-with-file-or-application
* https://unix.stackexchange.com/a/170368

### Uri use

* https://www.blackhat.com/presentations/bh-dc-08/McFeters-Rios-Carter/Presentation/bh-dc-08-mcfeters-rios-carter.pdf

### Desktop entry specification

* https://specifications.freedesktop.org/desktop-entry-spec/desktop-entry-spec-latest.html
* https://specifications.freedesktop.org/desktop-entry-spec/desktop-entry-spec-latest.html#exec-variables
