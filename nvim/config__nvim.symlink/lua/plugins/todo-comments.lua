-- highlight keywords in comments, with the extra ones of the old setup, matched as bare words
return {
  "folke/todo-comments.nvim",
  event = "VeryLazy",
  dependencies = { "nvim-lua/plenary.nvim" },
  opts = {
    signs = false, -- the sign column is shared with the line numbers
    keywords = {
      MAYBE = { icon = "? ", color = "hint" },
      YES = { icon = "+ ", color = "hint" },
      NO = { icon = "- ", color = "warning" },
      QUESTION = { icon = "? ", color = "info" },
    },
    highlight = { pattern = [[.{-}<(KEYWORDS)>]] }, -- the first keyword on a line (todo-comments highlights one per line)
    search = { pattern = [[\b(KEYWORDS)\b]] },
  },
}
