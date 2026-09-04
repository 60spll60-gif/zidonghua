# Dockerfile - 把应用打包成"集装箱"（镜像）的说明书
# 每一行指令都会生成一个"层"，改代码时只重跑后面的层，构建更快

# 第 1 步：选基础镜像。python:3.12-slim = 官方 Python 精简版（小、安全、够用）
FROM python:3.12-slim

# 第 2 步：设置容器内的工作目录（进去之后默认在这个目录干活）
WORKDIR /app

# 第 3 步：先复制依赖清单并安装。
# 为什么先复制 requirements.txt 而不是 app.py？
# Docker 构建有"层缓存"：只要这一层输入没变，就直接复用缓存。
# 依赖列表不常变，代码经常变——所以把不常变的东西放前面，改代码就不用重新装依赖
COPY requirements.txt .
RUN pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 第 4 步：复制应用代码（代码改动了，只重新执行这一步和之后的部分）
COPY app.py .

# 第 5 步：声明容器对外端口（声明而已，真正映射端口在 docker-compose 的 ports 里做）
EXPOSE 5000

# 第 6 步：容器启动时执行的命令
CMD ["python", "app.py"]
