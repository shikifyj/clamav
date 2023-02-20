import utils
import os

YAML_PATH = os.getcwd()


def create_yaml(filename, yaml_dict):
    filepath = os.getcwd() + f'/{filename}.yaml'
    utils.update_yaml(filepath, yaml_dict)
    utils.ConfFile(filepath).check_yaml()


def create_pod(filename):
    cmd = f'kubectl apply -f {YAML_PATH}/{filename}'
    utils.exec_cmd(cmd)


def check_pod(pod_name):
    cmd = f'kubectl get pod -o wide | grep {pod_name}'
    result = utils.exec_cmd(cmd)
    return result


def scanning(pod_name, container_name, scan_directory):
    cmd = f'kubectl exec -it {pod_name} -c {container_name} -- clamscan -r {scan_directory}'
    result = utils.exec_cmd(cmd)
    return result


def delete_docker(pod_name):
    cmd = f'kubectl delete pod {pod_name}'
    utils.exec_cmd(cmd)
