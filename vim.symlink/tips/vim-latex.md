## vim-latex guide

[Quick reference](https://michaelgoerz.net/refcards/vimlatexqrc.pdf)

[Documentation](http://vim-latex.sourceforge.net/documentation/latex-suite.html)

#### automagic goodness
* `^^` turns into `^{}<++>`
* `F5` prompts for environment to be inserted
* `S-F5` prompts to change the current environment
* `F7` while touching a word, create a command from that. On a white space, prompts
* `F9` inside `\ref{}` opens window of all labels, filtering partially written labels
* forward and inverse searches exist, remember it

#### Environment Macros
* apply to selection with `,it`
* `EDE` description
* `EIT` itemize
* `EEQ` equation
* `ECE` center
* `EVM` verbatim
* `EFI` figure
* `EMP` minipage

#### Font Macros
* `F**` insert font description `\text**{}` or `\emph{}`, works on selection with `` `**``

#### Bindings
* `` `a`` greek letters, some uppercase
* `` `/`` fraction
* `` `|`` big |
* `` `2`` sqrt
* `` `(`` enclose selection in `()`
* `` `[`` enclose selection in `[]`
* `` `{`` enclose selection in `{}`
* `` `$`` enclose selection in `$$` or `\[\]` char or line select
* `` `R`` expands to `\prod_{<++>}^{<++>}<++>`
* `` `U`` expands to `\sum_{<++>}^{<++>}<++>`
* `` `N`` expands to `\int_{<++>}^{<++>}<++>`

#### Alt key Macros
* `Alt-L` extend bracket constructs or insert label
* `Alt-B` enclose previous character in \mathbf{}
* `Alt-C` enclose in \mathcal{} or insert citation
* `Alt-I` insert list item intelligently

#### Objects
* `ic, ac` commands
* `id, ad` delimiters
* `ie, ae` LaTeX environments
* `i$, a$` inline math structures

#### Other
* `dsc, dse, ds$` delete surroundings command/env.
* `csc, cse, cs$` change surroundings command/env.
* `tse` toggle starred environment
* `tsd`toggle between e.g. () and \left(\right)

