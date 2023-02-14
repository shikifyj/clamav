import action
import yaml
import re
class AntiVirus(object):
    def __init__(self):
        pass

    def mount_docker_volume(self, claimname_list):
        pass
    def mount_docker_file(self, path_list):
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
            filename = f'config{i}.yaml'
            action.create_yaml(filename, dict_yaml)
        for i in range(len(path_list)):
            with open(f'config{i}.yaml') as f:
                doc = yaml.load(f, Loader=yaml.FullLoader)
            doc['metadata']['name'] = f'clamav{i}'
            doc['spec']['containers'][0]['name'] = f'clamav{i}'
            doc['spec']['containers'][0]['volumeMounts']['mountPath'] = f'/mnt{i}'
            doc['spec']['volumes'][0]['hostPath']['path'] = path_list[i]
            with open(f'config{i}.yaml', 'w', encoding='utf-8') as f:
                yaml.dump(doc, f)
            action.create_pod(f'config{i}.yaml')
            try:
                result = action.check_pod(f'clamav{i}')
                status = re.findall(r'clamav\s*\d*/\d*\s*([a-zA-Z]*)\s',result)



    def scan_directory(self):
        pass
    cc
