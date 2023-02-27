import sys
import action
import yaml
import re
import time
import utils
import os

logger = utils.Log()


class AntiVirus(object):
    def __init__(self, claimname=None, filepath=None, remove=''):
        self.pod_name_list = []
        self.container_name_list = []
        self.scan_directory_list = []
        self.claimname = claimname
        self.filepath = filepath
        self.filename = f'config_{int(round(time.time() * 1000))}'
        if claimname == None:
            self.mount_docker_file()
            self.scan_directory(remove)
        else:
            self.mount_docker_volume()
            self.scan_directory(remove)

    def mount_docker_volume(self):
        dict_yaml = {'apiVersion': 'v1',
                     'kind': 'Pod',
                     'metadata': {'name': 'clamav3'},
                     'spec': {'containers': [{'name': 'clamav3',
                                              'image': 'feixitek/clamav:2.0',
                                              'ports': [{'containerPort': 9009}],
                                              'volumeMounts': [{'name': 'logs-volume',
                                                                'mountPath': '/mnt'},
                                                               {'name': 'voluma',
                                                                'mountPath': '/data/definitions'}]}],
                              'volumes': [{'name': 'logs-volume',
                                           'persistentVolumeClaim': {'claimName': 'antivirus-pvc'}
                                           },
                                          {'name': 'voluma',
                                           'hostPath': {'path': '/root/clamav/database',
                                                        'type': 'Directory'}}
                                          ]
                              }
                     }
        action.create_yaml(self.filename, dict_yaml)
        print(f'Create yaml files：{self.filename}.yaml')
        logger.write_to_log("INFO", f'Create yaml files：{self.filename}.yaml')
        try:
            with open(os.getcwd() + f'/{self.filename}.yaml') as f:
                doc = yaml.load(f, Loader=yaml.FullLoader)
                doc['metadata']['name'] = f'clamb-{self.claimname}'
                doc['spec']['containers'][0]['name'] = f'clamb-{self.claimname}'
                doc['spec']['containers'][0]['volumeMounts'][0]['mountPath'] = f'/scan'
                doc['spec']['volumes'][0]['persistentVolumeClaim']['claimName'] = self.claimname
                logger.write_to_log('INFO',
                                    f'{self.filename}.yaml created successfully,volume_mount_path:/scan,claimName:{self.claimname}')
        except FileNotFoundError:
            print(f'WARNING：{self.filename}.yaml created failed')
            logger.write_to_log('WARNING', f'{self.filename}.yaml created failed')
            sys.exit()
        with open(os.getcwd() + f'/{self.filename}.yaml', 'w', encoding='utf-8') as f:
            yaml.dump(doc, f)
        print(f'Create pod: clamb-{self.claimname}')
        action.create_pod(f'{self.filename}.yaml')
        logger.write_to_log("INFO", f"Create pod: clamb-{self.claimname}")
        time.sleep(12)
        print(f'Check clamb-{self.claimname} status')
        result = action.check_pod(f'clamb-{self.claimname}')
        status = re.findall(fr'clamb-{self.claimname}+\s*\d*/\d*\s*([a-zA-Z]*)\s', result)
        if status[0] == 'Running':
            print(f'clamb-{self.claimname} is Running')
            pod_id = action.get_pid(f'clamb-{self.claimname}')
            logger.write_to_log('INFO', f'[{pod_id}]clamb-{self.claimname} is Running,PID is [{pod_id}]')
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
                                              'image': 'feixitek/clamav:2.0',
                                              'ports': [{'containerPort': 9009}],
                                              'volumeMounts': [{'name': 'logs-volume',
                                                                'mountPath': '/mnt'},
                                                               {'name': 'voluma',
                                                                'mountPath': '/data/definitions'}
                                                               ]}],
                              'volumes': [{'name': 'logs-volume',
                                           'hostPath': {'path': '/home/fxtadmin/fred_test',
                                                        'type': 'Directory'}
                                           },
                                          {'name': 'voluma',
                                           'hostPath': {'path': '/root/clamav/database',
                                                        'type': 'Directory'}}
                                          ]
                              }
                     }
        action.create_yaml(self.filename, dict_yaml)
        print(f'Create yaml for Pod：{self.filename}.yaml')
        logger.write_to_log("INFO", f'Create yaml for Pod：{self.filename}.yaml')
        try:
            with open(os.getcwd() + f'/{self.filename}.yaml') as f:
                doc = yaml.load(f, Loader=yaml.FullLoader)
                doc['metadata']['name'] = f'clamb-{self.filepath}'
                doc['spec']['containers'][0]['name'] = f'clamb-{self.filepath}'
                doc['spec']['containers'][0]['volumeMounts'][0]['mountPath'] = f'/scan'
                doc['spec']['volumes'][0]['hostPath']['path'] = self.filepath
                logger.write_to_log('INFO',
                                    f'{self.filename}.yaml created successfully,volume_mount_path:/scan,volumes_path:{self.filepath}')
        except FileNotFoundError:
            print(f'WARNING：{self.filename}.yaml created failed')
            logger.write_to_log('WARNING', f'{self.filename}.yaml created failed')
            sys.exit()
        with open(os.getcwd() + f'/{self.filename}.yaml', 'w', encoding='utf-8') as f:
            yaml.dump(doc, f)
        print(f'Create pod: clamb-{self.filepath}')
        action.create_pod(f'{self.filename}.yaml')
        logger.write_to_log("INFO", f"Create pod: clamb-{self.filepath}")
        time.sleep(12)
        print(f'Check clamb-{self.filepath} status')
        result = action.check_pod(f'clamb-{self.filepath}')
        status = re.findall(fr'clamb-{self.filepath}+\s*\d*/\d*\s*([a-zA-Z]*)\s', result)
        if status[0] == 'Running':
            pod_id = action.get_pid(f'clamb-{self.filepath}')
            print(f'clamb-{self.filepath} is Running')
            logger.write_to_log('INFO', f'[{pod_id}]clamb-{self.filepath} is Running,PID is [{pod_id}]')
            self.pod_name_list.append(f'clamb-{self.filepath}')
            self.scan_directory_list.append(f'/scan')
            self.container_name_list.append(f'clamb-{self.filepath}')
        else:
            action.delete_docker(f'clamb-{self.filepath}')
            print(f'WARNING:Please check clamb-{self.filepath} status,{self.filepath} stop disinfection')
            logger.write_to_log('WARNING',
                                f'Please check clamb-{self.filepath} status,{self.filepath} stop disinfection')
            sys.exit()

    def scan_directory(self, remove):
        if self.claimname == None:
            pod_id = action.get_pid(f'clamb-{self.filepath}')
            print(f'Scan the {self.filepath} ')
            logger.write_to_log("INFO", f'[{pod_id}]Start scanning the {self.filepath}')
        else:
            pod_id = action.get_pid(f'clamb-{self.claimname}')
            print(f'Scan the {self.claimname} ')
            logger.write_to_log("INFO", f'[{pod_id}]Scan the {self.claimname}')
        result = action.scanning(pod_name=self.pod_name_list[0],
                                 container_name=self.container_name_list[0],
                                 scan_directory=self.scan_directory_list[0],
                                 remove=remove)
        logger.write_to_log("INFO", f'[{pod_id}]Scan completely')
        print('Scan completely')
        print('----------------------Scan summary----------------------')
        file_list = re.findall(r'\/scan.*FOUND', result)
        for i in range(len(file_list)):
            if i >= 0:
                print(file_list[i])
                file1 = file_list[i].strip(': Eicar-Signature FOUND')
                logger.write_to_log('WARNING', f'{[pod_id]}Infected files:{file1}')
            else:
                pass
        known_viruses = re.findall(r'Known\s*viruses:\s*([0-9]+)', result)
        engine_version = re.findall(r'Engine\s*version:\s*([0-9]+.[0-9]+.[0-9])', result)
        scanned_directories = re.findall(r'Scanned\s*directories:\s*([0-9])', result)
        scanned_files = re.findall(r'Scanned\s*files:\s*([0-9])', result)
        infected_files = re.findall(r'Infected\s*files:\s*([0-9])', result)
        data_scanned = re.findall(r'Data\s*scanned:\s*([0-9]*.[0-9]*\s*[A-Z]*)', result)
        all_time = re.findall(r'Time:\s*([0-9]+.[0-9]+\s*[a-z]+)', result)
        start_date = re.findall(r'Start\s*Date:\s*([0-9]+:[0-9]+:[0-9]+\s*[0-9]+:[0-9]+:[0-9]+)', result)
        start_date1 = list(start_date[0])
        start_date1[4] = '-'
        start_date1[7] = '-'
        start_date2 = ''.join(start_date1)
        end_date = re.findall(r'End\s*Date:\s*([0-9]+:[0-9]+:[0-9]+\s*[0-9]+:[0-9]+:[0-9]+)', result)
        end_date1 = list(end_date[0])
        end_date1[4] = '-'
        end_date1[7] = '-'
        end_date2 = ''.join(end_date1)
        print(f'Scanned directories:{scanned_directories[0]}')
        print(f'Scanned files:{scanned_files[0]}')
        print(f'Infected files:{infected_files[0]}')
        print(f'Data scanned:{data_scanned[0]}')
        print(f'Time:{all_time[0]}')
        print(f'Start Date:{start_date2}')
        print(f'End Date:{end_date2}')
        print('----------------------------------------------------------')
        logger.write_to_log('INFO',
                            f'[{pod_id}]Sacn summary-Virus database：Known viruses:{known_viruses[0]},Engine version:{engine_version[0]}')
        for i in range(len(file_list)):
            if i >= 0:
                logger.write_to_log('WARNING',
                                    f'[{pod_id}]Scan summary-Task：Infected files:{infected_files[0]},'
                                    f'Scanned directories:{scanned_directories[0]},'
                                    f'Scanned files:{scanned_files[0]},'
                                    f'Data scanned:{data_scanned[0]},'
                                    f'Time:{all_time[0]},'
                                    f'Start Date:{start_date2},'
                                    f'End Date:{end_date2}')
            else:
                logger.write_to_log('INFO',
                                    f'[{pod_id}]Scan summary-Task：Infected files:{infected_files[0]},'
                                    f'Scanned directories:{scanned_directories[0]},'
                                    f'Scanned files:{scanned_files[0]},'
                                    f'Data scanned:{data_scanned[0]},'
                                    f'Time:{all_time[0]},'
                                    f'Start Date:{start_date2},'
                                    f'End Date:{end_date2}')
        for i in range(len(file_list)):
            if i >= 0 and remove == ' --remove':
                files = file_list[i].strip(': Eicar-Signature FOUND')
                print(f'Delete infected files:{files}')
                logger.write_to_log('INFO', f'[{pod_id}]Delete infected files:{files}')
                print(f'{files} deleted successfully')
                logger.write_to_log('INFO', f'[{pod_id}]{files} deleted successfully')
        print(f'Delete Pod:{self.pod_name_list[0]}')
        logger.write_to_log('INFO', f'[{pod_id}]Delete Pod:{self.pod_name_list[0]}')
        action.delete_docker(self.pod_name_list[0])
        logger.write_to_log('INFO', f'[{pod_id}]{self.pod_name_list[0]} deleted successfully')
        print(f'Delete yaml:{self.filename}.yaml')
        logger.write_to_log('INFO', f'[{pod_id}]Delete yaml:{self.filename}.yaml')
        action.delete_yaml(self.filename)
        logger.write_to_log('INFO', f'[{pod_id}]{self.filename}.yaml deleted successfully')
