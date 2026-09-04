# 02 - 安装 Nginx（实操记录）

> 环境：阿里云轻量应用服务器，Ubuntu 22.04，2核1G
> 本文记录真实执行过的命令，每条都带解释。

## 1. 连接到服务器
通过阿里云控制台的 **Workbench 远程连接**进入网页终端。

首次连接提示：
```
Are you sure you want to continue connecting (yes/no/[fingerprint])?
```
- 含义：第一次连这台机器，SSH 让你确认指纹（防止中间人攻击）
- 操作：输入 `yes` 回车

登录后默认是普通用户，切到 root：
```bash
sudo -i
# sudo = 以管理员(root)权限执行
# -i = 加载 root 的登录环境(interactive)，拿到干净的 root shell
```
成功后提示符变成 `root@主机名:~#`。

## 2. 更新软件包索引
```bash
apt update && apt upgrade -y
# apt update  = 刷新本地软件包清单（不安装，只同步列表）
# &&          = 前一条成功才执行后一条
# apt upgrade = 升级所有已安装的旧包
# -y          = 自动对所有提示回答 yes，免手动确认
```

### ⚠️ 踩坑：Waiting for cache lock
可能看到：
```
Waiting for cache lock: Could not get lock /var/lib/dpkg/lock-frontend ...
```
- 原因：阿里云开机时后台自动跑 `unattended-upgrades`，占用了 apt 锁
- 解决：等它跑完，或
```bash
kill 占用PID   # 强杀占用进程
rm /var/lib/dpkg/lock-frontend
rm /var/lib/dpkg/lock
dpkg --configure -a   # 修复被中断的包配置状态
```

## 3. 安装并启动 Nginx
```bash
apt install nginx -y
# 安装时若弹出 "Which services should be restarted" → Tab选<Ok>回车即可

systemctl start nginx     # 启动服务
systemctl enable nginx    # 设开机自启（enable=加入systemd启动序列）
systemctl status nginx    # 查看状态，看到 active (running) 即成功
```
退出 status 界面按 `q`。

## 4. 配置防火墙（UFW）
```bash
ufw status          # 查看防火墙状态，初始通常是 inactive
ufw enable          # 启用防火墙，会警告可能断SSH，输入 y
ufw allow 'Nginx Full'   # 放行 80(HTTP) + 443(HTTPS) 端口
ufw status          # 确认出现 Nginx Full ALLOW Anywhere
```
> `Nginx Full` 是 UFW 预设的应用配置，等价于放行 80 和 443 两个端口。

## 5. 验证
浏览器打开 `http://<公网IP>` → 看到 **Welcome to nginx!** = 安装成功。

✅ 此阶段完成。下一步：03-HTTPS配置.md
