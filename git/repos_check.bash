echo_color() {

    # prints a colored string
    # $1 is the string
    # $2 is the color name

    # color codes
    declare -A cc
    cc=(
        [black]=30
        [red]=31
        [green]=32
        [yellow]=33
        [blue]=34
        [magenta]=35
        [cyan]=36
        [white]=37
        [reset]=0
    )
    # access the element like this
    # echo ${cc[$2]}

    echo -en "\033[0;${cc[$2]}m"
    echo "$1"
    echo -en "\033[0;${cc[reset]}m"

}

repo_status() {
    # echo_color "Found repo at $1" magenta

    mod=0

    git_status=`git --git-dir=$1/.git --work-tree=$1 status`
    # echo "$git_status"
    # echo `echo "$git_status" | grep modified -c`

    # # Check for modified files
    if [ $(echo "$git_status" | grep 'modified' -c) -ne 0 ]
    then
        mod=1
        echo_color "    Modified files!" red
    fi

    # # Check for untracked files
    if [ $(echo "$git_status" | grep 'Untracked' -c) -ne 0 ]
    then
        mod=1
        echo_color "    Untracked files!" red
    fi

    # # Check for unpushed changes
    if [ $(echo "$git_status" | grep 'Your branch is ahead' -c) -ne 0 ]
    then
        mod=1
        echo_color "    Unpushed commit!" red
    fi

    # If nothing to commit, pull remote
    if [ $mod -eq 0 ]; then
        echo_color "    Nothing to commit" green

        # pull the repo
        # magic to deal with the password is setup in GIT_PASSWORD and GIT_ASKPASS
        if [ $do_pull -eq 1 ]; then

            git_pull=`GIT_ASKPASS=$GIT_ASKPASS GIT_PASSWORD=$GIT_PASSWORD git --git-dir=$1/.git --work-tree=$1 -c color.ui=always pull`
            if [ $(echo "$git_pull" | grep 'Already up to date.' -c) -ne 0 ]
            then
                echo_color "    No files pulled" green
            else
                echo "$git_pull"
            fi

        fi
    fi

}

repo_file_folder_check () {
    # the file contains a list of folders full of repos

    echo
    echo_color "Reading input file $1" cyan

    if [ ! -f "$1" ]; then
        echo_color "$1 does not exist." yellow
        return 1
    fi

    while read -r repo_folder_name
    do
        repo_folder_path=$HOME/$repo_folder_name/*

        echo
        echo_color "Repo folder path '$repo_folder_path'" magenta

        # Loop all sub-directories
        for repo_path in $repo_folder_path
        do

            # Only interested in directories
            [ -d "${repo_path}" ] || continue

            # Check if this subfolder is a repo
            if [ -d "$repo_path/.git" ]
            then
                # echo
                echo_color "Checking $repo_path" blue
                repo_status $repo_path
            fi
        done
    done < $1

}

repo_file_single_check() {
    # the file contains a list of repos

    echo
    echo_color "Reading input file $1" cyan
    echo

    if [ ! -f "$1" ]; then
        echo_color "$1 does not exist." yellow
        return 1
    fi

    while read -r repo_name
    do
        repo_path=$HOME/$repo_name

        # echo
        echo_color "Checking $repo_path" blue

        if [ -d "$repo_path/.git" ]
        then
            repo_status $repo_path
        else
            # the file contains explicit path to repos
            # if those are missing notify
			echo_color "Repo $repo_path not found." yellow
        fi

    done < $1

}

# the main command that will be called (mnemonic repos check)
rc() {

    # decide if we also want to pull: for now the command can accept
    # only a single parameter and it must be --pull
    do_pull=0
    if [ $# -eq 1 ]; then
        if [ "$1" = "--pull" ]; then
            do_pull=1
            echo_color "Input your git password:" cyan
            read -s GIT_PASSWORD
            GIT_ASKPASS=$HOME/dotfiles/git/git_askpass_helper.sh
        fi
    fi

    # in this files there are lists of specific repos to check
    input_single_repos=(
        "$HOME/dotfiles/git/repos_single_list.txt"
        # "$HOME/dotfiles/git/not_existent.txt"
    )
    for file_name_single_repo in "${input_single_repos[@]}"
    do
        repo_file_single_check $file_name_single_repo
    done

    # in this files there are lists of folders:
    # check every subfolders
    input_folder_repos=(
        "$HOME/dotfiles/git/repos_folder_list.txt"
    )
    for file_name_folder_repo in "${input_folder_repos[@]}"
    do
        repo_file_folder_check $file_name_folder_repo
    done

}

# every repo in repo folders must be checked
# only add in the single list repos in different places

### IDEAS / TODO ###
# move ideas and info in readme
# use default parameters for bold/background color
# move echo_color in ~/dotfiles/bash/echo_color.bash
# use # to skip lines in the list file
# add local file to check
# a verbose flag that prints git status output

### INFO ###

# colors and a very nice structure
# https://gist.github.com/mzabriskie/6631607

# check for git in different folder
# https://stackoverflow.com/a/24352829/2237151

# check for correct parameters
# https://tldp.org/LDP/abs/html/complexfunct.html

# look for _project_ both in $HOME and in $HOME/repos
# use a found=0 var to check

# Load Content of a File into an Array
# filecontent=( `cat "logfile" `)
# for t in "${filecontent[@]}"; do echo "$t"; done

# iterate over array
# for i in "${my_array[@]}"; do echo "$i"; done

# define hash tables in bash
# https://www.artificialworlds.net/blog/2012/10/17/bash-associative-array-examples/
# https://stackoverflow.com/questions/1494178/how-to-define-hash-tables-in-bash

# check if file exists
# https://linuxize.com/post/bash-check-if-file-exists/

# command options
# https://stackoverflow.com/a/29754866/2237151
# https://medium.com/@Drew_Stokes/bash-argument-parsing-54f3b81a6a8f

# pull with password
# https://serverfault.com/a/912788

# color in git output
# https://stackoverflow.com/a/27430972/2237151
