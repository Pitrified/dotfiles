-- Completion menu from LSP, paths, snippets (friendly-snippets, expanded by vim.snippet) and buffer words
return {
  "saghen/blink.cmp",
  version = "1.*", -- release tags, so blink downloads its prebuilt matcher
  dependencies = { "rafamadriz/friendly-snippets" },
  event = "InsertEnter",
  opts = {
    keymap = {
      preset = "default",
      -- the old UltiSnips keys: inside a snippet they jump, otherwise they act on the menu
      ["<C-j>"] = { "snippet_forward", "select_and_accept", "fallback" },
      ["<C-p>"] = { "snippet_backward", "select_prev", "fallback_to_mappings" },
    },
    completion = {
      -- the kind as text instead of an icon: no Nerd Font is in use
      menu = { draw = { columns = { { "label", "label_description", gap = 1 }, { "kind" } } } },
    },
    snippets = {
      -- with expr folds and foldlevel=0 the inserted snippet sits in a closed fold, so selecting a placeholder
      -- selects the whole fold and typing replaces the snippet: folds are off in the window until normal mode.
      -- vim.snippet passes through normal mode on its way to select mode, hence the scheduled mode check.
      expand = function(snippet)
        local win = vim.api.nvim_get_current_win()
        if vim.wo[win].foldenable then
          vim.wo[win].foldenable = false
          local group = vim.api.nvim_create_augroup("snippet_folds", { clear = true })
          vim.api.nvim_create_autocmd("ModeChanged", {
            group = group,
            pattern = "*:n",
            callback = function()
              vim.schedule(function()
                if vim.api.nvim_get_mode().mode ~= "n" then return end
                if vim.api.nvim_win_is_valid(win) then vim.wo[win].foldenable = true end
                pcall(vim.api.nvim_del_augroup_by_id, group)
              end)
            end,
          })
        end
        vim.snippet.expand(snippet)
      end,
    },
    -- command-line completion stays on wildmenu (wildmode in options.lua)
    cmdline = { enabled = false },
    sources = {
      default = { "lazydev", "lsp", "path", "snippets", "buffer" },
      providers = {
        lazydev = { name = "LazyDev", module = "lazydev.integrations.blink", score_offset = 100 },
        lsp = {
          -- blink scores snippets 3 lower (snippets.score_offset = -3), so a server's keyword items
          -- (Python's `for`, `try`) beat the snippet of the same name and <C-j> accepted the bare word;
          -- one point below the snippets keeps keywords in the menu, under their snippet
          transform_items = function(_, items)
            local keyword = require("blink.cmp.types").CompletionItemKind.Keyword
            for _, item in ipairs(items) do
              if item.kind == keyword then item.score_offset = (item.score_offset or 0) - 4 end
            end
            return items
          end,
        },
      },
    },
    fuzzy = { implementation = "prefer_rust_with_warning" },
  },
}
