-- labelled jumps (was easymotion); the README keys. s replaces the built-in s, use cl.
-- char mode (the default) also extends f/t/F/T
return {
  "folke/flash.nvim",
  event = "VeryLazy",
  opts = {},
  keys = {
    { "s", mode = { "n", "x", "o" }, function() require("flash").jump() end, desc = "Flash" },
    { "S", mode = { "n", "x", "o" }, function() require("flash").treesitter() end, desc = "Flash treesitter" },
    { "r", mode = "o", function() require("flash").remote() end, desc = "Remote flash" },
    { "R", mode = { "o", "x" }, function() require("flash").treesitter_search() end, desc = "Treesitter search" },
    { "<c-s>", mode = { "c" }, function() require("flash").toggle() end, desc = "Toggle flash search" },
  },
}
