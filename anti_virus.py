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
        self.scan = subp.add_parser("virus_scan", aliases=['v'], help="Scan virus")
        self.scan.add_argument('-n',
                               '--nodeName',
                               dest='nodeName',
                               required=True,
                               action='store')
        self.scan.add_argument('-f',
                               '--filepath',
                               dest='filepath',
                               help='Scan the directory',
                               action='store')
        self.scan.add_argument('-p',
                               '--volumes',
                               dest='volumes',
                               help='Scan the PVC',
                               action='store')
        self.scan.add_argument('-r',
                               '--remove',
                               dest='remove',
                               help='Remove infected files',
                               action='store_true')
        self.scan.set_defaults(func=self.scan_func)
        self.parser.set_defaults(func=self.help_usage)

    def scan_func(self, args):
        if args.filepath:
            control.AntiVirus(filepath=args.filepath, remove=args.remove, node_name=args.nodeName)
        elif args.volumes:
            control.AntiVirus(claimname=args.volumes, remove=args.remove, node_name=args.nodeName)

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
