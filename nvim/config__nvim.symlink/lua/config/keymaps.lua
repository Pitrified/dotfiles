-- Mappings that need no plugin. Plugin mappings live with their plugin spec.
local map = vim.keymap.set

-- leave insert mode
map("i", "jk", "<Esc>", { desc = "Leave insert mode" })
map("i", "jK", "<Esc>", { desc = "Leave insert mode (typo)" })
map("i", "kj", "<Esc>", { desc = "Leave insert mode" })

-- move by screen line when lines wrap; gj/gk keep the exact line jump for counts
map("n", "j", "gj", { desc = "Down by screen line" })
map("n", "k", "gk", { desc = "Up by screen line" })
map("n", "gj", "j", { desc = "Down by buffer line" })
map("n", "gk", "k", { desc = "Up by buffer line" })

-- in visual mode J/K are usually a typo from holding shift after V
map("v", "J", "j", { desc = "Down (shift typo)" })
map("v", "K", "k", { desc = "Up (shift typo)" })

-- yank a line and comment it, using the built-in gcc
map("n", "gcy", "yygcc", { remap = true, desc = "Yank line, comment it" })
map("n", "gcp", "yygccp", { remap = true, desc = "Comment line, paste copy below" })
map("n", "gcP", "yygccP", { remap = true, desc = "Comment line, paste copy above" })

-- save and quit
map("n", "<leader>w", "<cmd>update<CR>", { desc = "Save if modified" })
map("n", "<leader>q", "<cmd>q<CR>", { desc = "Quit window" })

-- edit and source config
map("n", "<leader>re", "<cmd>tabedit " .. vim.fn.stdpath("config") .. "/init.lua<CR>", { desc = "Edit init.lua" })
map("n", "<leader>rs", "<cmd>source %<CR>", { desc = "Source current file" })

-- toggles
map("n", "<leader>nh", "<cmd>set hlsearch!<CR>", { desc = "Toggle search highlight" })
map("n", "<leader>nc", "<cmd>set cursorcolumn!<CR>", { desc = "Toggle cursor column" })
map("n", "<leader>nw", "<cmd>set wrap!<CR>", { desc = "Toggle wrap" })
map("n", "<leader>nl", "<cmd>set list!<CR>", { desc = "Toggle listchars" })
map("n", "<leader>ns", "<cmd>setlocal spell! spelllang=en_us<CR>", { desc = "Toggle spell check" })

-- yank whole file into the system clipboard
map("n", "<leader>ya", "<cmd>%y+<CR>", { desc = "Yank file to clipboard" })

-- close all folds and go to the bottom, going to the top first to show as much as possible;
-- cc opens one level, for when you are inside a class
map("n", "<leader>cf", "zMggG", { desc = "Close all folds" })
map("n", "<leader>cc", "zMzrggG", { desc = "Close folds but one level" })

-- split, navigate and move windows
map("n", "<leader>d", "<C-w>v", { desc = "Vertical split" })
map("n", "<leader>s", "<C-w>s", { desc = "Horizontal split" })
for _, key in ipairs({ "h", "j", "k", "l" }) do
  map("n", "<leader>" .. key, "<C-w>" .. key, { desc = "Go to window " .. key })
  map("n", "<leader>m" .. key, "<C-w>" .. key:upper(), { desc = "Move window " .. key })
end

-- the same from a terminal, on <C-w> as in Vim's terminal (a <Space> prefix would delay every typed space):
-- leave terminal mode first, then the window command; <C-w>. sends a literal <C-w> to the shell
for _, key in ipairs({ "h", "j", "k", "l" }) do
  map("t", "<C-w>" .. key, "<C-\\><C-n><C-w>" .. key, { desc = "Go to window " .. key })
  map("t", "<C-w>" .. key:upper(), "<C-\\><C-n><C-w>" .. key:upper(), { desc = "Move window " .. key })
end
map("t", "<C-w>gt", "<C-\\><C-n>gt", { desc = "Next tab" })
map("t", "<C-w>gT", "<C-\\><C-n>gT", { desc = "Previous tab" })
map("t", "<C-w>.", "<C-w>", { desc = "Send <C-w> to the shell" })
map("t", "jk", "<C-\\><C-n>", { desc = "Leave terminal mode" })

-- quickfix and location list steps that wrap around at the ends (was vim-unimpaired plus wrap_command.vim);
-- quiet when the list is empty or missing
local function list_step(cmd, wrap_cmd)
  return function()
    local ok, err = pcall(vim.cmd, cmd)
    if ok then
      return
    end
    if err:find("E553") then
      vim.cmd(wrap_cmd)
    elseif not (err:find("E42") or err:find("E776")) then
      vim.notify(err, vim.log.levels.ERROR)
    end
  end
end
map("n", "[q", list_step("cprevious", "clast"), { desc = "Previous quickfix entry (wraps)" })
map("n", "]q", list_step("cnext", "cfirst"), { desc = "Next quickfix entry (wraps)" })
map("n", "[l", list_step("lprevious", "llast"), { desc = "Previous location entry (wraps)" })
map("n", "]l", list_step("lnext", "lfirst"), { desc = "Next location entry (wraps)" })

-- make and restore sessions; also `nvim -S <file>`
local sessions_dir = vim.fn.stdpath("state") .. "/sessions"
vim.fn.mkdir(sessions_dir, "p")
map("n", "<leader>ms", ":mksession! " .. sessions_dir .. "/<C-d>", { desc = "Save session" })
map("n", "<leader>mr", ":source " .. sessions_dir .. "/<C-d>", { desc = "Restore session" })

-- file explorer in a split
map("n", "<leader>es", "<cmd>Sexplore<CR>", { desc = "Explore in split" })

-- strip trailing whitespace, keeping the view and the last search
map("n", "<F5>", function()
  local view = vim.fn.winsaveview()
  vim.cmd([[keeppatterns %s/\s\+$//e]])
  vim.fn.winrestview(view)
end, { desc = "Strip trailing whitespace" })
