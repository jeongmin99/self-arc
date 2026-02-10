# DeepAuto Assignment

## 실행 환경 ##

Host: Windows

Kubernetes Cluster: Minikube

Programming Language: Python

Container Builder: Docker

CD: ArgoCD



## 아키텍처 ##

## 실행 방법 ##

1. minikube oidc 파라미터 설정하여 실행
```
minikube start ^
  --extra-config=apiserver.oidc-issuer-url=https://token.actions.githubusercontent.com ^
  --extra-config=apiserver.oidc-client-id=kubernetes ^
  --extra-config=apiserver.oidc-username-claim=sub
```

2. helm을 통한 argocd 설치
```
helm repo add argo https://argoproj.github.io/argo-helm
minikube kubectl create namespace argocd
helm install argocd -n argocd argo/argo-cd
```

3. ARC에서 사용하는 PAT을 위한 쿠버네티스 Secret 생성
```
minikube kubectl create ns actions-runner-system
minikube kubectl -- create secret generic controller-manager ^
  -n actions-runner-system ^
  --from-literal=github_token=<GITHUB_PAT>
```

4. bootstrap 폴더에서 add-repo.yaml 파일 편집 후 클러스터에 apply
```
apiVersion: v1
kind: Secret
metadata:
  name: repo-deepauto
  namespace: argocd
  labels:
    argocd.argoproj.io/secret-type: repository
stringData:
  url: https://github.com/jeongmin99/deepauto-assignment
  type: git
  username: <GITHUB_NAME>
  password: <GITHUB_PAT>
```

```
minikube kubectl -- apply -f add.repo.yaml
```

5. bootstrap 폴더에 있는 deploy-arc.yaml을 클러스터에 apply
```
minkube kubectl -- apply -f deploy-arc.yaml
```

