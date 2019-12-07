mkcdir ()
{
    mkdir -p -- "$1" &&
    cd -P -- "$1"
}

lt ()
{
    if [[ $# -eq 0 ]]
    then
        exa --long --git --all --tree --level=2
    fi

    if [[ $# -eq 1 ]]
    then
        exa --long --git --all --tree --level="$1"
    fi

    if [[ $# -eq 2 ]]
    then
        exa --long --git --all --tree --level="$1" --ignore-glob=.git"|$2"
    fi

    if [[ $# -eq 3 ]]
    then
        exa --long --git --all --tree --level="$1" --ignore-glob=.git"|$2" "$3"
    fi
}

gitid () {
    git config user.email "$1"
    git config user.name "$2"
}

# alias le="exa -lh --git"
alias le="exa --long --git --all"
# alias lt="exa --long --git --all --tree --level=2"

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

# Stash your environment variables in ~/.localrc. This means they'll stay out
# of your main dotfiles repository (which may be public, like this one), but
# you'll have access to them in your scripts.
# if [[ -a ~/.localrc ]]
# then
#   source ~/.localrc
# fi
# config_files=($ZSH/**/*.zsh)
# # load everything but the path and completion files
# for file in ${${config_files:#*/path.zsh}:#*/completion.zsh}
# do
#   source $file
# done

# put branch name in front of PS1
# PS1="\$(__git_ps1 '(%s)')"$PS1

# put branch name on end of PS1
# this is the length of a string
# echo ${#PS1}
# remove the last characters
PS1=${PS1:0:${#PS1}-3}
# add info on branches
PS1=$PS1" \$(__git_ps1 '(%s)')\$ "
