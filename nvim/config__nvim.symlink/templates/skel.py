"""MAKEDOC: @BASENAME@ module level docstring."""
import argparse
import logging
from pathlib import Path
import typing as ty


# from timeit import default_timer as timer
# import numpy as np  # type: ignore


def parse_arguments() -> argparse.Namespace:
    r"""Setup CLI interface.

    Returns:
        The parsed arguments.
    """
    parser = argparse.ArgumentParser(description="")

    default = "WARN"
    parser.add_argument(
        "--console_log_level",
        type=str,
        default=default,
        help=f"Level for the console logger, default {default}",
        choices=["DEBUG", "INFO", "WARN", "ERROR", "CRITICAL"],
    )

    default = "lnm"
    parser.add_argument(
        "--console_fmt_type",
        type=str,
        default=default,
        help=f"Message format for the console logger, default {default}",
        choices=["lanm", "lnm", "lm", "nm", "m"],
    )

    # last line to parse the args
    args = parser.parse_args()
    return args


def setup_logger(
    console_fmt_type: str = "m",
    console_log_level: str = "WARN",
    ui_fmt_type: ty.Optional[str] = None,
    ui_log_level: str = "INFO",
    file_fmt_type: ty.Optional[str] = None,
    file_log_level: str = "WARN",
    file_log_path: ty.Optional[Path] = None,
    file_log_mode: str = "a",
) -> None:
    r"""Setup loggers for the module.

    Args:
        console_fmt_type: Message format for the console logger.
        console_log_level: Logger level for the console logger.
        ui_fmt_type: Message format for the ui logger.
        ui_log_level: Logger level for the ui logger.
        file_fmt_type: Message format for the file logger.
        file_log_level: Logger level for the file logger.
        file_log_path: Path to the log file.
        file_log_mode: Mode for the file logger: [aw] append or write.
    """
    # setup the format strings
    format_types = {}
    format_types["lanm"] = "[%(levelname)-8s] %(asctime)s %(name)s: %(message)s"
    format_types["lnm"] = "[%(levelname)-8s] %(name)s: %(message)s"
    format_types["lm"] = "[%(levelname)-8s]: %(message)s"
    format_types["nm"] = "%(name)s: %(message)s"
    format_types["m"] = "%(message)s"

    # setup the console handler with the console formatter
    console_handler = logging.StreamHandler()
    console_formatter = logging.Formatter(format_types[console_fmt_type])
    console_handler.setFormatter(console_formatter)

    # setup the console logger with the console handler
    logconsole = logging.getLogger("c")
    logconsole.propagate = False
    logconsole.setLevel(console_log_level)
    logconsole.addHandler(console_handler)

    if ui_fmt_type is not None:
        # setup the ui handler with the ui formatter
        ui_handler = logging.StreamHandler()
        ui_formatter = logging.Formatter(format_types[ui_fmt_type])
        ui_handler.setFormatter(ui_formatter)

        # setup the ui logger with the ui handler
        logui = logging.getLogger("ui")
        logui.propagate = False
        logui.setLevel(ui_log_level)
        logui.addHandler(ui_handler)

    if file_fmt_type is not None and file_log_path is not None:
        # setup the file handler with the file formatter
        file_handler = logging.FileHandler(file_log_path, mode=file_log_mode)
        file_formatter = logging.Formatter(format_types[file_fmt_type])
        file_handler.setFormatter(file_formatter)

        # setup the file logger with the file handler
        logfile = logging.getLogger("f")
        logfile.propagate = False
        logfile.setLevel(file_log_level)
        logfile.addHandler(file_handler)


def setup_env() -> argparse.Namespace:
    r"""Setup the logger and parse the args.

    Returns:
        The parsed arguments.
    """
    # parse the command line arguments
    args = parse_arguments()

    # setup the loggers
    console_fmt_type = args.console_fmt_type
    console_log_level = args.console_log_level
    ui_fmt_type = "m"
    ui_log_level = "INFO"
    file_fmt_type = "lanm"
    file_log_level = "WARN"
    file_log_path = Path("log_@BASENAME@.log")
    file_log_mode = "a"
    setup_logger(
        console_fmt_type=console_fmt_type,
        console_log_level=console_log_level,
        ui_fmt_type=ui_fmt_type,
        ui_log_level=ui_log_level,
        file_fmt_type=file_fmt_type,
        file_log_level=file_log_level,
        file_log_path=file_log_path,
        file_log_mode=file_log_mode,
    )

    # build command string to repeat this run, useful to remember default values
    # if an option is a flag this does not work (can't just copy/paste), sorry
    recap = "python3 sample_logger.py"
    for a, v in args._get_kwargs():
        recap += f" --{a} {v}"
    logg = logging.getLogger(f"c.{__name__}.setup_env")
    logg.info(recap)

    return args


def run_@BASENAME@(args: argparse.Namespace) -> None:
    r"""MAKEDOC: What is @BASENAME@ doing?

    Args:
        args: The parsed cmdline arguments.
    """
    logg = logging.getLogger(f"c.{__name__}.run_@BASENAME@")
    logg.setLevel("DEBUG")
    logg.debug("Starting run_@BASENAME@")


if __name__ == "__main__":
    args = setup_env()
    run_@BASENAME@(args)
