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
