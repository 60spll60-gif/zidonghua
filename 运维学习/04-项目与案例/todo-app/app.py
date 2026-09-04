# app.py - 待办清单 Web 应用（Flask + MySQL）
# 这是你的"货物"：一个能存待办事项的小网站
import os
import pymysql
from flask import Flask, request, redirect, render_template_string

app = Flask(__name__)

# 数据库连接信息从"环境变量"读取（docker-compose.yml 里配置）
# 这样代码和配置分离：改配置不用改代码
DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "123456")
DB_NAME = os.getenv("DB_NAME", "todo")


def get_db():
    """建立数据库连接"""
    return pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        charset="utf8mb4",
    )


def init_db():
    """启动时建表（演示用；生产环境应该用 Alembic 这类迁移工具）"""
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS todos (
            id INT AUTO_INCREMENT PRIMARY KEY,
            content VARCHAR(255) NOT NULL,
            done TINYINT DEFAULT 0
        )
        """
    )
    conn.commit()
    conn.close()


@app.route("/")
def index():
    """首页：展示所有待办"""
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT id, content, done FROM todos ORDER BY id DESC")
    rows = cur.fetchall()
    conn.close()
    items = "".join(
        f"<li>{'✅' if d else '⬜'} {c} <a href='/delete/{i}'>删除</a></li>"
        for i, c, d in rows
    )
    return render_template_string(
        """
        <h1>📝 我的待办清单</h1>
        <form method="POST" action="/add">
            <input name="content" placeholder="写点什么..." required>
            <button>添加</button>
        </form>
        <ul>{{ items|safe }}</ul>
        """,
        items=items or "<li>还没有待办，添加一个吧</li>",
    )


@app.route("/add", methods=["POST"])
def add():
    """添加一条待办"""
    content = request.form["content"]
    conn = get_db()
    cur = conn.cursor()
    cur.execute("INSERT INTO todos (content) VALUES (%s)", (content,))
    conn.commit()
    conn.close()
    return redirect("/")


@app.route("/delete/<int:todo_id>")
def delete(todo_id):
    """删除一条待办"""
    conn = get_db()
    cur = conn.cursor()
    cur.execute("DELETE FROM todos WHERE id = %s", (todo_id,))
    conn.commit()
    conn.close()
    return redirect("/")


if __name__ == "__main__":
    init_db()
    # host=0.0.0.0 表示接受容器外（宿主机）的访问
    app.run(host="0.0.0.0", port=5000)
