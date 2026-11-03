-- gruvbox, with closed folds on the normal background (bg0) instead of bg1
return {
  "ellisonleao/gruvbox.nvim",
  lazy = false,
  priority = 1000, -- before any other plugin draws
  config = function()
    local gruvbox = require("gruvbox")
    gruvbox.setup({
      overrides = { Folded = { bg = gruvbox.palette.dark0 } },
    })
    vim.cmd.colorscheme("gruvbox")
  end,
}
