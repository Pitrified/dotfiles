import argparse
import logging

import numpy as np

from random import seed
from timeit import default_timer as timer

def parse_arguments():
    '''Setup CLI interface
    '''
    parser = argparse.ArgumentParser(
            description='@CURSOR@',
            )

    parser.add_argument('-i', "--input_path",
            type=str,
            default='hp.jpg',
            help="path to input image to use")

    parser.add_argument('-s', "--seed",
            type=int,
            default=-1,
            help="random seed to use")

    # last line to parse the args
    args = parser.parse_args()
    return args

def setup_logger(logLevel='DEBUG'):
    '''Setup logger that outputs to console for the module
    '''
    logmoduleconsole = logging.getLogger(f'{__name__}.console')
    logmoduleconsole.propagate = False
    logmoduleconsole.setLevel(logLevel)

    module_console_handler = logging.StreamHandler()

    #  log_format_module = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    log_format_module = '%(name)s - %(levelname)s: %(message)s'
    #  log_format_module = '%(levelname)s: %(message)s'
    formatter = logging.Formatter(log_format_module)
    module_console_handler.setFormatter(formatter)

    logmoduleconsole.addHandler(module_console_handler)

    logging.addLevelName(5, 'TRACE')
    # use it like this
    # logmoduleconsole.log(5, 'Exceedingly verbose debug')

    return logmoduleconsole

def main():
    args = parse_arguments()

    # setup seed value
    if args.seed == -1:
        myseed = 1
        myseed = int( timer() * 1e9 % 2**32 )
    else:
        myseed = args.seed
    seed(myseed)
    np.random.seed(myseed)

    path_input = args.input_path

    logmoduleconsole = setup_logger()

    logmoduleconsole.info(f'python3 @BASENAME@.py -s {myseed} -i {path_input}')

if __name__ == '__main__':
    main()
