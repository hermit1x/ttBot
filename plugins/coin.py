# coding:utf-8
import time
import random
from plugins.identify import id_func

coin_alias = ['coin', '抛硬币', '糖糖抛硬币']
async def coin(event, bot):
    msg = event.message.split()[0]
    if not msg in coin_alias:
        return False
    print('[+] 触发coin')
    if not id_func(event, 'coin'):
        return True
    await bot.send(event, '糖糖这就帮你抛硬币！')
    time.sleep(1)
    ans = random.randint(0, 31)
    if ans == 31:
        await bot.send(event, '硬币碎了QAQ')
    elif ans % 2 == 1:
        await bot.send(event, '是正面！')
    else:
        await bot.send(event, '是反面！')
    return True

async def dice(event, bot):
    msg = event.message
    if msg.find('d') == -1 and msg.find('D') == -1:
        return False
    roll_seq0 = msg.split('+')
    roll_seq1 = []
    for i in roll_seq0:
        j = i.strip()
        if j.find('d') == -1 and msg.find('D') == -1 and not j.isdigit():
            return False
        elif j.find('d') != -1:
            if len(j.split('d')) != 2:
                return False
            if j.split('d')[0].isdigit() == False:
                return False
            if j.split('d')[1].isdigit() == False:
                return False
        elif j.find('D') != -1:
            if len(j.split('D')) != 2:
                return False
            if j.split('D')[0].isdigit() == False:
                return False
            if j.split('D')[1].isdigit() == False:
                return False

    if not id_func(event, 'dice'):
        return True
    
    print('[+] 触发dice')
    if len(roll_seq0) > 10000:
        return True
    for i in roll_seq0:
        j = i.strip()
        if j.find('d') == -1 and msg.find('D') == -1:
            roll_seq1.append(int(j))
        elif j.find('d') != -1:
            k = j.split('d')
            roll_seq1.append((
                int(k[0].strip()),
                int(k[1].strip())
            ))
        elif j.find('D') != -1:
            k = j.split('D')
            roll_seq1.append((
                int(k[0].strip()),
                int(k[1].strip())
            ))
    
    cnt = 0
    ret = ""
    for i in roll_seq1:
        if type(i) == int:
            ret = ret + ' + ' + str(i)
            cnt = cnt + i
        else:
            ret = ret + ' + '
            if i[0] > 1:
                ret = ret + '('
            rand = random.randint(1, i[1])
            cnt = cnt + rand
            ret = ret + str(rand) # 第一个
            if i[0] > 10000:
                return True
            for j in range(1, i[0]):
                rand = random.randint(1, i[1])
                cnt = cnt + rand
                ret = ret + '+' + str(rand)
            if i[0] > 1:
                ret = ret + ')'
    ret = ret[3:]
    if len(roll_seq1) > 1 or roll_seq1[0][0] > 1:
        ret = ret + ' = '+ str(cnt)
    await bot.send(event, f"[CQ:reply,id={event['message_id']}]{ret}")