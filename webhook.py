import requests
import json
import random
import string
import time

url = 'https://kube-auditing-webhook-svc.kubesphere-logging-system.svc:6443/audit/webhook/event'


def wh_interface(Time, Workspace, Reason, AuditResType, ResName, SourceIPs, LogLevel):
    # print('webhokk info from bmcprogram',Time,Workspace,Reason,AuditResType,ResName,SourceIPs,LogLevel)

    audit_id_audit = ''.join(random.sample(string.ascii_lowercase + string.digits, 8)) + '-' + ''.join(
        random.sample(string.ascii_lowercase + string.digits, 4)) + '-' + ''.join(
        random.sample(string.ascii_lowercase + string.digits, 4)) + '-' + ''.join(
        random.sample(string.ascii_lowercase + string.digits, 4)) + '-' + ''.join(
        random.sample(string.ascii_lowercase + string.digits, 12))
    # print(audit_id_audit)
    headers = {
        'content-type': 'application/json'
    }
    data = {

        "Items": [

            {

                "Devops": "",

                "Workspace": Workspace,

                "Cluster": "",

                "Message": "",

                "Level": "Metadata",

                "AuditID": audit_id_audit,

                "Stage": "ResponseComplete",

                "RequestURI": "",

                "Verb": "",

                "User": {

                    "username": "system",

                    "groups": [

                        "system:authenticated"

                    ]

                },
                "ImpersonatedUser": None,

                "SourceIPs": [

                    SourceIPs

                ],

                "UserAgent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",

                "ObjectRef": {

                    "Resource": ResName,

                    "Namespace": "",

                    "Name": AuditResType,

                    "UID": "",

                    "APIGroup": "",

                    "APIVersion": "",

                    "ResourceVersion": "",

                    "Subresource": ""

                },

                "ResponseStatus": {
                    "code": 0,
                    "metadata": {},
                    "status": LogLevel,
                    "reason": Reason
                },
                "RequestObject": None,

                "ResponseObject": None,

                "RequestReceivedTimestamp": Time,

                "StageTimestamp": Time,

                "Annotations": None

            }

        ]

    }
    data = json.dumps(data)
    print(data)
    err_signal = True
    for i in range(10):
        try:
            response = requests.post(url, headers=headers, verify=False, data=data)
            # print(response)
            print('Data was written successfully')
            err_signal = False
            break
        except:
            time.sleep(2)
    if err_signal:
        print('Tried to rewrite the data 10 times, but the data write failed!')
