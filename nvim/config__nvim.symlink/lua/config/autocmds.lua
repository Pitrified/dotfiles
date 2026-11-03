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

-- extra keywords in every *Todo syntax group
local todo_keywords = { "NOTE", "MAYBE", "YES", "NO", "QUESTION" }
vim.api.nvim_create_autocmd("Syntax", {
  group = group,
  callback = function()
    local seen = {}
    for line in vim.gsplit(vim.fn.execute("syntax list"), "\n") do
      local syn_group = line:match("^(%w*Todo)%s")
      if syn_group and not seen[syn_group] then
        seen[syn_group] = true
        vim.cmd(("syntax keyword %s contained %s"):format(syn_group, table.concat(todo_keywords, " ")))
      end
    end
  end,
})
