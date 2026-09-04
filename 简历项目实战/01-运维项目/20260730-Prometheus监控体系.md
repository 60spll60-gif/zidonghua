---
title: Prometheus 监控体系搭建
created: 2026-07-30T16:00:00
modified: 2026-07-30T16:00:00
tags: [简历, 项目/运维, Prometheus, Grafana, 监控]
status: seedling
type: permanent
pillar: 简历项目实战
related: ["[[简历项目实战-MOC]]", "[[20260730-K8s容器编排实战]]", "[[20260730-CI-CD流水线搭建]]"]
---

# Prometheus 监控体系 — MTTR 从 45 分钟降到 10 分钟

## 📄 简历写法（可直接抄）

> **全栈监控告警平台建设** · 项目角色：独立搭建 · 2026.XX
>
> - 基于 **Prometheus + Grafana + Alertmanager** 搭建覆盖「主机→容器→应用」三层的监控体系，纳管 **N 台**服务器与核心服务
> - 设计 **20+ 条告警规则**并分级（P0 电话/P1 钉钉/P2 邮件），告警准确率 90%+，故障平均发现时间从 **45 分钟降至 3 分钟**
> - 输出标准化 Grafana 仪表盘，实现故障定位时间（MTTR）缩短 **75%**

> [!tip] 旁批：MTTR 是运维面试的硬通货
> MTTR（Mean Time To Repair，平均故障修复时间）= 发现时间 + 定位时间 + 修复时间。监控主要压缩前两段。面试时按这个公式讲，显得你理解监控的**目的**而不只是工具。

## 🧰 技术栈

| 工具 | 用途 | 为什么选它 |
|------|------|------------|
| Prometheus | 指标采集与存储 | 云原生监控标准，PromQL 查询语言强大 |
| node_exporter | 主机指标采集 | CPU/内存/磁盘/网络全覆盖，官方出品 |
| Grafana | 可视化仪表盘 | 图表美观，社区模板一键导入 |
| Alertmanager | 告警路由与静默 | 告警分组、去重、分级路由 |
| 钉钉/企微 Webhook | 告警通知 | 国内团队触达最快 |
| cAdvisor / kube-state-metrics | 容器/K8s 指标 | 有 K8s 项目时用 |

## 🛠️ 详细操作步骤

### 步骤 1：Docker Compose 一键起核心三件套

```yaml
# /opt/monitor/docker-compose.yml
services:
  prometheus:
    image: prom/prometheus:latest
    container_name: prometheus
    restart: always
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - ./rules/:/etc/prometheus/rules/
      - prometheus-data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.retention.time=30d'    # 数据保留 30 天

  grafana:
    image: grafana/grafana:latest
    container_name: grafana
    restart: always
    ports:
      - "3000:3000"
    volumes:
      - grafana-data:/var/lib/grafana
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=改个强密码

  alertmanager:
    image: prom/alertmanager:latest
    container_name: alertmanager
    restart: always
    ports:
      - "9093:9093"
    volumes:
      - ./alertmanager.yml:/etc/alertmanager/alertmanager.yml

volumes:
  prometheus-data:
  grafana-data:
```

```bash
cd /opt/monitor && docker compose up -d
```

### 步骤 2：被监控机器装 node_exporter

```bash
# 每台要监控的服务器执行
docker run -d --name node-exporter --restart always \
  -p 9100:9100 \
  -v /proc:/host/proc:ro \
  -v /sys:/host/sys:ro \
  -v /:/rootfs:ro \
  prom/node-exporter:latest \
  --path.procfs=/host/proc --path.sysfs=/host/sys
```

### 步骤 3：配置 Prometheus 采集

```yaml
# prometheus.yml
global:
  scrape_interval: 15s          # 每 15 秒抓一次指标
  evaluation_interval: 15s      # 每 15 秒算一次告警规则

rule_files:
  - "rules/*.yml"

alerting:
  alertmanagers:
    - static_configs:
        - targets: ["alertmanager:9093"]

scrape_configs:
  - job_name: "prometheus"
    static_configs:
      - targets: ["localhost:9090"]

  - job_name: "nodes"
    static_configs:
      - targets:
          - "192.168.1.10:9100"    # 被监控机器1
          - "192.168.1.11:9100"    # 被监控机器2
        labels:
          env: production
```

> [!tip] 旁批：scrape_interval 设多少合适
> 15s 是社区默认值，兼顾实时性与存储开销。关键业务可设 5s，但要注意：间隔越短数据量越大，30 天 retention 下每 5s 一个指标一年约 1GB。别设 1s——那是 APM 的领域不是监控的。

### 步骤 4：编写告警规则（项目灵魂）

```yaml
# rules/host-alerts.yml
groups:
- name: host-alerts
  rules:
  # P1: CPU 持续 5 分钟超 85%
  - alert: HighCPUUsage
    expr: 100 - (avg by(instance) (rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100) > 85
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "主机 {{ $labels.instance }} CPU 使用率过高"
      description: "当前 CPU 使用率 {{ $value | humanize }}%，持续超过 5 分钟"

  # P0: 磁盘剩余不足 10%
  - alert: DiskSpaceLow
    expr: (1 - node_filesystem_avail_bytes{mountpoint="/"} / node_filesystem_size_bytes{mountpoint="/"}) * 100 > 90
    for: 2m
    labels:
      severity: critical
    annotations:
      summary: "主机 {{ $labels.instance }} 磁盘即将写满"

  # P0: 机器失联（exporter 挂了或机器挂了）
  - alert: InstanceDown
    expr: up == 0
    for: 1m
    labels:
      severity: critical
    annotations:
      summary: "主机 {{ $labels.instance }} 监控失联"

  # P2: 内存超 90%
  - alert: HighMemoryUsage
    expr: (1 - node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes) * 100 > 90
    for: 5m
    labels:
      severity: info
    annotations:
      summary: "主机 {{ $labels.instance }} 内存使用率过高"
```

