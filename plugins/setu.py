from plugins.identify import id_func
async def setu(event, bot):
    if event.message == '-setu':
        if id_func(event, 'setu') == False:
            await bot.send(event, 'qwq，此功能未启用')
        if id_func(event, 'setu') == True:
            await bot.send(event, '整天色图色图是不是牛子长脑子里了')
        return True
    return False
