-- insert-mode abbreviations, local to the tex buffer
local abbreviations = {
  { "lrb", [[\langle \rangle<C-O>8<Left>]] },
  { "odo", [[\odot]] },
  { "opl", [[\oplus]] },
  { "zzn", [[\zz{n}]] },
  { "zsn", [[\zs{n}]] },
  { "rap", "rappresentante principale" },
  { "rapi", "rappresentanti principali" },
  { "caa", [[\cln{a}]] },
  { "mon", [[\bmod n]] },
  { "gcdan", "gcd(a, n)" },
  { "gcdbn", "gcd(b, n)" },
  { "algo", "algoritmo" },
  { "algi", "algoritmi" },
  { "mlrb", [[\ldblbrace<CR>\rdblbrace<C-O>O   ]] },
}

for _, abbr in ipairs(abbreviations) do
  vim.keymap.set("ia", abbr[1], abbr[2], { buffer = true })
end
