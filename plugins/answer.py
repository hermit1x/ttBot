import random
import json
from plugins.identify import id_func

answer_list = []

async def answer(event, bot):
    global answer_list
    if not '糖糖' == event.message[:2]:
        return False
    if not id_func(event, 'answer'):
        return True
    if len(answer_list) == 0:
        with open('src/answer.txt', 'r', encoding = 'utf-8') as f:
            answer_list = f.read().split()
    await bot.send(event, f"[CQ:reply,id={event['message_id']}]{random.choice(answer_list)}")
    return True