> [!important] 旁批：告警设计的三个心法（面试加分）
> 1. **告警要有 `for` 持续时间**：瞬时抖动不报警，避免"狼来了"导致团队对告警麻木——这是监控建设最大的坑
> 2. **按 severity 分级路由**：critical 打电话/钉钉强提醒，warning 发群里，info 只记录。所有告警一个通道 = 没有告警
> 3. **annotation 写人话**：值班的人凌晨 3 点看到 "CPU 过高，当前 92%，持续 5 分钟" 比看到 "HighCPUUsage firing" 有用一万倍

### 步骤 5：配置 Alertmanager 分级通知

```yaml
# alertmanager.yml
global:
  resolve_timeout: 5m

route:
  receiver: default
  group_by: ['alertname', 'severity']
  group_wait: 30s          # 同组告警等 30s 聚合发送，防轰炸
  group_interval: 5m
  repeat_interval: 4h      # 未恢复的告警 4 小时重发一次
  routes:
    - match:
        severity: critical
      receiver: dingtalk-urgent
    - match:
        severity: warning
      receiver: dingtalk-normal

receivers:
- name: default
  webhook_configs:
    - url: http://dingtalk-webhook:8060/dingtalk/ops/send

- name: dingtalk-urgent
  webhook_configs:
    - url: http://dingtalk-webhook:8060/dingtalk/ops/send
      send_resolved: true    # 恢复也通知，闭环

- name: dingtalk-normal
  webhook_configs:
    - url: http://dingtalk-webhook:8060/dingtalk/notice/send
```

> [!tip] 旁批：钉钉 webhook 怎么接
> Alertmanager 原生不支持钉钉，社区方案是跑一个 `prometheus-webhook-dingtalk` 小服务做格式转换，Docker 一行起。群机器人创建：钉钉群 → 智能群助手 → 添加机器人 → 自定义，拿到 webhook 地址填进去。

### 步骤 6：Grafana 仪表盘（5 分钟出效果）

```bash
# Grafana → Connections → Data sources → 添加 Prometheus
# URL 填 http://prometheus:9090

# 然后导入社区现成模板（不用自己画）：
# Dashboards → Import → 输入模板 ID：
#   1860   —— Node Exporter Full（主机监控，最经典）
#   315    —— Kubernetes cluster monitoring（有 K8s 时用）
#   893    —— Docker 监控
```

导入后你就有了一个**看起来很贵**的监控大屏——CPU/内存/磁盘/网络/进程全有，多机对比、历史趋势齐全。

### 步骤 7：演练！亲手制造一次故障

```bash
# 在被监控机器上跑死 CPU，验证全链路
stress-ng --cpu 4 --timeout 300s

# 观察：Prometheus 指标飙升 → 5分钟后告警触发 → 钉钉收到消息
# → stress 停止 → 指标回落 → 收到"已恢复"通知
```

> [!important] 旁批：演练是必做项
> 没演练过的告警等于没有告警——你永远不知道哪一环是断的（webhook 地址错了？规则表达式写错了？Alertmanager 没 reload？）。简历上写"通过定期故障演练验证告警链路有效性"是很亮眼的细节。

## 📊 成果量化模板

| 指标 | 建设前 | 建设后 |
|------|--------|--------|
| 故障发现 | 用户报障才知道，~45 分钟 | 告警主动推送，~3 分钟 |
| 故障定位 | 逐台登录机器排查 | 看大盘锁定异常机器，~10 分钟 |
| 磁盘写满事故 | 每季度 2~3 次 | 提前 1~2 天预警，0 次 |
| 告警有效性 | — | 分级 + 演练，准确率 90%+ |

## ❓ 面试高频问题

1. **Prometheus 是推还是拉？** → 拉（pull）：Prometheus 定期去各 exporter 的 `/metrics` 端点抓数据。好处：中心化管理目标、实例挂了马上知道（up==0）；缺点：短生命周期任务抓不到 → 用 Pushgateway 补充
2. **PromQL 里 rate 和 irate 区别？** → rate 取区间平均速率（平滑，适合告警）；irate 取最后两个点的瞬时速率（敏感，适合看图找尖刺）
3. **Prometheus 高可用怎么做？** → 双实例并行采集（数据重复但可接受）+ Thanos/VictoriaMetrics 做长期存储与全局视图
4. **监控和告警的边界？** → 监控覆盖面要广（能看一切），告警面要窄（只报需要人立即处理的）——"告警即工单"

## 相关笔记

- [[20260730-K8s容器编排实战|K8s 容器编排实战]] — K8s 的监控就是 Prometheus 全家桶，两个项目互相成就
- [[20260730-Ansible自动化运维|Ansible 自动化运维]] — 用 Ansible 批量装 node_exporter 是天然搭档
- [[简历项目实战-MOC|返回专栏首页]]
