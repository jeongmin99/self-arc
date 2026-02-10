# DeepAuto Assignment
이 문서는 Minikube 환경에서 ARC(Action Runner Controller)를 활용한 GitOps 파이프라인 구축 가이드를 담고 있습니다.

## 실행 환경 ##


## 아키텍처 ##

## 실행 방법 ##

### 1. minikube 실행 (OIDC 설정 포함) ###

GitHub Action Token을 인식할 수 있도록 API 서버를 설정하며 시작합니다.
```
minikube start ^
  --extra-config=apiserver.oidc-issuer-url=https://token.actions.githubusercontent.com ^
  --extra-config=apiserver.oidc-client-id=kubernetes ^
  --extra-config=apiserver.oidc-username-claim=sub
```

### 2. ArgoCD 설치 (helm 사용) ###

GitOps 방식으로 ARC를 관리하기 위해 ArgoCD를 먼저 설치하고 레포지토리를 등록합니다.
```
helm repo add argo https://argoproj.github.io/argo-helm
minikube kubectl create namespace argocd
helm install argocd -n argocd argo/argo-cd
```

### 3. ARC용 GitHub Token Secret 생성 ###

GitHub ARC가 GitHub 레포지토리에 접근할 수 있도록 Secret을 설정합니다.
```
minikube kubectl create ns actions-runner-system
```
```
minikube kubectl -- create secret generic controller-manager ^
  -n actions-runner-system ^
  --from-literal=github_token=<GITHUB_PAT>
```


### 4. ArgoCD Repository Secret 추가 ###

ArgoCD가 GitHub레포지토리를 인식할 수 있도록 Secret을 설정합니다.

이 때, <GITHB_NAME>에 GitHub 사용자명, <GITHUB_PAT>에 GitHub Action Token 값을 기입 후 배포합니다.
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
minikube kubectl -- apply -f bootstrap/add.repo.yaml
```

### 5. ARC 배포 ###

ArgoCD를 통해 GitHub ARC를 관리할 수 있도록 ARC 및 관련 구성 요소를 배포합니다.
```
minkube kubectl -- apply -f bootstrap/deploy-arc.yaml
```

