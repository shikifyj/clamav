import sys
import action
import yaml
import re
import time
import os

import utils

logger = utils.Log()


class AntiVirus(object):
    def __init__(self):
        self.pod_name_list = []
        self.container_name_list = []
        self.scan_directory_list = []
        self.log_directory = os.getcwd() + '/Anti_virus.log'
        self.scan_directory()

    def mount_docker_volume(self, claimname_list):
        status_list = []
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
        for i in range(len(claimname_list)):
            filename = f'config{i}'
            action.create_yaml(filename, dict_yaml)
            logger.write_to_log("INFO", f"create yaml--config{i}.yaml")
        for i in range(len(claimname_list)):
            with open(f'config{i}.yaml') as f:
                doc = yaml.load(f, Loader=yaml.FullLoader)
            doc['metadata']['name'] = f'clamb{i}'
            doc['spec']['containers'][0]['name'] = f'clamb{i}'
            doc['spec']['containers'][0]['volumeMounts'][0]['mountPath'] = f'/scana{i}'
            doc['spec']['volumes'][0]['persistentVolumeClaim']['claimName'] = claimname_list[i]
            with open(f'config{i}.yaml', 'w', encoding='utf-8') as f:
                yaml.dump(doc, f)
            print(f'star create pod --clamb{i}')
            action.create_pod(f'config{i}.yaml')
            logger.write_to_log("INFO", f"create pod--clamb{i}")
            time.sleep(5)
            print('Checking pod status')
        #     result = action.check_pod(f'clamb{i}')
        #     status = re.findall(r'clamb\s*\d*/\d*\s*([a-zA-Z]*)\s', result)
        #     status_list.append(status)
        # for i in range(len(status_list)):
        #     if status_list[i] == 'Running':
        #         print('Pod is Running')
        #         self.pod_name_list.append(f'clamb{i}')
            self.scan_directory_list.append(f'/scana{i}')
            self.container_name_list.append(f'clamb{i}')
        #     else:
        #         print('Please check pod')
        #         sys.exit()

    def mount_docker_file(self, path_list):
        status_list = []
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
        for i in range(len(path_list)):
            filename = f'config{i}'
            action.create_yaml(filename, dict_yaml)
        for i in range(len(path_list)):
            with open(f'config{i}.yaml') as f:
                doc = yaml.load(f, Loader=yaml.FullLoader)
            doc['metadata']['name'] = f'clamb{i}'
            doc['spec']['containers'][0]['name'] = f'clamb{i}'
            doc['spec']['containers'][0]['volumeMounts'][0]['mountPath'] = f'/scana{i}'
            doc['spec']['volumes'][0]['hostPath']['path'] = path_list[i]
            with open(f'config{i}.yaml', 'w', encoding='utf-8') as f:
                yaml.dump(doc, f)
            print(f'Start create pod --clamb{i}')
            action.create_pod(f'config{i}.yaml')
            result = action.check_pod(f'clamb{i}')
            time.sleep(2)
            status = re.findall(r'clamb\s*\d*/\d*\s*([a-zA-Z]*)\s', result)
            status_list.append(status)
        for i in range(len(status_list)):
            if status_list[i] == 'Running':
                self.pod_name_list.append(f'clamb{i}')
                self.scan_directory_list.append(f'/scana{i}')
                self.container_name_list.append(f'clamb{i}')
                print('Pod is Running')
            else:
                print('Please check pod')

    def scan_directory(self):
        for i in range(len(self.pod_name_list)):
            print(f'Start scanning the directory--/scana{i} ')
            result = action.scanning(pod_name=self.pod_name_list[i],
                            container_name=self.container_name_list[i],
                            scan_directory=self.scan_directory_list[i],
                            log_directory=self.log_directory)
            logger.write_to_log("INFO", f"scan result{result}")

if __name__ == '__main__':
    anti = AntiVirus()
    anti.mount_docker_volume(['test-pvc'])