import sys
import action
import yaml
import re
import time
import utils
import os

logger = utils.Log()


class AntiVirus(object):
    def __init__(self, remove, claimname=None, filepath=None, node_name=None):
        if remove:
            remove = ' --remove'
        else:
            remove = ''
        self.pod_name_list = []
        self.container_name_list = []
        self.scan_directory_list = []
        self.claimname = claimname
        self.filepath = filepath
        self.node_name = node_name
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
                     'spec': {'nodeName': '',
                              'containers': [{'name': 'clamav3',
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
        node_result = action.get_node()
        if self.node_name in node_result:
            action.create_yaml(self.filename, dict_yaml)
            # print(f'Create yaml files:{self.filename}.yaml')
            logger.write_to_log("INFO", f'Create yaml files:{self.filename}.yaml')
            try:
                with open(os.getcwd() + f'/{self.filename}.yaml') as f:
                    doc = yaml.load(f, Loader=yaml.FullLoader)
                    doc['metadata']['name'] = f'clamb-{self.claimname}'
                    doc['spec']['containers'][0]['name'] = f'clamb-{self.claimname}'
                    doc['spec']['containers'][0]['volumeMounts'][0]['mountPath'] = f'/scan'
                    doc['spec']['volumes'][0]['persistentVolumeClaim']['claimName'] = self.claimname
                    doc['spec']['nodeName'] = self.node_name
                    logger.write_to_log('INFO',
                                        f'{self.filename}.yaml created successfully,volume_mount_path:/scan,'
                                        f'claimName:{self.claimname}')
            except FileNotFoundError:
                print(f'WARNING:{self.filename}.yaml created failed')
                logger.write_to_log('WARNING', f'{self.filename}.yaml created failed')
                sys.exit()
            with open(os.getcwd() + f'/{self.filename}.yaml', 'w', encoding='utf-8') as f:
                yaml.dump(doc, f)
            pod_status = action.create_pod(f'{self.filename}.yaml')
            logger.write_to_log("INFO", f"Create pod: clamb-{self.claimname}")
            time.sleep(2)
            result = action.check_pod(f'clamb-{self.claimname}')
            if 'created' in pod_status:
                max_time = time.time() + 30
                print(f'Check Pod: clamb-{self.claimname} status')
                while time.time() < max_time:
                    status = re.findall(fr'clamb-{self.claimname}+\s*\d*/\d*\s*([a-zA-Z]*)\s', result)
                    if status[0] == 'Running':
                        break
                else:
                    action.delete_docker(f'clamb-{self.claimname}')
                    print(f'WARNING:Pod:clamb-{self.claimname} status is {status[0]},{self.claimname} stop to scan')
                    logger.write_to_log('WARNING',
                                        f'Because Pod:clamb-{self.claimname} status is {status[0]},'
                                        f'PVC:{self.claimname} scan failed', True)
                    sys.exit()
                node = re.findall(r'\.[0-9]+\s+([\w]+)\s', result)
                print(f"Pod:clamb-{self.claimname} run on {node[0]}")
                logger.write_to_log("INFO", f"Pod:clamb-{self.claimname} run on {node[0]}")
                print(f'clamb-{self.claimname} is Running')
                pod_id = action.get_pid(f'clamb-{self.claimname}')
                logger.write_to_log('INFO',
                                    f'[{pod_id}]clamb-{self.claimname} is Running, containerID is [{pod_id}]')
                self.pod_name_list.append(f'clamb-{self.claimname}')
                self.scan_directory_list.append(f'/scan')
                self.container_name_list.append(f'clamb-{self.claimname}')
            else:
                print(f'WARING:Pod:clamb-{self.claimname} created failed')
                logger.write_to_log("WARING", f"Because Pod:clamb-{self.claimname} created failed,"
                                              f"PVC:{self.claimname} scan failed", True)
                sys.exit()
        else:
            print(f'WARING:The node:{self.node_name} does not exist, please respecify the node')
            logger.write_to_log('WARNING',
                                f'The node:{self.node_name} does not exist,'
                                f'PVC:{self.claimname} scan failed', True)
            sys.exit()

    def mount_docker_file(self):
        dict_yaml = {'apiVersion': 'v1',
                     'kind': 'Pod',
                     'metadata': {'name': 'clamav3'},
                     'spec': {'nodeName': '',
                              'containers': [{'name': 'clamav3',
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
        node_result = action.get_node()
        if self.node_name in node_result:
            action.create_yaml(self.filename, dict_yaml)
            # print(f'Create yaml for Pod:{self.filename}.yaml')
            logger.write_to_log("INFO", f'Create yaml:{self.filename}.yaml')
            pod_name = f'clamb{self.filepath}'.replace('/', '-')
            try:
                with open(os.getcwd() + f'/{self.filename}.yaml') as f:
                    doc = yaml.load(f, Loader=yaml.FullLoader)
                    doc['metadata']['name'] = pod_name
                    doc['spec']['containers'][0]['name'] = pod_name
                    doc['spec']['containers'][0]['volumeMounts'][0]['mountPath'] = f'/scan'
                    doc['spec']['volumes'][0]['hostPath']['path'] = self.filepath
                    doc['spec']['nodeName'] = self.node_name
                    logger.write_to_log('INFO',
                                        f'{self.filename}.yaml created successfully,volume_mount_path:/scan,'
                                        f'volumes_path:{self.filepath}')
            except FileNotFoundError:
                print(f'WARNING:{self.filename}.yaml created failed')
                logger.write_to_log('WARNING', f'{self.filename}.yaml created failed')
                sys.exit()
            with open(os.getcwd() + f'/{self.filename}.yaml', 'w', encoding='utf-8') as f:
                yaml.dump(doc, f)
            # print(f'Create pod: clamb-{self.filepath}')
            pod_status = action.create_pod(f'{self.filename}.yaml')
            logger.write_to_log("INFO", f"Create pod:{pod_name}")
            time.sleep(12)
            result = action.check_pod(f'{pod_name}')
            if 'created' in pod_status:
                print(f'Check Pod:{pod_name} status')
                status = re.findall(fr'{pod_name}+\s*\d*/\d*\s*([a-zA-Z]*)\s', result)
                if status[0] == 'Running':
                    node = re.findall(r'\.[0-9]+\s+([\w]+)\s', result)
                    print(f"Pod:{pod_name} run on {node[0]}")
                    logger.write_to_log("INFO", f"Pod:{pod_name} run on {node[0]}")
                    pod_id = action.get_pid(f'{pod_name}')
                    print(f'{pod_name} is Running')
                    logger.write_to_log('INFO', f'[{pod_id}]{pod_name} is Running,containerID is [{pod_id}]')
                    self.pod_name_list.append(f'{pod_name}')
                    self.scan_directory_list.append(f'/scan')
                    self.container_name_list.append(f'{pod_name}')
                else:
                    action.delete_docker(f'clamb-{self.filepath}')
                    print(f'WARNING:Pod:{pod_name} status is {status[0]},{self.filepath} stop to scan')
                    logger.write_to_log('WARNING',
                                        f'Because Pod:{pod_name} status is {status[0]},'
                                        f'{self.filepath} scan failed', True)
                    sys.exit()
            else:
                print(f'WARING:Pod:{pod_name} created failed')
                logger.write_to_log("WARING", f"Because Pod:{pod_name} created failed,"
                                              f"{self.filepath} scan failed", True)
                sys.exit()
        else:
            print(f'WARING:The node:{self.node_name} does not exist, please respecify the node')
            logger.write_to_log('WARNING',
                                f'The node:{self.node_name} does not exist,'
                                f'PVC:{self.claimname} scan failed', True)
            sys.exit()

    def scan_directory(self, remove):
        if self.claimname == None:
            pod_id = action.get_pid(f'clamb-{self.filepath}'.replace('/', '-'))
            print(f'Scan the {self.filepath} ')
            logger.write_to_log("INFO", f'[{pod_id}]Scan the {self.filepath}', True)
        else:
            pod_id = action.get_pid(f'clamb-{self.claimname}')
            print(f'Scan the {self.claimname} ')
            logger.write_to_log("INFO", f'[{pod_id}]Scan the {self.claimname}', True)
        result = action.scanning(pod_name=self.pod_name_list[0],
                                 container_name=self.container_name_list[0],
                                 scan_directory=self.scan_directory_list[0],
                                 remove=remove)
        logger.write_to_log("INFO", f'[{pod_id}]Scan completely', True)
        print('Scan completely')
        file_list = re.findall(r'\/scan.*FOUND', result)
        for i in range(len(file_list)):
            if i >= 0:
                file1 = re.findall(r'/scan.*:', file_list[i])[0].strip(':').replace('/scan', '')
                if self.claimname == None:
                    str2 = f'{[pod_id]}Infected files:{self.filepath}{file1}'.replace("'", '')
                    logger.write_to_log('WARNING', f'{str2}', True)
                else:
                    str1 = f'{[pod_id]}Infected files:{self.claimname}{file1}'.replace("'", '')
                    logger.write_to_log('WARNING', f'{str1}', True)
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
        logger.write_to_log('INFO',
                            f'[{pod_id}]Sacn summary-Virus database:Known viruses:{known_viruses[0]},'
                            f'Engine version:{engine_version[0]}', True)
        if len(file_list) > 0:
            files_list = []
            virus_list = []
            print_table = utils.Table()
            logger.write_to_log('WARNING',
                                f'[{pod_id}]Scan summary-Task:Infected files:{infected_files[0]},'
                                f'Scanned directories:{scanned_directories[0]},'
                                f'Scanned files:{scanned_files[0]},'
                                f'Data scanned:{data_scanned[0]},'
                                f'Time:{all_time[0]},'
                                f'Start Date:{start_date2},'
                                f'End Date:{end_date2}', True)
            print('------------------------------------SCAN SUMMARY----------------------------------------')
            print(f'WARNING: Scan summary- {infected_files[0]} infected files found')
            print(
                f'Scan summary-Virus database:Known viruses:{known_viruses[0]},Engine version:{engine_version[0]}')
            print(
                f'Scan summary-Task:{scanned_directories[0]} directories scanned,{scanned_files[0]} files scanned,'
                f'Data scanned:{data_scanned[0]},Time:{all_time[0]},Start Date:{start_date2},End Date:{end_date2}')
            print('infected files list:')
            if self.claimname == None:
                for i in range(len(file_list)):
                    files_list.append(re.findall(r'/scan.*:', file_list[i])[0].strip(':').replace('/scan', ''))
                    virus_list.append(re.findall(r':\s[A-Za-z]+-[A-Za-z]+', file_list[i])[0].strip(':'))
                    print_table.add_data([f'{self.filepath}{files_list[i]}', f'{virus_list[i]}'])
                print_table.print_table()
            else:
                for i in range(len(file_list)):
                    files_list.append(re.findall(r'/scan.*:', file_list[i])[0].strip(':').replace('/scan', ''))
                    virus_list.append(re.findall(r':\s[A-Za-z]+-[A-Za-z]+', file_list[i])[0].strip(':'))
                    print_table.add_data([f'{self.claimname}{files_list[i]}', f'{virus_list[i]}'])
                print_table.print_table()
            print('----------------------------------------------------------------------------------------')
        else:
            logger.write_to_log('INFO',
                                f'[{pod_id}]Scan summary-Task:Infected files:{infected_files[0]},'
                                f'Scanned directories:{scanned_directories[0]},'
                                f'Scanned files:{scanned_files[0]},'
                                f'Data scanned:{data_scanned[0]},'
                                f'Time:{all_time[0]},'
                                f'Start Date:{start_date2},'
                                f'End Date:{end_date2}', True)
            print('------------------------------------SCAN SUMMARY----------------------------------------')
            print(f'INFO: Scan summary-NO infected files found')
            print(
                f'Scan summary-Virus database:Known viruses:{known_viruses[0]},Engine version:{engine_version[0]}')
            print(
                f'Scan summary-Task:{scanned_directories[0]} directories scanned,{scanned_files[0]} files scanned,'
                f'Data scanned:{data_scanned[0]},Time:{all_time[0]},Start Date:{start_date2},End Date:{end_date2}')
            print('----------------------------------------------------------------------------------------')
        for i in range(len(file_list)):
            if i >= 0 and remove == ' --remove':
                files = re.findall(r'/scan.*:', file_list[i])[0].strip(':').replace('/scan', '')
                print(f'Delete infected files:{files}')
                logger.write_to_log('INFO', f"[{pod_id}]Delete infected files:{files}", True)
                print(f'{files} deleted successfully')
                logger.write_to_log('INFO', f'[{pod_id}]{files} deleted successfully', True)
        # print(f'Delete Pod:{self.pod_name_list[0]}')
        logger.write_to_log('INFO', f'[{pod_id}]Delete Pod:{self.pod_name_list[0]}')
        action.delete_docker(self.pod_name_list[0])
        logger.write_to_log('INFO', f'[{pod_id}]{self.pod_name_list[0]} deleted successfully')
        # print(f'Delete yaml:{self.filename}.yaml')
        logger.write_to_log('INFO', f'[{pod_id}]Delete yaml:{self.filename}.yaml')
        action.delete_yaml(self.filename)
        logger.write_to_log('INFO', f'[{pod_id}]{self.filename}.yaml deleted successfully')
