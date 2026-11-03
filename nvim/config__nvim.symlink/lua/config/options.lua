-- Editor options. Only what differs from the Neovim 0.12 defaults is set here.
local opt = vim.opt

-- behavior
opt.viewoptions = { "folds", "options", "cursor", "unix", "slash" }
opt.virtualedit = "onemore" -- allow the cursor one past the last character
opt.gdefault = true -- :s replaces every match on the line by default
opt.mouse = "a"
opt.clipboard = { "unnamed", "unnamedplus" }

-- search
opt.showmatch = true
opt.matchtime = 3 -- tenths of a second
opt.ignorecase = true
opt.smartcase = true

-- command-line completion
opt.wildmode = { "list:longest", "full" }
opt.wildignore:append({ "*.pyc", "*.class" })
opt.wildignorecase = true

-- windows and lines
opt.splitright = true
opt.splitbelow = true
opt.wrap = false
opt.scrolloff = 8
opt.listchars = { tab = ">-", trail = "~", extends = ">", precedes = "<", space = "·", eol = "¬" }
opt.number = true
opt.relativenumber = true
opt.numberwidth = 3
opt.signcolumn = "number"
opt.cursorline = true
opt.showmode = true

-- indentation
opt.shiftwidth = 4
opt.expandtab = true
opt.tabstop = 4
opt.softtabstop = 4

-- backup and undo: swap and undo use the default state dirs;
-- backupdir drops the default leading "." so backups never land next to the files
opt.backup = true
local backupdir = vim.fn.stdpath("state") .. "/backup"
vim.fn.mkdir(backupdir, "p")
opt.backupdir = backupdir .. "//"
opt.undofile = true

-- colors
opt.termguicolors = true
opt.background = "dark"

-- statusline: path, flags, then diagnostic counts, buffer number, filetype, position
opt.statusline = table.concat({
  "%<", -- cut at start if the line is too long
  "%f", -- path relative to current directory
  " %h%m%r", -- help, modified, readonly flags
  "%=", -- right align from here
  -- diagnostic counts as `E:2 W:1 `, nothing when there are none (the guard from the 0.12 default statusline)
  "%{% luaeval('(package.loaded[''vim.diagnostic''] and next(vim.diagnostic.count()) and vim.diagnostic.status() .. '' '') or '''' ') %}",
  ":b%n", -- buffer number with :b in front
  "%y", -- filetype
  "%w", -- preview window flag
  " %l,%c%V", -- line, column, virtual column when different
  " %P", -- percentage through file
})

-- globals read by the runtime filetype plugins, so they must be set before any file opens
vim.g.tex_flavor = "latex"

-- netrw
vim.g.netrw_liststyle = 1 -- one file per line with size and time stamp (toggle with i)
vim.g.netrw_banner = 0 -- hide the banner (show with I)
