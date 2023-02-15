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
        self.parser_filepath = subp.add_parser("filepath", aliases=['f'], help='Directory to scan',
                                               )
        self.parser_filepath.add_argument(dest='filepath', help='', nargs='+')
        self.parser_volumes = subp.add_parser("volumes", aliases=['p'], help='Pvc to scan')
        self.parser_volumes.add_argument(dest='volumes', help='', nargs='+')

        self.parser_filepath.set_defaults(func=self.filepath_func)
        self.parser_volumes.set_defaults(func=self.volumes_func)
        self.parser.set_defaults(func=self.help_usage)

    def filepath_func(self, args):
        logger.write_to_log("INFO", f"Start to mount '{args.filepath}'")
        control.AntiVirus().mount_docker_file(args.filepath)
        control.AntiVirus().scan_directory()

    def volumes_func(self, args):
        logger.write_to_log("INFO", f"Start to mount '{args.volumes}'")
        control.AntiVirus().mount_docker_file(args.volumes)
        control.AntiVirus().scan_directory()

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
