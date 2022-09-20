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
        