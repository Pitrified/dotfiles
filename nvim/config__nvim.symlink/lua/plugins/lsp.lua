-- Language servers: nvim-lspconfig only supplies the server configs (its lsp/*.lua), Neovim runs them.
-- The servers are installed outside nvim: uv tool, go install, ~/.local (plans 02, decision 21).
return {
  {
    "neovim/nvim-lspconfig",
    lazy = false,
    config = function()
      -- pyright's normal level; a project can raise it in pyproject.toml
      vim.lsp.config("basedpyright", {
        settings = { basedpyright = { analysis = { typeCheckingMode = "standard" } } },
      })

      vim.lsp.enable({ "ruff", "basedpyright", "lua_ls", "gopls", "dartls", "bashls" })

      vim.api.nvim_create_autocmd("LspAttach", {
        group = vim.api.nvim_create_augroup("lsp_attach", { clear = true }),
        callback = function(args)
          local client = vim.lsp.get_client_by_id(args.data.client_id)
          if client and client.name == "ruff" then
            -- K shows basedpyright's hover, not ruff's
            client.server_capabilities.hoverProvider = false
          end
          -- the 0.12 defaults (grn, gra, grr, gri, grt, gO, K) stay; gd goes to the definition
          vim.keymap.set("n", "gd", vim.lsp.buf.definition, { buffer = args.buf, desc = "Go to definition" })
        end,
      })
    end,
  },
  {
    -- lua_ls learns the Neovim runtime and the plugin types when editing this config
    "folke/lazydev.nvim",
    ft = "lua",
    opts = {
      library = {
        { path = "${3rd}/luv/library", words = { "vim%.uv" } },
      },
    },
  },
}
