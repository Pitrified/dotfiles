# complete -W "$(tmux ls | awk -F ':' '{print $1}')" "tmux attach -t"
