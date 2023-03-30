from plugins.identify import id_func
import datetime
headcount = 0
daytag = datetime.datetime.now().day

print('[+] 机厅人数初始化成功')

def update(opt, x):
    global daytag, headcount
    daynow = datetime.datetime.now().day
    if daynow != daytag:
        daytag = daynow
        headcount = 0
    if opt == '+':
        headcount = headcount + x
    if opt == '-':
        headcount = headcount - x
    if opt == '=':
        headcount = x

def inrange(x):
    if x < 0 or x > 40:
        return False
    return True

async def maihc(event, bot):
    global headcount
    if id_func(event, 'maihc') == False:
        return False
    msg = event.message
    query_cmd = ['机厅几人', '机厅几人？', '几人', '几？', '几']
    if msg in query_cmd:
        await bot.send(event, '机厅现有 ' + str(headcount) + ' 人。')
        if headcount == 0:
            await bot.send(event, '零卡陷阱生效中')
        if headcount == 1:
            await bot.send(event, '我超 有人吧唧 快来')
        if headcount >= 6:
            await bot.send(event, '我超 大逼队 快跑')
        return True

    if msg[:2] == '机厅' and msg[-1] == '人' and msg[2:-1].strip().isdigit():
        if inrange(int(msg[2:-1].strip())):
            update('=', int(msg[2:-1].strip()))
            await bot.send(event, '记着了！机厅现有 ' + str(headcount) + ' 人。')
        else:
            await bot.send(event, '不许玩bot，傻卵')
        return True
    
    if msg[-1] == '卡' or msg[-1] == '人':
        msg = msg[:-1]
    
    if msg[0] == '+' and msg[1:].strip().isdigit():
        if inrange(headcount + int(msg[1:].strip())):
            update('+', int(msg[1:].strip()))
            await bot.send(event, '记着了！机厅现有 ' + str(headcount) + ' 人。')
        else:
            await bot.send(event, '不许玩bot，傻卵')
        return True

    if msg[0] == '-' and msg[1:].strip().isdigit():
        if inrange(headcount - int(msg[1:].strip())):
            update('-', int(msg[1:].strip()))
            await bot.send(event, '记着了！机厅现有 ' + str(headcount) + ' 人。')
        else:
            await bot.send(event, '不许玩bot，傻卵')
        return True

    
    return False