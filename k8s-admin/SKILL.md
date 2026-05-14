---
name: k8s-admin
description: "Kubernetes 集群管理工具。適用：列出資源、describe 物件、查看 Pod logs。使用 kubectl 指令。"
---

# Kubernetes 管理技能 (k8s-admin)

日常 K8s 管理查詢工具。

## 何時使用

- 列出 namespaces / pods / services 等資源
- 查看物件詳細資訊
- 查看 Pod logs

## 常用指令

### 列出資源

| 任務 | 指令 |
|------|------|
| 叢集層級 Namespaces | `kubectl get ns` |
| 叢集層級 Nodes | `kubectl get nodes` |
| 叢集層級 PVs | `kubectl get pv` |
| 叢集層級 StorageClasses | `kubectl get sc` |
| 所有 Namespaced 資源 | `kubectl get all --all-namespaces` |
| NS 層級 Pods | `kubectl get pods -n <namespace>` |
| NS 層級 Services | `kubectl get svc -n <namespace>` |
| NS 層級 Deployments | `kubectl get deploy -n <namespace>` |
| NS 層級 StatefulSets | `kubectl get sts -n <namespace>` |
| NS 層級 DaemonSets | `kubectl get ds -n <namespace>` |
| NS 層級 ConfigMaps | `kubectl get cm -n <namespace>` |
| NS 層級 Secrets | `kubectl get secret -n <namespace>` |
| NS 層級 PVCs | `kubectl get pvc -n <namespace>` |
| NS 層級 Ingresses | `kubectl get ingress -n <namespace>` |
| NS 層級 HPA | `kubectl get hpa -n <namespace>` |
| NS 層級 CronJobs | `kubectl get cj -n <namespace>` |
| NS 層級 Jobs | `kubectl get jobs -n <namespace>` |

### Describe (詳細資訊)

| 任務 | 指令 |
|------|------|
| Pod 詳細資訊 | `kubectl describe pod <name> -n <namespace>` |
| Service 詳細資訊 | `kubectl describe svc <name> -n <namespace>` |
| Deployment 詳細資訊 | `kubectl describe deploy <name> -n <namespace>` |
| Node 詳細資訊 | `kubectl describe node <name>` |

### Logs

| 任務 | 指令 |
|------|------|
| 查看 Pod Logs | `kubectl logs <name> -n <namespace>` |
| 最後 100 行 | `kubectl logs <name> -n <namespace> --tail 100` |
| 即時追蹤 | `kubectl logs <name> -n <namespace> -f` |
| 進入 Pod | `kubectl exec -it <name> -n <namespace> -- /bin/bash` |

## 參考資源

- [kubectl 官方文件](https://kubernetes.io/docs/reference/kubectl/)
- `references/README.md`
