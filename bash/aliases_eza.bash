# super fast useful info with eza
alias le="eza --long --git --all"

# use eza --tree
lt ()
{
    if [[ $# -eq 0 ]]
    then
        eza --long --git --all --tree --level=2 --ignore-glob='.git|__pycache__|.mypy_cache'
    fi

    # here we do not ignore glob: `lt 3` can be used to show all the tree
    if [[ $# -eq 1 ]]
    then
        eza --long --git --all --tree --level="$1"
    fi

    # if you do want to ignore glob with defaults, call `lt 3 ""` to fall in this branch
    if [[ $# -eq 2 ]]
    then
        eza --long --git --all --tree --level="$1" --ignore-glob='.git|__pycache__|.mypy_cache'"|$2"
    fi

    if [[ $# -eq 3 ]]
    then
        eza --long --git --all --tree --level="$1" --ignore-glob='.git|__pycache__|.mypy_cache'"|$2" "$3"
    fi
}

# use eza --tree without git info
ltn ()
{
    if [[ $# -eq 0 ]]
    then
        eza --long --all --tree --level=2 --ignore-glob='.git|__pycache__|.mypy_cache'
    fi

    # here we do not ignore glob: `lt 3` can be used to show all the tree
    if [[ $# -eq 1 ]]
    then
        eza --long --all --tree --level="$1"
    fi

    # if you do want to ignore glob with defaults, call `lt 3 ""` to fall in this branch
    if [[ $# -eq 2 ]]
    then
        eza --long --all --tree --level="$1" --ignore-glob='.git|__pycache__|.mypy_cache'"|$2"
    fi

    if [[ $# -eq 3 ]]
    then
        eza --long --all --tree --level="$1" --ignore-glob='.git|__pycache__|.mypy_cache'"|$2" "$3"
    fi
}
