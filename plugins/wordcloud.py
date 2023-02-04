from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator
import json
import time
import random
import jieba
import string
import jieba.analyse
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
from colorthief import ColorThief
import cv2
from urllib.request import urlretrieve
from nonebot.adapters.cqhttp import MessageSegment
from plugins.identify import id_func
import os


def record_for_wordcloud(event):
    if event.message_type == 'group':
        gid = event.group_id
        rmsg = str(event.message).strip()
        msgs = rmsg.split('[')
        for i in msgs:
            if i.startswith('CQ:'):
                j = i.split(']')[1]
            else:
                j = i
            if j != '':
                with open(f'data/wordcloud/rec_{gid}_{event.user_id}.txt', 'a') as f:
                    f.write(j + '。')

def GenerateFilename():
    return r''.join(random.sample(string.ascii_letters + string.digits, 16))
    


async def wordcloud(event, bot):
    if not '查成分' == event.message[:3]:
        return False
    if not id_func(event, 'wordcloud'):
        return True
    gid = event.group_id
    print('[·] 触发词云')
    content = event.message[3:].strip()
    if content == "":
        await bot.send(event, "请在查成分三个字后面at想查的人喵")
        return True

    if not (content.startswith("[CQ:at,qq=") and content.endswith("]")):
        await bot.send(event, '错了哦')
        return True

    # 进入主程序
    content = content.strip("[CQ:at,qq=")
    content = content.strip("]")
    uid = int(content)
    try:
        with open(f"data/wordcloud/rec_{gid}_{uid}.txt", "r") as f:
            rec = f.read()
    except:
        await bot.send(event, "[x] 发言记录获取失败。可能是还没在群里说过话？")
        return True

    try:
        avartar = "data/wordcloud/" + GenerateFilename() + ".jfif"
        urlretrieve(f"http://q.qlogo.cn/headimg_dl?dst_uin={uid}&spec=640&img_type=jpg", avartar)
    except:
        await bot.send(event, "[x] QQ头像获取失败。")
        return True

    try:
        words = jieba.analyse.extract_tags(rec, 300)
        txt = ' '.join(words)
    except:
        os.remove(avartar)
        await bot.send(event, "[x] 分词失败。")
        return True

    try:
        mask = np.array(Image.open(avartar))
        color_thief = ColorThief(avartar)
        dominant_color = color_thief.get_color(quality=1)

        wc = WordCloud(
            background_color = dominant_color,
            height = 300,
            width = 300,
            max_font_size = 50,
            mask = mask,
            repeat = True,
            font_path = 'src/fonts/msyh.ttc',
            stopwords = STOPWORDS,
        )
        wc.generate_from_text(txt)
        img_colors = ImageColorGenerator(mask)
        wc = wc.recolor(color_func=img_colors)
        wordcloud_img = "data/wordcloud/" + GenerateFilename() + ".jpg"
        wc.to_file(wordcloud_img)
    except Exception as ex:
        os.remove(avartar)
        await bot.send(event, "[x] 词云生成失败。")
        return True

    try:
        bottom = cv2.imread(avartar)
        top = cv2.imread(wordcloud_img)
        overlapping = cv2.addWeighted(bottom, 0.35, top, 0.65, 0)
        overlap_img = "data/wordcloud/" + GenerateFilename() + ".jpg"
        cv2.imwrite(overlap_img, overlapping)
    except:
        os.remove(avartar)
        os.remove(wordcloud_img)
        await bot.send(event, "[x] 图片渲染失败。")
        return True
    
    img_path = os.getcwd() + '/' + overlap_img
    await bot.send(event, f'[CQ:image,file=files:///{img_path}]')
    os.remove(avartar)
    os.remove(overlap_img)
    os.remove(wordcloud_img)
    return True