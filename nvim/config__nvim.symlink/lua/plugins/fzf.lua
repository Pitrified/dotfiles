-- fuzzy pickers on the fzf binary (~/.fzf/bin); live grep needs ripgrep, file search uses fd or fdfind
local function files(cwd)
  return function() require("fzf-lua").files({ cwd = cwd }) end
end

return {
  "ibhagwan/fzf-lua",
  cmd = "FzfLua",
  keys = {
    { "<leader>ff", files(nil), desc = "Find files" },
    { "<leader>fp", files(".."), desc = "Find files in parent folder" },
    { "<leader>fd", files("~/dotfiles"), desc = "Find files in dotfiles" },
    { "<leader>fe", files("~/ephem"), desc = "Find files in ephem" },
    { "<leader>fr", files("~/repos"), desc = "Find files in repos" },
    { "<leader>fa", function() require("fzf-lua").live_grep() end, desc = "Grep" },
    { "<leader>fb", function() require("fzf-lua").buffers() end, desc = "Find buffer" },
    { "<leader>fl", function() require("fzf-lua").lines() end, desc = "Find line in open buffers" },
  },
  opts = {},
}
