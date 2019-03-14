#### install.py
Deve simlinkare tutto, e aggiungere i file di cui fare source a `~/.bash_aliases`. `.bash_aliases` e\` un file nel tuo pc, non lo version controlli, viene generato da `install.py`. Se ci sono tuoi `bash_aliases` li metti in `~/dotfiles/bash/bash_aliases.bash` e ne fara\` il source (indicandolo in `~/bash_aliases`.
* **topic/\*.bash**: source it
* **topic/\*.symlink**: symlink it

Se ci sono cartelle topic.symlink le simlinka tutte
* .vim
* .teamocil

#### Struttura
* Ispirato da [holman](https://github.com/holman/dotfiles)
* `~/.bash_aliases` fa fare source ai `.bash`, viene generato da `install.py`
* info private di git vengono salvate in `~/.gitconfig.local`, che viene incluso da `gitconfig`

### TODO list
Better backup if folder exixts
