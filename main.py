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
from plugins.room import room
from plugins.openai import openai
from plugins.answer import answer
from plugins.thanks import thanks
from plugins.lottery import auto_buy
from plugins.wordcloud import wordcloud, record_for_wordcloud
from plugins.history import monitor, peep, eavesdrop, essence, retract_monitor
from plugins.identify import message_pre_handle, change_config, SU
from plugins.friend_add import friend_add
from plugins.maihc import maihc

from plugins.maimai import b40

bot = CQHttp()

def wait():
    time.sleep(random.randint(100, 800) / 1000)

async def handle_seq(event, bot, funcs):
    for func in funcs:
        if await func(event, bot):
            return

@bot.on_message # 所有的message
async def handle_message(event: Event):
    permission = message_pre_handle(event)
    if permission == 'NO':
        if event.message_type == 'group' and event.user_id in SU:
            await change_config(event, bot)
        return
    monitor(event)
    record_for_wordcloud(event)
    wait()
    # 一个一个来
    await handle_seq(event, bot,
        [
            change_config,
            help,
            peep,
            test,
            setu,
            coin,
            todo,
            dice,
            room,
            thanks,
            essence,
            auto_buy,
            eavesdrop,
            wordcloud,
            openai,
            answer,
            b40,
            maihc, 
        ]
    ) # 糖糖问答是在别的‘糖糖xxx’都没有响应的时候才响应

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