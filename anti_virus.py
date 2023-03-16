# -*- coding:utf-8 -*-
import argparse
import sys
import control
import utils

logger = utils.Log()


class InputParser(object):

    def __init__(self):
        self.parser = argparse.ArgumentParser(description="杀毒工具")
        self.setup_parser()
        self.conf_args = {}

    def setup_parser(self):
        subp = self.parser.add_subparsers(metavar='', dest='subargs_basic')
        self.parser.add_argument('-v',
                                 '--version',
                                 dest='version',
                                 help='Show current version',
                                 action='store_true')
        self.scan = subp.add_parser("virus_scan", aliases=['v'], help="扫描病毒功能")
        self.scan.add_argument('-n',
                               '--nodeName',
                               dest='nodeName',
                               required=True,
                               help='选择运行杀毒程序的节点',
                               action='store')
        self.scan.add_argument('-f',
                               '--filepath',
                               dest='filepath',
                               help='扫描目录或者文件',
                               action='store')
        self.scan.add_argument('-p',
                               '--volumes',
                               dest='volumes',
                               help='扫描PVC',
                               action='store')
        self.scan.add_argument('-r',
                               '--remove',
                               dest='remove',
                               help='删除感染文件',
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
