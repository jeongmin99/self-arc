import time
import os
from kubernetes import client


POD_NAME="hello"
NAMESPACE="default"

def main():

    TOKEN = os.environ["KUBE_TOKEN"]

    config = client.Configuration()
    config.host = "https://kubernetes.default.svc"
    config.ssl_ca_cert = "/ca/ca.crt"

    config.api_key = {
        "authorization": "Bearer " + TOKEN
    }

    client.Configuration.set_default(config)
    v1=client.CoreV1Api()

    pod_manifest = {
        'apiVersion': 'v1',
        'kind': 'Pod',
        'metadata': {
            'name': POD_NAME
        },
        'spec': {
            'containers': [{
                'image': 'busybox',
                'name': 'hello',
                'command': ["/bin/echo"],
                "args": ["Hello world"]
            }],
            'restartPolicy': 'Never'
        }

    }

    # 파드 생성
    resp = v1.create_namespaced_pod(body=pod_manifest, namespace=NAMESPACE)


    # 파드 waiting 중 stdout 출력
    printed=False
    while True:
        pod= v1.read_namespaced_pod(name=POD_NAME, namespace=NAMESPACE)
        if pod.status.phase in ["Running","Succeeded"] and printed == False: # 실행 중 또는 성공일 때 stdout이 출력된 적 없으면
            logs= v1.read_namespaced_pod_log(name=POD_NAME, namespace=NAMESPACE)
            print(logs)
            printed=True

        # 파드 성공 시 대기 종료
        if pod.status.phase == "Succeeded":
            break

    time.sleep(1)

    # 파드 삭제
    v1.delete_namespaced_pod(name=POD_NAME, namespace=NAMESPACE)


if __name__ == "__main__":
    main()