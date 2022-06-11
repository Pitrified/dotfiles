gitid () {
    if [[ $# -eq 2 ]]; then
        # magic to check for a substring in a string
        # this is neat because usually there are no @ in the username
        # so if you put them swapped this will notice
        if [[ "$1" == *"@"* ]]; then
            git config user.email "$1"
            git config user.name "$2"
            git config credential.https://github.com.username "$2"
        else
            echo "There is no @ in the email, did you type it correctly?"
            echo "Usage: gitid email username"
        fi
    else
        echo "Usage: gitid email username"
    fi
}


alias gc="git commit"
alias gca="git commit -a"
alias gs="git status"
