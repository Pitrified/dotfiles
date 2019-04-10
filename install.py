#!/usr/bin/env python3

from os import listdir
from os.path import expanduser
from os.path import isdir
from os.path import islink
from os.path import isfile
from os.path import join
from os.path import splitext
from os import makedirs
from os import symlink
from shutil import move

def isConfDir(pathto, mydir):
    excludeDir = ['.git']
    if mydir not in excludeDir and isdir(join(pathto, mydir) ):
        return True
    else:
        return False

def backup(dir_old, myfile, dir_back, newfile=None):
    if newfile is None:
        newfile = myfile
    oldfull = join(dir_old, myfile)
    newfull = join(dir_back, newfile)
    print(f'Backing up: {oldfull}')
    if not isfile(oldfull) and not isdir(oldfull) and not islink(oldfull):
        print('       !!!! Not a file nor a folder nor a link')
        return
    print(f'      Into: {newfull}')

    if not isdir(dir_back):
        makedirs(dir_back)
    move(oldfull, newfull)

def createsymlink(dir_target, name_target, dir_link, name_link, dir_back):
    #  symlink(target, link_name)
    backup(dir_link, name_link, dir_back)
    targetfull = join(dir_target, name_target)
    linkfull = join(dir_link, name_link)
    print(f'Symlinking: {targetfull}')
    print(f'        To: {linkfull}')
    symlink(targetfull, linkfull)

def addsource(filealias, newalias):
    sourcestr = 'if [ -f {0} ]; then\n    . {0}\nfi\n\n'
    print(f'Adding to sourced files: {newalias}')
    with open(filealias, 'a') as fa:
        fa.write(sourcestr.format(newalias))

def main():
    dir_home = expanduser('~') # or os.getenv('HOME')
    dir_dot = join(dir_home, 'dotfiles')
    dir_back = join(dir_home, '.rcback')

    #!!!# put local aliases in ~/.bash_aliases.local
    backup(dir_home, '.bash_aliases', dir_back)
    bashalia = join(dir_home, '.bash_aliases')
    addsource(bashalia, '~/.bash_aliases.local')
    #  createsymlink(dir_dot, 'vim', dir_home, '.vim', dir_back)

    dirs = [d for d in listdir(dir_dot) if isConfDir(dir_dot, d ) ]
    for topic in dirs:
        print()
        topic_name, topic_ext = splitext(topic)
        print(f'Topic: {topic_name} {topic_ext}')
        if topic_ext == '.symlink':
            createsymlink(dir_dot, topic, dir_home, f'.{topic_name}', dir_back)

        dir_topic = join(dir_dot, topic)
        configs = [c for c in listdir(dir_topic)]
        print(f'{dir_topic}: {configs}')
        for config in configs:
            name, ext = splitext(config)
            #  print(f'{config}: {name}  {ext}')
            if ext == '.symlink':
                createsymlink(dir_topic, config, dir_home, '.'+name, dir_back)
            elif ext == '.bash':
                addsource(bashalia, join(dir_topic, config) )

if __name__ == '__main__':
    main()

# esplora le cartelle
# if file /**/*.bash source it in ~/bash_alias
# if file /**/*.symlink it in ~/.\1
#   if that existed, backup it in ~/.rcback/.\1
# vim e` un bambino speciale, devi symlinkare tutta la cartella
# se c'e' ~/.vimrc backup anche quello e toglilo
