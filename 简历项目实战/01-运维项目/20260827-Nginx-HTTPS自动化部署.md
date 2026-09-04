---
title: Nginx + Let's Encrypt 自动化HTTPS部署与证书管理
created: 2026-08-27T10:00:00
modified: 2026-08-27T10:00:00
tags: [简历, 项目/运维, Nginx, HTTPS, SSL, Let's Encrypt, 证书管理]
status: seedling
type: permanent
pillar: 简历项目实战
related: ["[[简历项目实战-MOC]]", "[[20260730-CI-CD流水线搭建]]", "[[20260730-Prometheus监控体系]]"]
---

# Nginx + Let's Encrypt 自动化HTTPS部署与证书管理

## 📄 简历写法（可直接抄）

> **HTTPS自动化部署与证书管理平台** · 项目角色：主导搭建 · 2026.XX
>
> - 针对企业网站HTTP明文传输存在**数据泄露风险**、手动管理SSL证书**易过期导致服务中断**的问题，基于 **Nginx + Let's Encrypt + Certbot** 设计并实现全自动HTTPS部署与证书生命周期管理
> - 实现证书**自动申请、自动部署、自动续期**，证书管理效率提升 **95%**，HTTPS部署时间从 **2小时** 缩短至 **5分钟**
> - 配置 **HSTS、OCSP Stapling、TLS 1.3** 等安全特性，SSL Labs 评分从 **C级** 提升至 **A+级**，安全合规性达到金融行业标准

> [!tip] 旁批：数字怎么来
> 没有公司数据就按个人项目如实写："个人博客/开源项目HTTPS改造"。面试官追问时，讲清楚**改造前后的对比逻辑**（手动证书管理有哪些痛点、HTTPS能解决什么安全问题）比编数字更有说服力。

## 🧰 技术栈

| 工具 | 用途 | 为什么选它（面试考点） |
|------|------|------------------------|
| Nginx 1.24+ | Web服务器 + 反向代理 | 性能优异、配置灵活、国内使用最广泛 |
| Let's Encrypt | 免费SSL证书颁发机构 | 免费、自动化、全球信任、ozilla推荐 |
| Certbot | 证书申请与管理客户端 | 官方推荐、自动续期、支持Nginx插件 |
| OpenSSL | 证书生成与验证工具 | 行业标准、功能完整 |
| Systemd | 服务管理 | 自动续期定时器、日志管理 |

## 🛠️ 详细操作步骤

### 步骤 0：准备环境

**在哪里操作**：您的本地电脑（Windows/Mac/Linux都可以）

**操作目的**：准备一台云服务器作为实验环境

```bash
# 1. 购买云服务器（推荐配置）
# - 阿里云/腾讯云/华为云 学生机（约¥10/月）
# - 配置：2核CPU、2GB内存、40GB硬盘
# - 系统：Ubuntu 22.04 LTS（推荐）或 CentOS 7/8

# 2. 登录服务器（在本地电脑终端执行）
# Windows用户：使用PowerShell或Git Bash
# Mac/Linux用户：打开终端
ssh root@你的服务器IP

# 3. 更新系统（必须执行）
sudo apt update && sudo apt upgrade -y

# 4. 安装必要工具
sudo apt install -y curl wget git vim
```

> [!warning] 旁批：为什么选Ubuntu
> Ubuntu对新手更友好，apt包管理器简单易用，文档也最全。CentOS已经停止维护，不推荐新项目使用。

### 步骤 1：安装Nginx

**在哪里操作**：SSH连接到您的云服务器

**操作目的**：安装Web服务器

```bash
# 1. 安装Nginx
sudo apt install -y nginx

# 2. 启动Nginx并设置开机自启
sudo systemctl start nginx
sudo systemctl enable nginx

# 3. 检查Nginx状态（应该显示 active (running)）
sudo systemctl status nginx

# 4. 验证安装（在本地浏览器访问）
# 打开浏览器，访问：http://你的服务器IP
# 应该看到 "Welcome to nginx!" 页面
```

**代码解释**：
- `sudo apt install -y nginx`：使用apt包管理器安装Nginx，`-y`表示自动确认
- `systemctl start nginx`：启动Nginx服务
- `systemctl enable nginx`：设置开机时自动启动Nginx
- `systemctl status nginx`：查看服务状态

> [!tip] 旁批：验证安装
> 如果浏览器打不开，检查云服务器的安全组设置，确保开放了80端口（HTTP）。

### 步骤 2：配置域名解析

**在哪里操作**：您的域名管理控制台（阿里云/腾讯云等）

**操作目的**：将域名指向您的服务器IP

```bash
# 1. 购买域名（如果没有）
# 推荐：阿里云万网、腾讯云DNSPod、Cloudflare
# 价格：.com域名约¥50/年

# 2. 添加DNS解析记录
# 记录类型：A记录
# 主机记录：@（代表根域名）和 www（代表www子域名）
# 记录值：你的服务器IP
# TTL：600（10分钟）

# 3. 等待DNS生效（通常5-10分钟）
# 在本地电脑验证解析是否生效：
nslookup 你的域名
```

**代码解释**：
- **A记录**：将域名指向一个IPv4地址
- **@**：代表根域名（如 example.com）
- **www**：代表www子域名（如 www.example.com）
- **TTL**：Time To Live，DNS缓存时间，600秒=10分钟

> [!warning] 旁批：域名备案
> 如果使用国内服务器，域名需要备案才能正常使用。建议使用香港或海外服务器进行测试，无需备案。

### 步骤 3：安装Certbot（Let's Encrypt客户端）

**在哪里操作**：SSH连接到您的云服务器

**操作目的**：安装证书申请工具

```bash
# 1. 安装Certbot和Nginx插件
sudo apt install -y certbot python3-certbot-nginx

# 2. 验证安装
certbot --version
# 应该显示类似：certbot 2.7.4

# 3. 查看帮助信息
certbot --help
```

**代码解释**：
- `certbot`：Let's Encrypt官方推荐的客户端工具
- `python3-certbot-nginx`：Nginx插件，可以自动修改Nginx配置
- 安装后Certbot会自动配置Nginx的HTTPS

> [!tip] 旁批：为什么用Certbot
> Certbot是Let's Encrypt官方推荐的工具，支持自动申请、自动部署、自动续期，是目前最简单的HTTPS解决方案。

### 步骤 4：申请SSL证书

**在哪里操作**：SSH连接到您的云服务器

**操作目的**：为您的域名申请免费SSL证书

```bash
# 1. 申请证书（替换为你的域名和邮箱）
sudo certbot --nginx -d 你的域名.com -d www.你的域名.com --email 你的邮箱@example.com

# 示例：
sudo certbot --nginx -d example.com -d www.example.com --email admin@example.com

# 2. 按照提示操作
# - 同意服务条款：输入 Y
# - 是否分享邮箱：输入 N（或Y，随意）
# - 选择重定向：选择 2（将HTTP重定向到HTTPS）

# 3. 验证证书安装
# 浏览器访问：https://你的域名.com
# 应该看到安全锁标志，表示HTTPS生效
```

**代码解释**：
- `--nginx`：使用Nginx插件，自动修改Nginx配置
- `-d`：指定要申请证书的域名，可以指定多个
- `--email`：用于接收证书过期提醒的邮箱
- 选择"重定向"会自动将所有HTTP请求转为HTTPS

> [!warning] 旁批：常见错误
> 如果出现"DNS问题"，说明域名解析还没生效。等待5-10分钟后重试，或检查DNS记录是否正确。

### 步骤 5：配置Nginx（手动配置示例）

**在哪里操作**：SSH连接到您的云服务器

**操作目的**：了解Nginx配置结构，以便后续自定义

```bash
# 1. 查看Nginx配置文件位置
ls -la /etc/nginx/
# 主配置文件：/etc/nginx/nginx.conf
# 站点配置：/etc/nginx/sites-available/
# 启用站点：/etc/nginx/sites-enabled/

# 2. 备份原始配置（重要！）
sudo cp /etc/nginx/nginx.conf /etc/nginx/nginx.conf.backup
sudo cp /etc/nginx/sites-available/default /etc/nginx/sites-available/default.backup

# 3. 查看当前Nginx配置（Certbot自动修改后的）
sudo cat /etc/nginx/sites-available/default
```

**代码解释**：
- `/etc/nginx/nginx.conf`：Nginx主配置文件
- `/etc/nginx/sites-available/`：存放所有可用站点配置
- `/etc/nginx/sites-enabled/`：存放已启用的站点配置（通常是符号链接）

### 步骤 6：深入理解Nginx配置

**在哪里操作**：SSH连接到您的云服务器

**操作目的**：编写自定义Nginx配置

```bash
# 1. 创建新的站点配置文件
sudo vim /etc/nginx/sites-available/mysite

# 2. 输入以下内容（请将域名替换为你的实际域名）：
```

```nginx
# HTTP服务器（80端口）- 自动跳转到HTTPS
server {
    listen 80;
    listen [::]:80;
    server_name example.com www.example.com;
    
    # 将所有HTTP请求重定向到HTTPS
    return 301 https://$server_name$request_uri;
}

# HTTPS服务器（443端口）
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name example.com www.example.com;
    
    # SSL证书配置（Certbot自动生成）
    ssl_certificate /etc/letsencrypt/live/example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/example.com/privkey.pem;
    
    # SSL安全配置（重要！）
    ssl_protocols TLSv1.2 TLSv1.3;  # 只允许TLS 1.2和1.3
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    
    # HSTS配置（告诉浏览器只用HTTPS访问）
    add_header Strict-Transport-Security "max-age=63072000; includeSubDomains; preload" always;
    
    # OCSP Stapling配置（提升性能）
    ssl_stapling on;
    ssl_stapling_verify on;
    resolver 8.8.8.8 8.8.4.4 valid=300s;
    resolver_timeout 5s;
    
    # 网站根目录
    root /var/www/html;
    index index.html index.htm;
    
    # 日志配置
    access_log /var/log/nginx/mysite.access.log;
    error_log /var/log/nginx/mysite.error.log;
    
    # 主要位置配置
    location / {
        try_files $uri $uri/ =404;
    }
    
    # 静态文件缓存
    location ~* \.(jpg|jpeg|png|gif|ico|css|js)$ {
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
}
```

**代码解释**：
- `listen 443 ssl http2`：监听443端口，启用SSL和HTTP/2
- `ssl_protocols`：指定允许的SSL/TLS协议版本，禁用不安全的旧版本
- `ssl_ciphers`：指定加密算法套件，选择安全且高性能的组合
- `add_header Strict-Transport-Security`：启用HSTS，强制浏览器使用HTTPS
- `ssl_stapling`：启用OCSP Stapling，提升SSL握手性能
- `try_files`：尝试按顺序查找文件，找不到则返回404

### 步骤 7：启用站点并测试配置

**在哪里操作**：SSH连接到您的云服务器

**操作目的**：启用新配置并测试

```bash
# 1. 创建符号链接启用站点
sudo ln -s /etc/nginx/sites-available/mysite /etc/nginx/sites-enabled/

# 2. 删除默认站点（可选）
sudo rm /etc/nginx/sites-enabled/default

# 3. 测试Nginx配置语法
sudo nginx -t
# 应该显示：
# nginx: the configuration file /etc/nginx/nginx.conf syntax is ok
# nginx: configuration file /etc/nginx/nginx.conf test is successful

# 4. 重新加载Nginx（不中断服务）
sudo systemctl reload nginx

# 5. 验证配置
# 浏览器访问：https://你的域名.com
# 应该看到安全锁标志，SSL Labs评分应该很高
```

**代码解释**：
- `ln -s`：创建符号链接，相当于Windows的快捷方式
- `nginx -t`：测试配置文件语法是否正确
- `reload`：重新加载配置，不会中断现有连接

> [!tip] 旁批：为什么用reload而不是restart
> reload会平滑地重新加载配置，不会中断正在处理的请求。restart会完全停止再启动，可能导致用户访问中断。

### 步骤 8：配置自动续期

**在哪里操作**：SSH连接到您的云服务器

**操作目的**：设置证书自动续期，避免过期

```bash
# 1. 测试证书续期命令
sudo certbot renew --dry-run
# 如果没有错误，说明自动续期配置正确

# 2. 查看Certbot创建的定时器
sudo systemctl list-timers | grep certbot
# 应该看到：certbot.timer

# 3. 查看定时器详情
sudo systemctl status certbot.timer

# 4. 手动续期证书（如果需要）
sudo certbot renew

# 5. 查看证书信息
sudo certbot certificates
```

**代码解释**：
- `--dry-run`：模拟运行，不实际续期，用于测试
- `certbot.timer`：Systemd定时器，每天运行两次检查是否需要续期
- Let's Encrypt证书有效期90天，Certbot会在过期前30天自动续期

> [!warning] 旁批：自动续期原理
> Certbot安装时会创建一个Systemd定时器，每天运行两次。如果距离过期不足30天，会自动续期并重新加载Nginx。

### 步骤 9：配置防火墙

**在哪里操作**：SSH连接到您的云服务器

**操作目的**：只开放必要端口，提升安全性

```bash
# 1. 查看当前防火墙状态
sudo ufw status
# 如果显示inactive，需要先启用

# 2. 允许SSH连接（重要！否则会锁死自己）
sudo ufw allow OpenSSH

# 3. 允许HTTP和HTTPS
sudo ufw allow 'Nginx Full'

# 4. 启用防火墙
sudo ufw enable
# 输入 y 确认

# 5. 查看状态
sudo ufw status verbose
# 应该看到：
# 22/tcp (OpenSSH)    ALLOW    Anywhere
# 80/tcp (Nginx HTTP) ALLOW    Anywhere
# 443/tcp (Nginx HTTPS) ALLOW   Anywhere
```

**代码解释**：
- `ufw`：Uncomplicated Firewall，Ubuntu默认的防火墙管理工具
- `allow OpenSSH`：允许SSH连接（端口22），否则无法远程管理
- `allow 'Nginx Full'`：允许HTTP(80)和HTTPS(443)端口
- `enable`：启用防火墙，拒绝所有未明确允许的连接

> [!warning] 旁批：防火墙重要性
> 不配置防火墙，服务器就像没关门的房子。开放SSH后先测试能否连接，再启用防火墙。

### 步骤 10：验证HTTPS配置

**在哪里操作**：本地电脑浏览器

**操作目的**：验证HTTPS是否正确配置

```bash
# 1. 在浏览器访问您的网站
# https://你的域名.com
# 应该看到：
# - 安全锁标志（地址栏左侧）
# - 网站内容正常显示
# - 没有混合内容警告

# 2. 使用SSL Labs测试（重要！）
# 访问：https://www.ssllabs.com/ssltest/
# 输入您的域名，等待测试完成
# 目标：评分达到A+

# 3. 使用命令行测试（可选）
# 在本地电脑终端执行：
openssl s_client -connect 你的域名.com:443 -servername 你的域名.com
# 查看输出中的"Verify return code: 0 (ok)"
```

**代码解释**：
- SSL Labs是业界最权威的SSL测试工具
- A+评级表示配置符合最佳安全实践
- `openssl s_client`：命令行SSL测试工具

### 步骤 11：配置安全增强（可选但推荐）

**在哪里操作**：SSH连接到您的云服务器

**操作目的**：进一步提升安全性

```bash
# 1. 安全加固Nginx配置
sudo vim /etc/nginx/nginx.conf

# 2. 在http块中添加以下内容：
```

```nginx
http {
    # 隐藏Nginx版本号（安全最佳实践）
    server_tokens off;
    
    # 限制请求体大小（防止大文件攻击）
    client_max_body_size 10M;
    
    # 限制连接数（防止DDoS）
    limit_conn_zone $binary_remote_addr zone=conn_limit:10m;
    limit_req_zone $binary_remote_addr zone=req_limit:10m rate=10r/s;
    
    # 安全响应头
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    add_header Content-Security-Policy "default-src 'self' http: https: ws: wss:" always;
    
    # gzip压缩（提升性能）
    gzip on;
    gzip_vary on;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_types text/plain text/css text/xml application/json application/javascript application/xml+rss application/atom+xml image/svg+xml;
}
```

**代码解释**：
- `server_tokens off`：隐藏Nginx版本号，防止攻击者利用已知漏洞
- `client_max_body_size`：限制上传文件大小，防止大文件攻击
- `limit_conn_zone/limit_req_zone`：限制连接数和请求率，防止DDoS
- `X-Frame-Options`：防止点击劫持攻击
- `X-Content-Type-Options`：防止MIME类型嗅探
- `X-XSS-Protection`：启用浏览器XSS防护
- `Content-Security-Policy`：防止XSS和数据注入攻击

### 步骤 12：配置日志轮转

**在哪里操作**：SSH连接到您的云服务器

**操作目的**：防止日志文件过大

```bash
# 1. 查看当前日志大小
ls -lh /var/log/nginx/
# 可以看到access.log和error.log

# 2. 查看日志轮转配置
cat /etc/logrotate.d/nginx

# 3. 自定义日志轮转（可选）
sudo vim /etc/logrotate.d/nginx-custom
```

```bash
/var/log/nginx/*.log {
    daily
    missingok
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 www-data adm
    sharedscripts
    postrotate
        [ -f /var/run/nginx.pid ] && kill -USR1 `cat /var/run/nginx.pid`
    endscript
}
```

**代码解释**：
- `daily`：每天轮转一次
- `rotate 14`：保留14天的日志
- `compress`：压缩旧日志
- `create 0640 www-data adm`：创建新日志文件的权限
- `kill -USR1`：通知Nginx重新打开日志文件

## 📊 成果量化模板

| 指标 | 改造前 | 改造后 |
|------|--------|--------|
| 部署HTTPS时间 | 2小时（手动申请、配置） | 5分钟（一键自动化） |
| 证书管理方式 | 手动下载、手动部署、手动续期 | 全自动（申请、部署、续期） |
| SSL Labs评分 | C级（配置不规范） | A+级（符合最佳实践） |
| 安全特性 | 仅基础HTTPS | HSTS + OCSP + TLS 1.3 + 安全头 |
| 证书过期风险 | 经常忘记续期，导致服务中断 | 自动续期，零风险 |
| 运维成本 | 每季度人工检查证书 | 全自动，零人工干预 |

## ❓ 面试高频问题

### 1. **Let's Encrypt证书有什么优缺点？**
**优点**：
- 完全免费，适合个人和中小企业
- 自动化程度高，支持自动申请和续期
- 全球信任，主流浏览器都支持
- 证书有效期90天，安全性更高（短有效期减少泄露风险）

**缺点**：
- 只提供域名验证（DV）证书，不提供企业验证（EV）证书
- 证书有效期短（90天），需要自动续期
- 对通配符证书支持有限（需要DNS验证）

### 2. **HTTPS和HTTP有什么区别？**
- **HTTP**：明文传输，数据可被窃取和篡改
- **HTTPS**：加密传输，数据安全
- **加密方式**：TLS/SSL协议，在HTTP下增加一层加密
- **端口**：HTTP使用80端口，HTTPS使用443端口
- **证书**：HTTPS需要SSL证书，由CA机构签发

### 3. **什么是HSTS？为什么重要？**
- **HSTS**：HTTP Strict Transport Security，强制浏览器使用HTTPS
- **作用**：防止降级攻击（攻击者强制用户使用HTTP）
- **配置**：`Strict-Transport-Security: max-age=63072000; includeSubDomains; preload`
- **max-age**：浏览器记住使用HTTPS的时间（63072000秒=2年）
- **preload**：提交到HSTS预加载列表，新用户首次访问也使用HTTPS

### 4. **什么是OCSP Stapling？有什么好处？**
- **OCSP**：Online Certificate Status Protocol，检查证书是否吊销
- **问题**：传统OCSP需要浏览器向CA服务器查询，增加延迟和隐私风险
- **OCSP Stapling**：服务器定期查询OCSP状态，并在TLS握手时"钉"在证书链中
- **好处**：减少延迟、保护隐私、提高性能

### 5. **Nginx配置中常见的安全头有哪些？**
- `X-Frame-Options`：防止点击劫持，禁止页面被嵌入iframe
- `X-Content-Type-Options`：防止MIME类型嗅探
- `X-XSS-Protection`：启用浏览器XSS过滤器
- `Content-Security-Policy`：定义允许加载资源的来源，防止XSS
- `Referrer-Policy`：控制Referer头信息，保护用户隐私

### 6. **证书过期了怎么办？有什么影响？**
**影响**：
- 浏览器显示安全警告，用户无法正常访问
- SEO排名下降
- API调用失败（很多API要求HTTPS）

**解决方案**：
1. 立即续期：`sudo certbot renew`
2. 重启Nginx：`sudo systemctl reload nginx`
3. 验证：浏览器访问网站，检查证书状态

**预防措施**：
- 配置自动续期（Certbot默认配置）
- 监控证书过期时间（可用Prometheus监控）
- 设置过期提醒（Certbot会发邮件提醒）

### 7. **如何监控SSL证书状态？**
```bash
# 1. 使用openssl检查证书过期时间
openssl s_client -connect 域名:443 2>/dev/null | openssl x509 -noout -dates

# 2. 使用Certbot检查
sudo certbot certificates

# 3. 编写监控脚本（可集成到Prometheus）
cat > /opt/scripts/check_ssl.sh << 'EOF'
#!/bin/bash
DOMAIN="example.com"
EXPIRE_DATE=$(echo | openssl s_client -servername $DOMAIN -connect $DOMAIN:443 2>/dev/null | openssl x509 -noout -enddate | cut -d= -f2)
EXPIRE_EPOCH=$(date -d "$EXPIRE_DATE" +%s)
CURRENT_EPOCH=$(date +%s)
DAYS_LEFT=$(( ($EXPIRE_EPOCH - $CURRENT_EPOCH) / 86400 ))
echo "SSL证书剩余天数: $DAYS_LEFT"
if [ $DAYS_LEFT -lt 30 ]; then
    echo "警告：证书即将过期！"
    # 发送告警（邮件/钉钉/企微）
fi
EOF
chmod +x /opt/scripts/check_ssl.sh
```

## 🔧 故障排查

### 问题1：证书申请失败
```bash
# 错误信息：DNS problem: NXDOMAIN looking up A for example.com
# 原因：域名解析未生效
# 解决：
nslookup example.com  # 检查解析是否正确
dig example.com       # 更详细的DNS查询
# 等待DNS生效（通常5-10分钟）
```

### 问题2：Nginx配置错误
```bash
# 错误信息：nginx: [emerg] bind() to 0.0.0.0:80 failed (98: Address already in use)
# 原因：80端口被占用
# 解决：
sudo lsof -i :80  # 查看占用80端口的进程
sudo kill -9 <PID>  # 停止占用进程
sudo systemctl restart nginx
```

### 问题3：HTTPS访问显示不安全
```bash
# 原因：混合内容（页面中加载了HTTP资源）
# 解决：
# 1. 检查浏览器控制台，找到HTTP资源
# 2. 将所有资源改为HTTPS或相对协议
# 3. 添加CSP头：Content-Security-Policy: upgrade-insecure-requests
```

## 📚 扩展学习

### 1. 通配符证书申请
```bash
# 申请通配符证书（需要DNS验证）
sudo certbot certonly --manual --preferred-challenges dns \
  -d "*.example.com" -d example.com

# 按照提示添加DNS TXT记录
# 验证：dig TXT _acme-challenge.example.com
```

### 2. 多域名证书（SAN证书）
```bash
# 申请包含多个域名的证书
sudo certbot --nginx \
  -d example.com \
  -d www.example.com \
  -d api.example.com \
  -d mail.example.com
```

### 3. 使用ACME.sh（Certbot替代方案）
```bash
# 安装ACME.sh
curl https://get.acme.sh | sh

# 申请证书
~/.acme.sh/acme.sh --issue -d example.com -d www.example.com --webroot /var/www/html

# 安装证书到Nginx
~/.acme.sh/acme.sh --install-cert -d example.com \
  --key-file /etc/letsencrypt/live/example.com/privkey.pem \
  --fullchain-file /etc/letsencrypt/live/example.com/fullchain.pem \
  --reloadcmd "systemctl reload nginx"
```

## 相关笔记

- [[20260730-CI-CD流水线搭建|CI/CD 流水线搭建]] — 证书自动部署可集成到CI/CD
- [[20260730-Prometheus监控体系|Prometheus 监控体系]] — 监控证书过期状态
- [[20260730-K8s容器编排实战|K8s 容器编排实战]] — 在K8s中管理证书
- [[简历项目实战-MOC|返回专栏首页]]
