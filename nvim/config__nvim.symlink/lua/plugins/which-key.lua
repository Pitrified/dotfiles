-- popup of the mappings that follow a typed prefix; labels come from each mapping's desc
return {
  "folke/which-key.nvim",
  event = "VeryLazy",
  opts = {
    spec = {
      { "<leader>b", group = "format" },
      { "<leader>c", group = "folds" },
      { "<leader>e", group = "explore" },
      { "<leader>f", group = "find" },
      { "<leader>m", group = "move window, sessions" },
      { "<leader>n", group = "toggles" },
      { "<leader>r", group = "config" },
      { "<leader>y", group = "yank" },
      { "gr", group = "LSP" },
    },
  },
}
