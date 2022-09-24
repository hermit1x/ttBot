# coding:utf-8

from aiocqhttp import CQHttp, Event
import random
import time

from plugins.test import test
from plugins.poke import poke
from plugins.help import help
from plugins.setu import setu
from plugins.coin import coin, dice
from plugins.todo import todo
from plugins.answer import answer
from plugins.lottery import auto_buy
from plugins.history import monitor, peep, eavesdrop, essence, retract_monitor
from plugins.identify import message_pre_handle, change_config, SU
from plugins.friend_add import friend_add
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
    if await dice(event, bot):
        return
    if await essence(event, bot):
        return
    if await auto_buy(event, bot):
        return
    if await eavesdrop(event, bot):
        return
    if await answer(event, bot):
        return # 糖糖问答是在别的‘糖糖xxx’都没有响应的时候才响应

@bot.on_notice # 戳一戳、撤回
async def handle_notice(event: Event):
    retract_monitor(event)
    wait()
    await poke(event, bot)

@bot.on_request
async def handle_request(event: Event):
    wait()
    await friend_add(event, bot)

bot.run(host = '127.0.0.1', port = 8080, debug = False)