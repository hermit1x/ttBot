# coding:utf-8

from aiocqhttp import CQHttp, Event
import random
import time

from plugins.test import *
from plugins.poke import *
from plugins.help import *
from plugins.setu import *
from plugins.coin import *
from plugins.todo import *
from plugins.answer import *
from plugins.lottery import *
from plugins.history import *
from plugins.identify import *

#from plugins.group_config import *
bot = CQHttp()

def wait():
    time.sleep(random.randint(100, 800) / 1000)

@bot.on_message # 所有的message
async def handle_message(event: Event):
    
    permission = message_pre_handle(event)
    if permission == 'NO':
        if event.message_type == 'group' and event.user_id in SU:
            await change_config(event, bot)
        return
    wait()
    # 阻塞式编程，一个一个来
    monitor(event)
    if await change_config(event, bot):
        return
    if await help(event, bot):
        return
    if await peep(event, bot):
        return 
    if await test(event, bot):
        return
    if await setu(event, bot):
        return
    if await coin(event, bot):
        return
    if await todo(event, bot):
        return
    if await auto_buy(event, bot):
        return
    if await eavesdrop(event, bot):
        return
    if await answer(event, bot):
        return # 糖糖问答是在别的‘糖糖xxx’都没有响应的时候才响应

@bot.on_notice # 戳一戳、撤回、好友和群请求
async def handle_notice(event: Event):
    retract_monitor(event)
    wait()
    await poke(event, bot)

bot.run(host = '127.0.0.1', port = 8080, debug = False)