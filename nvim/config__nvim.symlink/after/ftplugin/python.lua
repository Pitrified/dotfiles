vim.opt_local.textwidth = 88

local function termcodes(keys)
  return vim.api.nvim_replace_termcodes(keys, true, false, true)
end

-- the macros are set charwise ("c"): setreg would guess linewise for @s, which ends in <CR>

-- @r: yank what is inside the parenthesis into `recap`, open a new line with `recap +=`
-- ready, and leave `recap` inside the parenthesis
vim.fn.setreg("r", [[0f(lcibrecapjkOrecap = jk"-porecap += f" "jki]], "c")

-- @t: sort the comma-separated words after the cursor; needs a new line after it
vim.fn.setreg("t", termcodes([[i<CR>jkmy:s/, /\r<CR>V`y:sort<CR>gv:s/\n/, <CR>kJA<BS><BS>jk] ]]), "c")

-- @s: sort the lines of a paragraph on what follows from/import
vim.fn.setreg("s", termcodes([[vip:sort '^\(from\|import\) '<CR>]]), "c")
