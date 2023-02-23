# override hist sizes
HISTSIZE=100000
HISTFILESIZE=200000

# https://www.shellhacks.com/tune-command-line-history-bash/
# use history -a to append immediately a command, in case of crash
PROMPT_COMMAND='history -a'

mkcdir ()
{
    mkdir -p -- "$1" && cd -P -- "$1"
}


# open file explorer in the folder you are in (Explorer HEre)
alias ehe="gio open ."

alias wehe='explorer.exe `wslpath -w "$PWD"`'

# grep for TODOs and MAYBEs and IDEAs and QUESTIONs
alias greptodo="grep -r -I --exclude-dir=.nox 'TODO\|MAYBE\|IDEA\|QUESTION'"

# scale the text for HiDPI display
# https://askubuntu.com/questions/1029436/enable-fractional-scaling-for-ubuntu-18-04
settextzoom() {
    gsettings set org.gnome.desktop.interface text-scaling-factor "$@";
}
# proper scaling might work like this
# https://www.linuxuprising.com/2019/04/how-to-enable-hidpi-fractional-scaling.html
# http://ubuntuhandbook.org/index.php/2019/10/how-to-enable-fractional-scaling-in-ubuntu-19-10-eoan/


# put branch name in front of PS1
# PS1="\$(__git_ps1 '(%s)')"$PS1

# here might be a better way TODO
# https://stackoverflow.com/a/3058390/2237151
# https://github.com/git/git/blob/master/contrib/completion/git-prompt.sh

# poetry virtualenvs
# echo '(env-name-A5Y8HpgU-py3.88) $ prompt fake-ABC098ab-py3.0' |
# perl -pe 's/^(.*?)-[A-Za-z0-9]{8}-(py[0-9].[0-9]{1,2})/\1-\2/'
#             | |     |               |                   |> print the useful parts
#             | |     |               |> py3.12
#             | |     |> 8 alphanumeric chars
#             | |> the env name, with greedy quantifier
#             |> start of string, don't match this in the middle of the prompt
# prints (env-name-py3.88) $ prompt fake-ABC098ab-py3.0  
# echo before
# echo $PS1
# PS1=`echo $PS1 | perl -pe 's/^(.*?)-[A-Za-z0-9]{8}-(py[0-9].[0-9]{1,2})/\1-\2/'`
# echo after
# echo $PS1
# the problem is that poetry shell is called after the new shell is opened
# the command does work if called again from terminal

# put branch name on end of PS1
# this is the length of a string
# echo ${#PS1}
# remove the last characters
PS1=${PS1:0:${#PS1}-3}
# add info on branches
PS1=$PS1" \$(__git_ps1 '(%s)')\$ "

# diff files in separate folders
# $1 is the folder of the different file, with trailing slash
# $2 is the name of the file
gd() {
    gvimdiff "$1""$2" "$2"
}

# Ctrl+r history commands often do not have the leading ~/
# press home to get to the start of line and add an h :D
hcd() {
    cd $HOME/$1
}

alias c="code ."
alias p8="ping 8.8.8.8 -c 4"

