mkcdir ()
{
    mkdir -p -- "$1" &&
    cd -P -- "$1"
}

alias le="exa -lh --git"

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
