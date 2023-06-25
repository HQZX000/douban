import sqlite3  # 用于与SQLite数据库进行交互的包
import urllib.error  # 用于处理与HTTP请求相关的错误
import urllib.request  # 用于发送HTTP请求和获取远程数据
import re  # 用于进行正则表达式匹配和操作的包
import xlwt  # 用于创建和操作Microsoft Excel文件（.xls格式）的包
from bs4 import BeautifulSoup  # 用于解析HTML和XML文档，从网页中提取数据的包

def gethtml(url):
    # 创建一个请求头，包括用户代理信息，用于发送请求时模拟浏览器
    head = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36 Edg/113.0.1774.57',
    }

    # 创建一个包含请求头的请求对象，指定要访问的 URL
    request = urllib.request.Request(url, headers=head)
    try:
        # 发送请求并获取响应
        response = urllib.request.urlopen(request)
        # 读取响应的内容，并使用 UTF-8 解码为字符串
        html = response.read().decode("utf-8")
        # 返回获取到的 HTML 内容
        return html
    except urllib.error.URLError as e:
        # 处理异常，例如网络连接错误等
        if hasattr(e, "code") and hasattr(e, "reason"):
            print(e.reason)
            print(e.code)



def dealhtml(baseurl):
    alldata = []

    # 正则表达式模式：匹配电影名称
    pat_name = re.compile('<span class="title">(.*)</span>')
    # 正则表达式模式：匹配电影链接
    pat_link = re.compile('<a href="(.*?)">')
    # 正则表达式模式：匹配电影图片链接
    pat_img = re.compile(r'<img.*src="([\S]*\.jpg)".*>', re.S)
    # 正则表达式模式：匹配电影评分
    pat_rate = re.compile('<span class="rating_num" property="v:average">(.*)</span>')
    # 正则表达式模式：匹配电影评价人数
    pat_pnumber = re.compile(r'<span>(\d*)人评价</span>')
    # 正则表达式模式：匹配电影简介
    pat_inp = re.compile('<span class="inq">(.*)</span>')
    # 正则表达式模式：匹配电影内容
    pat_content = re.compile('<p class="">(.*?)</p>', re.S)

    # 遍历页码，每页有 10 个条目
    for i in range(0, 10):
        # 拼接 URL
        url = baseurl + str(i * 25)
        html = gethtml(url)  # 调用 gethtml 函数获取 HTML 内容
        soup = BeautifulSoup(html, "html.parser")

        # 遍历每个条目
        for item in soup.find_all('div', class_="item"):
            data = []
            item = str(item)
            name = pat_name.findall(item)  # 匹配电影名称
            if len(name) == 2:
                name = name[:1]
            data.append(name[0])
            link = pat_link.findall(item)[0]  # 匹配电影链接
            data.append(link)
            img = pat_img.findall(item)[0]  # 匹配电影海报图片链接
            data.append(img)
            rate = pat_rate.findall(item)[0]  # 匹配电影评分
            data.append(rate)
            pnumber = pat_pnumber.findall(item)[0]  # 匹配评价人数
            data.append(pnumber)
            inq = pat_inp.findall(item)  # 匹配电影引语
            if len(inq) != 0:
                inq = inq[0].replace("。", "")
                data.append(inq)
            else:
                data.append(" ")
            content = pat_content.findall(item)[0]  # 匹配电影简介
            # 除去空格和无关字符
            content = re.sub(r'<br(\s+)?/>(\s+)?', " ", content)
            content = re.sub(r'/', " ", content)
            content = content.strip()
            data.append(content)
            alldata.append(data)

    return alldata


def dbcreate(dbpath):
    sql = """ 
            create table movie250
            (
            id integer  primary key autoincrement,
            movie_name varchar ,
            img_link text,
            link text,
            score numeric ,
            pnumber numeric ,
            inq text,
            info text 
            )
    """
    conn = sqlite3.connect(dbpath)  # 连接SQLite数据库
    cursor = conn.cursor()  # 创建游标对象
    cursor.execute(sql)  # 执行SQL创建表格语句
    conn.commit()  # 提交事务
    cursor.close()  # 关闭游标
    conn.close()  # 关闭数据库连接

def savedatadb(datalist, dbpath):
    dbcreate(dbpath)  # 创建数据库表格
    conn = sqlite3.connect(dbpath)  # 连接SQLite数据库
    cur = conn.cursor()  # 创建游标对象

    for data in datalist:
        for index in range(len(data)):
            if index == 3 or index == 4:
                continue
            data[index] = '"' + data[index] + '"'  # 将特定字段加上双引号

        sql = """
            insert into movie250(
            movie_name,link,img_link,score,pnumber,inq,info)
            values(%s)""" % ",".join(data)  # 构建插入数据的SQL语句
        cur.execute(sql)  # 执行插入数据的SQL语句
        conn.commit()  # 提交事务
    cur.close()  # 关闭游标
    conn.close()  # 关闭数据库连接


if __name__ == "__main__":
    baseurl = "https://movie.douban.com/top250?start="
    datalist = dealhtml(baseurl)  # 获取电影数据列表
    dbpath = "movie.db"  # 数据库文件路径
    savedatadb(datalist, dbpath)  # 保存电影数据到数据库

    # excel保存数据
    book = xlwt.Workbook(encoding="utf-8", style_compression=0)  # 创建Excel工作簿
    sheet = book.add_sheet("豆瓣电影top250", cell_overwrite_ok=True)  # 添加工作表
    col = ("电影名称", "电影图片链接", "电影链接", "评分", "评论人数", "简评", "概况")  # 列名
    for i in range(0, 7):
        sheet.write(0, i, col[i])  # 写入列名

    for i in range(0, 250):
        data = datalist[i]  # 获取一部电影的数据
        for j in range(0, 7):
            sheet.write(i+1, j, data[j])  # 写入电影数据

    book.save("movie.xls")  # 保存Excel文件

