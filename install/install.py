import argparse
import filecmp
import logging
from pathlib import Path
from timeit import default_timer as timer


def parse_arguments():
    """Setup CLI interface"""
    parser = argparse.ArgumentParser(description="")

    parser.add_argument(
        "-bd",
        "--backup_dir",
        type=str,
        default=".rcback",
        help="Name of the backup folder",
    )

    parser.add_argument(
        "-n",
        "--dry-run",
        action="store_true",
        help="Show what would happen without changing anything",
    )

    parser.add_argument(
        "-lld",
        "--log_level_debug",
        type=str,
        default="INFO",
        help="LogLevel for the debugging logger",
        choices=["TRACE", "DEBUG", "INFO", "WARN", "ERROR", "CRITICAL"],
    )

    # last line to parse the args
    args = parser.parse_args()
    return args


def setup_logger(logLevel="DEBUG"):
    """Setup logger that outputs to console for the module"""
    logroot = logging.getLogger("c")
    logroot.propagate = False
    logroot.setLevel(logLevel)

    module_console_handler = logging.StreamHandler()

    #  log_format_module = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    #  log_format_module = "%(name)s - %(levelname)s: %(message)s"
    #  log_format_module = '%(levelname)s: %(message)s'
    #  log_format_module = '%(name)s: %(message)s'
    log_format_module = "%(message)s"

    formatter = logging.Formatter(log_format_module)
    module_console_handler.setFormatter(formatter)

    logroot.addHandler(module_console_handler)

    logging.addLevelName(5, "TRACE")
    # use it like this
    # logroot.log(5, 'Exceedingly verbose debug')


def setup_env():
    args = parse_arguments()

    setup_logger(args.log_level_debug)

    # build command string to repeat this run
    # FIXME if an option is a flag this does not work, sorry
    recap = "uv run install.py"
    for a, v in args._get_kwargs():
        recap += f" --{a} {v}"

    logmain = logging.getLogger(f"c.{__name__}.setup_env")
    logmain.info(recap)

    return args


def find_free_dir(home_dir, dir_name_root):
    """Finds a directory in home_dir with an unique name"""
    # logg = logging.getLogger(f"c.{__name__}.find_free_dir")

    for i in range(100):
        new_dir = home_dir / f"{dir_name_root}{i:02d}"
        if not new_dir.exists():
            return new_dir

    return None


def is_conf_dir(conf_dir):
    """Returns true if conf_dir is, indeed, a config folder"""
    # logg = logging.getLogger(f"c.{__name__}.is_conf_dir")

    exclude_dir = [".git"]

    if conf_dir.is_dir() and conf_dir.name not in exclude_dir:
        return True
    else:
        return False


def backup(src_at_home, backup_dir, dry_run=False):
    """Moves src_at_home into backup_dir, keeping the same name"""
    logg = logging.getLogger(f"c.{__name__}.backup")
    # logg.debug(f"Start backup")

    # exists() follows symlinks, so a real-but-symlinked target still backs up;
    # also catch dangling symlinks that exists() would miss
    if src_at_home.exists() or src_at_home.is_symlink():
        src_at_back = backup_dir / src_at_home.name
        logg.debug(f"   src_at_back:\t{src_at_back}")
        if dry_run:
            logg.info(f"\t[dry-run] Would back up {src_at_home} to {src_at_back}")
            return
        src_at_home.rename(src_at_back)
        logg.info(f"\tBacked up {src_at_home} to {src_at_back}")


def link_config(config_at_dot, home_dir, backup_dir, dry_run=False):
    """Symlinks config_at_dot to its target in home_dir.

    A "__" in the stem expands to "/", so nested targets like
    claude__rules__python.md.symlink -> ~/.claude/rules/python.md
    (a topic with no "__" resolves flat, e.g. bash.symlink -> ~/.bash).
    Shared by both the topic-level (whole folder) and item-level symlinks.
    """
    logg = logging.getLogger(f"c.{__name__}.link_config")

    # find the path of config_at_dot in the home directory
    rel_at_home = config_at_dot.stem.replace("__", "/")
    config_at_home = home_dir / f".{rel_at_home}"
    logg.debug(f"config_at_home:\t{config_at_home}")

    # already correctly linked: skip, so re-running is a no-op and we
    # do not churn the backup folder with the existing symlink
    if (
        config_at_home.is_symlink()
        and config_at_home.resolve() == config_at_dot.resolve()
    ):
        logg.info(f"\tAlready linked {config_at_home}")
        return

    # divergence guard: a real (non-symlink) file means an external
    # writer (e.g. an app rewriting its own config) replaced our
    # symlink. Warn loudly so we never silently revert newer content
    # to the stale repo copy. The file is still backed up below, so
    # the newer content is recoverable from the backup folder.
    if (
        config_at_home.is_file()
        and not config_at_home.is_symlink()
        and not filecmp.cmp(config_at_home, config_at_dot, shallow=False)
    ):
        logg.warning(
            f"\t!! {config_at_home} is a real file that DIFFERS from the repo source.\n"
            f"\t   Something replaced the symlink and wrote newer content.\n"
            f"\t   It will be backed up to {backup_dir}, but the relink points at the\n"
            f"\t   stale repo copy. Reconcile before trusting it (the backup has the newer file)."
        )

    # make sure the parent dir exists for nested targets
    if not dry_run:
        config_at_home.parent.mkdir(parents=True, exist_ok=True)

    # backup the current config_at_home into rcback
    backup(config_at_home, backup_dir, dry_run)

    # link config_at_home to config_at_dot
    if dry_run:
        logg.info(f"\t[dry-run] Would symlink {config_at_home} to {config_at_dot}")
    else:
        config_at_home.symlink_to(
            config_at_dot, target_is_directory=config_at_dot.is_dir()
        )
        logg.info(f"\tSymlinked {config_at_home} to {config_at_dot}")


