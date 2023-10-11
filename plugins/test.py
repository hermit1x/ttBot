# coding:utf-8

from plugins.identify import id_func
from plugins.maimai import b50
async def test(event, bot):
    if event.message == 'test' or event.message == '糖糖在吗':
        if id_func(event, 'test') == False:
            await bot.send(event, 'qwq，此功能未启用')
        if id_func(event, 'test') == True:
            await bot.send(event, '糖糖活着！')
            # event.message = 'b50'
            # event.user_id = 2511848359
            # await b50(event, bot)
        return True
    return False
