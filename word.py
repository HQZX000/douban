from wordcloud import WordCloud
import sqlite3
from matplotlib import pyplot as plt
from PIL import Image
import numpy as np
import jieba

# 列表指出要去掉的虚词
stopwords = ["的", "了", "是", "我", "你", "他","都","最","就是","世界","让","一个","和","在"]

# 要保留的关键词列表
keywords = ["电影", "永恒的", "爱", "人", "幸福", "孤独"]

conn = sqlite3.connect("movie.db")
cursor = conn.cursor()
sql = 'select inq from movie250'
data = cursor.execute(sql)
text = ''
for item in data:
    text += item[0]
cursor.close()
conn.close()

cut = jieba.cut(text)
words = ' '.join([word for word in cut if word not in stopwords or word in keywords])

img = Image.open("static/assets/img/3.jpg")
img_array = np.array(img)

wc = WordCloud(
    background_color="white",
    mask=img_array,
    font_path="simhei.ttf"
)

wc.generate_from_text(words)

fig = plt.figure(1)
plt.imshow(wc)
plt.axis("off")
plt.savefig("static/assets/img/word3.jpg", dpi=600)
