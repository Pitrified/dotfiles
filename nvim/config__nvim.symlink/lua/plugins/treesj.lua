-- split and join code blocks on the splitjoin.vim keys; the default <space> keys would clash with leader
return {
  "Wansmer/treesj",
  keys = {
    { "gS", function() require("treesj").split() end, desc = "Split block" },
    { "gJ", function() require("treesj").join() end, desc = "Join block" },
  },
  opts = { use_default_keymaps = false },
}
