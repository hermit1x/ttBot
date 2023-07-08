from plugins.identify import id_func
import datetime, json
time_format = '%Y-%m-%d %H:%M:%S'
headcount = 0
daytag = datetime.datetime.now().day

try:
    with open("data/maihc.log", 'rb') as f:
        f.seek(-48, 2) # 暂时默认是一位数的人数，基本上不会挂（？）
        last = f.read().strip()
        last = json.loads(last)
        daytag = datetime.datetime.strptime(last['time'], time_format).day
        headcount = last['headcount']
except:
    print('[x] 机厅初始化挂了，但是问题不大')
    pass

print('[+] 机厅初始化成功')

async def maihc(event, bot):
    global headcount, daytag
    if id_func(event, 'maihc') == False:
        return False
    # 预先分拣指令，看看是不是maihc的指令，顺便分拣一下值
    is_maihc_cmd = False
    opt = ''
    x = 0
    
    msg = event.message
    query_cmd = ['机厅几人', '机厅几人？', '几人', '几？', '几']
    if msg in query_cmd:
        is_maihc_cmd = True
        opt = '?'
    elif msg[:2] == '机厅' and msg[-1] == '人' and msg[2:-1].strip().isdigit():
        is_maihc_cmd = True
        opt = '='
        x = int(msg[2:-1].strip())
    elif msg[0] == '+' and msg[1:].strip().isdigit():
        is_maihc_cmd = True
        opt = '+'
        x = int(msg[1:].strip())
    elif msg[0] == '-' and msg[1:].strip().isdigit():
        is_maihc_cmd = True
        opt = '-'
        x = int(msg[1:].strip())
    
    # 不是maihc的指令
    if is_maihc_cmd == False:
        return False

    # 闭店检查
    h = datetime.datetime.now().hour
    if h < 9 or h >= 22:
        await bot.send(event, '闭店了闭店了，别惦记你那破maimai了')
        return True
    
    # 日期更新检查
    daynow = datetime.datetime.now().day
    if daynow != daytag:
        daytag = daynow
        headcount = 0  
        print('[+] maihc归零，day' + str(daynow))
    # 应用更新后的hc
    if opt == '+':
        x = headcount + x
    if opt == '-':
        x = headcount - x

    if opt == '?':
        await bot.send(event, '机厅现有 ' + str(headcount) + ' 人。')
        if headcount == 0:
            await bot.send(event, '警钟长鸣')
        if headcount == 1:
            await bot.send(event, '我超 有人吧唧 快来')
        if headcount >= 6:
            await bot.send(event, '我超 大逼队 快跑')
        return True

    if x < 0 or x > 20:
        await bot.send(event, '不许玩bot，傻卵')
        return True
    
    headcount = x
    await bot.send(event, '记着了！机厅现有 ' + str(headcount) + ' 人。')
    with open('data/maihc.log', 'a') as f:
        f.write(json.dumps(
            {
                'time': datetime.datetime.now().strftime(time_format),
                'headcount': headcount
            }
        ) + '\n')
    return True