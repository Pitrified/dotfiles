import argparse
import logging

# from timeit import default_timer as timer
# import numpy as np  # type: ignore


def parse_arguments() -> argparse.Namespace:
    r"""Setup CLI interface"""
    parser = argparse.ArgumentParser(description="")

    default = "DEBUG"
    parser.add_argument(
        "-lld",
        "--log_level_debug",
        type=str,
        default=default,
        help=f"Level for the debugging logger, default {default}",
        choices=["DEBUG", "INFO", "WARN", "ERROR", "CRITICAL"],
    )

    default = "m"
    parser.add_argument(
        "-llt",
        "--log_level_type",
        type=str,
        default=default,
        help=f"Message format for the debugging logger, default {default}",
        choices=["anlm", "nlm", "lm", "nm", "m"],
    )

    # last line to parse the args
    args = parser.parse_args()
    return args


def setup_logger(logLevel: str = "DEBUG", msg_type: str = "m") -> None:
    r"""Setup logger that outputs to console for the module"""
    logroot = logging.getLogger("c")
    logroot.propagate = False
    logroot.setLevel(logLevel)

    module_console_handler = logging.StreamHandler()

    if msg_type == "anlm":
        log_format_module = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    elif msg_type == "nlm":
        log_format_module = "%(name)s - %(levelname)s: %(message)s"
    elif msg_type == "lm":
        log_format_module = "%(levelname)s: %(message)s"
    elif msg_type == "nm":
        log_format_module = "%(name)s: %(message)s"
    else:
        log_format_module = "%(message)s"

    formatter = logging.Formatter(log_format_module)
    module_console_handler.setFormatter(formatter)

    logroot.addHandler(module_console_handler)


def setup_env() -> argparse.Namespace:
    r"""Setup the logger and parse the args"""
    args = parse_arguments()
    setup_logger(args.log_level_debug, args.log_level_type)

    # build command string to repeat this run, useful to remember default values
    # FIXME if an option is a flag this does not work (can't just copy/paste), sorry
    recap = "python3 imagenet_preprocess.py"
    for a, v in args._get_kwargs():
        recap += f" --{a} {v}"

    logmain = logging.getLogger(f"c.{__name__}.setup_env")
    logmain.info(recap)

    return args


def run_@BASENAME@(args: argparse.Namespace) -> None:
    r"""MAKEDOC: What is @BASENAME@ doing?"""
    logg = logging.getLogger(f"c.{__name__}.run_@BASENAME@")
    logg.debug("Starting run_@BASENAME@")


if __name__ == "__main__":
    args = setup_env()
    run_@BASENAME@(args)
