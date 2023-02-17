import sys
import action
import yaml
import re
import time
import os
import utils

logger = utils.Log()


class AntiVirus(object):
    def __init__(self, claimname=None, filepath=None):
        self.pod_name_list = []
        self.container_name_list = []
        self.scan_directory_list = []
        self.claimname = claimname
        self.filepath = filepath
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
        filename = f'config_{int(round(time.time() * 1000))}'
        action.create_yaml(filename, dict_yaml)
        print(f'Create yaml for Pod：{filename}.yaml')
        #logger.write_to_log("INFO", f"Create yaml: config{i}.yaml")
        with open(f'{filename}.yaml') as f:
            doc = yaml.load(f, Loader=yaml.FullLoader)
        doc['metadata']['name'] = f'clamb-{self.claimname}'
        doc['spec']['containers'][0]['name'] = f'clamb-{self.claimname}'
        doc['spec']['containers'][0]['volumeMounts'][0]['mountPath'] = f'/scan'
        doc['spec']['volumes'][0]['persistentVolumeClaim']['claimName'] = self.claimname
        with open(f'{filename}.yaml', 'w', encoding='utf-8') as f:
            yaml.dump(doc, f)
        print(f'Start create pod: clamb-{self.claimname}')
        action.create_pod(f'{filename}.yaml')
        logger.write_to_log("INFO", f"Create pod: clamb-{self.claimname}")
        time.sleep(8)
        print(f'Checking clamb-{self.claimname} status')
        result = action.check_pod(f'clamb-{self.claimname}')
        status = re.findall(r'clamb[0-9]+\s*\d*/\d*\s*([a-zA-Z]*)\s', result)
        if status[0] == 'Running':
            print(f'clamb-{self.claimname} is Running')
            self.pod_name_list.append(f'clamb-{self.claimname}')
            self.scan_directory_list.append(f'/scan')
            self.container_name_list.append(f'clamb-{self.claimname}')
        else:
            action.delete_docker(f'clamb-{self.claimname}')
            print(f'Please check clamb-{self.claimname} status')
            sys.exit()

    def mount_docker_file(self):
        dict_yaml = {'apiVersion': 'v1',
                     'kind': 'Pod',
                     'metadata': {'name': 'clamav3'},
                     'spec': {'containers': [{'name': 'clamav3',
                                              'image': 'tiredofit/clamav:2.5.3',
                                              'ports': [{'containerPort': 9009}],
                                              'volumeMounts': {'name': 'logs-volume',
                                                               'mountPath': '/mnt'}}],
                              'volumes': [{'name': 'logs-volume',
                                           'hostPath': {'path': '/home/fxtadmin/fred_test',
                                                        'type': 'Directory'}
                                           }
                                          ]
                              }
                     }
        filename = f'config_{int(round(time.time() * 1000))}'
        action.create_yaml(filename, dict_yaml)
        print(f'Create yaml for Pod：{filename}')
        #logger.write_to_log("INFO", f"Create yaml: config{i}.yaml")
        with open(f'{filename}.yaml') as f:
            doc = yaml.load(f, Loader=yaml.FullLoader)
            doc['metadata']['name'] = f'clamb-{self.filepath}'
            doc['spec']['containers'][0]['name'] = f'clamb-{self.filepath}'
            doc['spec']['containers'][0]['volumeMounts'][0]['mountPath'] = f'/scan'
            doc['spec']['volumes'][0]['hostPath']['path'] = self.filepath
            with open(f'{filename}.yaml', 'w', encoding='utf-8') as f:
                yaml.dump(doc, f)
            print(f'Start create pod: clamb-{self.filepath}')
            action.create_pod(f'{filename}.yaml')
            logger.write_to_log("INFO", f"Create pod: clamb-{self.filepath}")
            time.sleep(8)
            print(f'Checking clamb-{self.filepath} status')
            result = action.check_pod(f'clamb-{self.filepath}')
            status = re.findall(r'clamb[0-9]+\s*\d*/\d*\s*([a-zA-Z]*)\s', result)
            if status[0] == 'Running':
                print(f'clamb-{self.filepath} is Running')
                self.pod_name_list.append(f'clamb-{self.filepath}')
                self.scan_directory_list.append(f'/scan')
                self.container_name_list.append(f'clamb-{self.filepath}')
            else:
                action.delete_docker(f'clamb-{self.filepath}')
                print(f'Please check clamb-{self.filepath} status')
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
        engine_version = re.findall(r'Engine\s*version:\s*([0-9]+.[0-9]+.[0-9])', result)
        logger.write_to_log("INFO", f"Engine version:{engine_version[0]}")
        scanned_directories = re.findall(r'Scanned\s*directories:\s*([0-9])', result)
        logger.write_to_log("INFO", f"Scanned directories:{scanned_directories[0]}")
        scanned_files = re.findall(r'Scanned\s*files:\s*([0-9])', result)
        logger.write_to_log("INFO", f"Scanned files:{scanned_files[0]}")
        infected_files = re.findall(r'Infected\s*files:\s*([0-9])', result)
        logger.write_to_log("INFO", f"Infected files:{infected_files[0]}")
        all_time = re.findall(r'Time:\s*([0-9]+.[0-9]+\s*[a-z]+)', result)
        logger.write_to_log("INFO", f"Time:{all_time[0]}")
        start_date = re.findall(r'Start\s*Date:\s*([0-9]+:[0-9]+:[0-9]+\s*[0-9]+:[0-9]+:[0-9]+)', result)
        logger.write_to_log("INFO", f"Start Date:{start_date[0]}")
        end_date = re.findall(r'End\s*Date:\s*([0-9]+:[0-9]+:[0-9]+\s*[0-9]+:[0-9]+:[0-9]+)', result)
        logger.write_to_log("INFO", f"End Date:{end_date[0]}")
        logger.write_to_log("INFO", 'Scan completely')
        time.sleep(1)
        print('All directories are scanned')
        time.sleep(1)
        print('Start deleting containers')



if __name__ == '__main__':
    anti = AntiVirus()
    anti.mount_docker_volume(['test-pvc'])
    anti.scan_directory()
