import sqlite3  # 用于与SQLite数据库进行交互的包
import jieba  # 用于中文分词的包
from flask import Flask, render_template
#导入Flask，用于创建Flask应用程序对象
#导入render_template函数，用于渲染HTML模板

app = Flask(__name__)  # 创建Flask应用程序对象

@app.route('/')  # 定义根路径的路由
def index():
    return render_template("index.html")  # 渲染index.html模板并返回

@app.route('/movie')  # 定义/movie路径的路由
def movie():
    movies = []
    conn = sqlite3.connect('movie.db')  # 连接SQLite数据库
    cursor = conn.cursor()
    sql = "select * from movie250"  # 查询movie250表的所有数据
    data = cursor.execute(sql)
    for item in data:
        movies.append(item)
    cursor.close()
    conn.close()

    return render_template("movie.html", movies=movies)  # 渲染movie.html模板并返回，传入movies数据

@app.route('/team')  # 定义/team路径的路由
def team():
    return render_template("team.html")  # 渲染team.html模板并返回

@app.route('/word')  # 定义/word路径的路由
def word():
    return render_template("word.html")  # 渲染word.html模板并返回

@app.route('/rate')  # 定义/rate路径的路由
def rate():
    score = []  # 评分
    score_number = []  # 评分数目
    conn = sqlite3.connect("movie.db")  # 连接SQLite数据库
    cursor = conn.cursor()
    sql = "select score,count(score) from movie250 group by score"  # 按评分分组统计数量
    data = cursor.execute(sql)
    for item in data:
        score.append(item[0])
        score_number.append(item[1])
    cursor.close()
    conn.close()
    return render_template("rate.html", score=score, num=score_number)  # 渲染rate.html模板并返回，传入score和num数据

@app.route('/home')  # 定义/home路径的路由
def home():
    return index()  # 返回index函数的执行结果


if __name__ == '__main__':
    app.run()  # 运行Flask应用程序

