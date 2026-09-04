---
title: Kubernetes实践
created: 2026-07-17T16:00:00
modified: 2026-07-17T16:00:00
tags: [运维, 运维/K8s]
status: seedling
type: permanent
pillar: 运维学习
---

# Kubernetes 实践

## 是什么

Kubernetes（K8s）是一个容器编排平台，帮你管理几十上百个容器的部署、伸缩、负载均衡、故障恢复。它不关心你容器里跑的是什么，只关心「你要几个副本」「网络怎么通」「挂了怎么办」。

## 为什么重要

手动管 3 个容器还行，30 个就疯了。K8s 让你声明「我要 5 个 Web 实例 + 2 个 Worker」，它自己搞定调度、健康检查、自动重启。这就是「云原生」的操作系统。

## 核心组件速记

| 组件 | 作用 |
|------|------|
| Pod | 最小调度单元，1 个 Pod = 1 或多个容器共享网络和存储 |
| Service | 给一组 Pod 提供一个固定的访问入口（IP + DNS），Pod 重启 IP 会变，Service 不变 |
| Deployment | 声明式管理 Pod 的副本数、更新策略、回滚 |
| ConfigMap / Secret | 配置和敏感信息（密码/Token）与代码分离 |
| Ingress | 把外部 HTTP 流量路由到集群内的 Service |

## 常用操作

```bash
kubectl get pods -n <namespace>         # 看 Pod 状态
kubectl describe pod <name>             # 看 Pod 详细信息（排查首选）
kubectl logs -f <pod>                   # 实时日志
kubectl exec -it <pod> -- bash          # 进容器
kubectl apply -f deployment.yaml        # 声明式部署
kubectl rollout restart deployment <name>  # 重启所有 Pod
kubectl rollout undo deployment <name>  # 回滚
```

## 一句话带走

> K8s 是运维的自动驾驶系统——你告诉它目的地（期望状态），它自己找路、避障、停车。

## 相关笔记

- [[容器化]]
- [[Docker]]
- [[CI与CD]]
