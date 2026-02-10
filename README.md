# DeepAuto Assignment
이 문서는 Minikube 환경에서 ARC(Action Runner Controller)를 활용한 GitOps 파이프라인 구축 가이드를 담고 있습니다.

# 실행 환경 #
| 항목 | 내용 |
|------|------|
| Host OS | Windows 10 |
| K8s Cluster | Minikube |
| Nested Container Runtime | Docker |
| CI/CD Pipeline | GitHub Actions & ArgoCD (GitOps) |
| Runner Controller | Actions Runner Controller (ARC) |
| Language | Python (Kubernetes Python SDK) |
| Authentication | OIDC (GitHub ID Token ↔ K8s API Server) |


# 아키텍처 #

<img src=https://github.com/user-attachments/assets/30fd574c-7a63-4caa-b49b-7b0fd724aacf>

본 저장소는 다음 과제(Task)들을 구현한 결과를 포함하고 있습니다.

- Task 1 - `hello-kube`: Kubernetes Pod 실행 CLI 구현
- Task 2 - Kubernetes 환경에 GitHub Actions Runner Controller(ARC) 배포
- Task 3 - GitHub Actions에서 `hello-kube` 실행 (OIDC 인증 사용)
- Extra Credit 1 - ArgoCD 기반 GitOps 방식으로 ARC 배포 관리
- Extra Credit 2 - GitHub Actions를 통한 Docker 이미지 빌드


## Task 1 — hello-kube CLI 구현

### 설명

`hello-kube`는 Kubernetes API를 사용하여 Pod을 생성 및 관리하는 간단한 CLI 도구입니다.

구현 기능:

- `hello`라는 이름의 Pod 생성
- Pod 완료 상태까지 대기
- 대기 중 stdout(Hello world) 출력
- 작업 완료 후 Pod 자동 삭제

### 사용 기술

- Python
- Kubernetes Python Client SDK

동작 흐름:

1. Kubernetes API 연결
2. Pod 생성
3. Pod 상태 모니터링
4. 로그 스트리밍
5. Pod 종료 후 삭제



## Task 2 — GitHub Actions Runner Controller (ARC) 배포

Kubernetes 환경에서 GitHub Actions Runner Controller(ARC)를 배포하여 Kubernetes 기반 GitHub Actions Runner를 구성했습니다.

구성 내용:

- ARC 설치
- GitHub PAT Secret 설정
- Kubernetes Pod 기반 Runner 구성

ARC를 통해:

- Kubernetes에서 GitHub Actions 실행 가능
- 동적 Runner 관리



## Task 3 — GitHub Actions에서 hello-kube 실행

GitHub Actions Workflow를 작성하여 `hello-kube`를 실행하도록 구성했습니다.

요구사항:

- hello-kube가 Kubernetes API Server 인증 수행
- ServiceAccount 대신 GitHub Actions Token(OIDC) 사용


## Extra Credit 1 — ArgoCD 기반 GitOps 관리

GitHub ARC 배포를 ArgoCD를 사용한 GitOps 방식으로 관리했습니다.

구성:

- Git Repository 기반 선언형 배포
- Self-Heal 활성화


## Extra Credit 2 — GitHub Actions Docker 이미지 빌드

GitHub Actions Workflow를 통해 `hello-kube` Docker 이미지를 자동 빌드하도록 구성했습니다.

파이프라인:

1. Repository Checkout
2. Docker Image Build
3. 이미지 Run







---

# 실행 방법 #

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

이 때, <GITHUB_NAME>에 GitHub 사용자명, <GITHUB_PAT>에 GitHub Action Token 값을 기입 후 배포합니다.

<sub>boostrap/add-repo.yaml</sub>
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
minikube kubectl -- apply -f bootstrap/add-repo.yaml
```

### 5. ARC 배포 ###

ArgoCD를 통해 GitHub ARC를 관리할 수 있도록 ARC 및 관련 구성 요소를 배포합니다.
```
minkube kubectl -- apply -f bootstrap/deploy-arc.yaml
```

