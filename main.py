# -*- coding:utf-8 -*-
import argparse
import sys

import control
import utils

logger = utils.Log()


class InputParser(object):

    def __init__(self):
        self.parser = argparse.ArgumentParser(description="Antivirus tools")
        self.setup_parser()
        self.conf_args = {}

    def setup_parser(self):
        subp = self.parser.add_subparsers(metavar='', dest='subargs_basic')
        self.parser.add_argument('-v',
                                 '--version',
                                 dest='version',
                                 help='Show current version',
                                 action='store_true')

        self.parser_filepath = subp.add_parser("filepath", aliases=['f'], help="Directory to scan")
        self.parser_filepath.add_argument('-f',
                                       '--filepath',
                                       dest='filepath',
                                       help='file to scan',
                                       action='store')
        self.parser_volumes = subp.add_parser("volumes", aliases=['v'], help="Pvc to scan")
        self.parser_volumes.add_argument('-p',
                                       '--pcv',
                                       dest='pvc',
                                       help='pvc to scan',
                                       action='store')

        self.parser_filepath.set_defaults(func=self.filepath_func)
        self.parser_volumes.set_defaults(func=self.volumes_func)
        self.parser.set_defaults(func=self.help_usage)

    def filepath_func(self, args):
        logger.write_to_log("INFO", f"Start to mount '{args.filepath}'")
        control.AntiVirus().mount_docker_file(args.filepath)

    def volumes_func(self, args):
        logger.write_to_log("INFO", f"Start to mount '{args.pvc}'")
        control.AntiVirus().mount_docker_file(args.pvc)

    def help_usage(self, args):
        if args.version:
            print(f'Version: {consts.VERSION}')
        else:
            self.parser.print_help()

    def parse(self):  # 调用入口
        args = self.parser.parse_args()
        args.func(args)


def main():
    try:
        run_program = InputParser()
        run_program.parse()
    except KeyboardInterrupt:
        sys.stderr.write("\nClient exiting (received SIGINT)\n")


if __name__ == '__main__':
    main()
