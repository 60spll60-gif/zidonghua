# 03 - 配置 HTTPS（实操记录）

> 说明：本项目原计划用 Let's Encrypt 申请域名证书，但国内服务器域名**需先ICP备案**
> 才能通过域名解析正常访问。在备案完成前，先用**自签名证书**跑通完整HTTPS链路，
> 等备案+解析生效后，再用 Certbot 换成正式证书。

## 1. 安装 Certbot（为后续正式证书准备）
```bash
apt install certbot python3-certbot-nginx -y
# certbot              = Let's Encrypt 官方证书客户端
# python3-certbot-nginx = Certbot 的 Nginx 插件，能自动改Nginx配置
```

## 2. 生成自签名 SSL 证书
```bash
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout /etc/ssl/private/nginx-selfsigned.key \
  -out /etc/ssl/certs/nginx-selfsigned.crt
```
逐参数解释：
| 参数 | 含义 |
|------|------|
| `req -x509` | 直接生成自签名证书（x509格式），而非仅生成证书请求 |
| `-nodes` | no DES，私钥不加密，Nginx启动时不用输密码 |
| `-days 365` | 有效期365天 |
| `-newkey rsa:2048` | 同时新建 2048位 RSA 密钥对 |
| `-keyout` | 私钥输出路径（保密，权限 600） |
| `-out` | 证书输出路径（公开，权限 644） |

执行后会问国家/省/市/组织等，**Common Name 填服务器公网IP** `101.200.51.101`。

验证文件生成：
```bash
ls -la /etc/ssl/private/nginx-selfsigned.key /etc/ssl/certs/nginx-selfsigned.crt
# .key 是 -rw-------（仅root可读，对）  .crt 是 -rw-r--r--（公开，对）
```

## 3. 创建 SSL 配置片段
```bash
nano /etc/nginx/snippets/ssl-selfsigned.conf
```
写入：
```nginx
ssl_certificate     /etc/ssl/certs/nginx-selfsigned.crt;
ssl_certificate_key /etc/ssl/private/nginx-selfsigned.key;
ssl_protocols       TLSv1.2 TLSv1.3;   # 只允许安全的TLS版本
```
nano 保存：`Ctrl+O` → 回车 → `Ctrl+X` 退出。

## 4. 配置 Nginx 站点
先备份（好习惯）：
```bash
cp /etc/nginx/sites-available/default /etc/nginx/sites-available/default.backup
```
写入双 server 块（HTTP + HTTPS）：
```bash
cat > /etc/nginx/sites-available/default << 'EOF'
server {
    listen 80 default_server;
    server_name _;
    root /var/www/html;
    index index.html;
    location / { try_files $uri $uri/ =404; }
}
server {
    listen 443 ssl default_server;
    server_name _;
    root /var/www/html;
    index index.html;
    include snippets/ssl-selfsigned.conf;   # 引用上面的SSL配置
    location / { try_files $uri $uri/ =404; }
}
EOF
```

## 5. 测试 + 重载
```bash
nginx -t            # 测试配置语法，必须显示 test is successful
systemctl reload nginx   # reload=不中断地重新加载配置（比restart安全）
```

## 6. 验证 HTTPS
浏览器访问 `https://<公网IP>`：
- 出现"您的连接不是私密连接"= **正常**（自签名证书浏览器不信任）
- 点"高级 → 继续前往"，能看到页面 = HTTPS 链路跑通

## ⚠️ 踩坑：403 Forbidden
若访问返回 `403`：说明 Nginx 正常，只是 `/var/www/html/` 下**没有 index.html**。
```bash
echo '<h1>Nginx + HTTPS 部署成功</h1>' > /var/www/html/index.html
```

## ⚠️ 踩坑：echo 写中文导致乱码
用 `echo '中文...' > index.html` 时，浏览器打开是乱码（如"部署成功"变"鑷鍔熷姛"）。

- **原因**：echo 把中文作为**命令文本**经 Windows(GBK) → SSH通道 → Linux(UTF-8)，编码链路不一致
- **关键**：这是命令传输问题，与 HTTPS/证书/Nginx **无关**

### 解决：
| 场景 | 方法 |
|------|------|
| 临时测试页 | 用 `printf` 写**纯英文**（避开中文传输） |
| 含中文的真实页面 | **文件上传**或**服务器端 curl 直接拉取**（二进制传输，UTF-8原样保留） |

```bash
# 最终部署知识库仪表盘：让服务器直接下载已部署的页面（中文0乱码）
curl -L -o /var/www/html/index.html "https://.../index.html"
```

> ✅ 验证：`https://101.200.51.101` 浏览器显示仪表盘完整、中文正常、地址栏带锁(HTTPS)。
> 至此自签名 HTTPS 项目核心目标全部达成。下一步 04：换正式证书 + 自动续签。
