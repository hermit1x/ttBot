import json, os
from functools import cmp_to_key
from PIL import Image, ImageDraw, ImageFont
from plugins.identify import id_func, SU
import time

long_term = [] # {name="", done=T/F}
short_term = [] # {name="", parts=ini, part_name="", to_part="", time=""}
dir_path = os.getcwd() + '/data/todo/'

def init():
    global long_term, short_term
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
    
    try:
        with open(dir_path + 'long_term.json', 'r', encoding = 'utf-8') as f:
            long_term = json.load(f)
    except FileNotFoundError:
        with open(dir_path + 'long_term.json', 'w', encoding = 'utf-8') as f:
            json.dump(long_term, f)

    try:
        with open(dir_path + 'short_term.json', 'r', encoding = 'utf-8') as f:
            short_term = json.load(f)
    except FileNotFoundError:
        with open(dir_path + 'short_term.json', 'w', encoding = 'utf-8') as f:
            json.dump(short_term, f)

    print('[+] todo组件初始化成功')

init()

def write_json():
    with open(dir_path + 'long_term.json', 'w', encoding = 'utf-8') as f:
        json.dump(long_term, f)
    with open(dir_path + 'short_term.json', 'w', encoding = 'utf-8') as f:
        json.dump(short_term, f)
    
def short_cmp(t1, t2):
    if t1['done'] != t2['done']:
        if t1['done'] == True:
            return 1
        else:
            return -1
    return len(t1['name']) - len(t2['name'])

def long_cmp(t1, t2):
    return -t1['to_part']/t1['parts'] + t2['to_part']/t2['parts']

def once_modify():
    short_term.sort(key = cmp_to_key(short_cmp))
    long_term.sort(key = cmp_to_key(long_cmp))
    write_json()
    if os.path.exists(dir_path + 'todo.png'):
        os.remove(dir_path + 'todo.png')

def get_font(id, size):
    FONTS_PATH = 'src/fonts'
    if id == 'wh':
        return ImageFont.truetype(os.path.join(FONTS_PATH, '汉仪文黑.ttf'), size)
    if id == 'num':
        return ImageFont.truetype(os.path.join(FONTS_PATH, 'JetBrainsMono-ExtraBold-6.ttf'), size)

white = (0xff, 0xff, 0xff, 0xff)
black = (0x00, 0x00, 0x00, 0xff)
gray = (0xe0, 0xe0, 0xe0, 0xff)
dark_blue = (0x0f, 0x1f, 0x3f, 0xff)

def draw_short(id, T):
    width = 800
    height = 100

    # 先画左边那个小框框
    check = Image.open(os.getcwd() + '/src/check.png')
    check = check.resize((75, 70))
    check_box = Image.new('RGBA', (75, 70), (0xdf, 0xdf, 0xdf, 0xff))
    draw_check = ImageDraw.Draw(check_box)
    # draw.rectangle((15, 15, 90, 85), fill=(0xbf, 0xbf, 0xbf, 0xff))
    draw_check.text((5, 2), str(id).zfill(2), fill=dark_blue, font=get_font('num', 55))
    check = Image.blend(check, Image.new("RGBA", (75, 70), (0, 0, 0, 0)), 0.2)
    if T['done']:
        check_box.paste(check, (0, 0), mask=check)

    # 再画大框框和字
    img = Image.new('RGBA', (width, height), white)
    draw = ImageDraw.Draw(img)
    draw.text((120, 16), str(T['name']), fill=black, font=get_font('wh', 60))
    img.paste(check_box, (15, 15))
    # img.save(img_path)
    return img


def draw_long(id, T):
    width = 800
    height = 160
    img = Image.new('RGBA', (width, height), white)
    draw = ImageDraw.Draw(img)

    # id的小框
    x0, y0 = 20, 90
    w0, h0 = 140, 50
    id = "{0:#0{1}x}".format(id,4)
    draw.rectangle((x0, y0, x0 + w0, y0 + h0), fill = gray)
    draw.text((x0 + 10, y0), id, fill = dark_blue, font = get_font('wh', 45))

    # name
    x1, y1 = 20, 20
    w1, h1 = 600, 60
    draw.rectangle((x1, y1, x1 + w1, y1 + h1), fill = gray)
    text = T['name']
    draw.text((x1 + 10, y1 + 8), text, fill = black, font=get_font('wh', 40))

    # part name
    x2, y2 = 170, 90
    w2, h2 = x1 + w1 - x2, 50
    draw.rectangle((x2, y2, x2 + w2, y2 + h2), fill = (0xef, 0xef, 0xef, 0xff))
    draw.text((x2 + 10, y2 + 5), '事项进度：' + T['part_name'], fill = black, font=get_font('wh', 20))
    # time
    x3, y3 = x2, y2 + 20
    draw.text((x3 + 10, y3 + 5), '上次更新：' + T['time'], fill = black, font=get_font('wh', 20))

    # 圈圈
    x4, y4 = 720, 80
    r4 = 70
    draw.ellipse((x4 - r4, y4 - r4, x4 + r4, y4 + r4), fill = None, outline = (0xa0, 0xa0, 0xa0, 0xff), width = 35)
    start = -90
    end = -90 + 360 * T['to_part'] / T['parts']
    draw.arc((x4 - r4, y4 - r4, x4 + r4, y4 + r4), fill = (0x00, 0xff, 0x00, 0xff), start = start, end = end, width = 35)
    

    # 进度字样
    x4, y4 = x2 + 330, y3 + 5
    draw.text((x4, y4), '进度：' + str(T['to_part']).zfill(2) + '/' + str(T['parts']).zfill(2), fill = black, font = get_font('wh', 20))
    return img

