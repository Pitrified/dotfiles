-- <leader>bb formats the buffer: the listed formatter, else the LSP; no format on save
return {
  "stevearc/conform.nvim",
  cmd = "ConformInfo",
  keys = {
    {
      "<leader>bb",
      function() require("conform").format({ async = true, lsp_format = "fallback" }) end,
      desc = "Format buffer",
    },
  },
  opts = {
    formatters_by_ft = {
      python = { "ruff_format" },
      go = { "gofmt" },
      sh = { "shfmt" },
      bash = { "shfmt" },
    },
  },
}
