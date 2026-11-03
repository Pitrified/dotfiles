-- Entry point: leader first, so every mapping defined later sees it.
vim.g.mapleader = " "

require("config.options")
require("config.keymaps")
require("config.autocmds")
require("config.diagnostics")
require("config.lazy")

-- Machine-specific overrides, kept out of the repo.
local local_config = vim.fn.expand("~/.nvim.local.lua")
if vim.fn.filereadable(local_config) == 1 then
  dofile(local_config)
end