def draw_todo():
    img_path = dir_path + '/todo.png'

    if os.path.exists(img_path):
        return img_path

    height = 104 * len(short_term) + 164 * len(long_term) + 280
    width = 960
    img = Image.new('RGBA', (width, height), gray)
    draw = ImageDraw.Draw(img)
    draw.text((300, 20), '短期事项', fill = dark_blue, font = get_font('wh', 80))
    px = 80
    py = 120
    idx = 0
    for i in short_term:
        img.paste(draw_short(idx, i), (px, py))
        idx = idx + 1
        py = py + 102

    py = py + 30
    draw.text((300, py), '长期事项', fill = dark_blue, font = get_font('wh', 80))
    py = py + 100
    idx = 0
    for i in long_term:
        img.paste(draw_long(idx, i), (px, py))
        idx = idx + 1
        py = py + 164
    img.save(img_path)
    return img_path

async def show_todo(event, bot):
    print('[+] 触发show_todo')
    await bot.send(event, f'[CQ:image,file=files:///{draw_todo()}]')

def get_time_str():
    return time.strftime("%Y/%m/%d %H:%M", time.localtime())

async def add_todo(T, event, bot):
    print('[+] 触发add_todo')
    T = T.replace("'", '"')
    try:
        T = json.loads(T)
    except json.decoder.JSONDecodeError:
        await bot.send(event, '格式错了，改一改再试试呢')
        return
    
    if not 'type' in T:
        await bot.send(event, '缺少事件类型，改一下再试试呢')
        return
    if not 'name' in T:
        await bot.send(event, '缺少事件名，改一下再试试呢')
        return
    
    if T['type'] == 'short':
        short_term.append({'name': T['name'], 'done': False})
        once_modify()
        await bot.send(event, '添加成功')
        await show_todo(event, bot)
        return
    elif T['type'] == 'long':
        if not 'parts' in T or type(T['parts']) != int:
            await bot.send(event, '总进度参数错误')
            return
        if 'part' in T and type(T['part']) == int and 'pname' in T:
            to_part = T['part']
            part_name = T['pname']
        else:
            to_part = 0
            part_name = 'None'
        time_str = get_time_str()
        long_term.append({
                    'name': T['name'],
                    'parts': T['parts'],
                    'to_part': to_part,
                    'part_name': part_name,
                    'time': time_str
                })
        once_modify()
        await bot.send(event, '添加成功')
        await show_todo(event, bot)
        return
    else:
        await bot.send(event, 'type参数错误')
        return

async def done_todo(T, event, bot):
    print('[+] 触发done_todo')
    if T.isdigit():
        T = int(T)
        if T < len(short_term):
            short_term[T]['done'] = True
            once_modify()
            await bot.send(event, '记下了！')
            return
        else:
            await bot.send(event, 'IndexError!!!你个傻逼!')
            return
    else:
        T = T.replace("'", '"')
        try:
            T = json.loads(T)
        except json.decoder.JSONDecodeError:
            await bot.send(event, '格式错了，改一改再试试呢')
            return
        if 'id' in T and 'part' in T and 'pname' in T:
            time_str = get_time_str()
            id = int(T['id'], base = 16)
            if id < len(long_term):
                long_term[id]['time'] = time_str
                long_term[id]['to_part'] = T['part']
                long_term[id]['part_name'] = T['pname']
                once_modify()
                await bot.send(event, '记下了')
                return
            else:
                await bot.send(event, 'IndexError!!!你个傻逼!')
                return
        else:
            await bot.send(event, '缺参数了！')
            return


    
async def del_todo(id, event, bot):
    print('[+] 触发del_todo')
    if id[:2] == '0x':
        try:
            id = int(id, base=16)
        except ValueError:
            await bot.send(event, 'ValueError!!!你个傻逼!')
            return
        else:
            if id < len(long_term):
                long_term.pop(id)
                once_modify()
                await bot.send(event, '删除成功了喔')
                return
            else:
                await bot.send(event, 'IndexError!!!你个傻逼!')
                return
    else:
        try:
            id = int(id)
        except ValueError:
            await bot.send(event, 'ValueError!!!你个傻逼!')
            return
        else:
            if id < len(short_term):
                short_term.pop(id)
                once_modify()
                await bot.send(event, '删除成功了喵')
                return
            else:
                await bot.send(event, 'IndexError!!!你个傻逼!')
                return

async def todo(event, bot):
    msg = str(event.message)
    if msg[:5] != '-todo':
        return False

    if not id_func(event, 'todo'):
        return True
    
    if msg == '-todo':
        await show_todo(event, bot)
        return True
    
    if not event.user_id in SU:
        await bot.send(event, 'QAQ 只有华华可以改自己的todolist...')
        return True
    
    msg = msg[6:]
    if msg[:3] == 'add':
        await add_todo(msg[4:], event, bot)
    elif msg[:4] == 'done':
        await done_todo(msg[5:], event, bot)
    elif msg[:3] == 'del':
        await del_todo(msg[4:], event, bot)
    else:
        await bot.send(event, '指令错了喵')
    return True