def add_source(alias_at_home, config_at_dot, dry_run=False):
    """Sources config_at_dot in alias_at_home"""
    logg = logging.getLogger(f"c.{__name__}.add_source")
    # logg.debug(f"Start add_source")

    if dry_run:
        logg.info(f"\t[dry-run] Would source {config_at_dot} in {alias_at_home}")
        return

    # the string to source a file from bash_aliases
    sourcestr = "if [ -f {0} ]; then\n    . {0}\nfi\n\n"

    with open(alias_at_home, "a") as fa:
        fa.write(sourcestr.format(config_at_dot))
        logg.info(f"\tSourced {config_at_dot} in ~/.bash_aliases")


def run_install(args):
    """Sets up the environment"""
    logg = logging.getLogger(f"c.{__name__}.run_install")

    install_start = timer()

    dry_run = args.dry_run
    if dry_run:
        logg.info("\n*** DRY RUN: no files will be moved, written, or linked ***")

    home_dir = Path.home()
    logg.debug(f"      home_dir:\t{home_dir}")

    # find a new free backup folder
    backup_dir = find_free_dir(home_dir, args.backup_dir)
    if backup_dir is None:
        logg.critical("No empty backup folder found, aborting.")
        return False
    logg.debug(f"    backup_dir:\t{backup_dir}")
    if not dry_run:
        backup_dir.mkdir()

    # the repo folder: install.py lives at <dotfiles_dir>/install/install.py
    dotfiles_dir = Path(__file__).resolve().parent.parent
    logg.debug(f"  dotfiles_dir:\t{dotfiles_dir}")

    logg.info(f"\nUsing backup folder {backup_dir}")

    logg.info("\nSetup bash aliases")

    # the bash_aliases file
    alias_at_home = home_dir / ".bash_aliases"
    logg.debug(f"\nalias_at_home:\t{alias_at_home}")
    # backup it
    backup(alias_at_home, backup_dir, dry_run)

    # add line telling that the file is autogenerated, do not modify
    if dry_run:
        logg.info(f"\t[dry-run] Would regenerate {alias_at_home}")
    else:
        with open(alias_at_home, "a") as fa:
            fa.write("# Auto-generated file. Do not modify.\n")
            fa.write("# Run python ~/dotfiles/install.py to reload the file.\n")
            fa.write(
                "# Add content in ~/.bash_aliases.local or ~/.bash_aliases.after.local.\n"
            )
            fa.write("\n")

    # source ~/.bash_aliases.local
    alias_local = home_dir / ".bash_aliases.local"
    add_source(alias_at_home, alias_local, dry_run)

    for topic_at_dot in dotfiles_dir.iterdir():
        # check if the folder is a valid config dir
        if not is_conf_dir(topic_at_dot):
            # logg.debug(f"\tNot a config folder, skipping it")
            continue

        logg.info(f"\nTopic: {topic_at_dot.name}")
        logg.debug(f"  topic_at_dot:\t{topic_at_dot}")

        # check if we need to link the whole folder
        if topic_at_dot.suffix == ".symlink":
            link_config(topic_at_dot, home_dir, backup_dir, dry_run)

        # go through all the items in the topic dir
        for config_at_dot in topic_at_dot.iterdir():
            # source the .bash files
            if config_at_dot.suffix == ".bash":
                logg.debug(f" config_at_dot:\t{config_at_dot}")

                # add the formatted lines in ~/.bash_aliases
                add_source(alias_at_home, config_at_dot, dry_run)

            # symlink the .symlink files
            if config_at_dot.suffix == ".symlink":
                logg.debug(f" config_at_dot:\t{config_at_dot}")
                link_config(config_at_dot, home_dir, backup_dir, dry_run)

    logg.info("\nSetup bash aliases after")
    # source ~/.bash_aliases.after.local
    alias_local_after = home_dir / ".bash_aliases.after.local"
    add_source(alias_at_home, alias_local_after, dry_run)

    install_end = timer()
    logg.info(f"\nDone installing, took {install_end - install_start:.3f} s")
    logg.info("Remember to do 'source ~/.bashrc'")


if __name__ == "__main__":
    args = setup_env()
    run_install(args)
