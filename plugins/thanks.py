from plugins.identify import id_func
import os
async def thanks(event, bot):
    if event.message == '谢谢糖糖':
        if id_func(event, 'thanks') == True:
            img_path = os.getcwd() + '/src/thanks.png'
            await bot.send(event, f'[CQ:image,file=files:///{img_path}]')
        return True
    return False