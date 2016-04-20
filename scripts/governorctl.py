#!/usr/bin/env python
from governor import governor, helpers
import sys, yaml, argparse, logging

import os.path

class LogLevelAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, logging.getLevelName(values.upper()))

def is_valid_file(parser, arg):
    if not os.path.exists(arg):
        parser.error("The file '{}' does not exist!".format(arg))

    with open(arg, "r") as f:
        return yaml.load(f.read())

def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("config",
                        metavar="file",
                        default="postgres.yml",
                        type=lambda x: is_valid_file(parser, x),
                        help="location of the configuration file",
                        nargs='?')
    parser.add_argument("--log-level",
                        help="set the log level",
                        dest="log_level",
                        default=logging.DEBUG,
                        choices=['debug', 'info', 'warning', 'error', 'critical'],
                        action=LogLevelAction)
    args = parser.parse_args()
    return args

def main():
    args = parse_arguments()
    logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s', level=args.log_level)
    governor.run(args.config)

if __name__ == "__main__":
    main()
