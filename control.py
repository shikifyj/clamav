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
            logger.write_to_log("INFO", f'创建yaml文件:{self.filename}.yaml')
            try:
                with open(os.getcwd() + f'/{self.filename}.yaml') as f:
                    doc = yaml.load(f, Loader=yaml.FullLoader)
                    doc['metadata']['name'] = f'clamb-{self.claimname}'
                    doc['spec']['containers'][0]['name'] = f'clamb-{self.claimname}'
                    doc['spec']['containers'][0]['volumeMounts'][0]['mountPath'] = f'/scan'
                    doc['spec']['volumes'][0]['persistentVolumeClaim']['claimName'] = self.claimname
                    doc['spec']['nodeName'] = self.node_name
                    logger.write_to_log('INFO',
                                        f'{self.filename}.yaml创建成功,主要参数:volume_mount_path:/scan,'
                                        f'claimName:{self.claimname}')
            except FileNotFoundError:
                print(f'WARNING:{self.filename}.yaml创建失败')
                logger.write_to_log('WARNING', f'{self.filename}.yaml创建失败')
                sys.exit()
            with open(os.getcwd() + f'/{self.filename}.yaml', 'w', encoding='utf-8') as f:
                yaml.dump(doc, f)
            pod_status = action.create_pod(f'{self.filename}.yaml')
            logger.write_to_log("INFO", f"创建Pod: clamb-{self.claimname}")
            time.sleep(2)
            if 'created' in pod_status:
                max_time = time.time() + 30
                print(f'检查Pod:clamb-{self.claimname}的状态')
                while time.time() < max_time:
                    result = action.check_pod(f'clamb-{self.claimname}')
                    status = re.findall(fr'clamb-{self.claimname}+\s*\d*/\d*\s*([a-zA-Z]*)\s', result)
                    if status[0] == 'Running':
                        node = re.findall(r'\.[0-9]+\s+([\w]+)\s', result)
                        pod_id = action.get_pid(f'clamb-{self.claimname}')
                        print(f"Pod:clamb-{self.claimname}运行在{node[0]}节点")
                        logger.write_to_log("INFO", f"Pod:clamb-{self.claimname}运行在{node[0]}节点,容器ID是[{pod_id}]")
                        break
                else:
                    result = action.check_pod(f'clamb-{self.claimname}')
                    status = re.findall(fr'clamb-{self.claimname}+\s*\d*/\d*\s*([a-zA-Z]*)\s', result)
                    action.delete_docker(f'clamb-{self.claimname}')
                    print(f'WARNING:Pod:clamb-{self.claimname}的状态是"{status[0]}",PVC:{self.claimname}扫描失败')
                    logger.write_to_log('WARNING',
                                        f'由于Pod:clamb-{self.claimname}的状态是"{status[0]}",'
                                        f'PVC:{self.claimname}扫描失败', True)
                    sys.exit()
                self.pod_name_list.append(f'clamb-{self.claimname}')
                self.scan_directory_list.append(f'/scan')
                self.container_name_list.append(f'clamb-{self.claimname}')
            else:
                print(f'WARING:Pod:clamb-{self.claimname}创建失败')
                logger.write_to_log("WARING", f"由于Pod:clamb-{self.claimname}创建失败,"
                                              f"PVC:{self.claimname}扫描失败", True)
                sys.exit()
        else:
            print(f'WARING:节点:{self.node_name}不存在,请重新选择节点运行杀毒程序')
            logger.write_to_log('WARNING',
                                f'节点:{self.node_name}不存在,'
                                f'PVC:{self.claimname}扫描失败', True)
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
            logger.write_to_log("INFO", f'创建yaml文件:{self.filename}.yaml')
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
                                        f'{self.filename}.yaml创建成功,主要参数:volume_mount_path:/scan,'
                                        f'volumes_path:{self.filepath}')
            except FileNotFoundError:
                print(f'WARNING:{self.filename}.yaml创建失败')
                logger.write_to_log('WARNING', f'{self.filename}.yaml创建失败')
                sys.exit()
            with open(os.getcwd() + f'/{self.filename}.yaml', 'w', encoding='utf-8') as f:
                yaml.dump(doc, f)
            pod_status = action.create_pod(f'{self.filename}.yaml')
            logger.write_to_log("INFO", f"创建Pod:{pod_name}")
            time.sleep(2)
            if 'created' in pod_status:
                max_time = time.time() + 30
                print(f'检查Pod:{pod_name}的状态')
                while time.time() < max_time:
                    result = action.check_pod(f'{pod_name}')
                    status = re.findall(fr'{pod_name}+\s*\d*/\d*\s*([a-zA-Z]*)\s', result)
                    if status[0] == 'Running':
                        node = re.findall(r'\.[0-9]+\s+([\w]+)\s', result)
                        pod_id = action.get_pid(f'{pod_name}')
                        print(f"Pod:{pod_name}运行在{node[0]}节点")
                        logger.write_to_log("INFO", f"Pod:{pod_name}运行在{node[0]}节点,容器ID是[{pod_id}]")
                        break
                else:
                    result = action.check_pod(f'{pod_name}')
                    status = re.findall(fr'{pod_name}+\s*\d*/\d*\s*([a-zA-Z]*)\s', result)
                    action.delete_docker(f'{pod_name}')
                    print(f'WARNING:Pod:{pod_name}的状态是"{status[0]}",{self.filename}扫描失败')
                    logger.write_to_log('WARNING',
                                        f'由于Pod:clamb-{self.filename}的状态是"{status[0]}",'
                                        f'{self.filename}扫描失败', True)
                    sys.exit()
                self.pod_name_list.append(f'{pod_name}')
                self.scan_directory_list.append(f'/scan')
                self.container_name_list.append(f'{pod_name}')
            else:
                print(f'WARING:Pod:{pod_name}创建失败')
                logger.write_to_log("WARING", f"由于Pod:{pod_name}创建失败,"
                                              f"{self.filename}扫描失败", True)
                sys.exit()
        else:
            print(f'WARING:节点:{self.node_name}不存在,请重新选择节点运行杀毒程序')
            logger.write_to_log('WARNING',
                                f'节点:{self.node_name}不存在,'
                                f'{self.filename}扫描失败', True)
            sys.exit()

    def scan_directory(self, remove):
        if self.claimname == None:
            pod_id = action.get_pid(f'clamb-{self.filepath}'.replace('/', '-'))
            print(f'正在扫描{self.filepath} ')
            logger.write_to_log("INFO", f'[{pod_id}]扫描{self.filepath}', True)
        else:
            pod_id = action.get_pid(f'clamb-{self.claimname}')
            print(f'正在扫描PVC:{self.claimname} ')
            logger.write_to_log("INFO", f'[{pod_id}]扫描PVC:{self.claimname}', True)
        result = action.scanning(pod_name=self.pod_name_list[0],
                                 container_name=self.container_name_list[0],
                                 scan_directory=self.scan_directory_list[0],
                                 remove=remove)
        logger.write_to_log("INFO", f'[{pod_id}]扫描完成', True)
        print('扫描完成')
        file_list = re.findall(r'\/scan.*FOUND', result)
        for i in range(len(file_list)):
            if i >= 0:
                file1 = re.findall(r'/scan.*:', file_list[i])[0].strip(':').replace('/scan', '')
                if self.claimname == None:
                    str2 = f'{[pod_id]}感染文件:{self.filepath}{file1}'.replace("'", '')
                    logger.write_to_log('WARNING', f'{str2}', True)
                else:
                    str1 = f'{[pod_id]}感染文件:{self.claimname}{file1}'.replace("'", '')
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
                            f'[{pod_id}]扫描总结-病毒库:已知病毒数:{known_viruses[0]},'
                            f'引擎版本:{engine_version[0]}', True)
        if len(file_list) > 0:
            files_list = []
            virus_list = []
            print_table = utils.Table()
            logger.write_to_log('WARNING',
                                f'[{pod_id}]扫描总结-任务:感染文件数量:{infected_files[0]},'
                                f'扫描目录数量:{scanned_directories[0]},'
                                f'扫描文件数量:{scanned_files[0]},'
                                f'扫描文件总大小:{data_scanned[0]},'
                                f'扫描时间:{all_time[0]},'
                                f'起始时间:{start_date2},'
                                f'结束时间:{end_date2}', True)
            print('------------------------------------扫描总结----------------------------------------')
            print(f'WARNING: 扫描总结-找到{infected_files[0]}个感染文件')
            print(
                f'扫描总结-病毒库:已知病毒数:{known_viruses[0]},引擎版本:{engine_version[0]}')
            print(
                f'扫描总结-任务:扫描了{scanned_directories[0]}个目录,扫描了{scanned_files[0]}个文件,'
                f'扫描文件总大小为{data_scanned[0]},扫描时间:{all_time[0]},起始时间:{start_date2},结束时间:{end_date2}')
            print('感染文件表:')
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
                                f'[{pod_id}]扫描总结-任务:感染文件数量:{infected_files[0]},'
                                f'扫描目录数量:{scanned_directories[0]},'
                                f'扫描文件数量:{scanned_files[0]},'
                                f'扫描文件总大小:{data_scanned[0]},'
                                f'扫描时间:{all_time[0]},'
                                f'起始时间:{start_date2},'
                                f'结束时间:{end_date2}', True)
            print('------------------------------------扫描总结----------------------------------------')
            print(f'INFO: 扫描总结-没有找到感染文件')
            print(
                f'扫描总结-病毒库:已知病毒数:{known_viruses[0]},引擎版本:{engine_version[0]}')
            print(
                f'扫描总结-任务:扫描了{scanned_directories[0]}个目录,扫描了{scanned_files[0]}个文件,'
                f'扫描文件总大小为{data_scanned[0]},扫描时间:{all_time[0]},起始时间:{start_date2},结束时间:{end_date2}')
            print('----------------------------------------------------------------------------------------')
        for i in range(len(file_list)):
            if i >= 0 and remove == ' --remove':
                files = re.findall(r'/scan.*:', file_list[i])[0].strip(':').replace('/scan', '')
                print(f'删除感染文件:{files}')
                logger.write_to_log('INFO', f"[{pod_id}]删除感染文件:{files}", True)
                print(f'{files}成功删除')
                logger.write_to_log('INFO', f'[{pod_id}]{files}成功删除', True)
        # print(f'Delete Pod:{self.pod_name_list[0]}')
        logger.write_to_log('INFO', f'[{pod_id}]删除Pod:{self.pod_name_list[0]}')
        action.delete_docker(self.pod_name_list[0])
        logger.write_to_log('INFO', f'[{pod_id}]{self.pod_name_list[0]}成功删除')
        # print(f'Delete yaml:{self.filename}.yaml')
        logger.write_to_log('INFO', f'[{pod_id}]删除:{self.filename}.yaml')
        action.delete_yaml(self.filename)
        logger.write_to_log('INFO', f'[{pod_id}]{self.filename}.yaml成功删除')
