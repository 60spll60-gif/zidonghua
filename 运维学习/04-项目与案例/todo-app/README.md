# Todo 应用容器化部署 —— 第一个运维实战项目

> 目标：亲手把「一个 Flask 网页应用 + 一个 MySQL 数据库」用 Docker 跑起来，
> 并掌握日常运维操作。全程在 Windows + Docker Desktop 完成，零成本。

## 项目结构

```
todo-app/
├── app.py              # Flask 应用代码（待办清单）
├── requirements.txt    # Python 依赖清单
├── Dockerfile          # 把应用打包成镜像的说明书
├── docker-compose.yml  # 编排：web + db 两个服务
└── .dockerignore       # 打包时排除的文件
```

## 快速开始

```bash
# 1. 启动（第一次会自动构建镜像 + 拉取 MySQL 镜像）
docker-compose up -d

# 2. 看是否启动成功
docker-compose ps

# 3. 浏览器打开
#    http://localhost:5000

# 4. 看日志
docker-compose logs -f web

# 5. 停止（数据保留）
docker-compose down

# 6. 停止并清掉数据卷（数据也没了，慎用）
docker-compose down -v
```

## 六个阶段学习路线

| 阶段 | 做什么 | 核心知识点 |
|------|--------|-----------|
| 0 | 装 Docker Desktop | 镜像/容器/仓库三概念 |
| 1 | 写应用代码 | 代码与配置分离（环境变量） |
| 2 | 写 Dockerfile | 镜像构建、层缓存 |
| 3 | 写 docker-compose.yml | 多容器编排、网络、数据卷 |
| 4 | 跑起来并验证 | up/ps/logs、健康检查 |
| 5 | 日常运维操练 | 重启、进容器、看日志、备份 |
| 6 (进阶) | 接 CI/CD | 提交代码自动构建部署 |

## 常用运维命令速查

```bash
docker-compose ps                  # 看所有服务状态
docker-compose logs -f web         # 实时看 web 日志
docker exec -it todo-web bash      # 进入应用容器内部
docker exec -it todo-db mysql -uroot -p123456   # 进入 MySQL 命令行
docker-compose restart web         # 重启 web（代码改了要重建：up -d --build）
docker-compose down                # 停止并删除容器（卷保留）
docker system prune -a             # 清理无用镜像/缓存（慎用）
docker volume ls                   # 查看数据卷
```

## 常见问题

- **访问 localhost:5000 打不开**：先 `docker-compose ps` 看状态，再看 `docker-compose logs web`
- **web 一直重启**：多半是连不上数据库，检查环境变量 DB_HOST 是不是 `db`，数据库健康检查是否通过
- **端口被占用**：改 docker-compose.yml 里 `ports` 的左边数字（如 5001:5000）
- **改代码不生效**：代码在镜像里，需要 `docker-compose up -d --build` 重新构建
