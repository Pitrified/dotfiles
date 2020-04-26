nnoremap <silent> <Plug>LocationPrevious    :<C-u> call wrap_command#WrapCommand("up", "l")<CR>
nnoremap <silent> <Plug>LocationNext        :<C-u> call wrap_command#WrapCommand("down", "l")<CR>

nnoremap <silent> <Plug>QuickFixPrevious    :<C-u> call wrap_command#WrapCommand("up", "c")<CR>
nnoremap <silent> <Plug>QuickFixNext        :<C-u> call wrap_command#WrapCommand("down", "c")<CR>
