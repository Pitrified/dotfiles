-- How diagnostics show. Signs land in the number column (signcolumn=number in options.lua);
-- the float is the 0.12 default <C-w>d, and ]d/[d jump between them.
vim.diagnostic.config({
  virtual_text = true,
  severity_sort = true,
})

-- fill the location list on demand (was :SyntasticCheck), so [l/]l walk it
vim.keymap.set("n", "<leader>bs", vim.diagnostic.setloclist, { desc = "Diagnostics to location list" })
