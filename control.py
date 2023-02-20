import sys
import action
import yaml
import re
import time
import utils
import os

logger = utils.Log()


class AntiVirus(object):
    def __init__(self, claimname=None, filepath=None):
        self.pod_name_list = []
        self.container_name_list = []
        self.scan_directory_list = []
        self.claimname = claimname
        self.filepath = filepath
        self.filename = f'config_{int(round(time.time() * 1000))}'
        if claimname == None:
            self.mount_docker_file()
            self.scan_directory()
        else:
            self.mount_docker_volume()
            self.scan_directory()

    def mount_docker_volume(self):
        dict_yaml = {'apiVersion': 'v1',
                     'kind': 'Pod',
                     'metadata': {'name': 'clamav3'},
                     'spec': {'containers': [{'name': 'clamav3',
                                              'image': 'tiredofit/clamav:2.5.3',
                                              'ports': [{'containerPort': 9009}],
                                              'volumeMounts': [{'name': 'logs-volume',
                                                                'mountPath': '/mnt'}]}],
                              'volumes': [{'name': 'logs-volume',
                                           'persistentVolumeClaim': {'claimName': 'antivirus-pvc'}
                                           }
                                          ]
                              }
                     }
        action.create_yaml(self.filename, dict_yaml)
        print(f'Create yaml for Pod：{self.filename}.yaml')
        logger.write_to_log("INFO", f'Create yaml for Pod：{self.filename}.yaml')
        try:
            with open(os.getcwd() + f'/{self.filename}.yaml') as f:
                logger.write_to_log('INFO', f'{self.filename}.yaml created successfully')
                doc = yaml.load(f, Loader=yaml.FullLoader)
                doc['metadata']['name'] = f'clamb-{self.claimname}'
                doc['spec']['containers'][0]['name'] = f'clamb-{self.claimname}'
                doc['spec']['containers'][0]['volumeMounts'][0]['mountPath'] = f'/scan'
                doc['spec']['volumes'][0]['persistentVolumeClaim']['claimName'] = self.claimname
        except FileNotFoundError:
            print(f'WARNING：{self.filename}.yaml created failed')
            logger.write_to_log('WARNING', f'{self.filename}.yaml created failed')
            sys.exit()
        with open(os.getcwd() + f'/{self.filename}.yaml', 'w', encoding='utf-8') as f:
            yaml.dump(doc, f)
        print(f'Start create pod: clamb-{self.claimname}')
        action.create_pod(f'{self.filename}.yaml')
        logger.write_to_log("INFO", f"Create pod: clamb-{self.claimname}")
        time.sleep(8)
        print(f'Checking clamb-{self.claimname} status')
        result = action.check_pod(f'clamb-{self.claimname}')
        status = re.findall(fr'clamb-{self.claimname}+\s*\d*/\d*\s*([a-zA-Z]*)\s', result)
        if status[0] == 'Running':
            print(f'clamb-{self.claimname} is Running')
            pod_id = action.get_pid(f'clamb-{self.claimname}')
            print(pod_id)
            logger.write_to_log('INFO', f'clamb-{self.claimname} is Running')
            self.pod_name_list.append(f'clamb-{self.claimname}')
            self.scan_directory_list.append(f'/scan')
            self.container_name_list.append(f'clamb-{self.claimname}')
        else:
            action.delete_docker(f'clamb-{self.claimname}')
            print(f'WARNING:Please check clamb-{self.claimname} status,{self.claimname} stop disinfection')
            logger.write_to_log('WARNING',
                                f'Please check clamb-{self.claimname} status,{self.claimname} stop disinfection')
            sys.exit()

    def mount_docker_file(self):
        dict_yaml = {'apiVersion': 'v1',
                     'kind': 'Pod',
                     'metadata': {'name': 'clamav3'},
                     'spec': {'containers': [{'name': 'clamav3',
                                              'image': 'tiredofit/clamav:2.5.3',
                                              'ports': [{'containerPort': 9009}],
                                              'volumeMounts': [{'name': 'logs-volume',
                                                                'mountPath': '/mnt'}]}],
                              'volumes': [{'name': 'logs-volume',
                                           'hostPath': {'path': '/home/fxtadmin/fred_test',
                                                        'type': 'Directory'}
                                           }
                                          ]
                              }
                     }
        action.create_yaml(self.filename, dict_yaml)
        print(f'Create yaml for Pod：{self.filename}.yaml')
        logger.write_to_log("INFO", f'Create yaml for Pod：{self.filename}.yaml')
        try:
            with open(os.getcwd() + f'/{self.filename}.yaml') as f:
                logger.write_to_log('INFO', f'{self.filename}.yaml created successfully')
                doc = yaml.load(f, Loader=yaml.FullLoader)
                doc['metadata']['name'] = f'clamb-{self.filepath}'
                doc['spec']['containers'][0]['name'] = f'clamb-{self.filepath}'
                doc['spec']['containers'][0]['volumeMounts'][0]['mountPath'] = f'/scan'
                doc['spec']['volumes'][0]['hostPath']['path'] = self.filepath
        except FileNotFoundError:
            print(f'WARNING：{self.filename}.yaml created failed')
            logger.write_to_log('WARNING', f'{self.filename}.yaml created failed')
            sys.exit()
        with open(os.getcwd() + f'/{self.filename}.yaml', 'w', encoding='utf-8') as f:
            yaml.dump(doc, f)
        print(f'Start create pod: clamb-{self.filepath}')
        action.create_pod(f'{self.filename}.yaml')
        logger.write_to_log("INFO", f"Create pod: clamb-{self.filepath}")
        time.sleep(8)
        print(f'Checking clamb-{self.filepath} status')
        result = action.check_pod(f'clamb-{self.filepath}')
        status = re.findall(fr'clamb-{self.filepath}+\s*\d*/\d*\s*([a-zA-Z]*)\s', result)
        if status[0] == 'Running':
            print(f'clamb-{self.filepath} is Running')
            logger.write_to_log('INFO', f'clamb-{self.filepath} is Running')
            self.pod_name_list.append(f'clamb-{self.filepath}')
            self.scan_directory_list.append(f'/scan')
            self.container_name_list.append(f'clamb-{self.filepath}')
        else:
            action.delete_docker(f'clamb-{self.filepath}')
            print(f'WARNING:Please check clamb-{self.filepath} status,{self.filepath} stop disinfection')
            logger.write_to_log('WARNING',
                                f'Please check clamb-{self.filepath} status,{self.filepath} stop disinfection')
            sys.exit()

    def scan_directory(self):
        if self.claimname == None:
            print(f'Start scanning the {self.filepath} ')
            logger.write_to_log("INFO", f'Start scanning the {self.filepath}')
        else:
            print(f'Start scanning the {self.claimname} ')
            logger.write_to_log("INFO", f'Start scanning the {self.claimname}')
        result = action.scanning(pod_name=self.pod_name_list[0],
                                 container_name=self.container_name_list[0],
                                 scan_directory=self.scan_directory_list[0])
        logger.write_to_log("INFO", 'Scan completely')
        print('Scan completely')
        print('----------------------Scan summary----------------------')
        known_viruses = re.findall(r'Known\s*viruses:\s*([0-9]+)')
        engine_version = re.findall(r'Engine\s*version:\s*([0-9]+.[0-9]+.[0-9])', result)
        scanned_directories = re.findall(r'Scanned\s*directories:\s*([0-9])', result)
        scanned_files = re.findall(r'Scanned\s*files:\s*([0-9])', result)
        infected_files = re.findall(r'Infected\s*files:\s*([0-9])', result)
        data_scanned = re.findall(r'Data\s*scanned:\s*([0-9]*.[0-9]*\s*[A-Z]*)')
        all_time = re.findall(r'Time:\s*([0-9]+.[0-9]+\s*[a-z]+)', result)
        start_date = re.findall(r'Start\s*Date:\s*([0-9]+:[0-9]+:[0-9]+\s*[0-9]+:[0-9]+:[0-9]+)', result)
        end_date = re.findall(r'End\s*Date:\s*([0-9]+:[0-9]+:[0-9]+\s*[0-9]+:[0-9]+:[0-9]+)', result)
        print(f'Scanned directories:{scanned_directories}')
        print(f'Scanned files:{scanned_files}')
        print(f'Infected files:{infected_files}')
        print(f'Data scanned:{data_scanned}')
        print(f'Time:{all_time} sec')
        print(f'Start Date:{start_date}')
        print(f'End Date:{end_date}')
        logger.write_to_log('INFO',
                            f'Sacn summary-Virus database：Known viruses:{known_viruses},Engine version:{engine_version}')
        logger.write_to_log('INFO',
                            f'Scan summary-Task：Infected files:{infected_files},Scanned directories:{scanned_directories},Scanned files:{scanned_files},Data scanned:{data_scanned},Time:{all_time} sec,Start Date:{start_date},End Date:{end_date}')
        print(f'Start deleting Pod:{self.pod_name_list[0]}')
        logger.write_to_log('INFO', f'Start deleting Pod:{self.pod_name_list[0]}')
        action.delete_docker(self.pod_name_list[0])
        logger.write_to_log('INFO', f'{self.pod_name_list[0]} deleted successfully')
        print(f'Start deleting yaml:{self.filename}.yaml')
        logger.write_to_log('INFO', f'Start deleting yaml:{self.filename}.yaml')
        logger.write_to_log('INFO', f'{self.filename}.yaml deleted successfully')

if __name__ == '__main__':
    anti = AntiVirus()
    anti.mount_docker_volume(['test-pvc'])
    anti.scan_directory()
