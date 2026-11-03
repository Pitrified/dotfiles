-- nvim-treesitter (main branch) only installs parsers; highlighting and folds are Neovim's own,
-- started per buffer below wherever a parser exists. Other filetypes keep regex syntax.
local parsers = {
  "python", "lua", "go", "gomod", "bash",
  "markdown", "markdown_inline", "yaml", "json", "toml",
  "html", "css", "javascript", "typescript", "tsx",
  "gitcommit", "diff", "dockerfile",
  "vim", "vimdoc", "query", "regex",
}

return {
  "nvim-treesitter/nvim-treesitter",
  branch = "main",
  lazy = false, -- the main branch does not support lazy-loading
  build = ":TSUpdate",
  config = function()
    require("nvim-treesitter").install(parsers)

    -- indent stays on the runtime indent scripts: treesitter indent is experimental
    vim.api.nvim_create_autocmd("FileType", {
      group = vim.api.nvim_create_augroup("treesitter", { clear = true }),
      callback = function(args)
        if not pcall(vim.treesitter.start, args.buf) then
          return
        end
        vim.wo[0][0].foldmethod = "expr"
        vim.wo[0][0].foldexpr = "v:lua.vim.treesitter.foldexpr()"
      end,
    })
  end,
}
