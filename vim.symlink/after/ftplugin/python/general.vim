nnoremap <leader>bb :Black<CR>
nnoremap <leader>bf mb:Black<CR>:update<CR>`b
nnoremap <leader>gd :YcmCompleter GetDoc<CR>

" yank whatever is inside the parenthesis, save it in the variable recap, create a new
" line with recap+= ready and leave recap inside the parenthesis
let @r = "0f(lcibrecapjkOrecap = jk\"-porecap += f\" \"jki"

" sort the word in a line after the cursor, separated by a comma, needs a new
" line after it
let @t = "i\<CR>jkmy:s/, /\\r\<CR>V`y:sort\<CR>gv:s/\\n/, \<CR>kJA\<BS>\<BS>jk] "

setlocal textwidth=88
