local group = vim.api.nvim_create_augroup("config", { clear = true })

-- fold vimscript on {{{ }}} markers
vim.api.nvim_create_autocmd("FileType", {
  group = group,
  pattern = "vim",
  callback = function()
    vim.opt_local.foldmethod = "marker"
  end,
})

-- restore the cursor to its last position, except in git messages, which start at the top
vim.api.nvim_create_autocmd("BufReadPost", {
  group = group,
  callback = function(args)
    if vim.tbl_contains({ "gitcommit", "gitrebase" }, vim.bo[args.buf].filetype) then
      return
    end
    local mark = vim.api.nvim_buf_get_mark(args.buf, '"')
    if mark[1] > 0 and mark[1] <= vim.api.nvim_buf_line_count(args.buf) then
      pcall(vim.api.nvim_win_set_cursor, 0, mark)
    end
  end,
})

-- .html is always html, even with {% %} templates that would detect as htmldjango
vim.filetype.add({ extension = { html = "html" } })

-- new python files start from the skeleton, with @BASENAME@ as the file name without extension
local skeleton = vim.fn.stdpath("config") .. "/templates/skel.py"
vim.api.nvim_create_autocmd("BufNewFile", {
  group = group,
  pattern = "*.py",
  callback = function(args)
    local basename = vim.fn.fnamemodify(args.file, ":t:r"):gsub("%%", "%%%%")
    local lines = vim.fn.readfile(skeleton)
    for i, line in ipairs(lines) do
      lines[i] = line:gsub("@BASENAME@", basename)
    end
    vim.api.nvim_buf_set_lines(args.buf, 0, -1, false, lines)
  end,
})
