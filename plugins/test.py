# coding:utf-8

from plugins.identify import id_func
async def test(event, bot):
    if event.message == 'test' or event.message == '糖糖在吗':
        if id_func(event, 'test') == False:
            await bot.send(event, 'qwq，此功能未启用')
        if id_func(event, 'test') == True:
            await bot.send(event, '糖糖活着！')
        return True
    return False
