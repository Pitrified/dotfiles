git_remote_swap () {
    # toggle the 'origin' remote transport between https and ssh (github only)
    old=$(git remote get-url origin 2>/dev/null) || {
        echo "Not a git repo or no 'origin' remote."
        return 1
    }

    if [[ "$old" == https://github.com/* ]]; then
        new=$(echo "$old" | sed -E 's#^https://github.com/#git@github.com:#')
    elif [[ "$old" == git@github.com:* ]]; then
        new=$(echo "$old" | sed -E 's#^git@github.com:#https://github.com/#')
    else
        echo "Unrecognized github remote, leaving it alone:"
        echo "  $old"
        return 1
    fi

    echo "  old: $old"
    echo "  new: $new"
    git remote set-url origin "$new"
    git remote -v
}
