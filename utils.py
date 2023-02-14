import subprocess
import socket
import sys
import time
import logging
import threading
import os
import yaml

LOG_PATH = os.getcwd() + '/Anti_virus.log'


def exec_cmd(cmd, timeout=60):
    p = subprocess.Popen(cmd, stderr=subprocess.STDOUT,
                         stdout=subprocess.PIPE, shell=True)
    t_beginning = time.time()
    seconds_passed = 0
    if timeout > 0:
        while True:
            if p.poll() is not None:
                break
            seconds_passed = time.time() - t_beginning
            if timeout and seconds_passed > timeout:
                p.terminate()
                raise TimeoutError(cmd, timeout)
            time.sleep(0.1)
    output = p.stdout.read().decode()
    return output


def get_hostname():
    hostname = socket.gethostname()
    return hostname


def get_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    finally:
        s.close()
    return ip


def get_auditobj():
    auditobj = "StorService"
    return auditobj


def get_proc():
    proc = "antivirus"
    return proc


class MyLoggerAdapter(logging.LoggerAdapter):
    """
    实现一个LoggerAdapter的子类，重写process()方法。
    其中对于kwargs参数的操作应该是先判断其本身是否包含extra关键字，如果包含则不使用默认值进行替换；
    如果kwargs参数中不包含extra关键字则取默认值。
    """
    extra_dict = {
        "host": "",
        "domain": "",
        "auditobj": "",
        "proc": "",
        "level": "",
        "msgdata": ""}

    def __init__(self, log_path):
        super().__init__(self.get_my_logger(log_path), self.extra_dict)

    def process(self, msg, kwargs):
        if 'extra' not in kwargs:
            kwargs["extra"] = self.extra
        return msg, kwargs

    def get_my_logger(self, log_path):
        handler_input = logging._handlers.RotatingFileHandler(filename=f'{log_path}',
                                                             mode='a',
                                                             maxBytes=10 * 1024 * 1024, backupCount=20)
        fmt = logging.Formatter(
            "%(asctime)s %(host)s %(domain)s %(auditobj)s %(proc)s: %(level)s %(msgdata)s",
            datefmt='%b %d %Y %H:%M:%S')
        handler_input.setFormatter(fmt)
        logger = logging.getLogger('vtel_logger')
        logger.addHandler(handler_input)
        logger.setLevel(logging.DEBUG)
        self.handler_input = handler_input
        return logger

    def remove_my_handler(self):
        # 可以考虑修改为异常处理
        if self.handler_input:
            self.logger.removeHandler(self.handler_input)


class Log(object):
    """
    日志格式：
    asctime：时间; 格式 Feb 01 2023 16:10:33
    host：hostname 主机名
    domain：域名 (目前 value 为主机 IP 地址)
    auditobj: 审计对象 (StorServer, StorServerBMC, Switch, StorDevice, VersaSDS, CosanManager, StorService)
    proc：进程名
    level：日志信息等级（EMERG, ALERT, CRIT, ERR, WARNING, NOTICE, INFO, DEBUG)
    msgdata：具体的message
    """
    _instance_lock = threading.Lock()
    host = None
    domain = None
    proc = None
    auditobj = None
    log_path = LOG_PATH
    log_switch = True
    logger = None

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '_instance'):
            with Log._instance_lock:
                if not hasattr(cls, '_instance'):
                    Log._instance = super().__new__(cls)
                    Log._instance.logger = MyLoggerAdapter(cls.log_path)

        return Log._instance

    # write to log file
    def write_to_log(self, level, msg):
        logger = Log._instance.logger

        # 获取到日志开关不为True时，移除处理器，不再将数据记录到文件中
        if not self.log_switch:
            logger.remove_my_handler()

        if not self.host:
            self.host = get_hostname()
        if not self.domain:
            self.domain = get_ip()
        if not self.auditobj:
            self.auditobj = get_auditobj()

        if not self.proc:
            self.proc = get_proc()

        logger.debug(
            "",
            extra={
                'host': self.host,
                'domain': self.domain,
                'auditobj': self.auditobj,
                'proc': self.proc,
                'level': level,
                'msgdata': msg})


class ConfFile(object):
    def __init__(self, file_path):
        self.file_path = file_path
        self.config = self.read_yaml()

    def read_yaml(self):
        """
        读yaml文件
        """
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                yaml_file = yaml.load(f, Loader=yaml.FullLoader)
            return yaml_file
        except FileNotFoundError:
            print("File not found")
        except TypeError:
            print("Error in the type of file .")

    def update_yaml(self, yaml_dict):
        """
        更新yaml文件
        """
        try:
            with open(self.file_path, 'w', encoding='utf-8') as f:
                yaml.dump(yaml_dict, f, default_flow_style=False)
        except FileNotFoundError:
            print("File not found")
        except TypeError:
            print("Error in the type of file .")

    def check_yaml(self):

        try:
            if self.config['spec']['containers']['volumeMounts']['mountPath'] is None:
                print("Please check whether the 'mountPath' are filled in yaml file")
                sys.exit()
            if self.config['spec']['volumes']['hostPath']['mountPath']['path'] is None:
                print("Please check whether the 'path' are filled in yaml file")
                sys.exit()
            if self.config['spec']['volumes']['hostPath']['persistentVolumeClaim']['myclaim'] is None:
                print("Please check whether the 'myclaim' are filled in yaml file")
                sys.exit()
        except KeyError as e:
            print(f"Missing configuration item {e}.")
            sys.exit()
