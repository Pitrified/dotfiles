# override hist sizes
HISTSIZE=10000
HISTFILESIZE=20000

# https://www.shellhacks.com/tune-command-line-history-bash/
# use history -a to append immediately a command, in case of crash
PROMPT_COMMAND='history -a'

mkcdir ()
{
    mkdir -p -- "$1" && cd -P -- "$1"
}


# open file explorer in the folder you are in (Explorer HEre)
alias ehe="gio open ."

# grep for TODOs and MAYBEs
alias greptodo="grep -r -I 'TODO\|MAYBE'"

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
