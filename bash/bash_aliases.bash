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

# alias le="exa -lh --git"
alias le="exa --long --git --all"
# alias lt="exa --long --git --all --tree --level=2"

# open file explorer in the folder you are in
alias nahe="nautilus --browser `pwd`"

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
