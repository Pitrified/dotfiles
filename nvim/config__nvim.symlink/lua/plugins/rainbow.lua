-- rainbow parentheses through treesitter, on by default
return {
  "HiPhish/rainbow-delimiters.nvim",
  lazy = false,
  keys = {
    { "<leader>nr", function() require("rainbow-delimiters").toggle(0) end, desc = "Toggle rainbow delimiters" },
  },
}
