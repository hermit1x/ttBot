from plugins.identify import id_func
from plugins.maimai.maimai_best_40 import generate
from plugins.maimai.maimai_best_50 import generate50
from plugins.maimai.image import image_to_base64
async def b40(event, bot):
    if event.message[:3] != 'b40':
        return False
    if not id_func(event, 'b40'):
        return True
    print('[ ] 触发b40')
    username = event.message[3:].strip()
    if username == "":
        payload = {'qq': str(event.user_id)}
    else:
        payload = {'username': username}
    img, success = await generate(payload)
    if success == 400:
        await bot.send(event, "未找到此玩家，请确保此玩家的用户名和查分器中的用户名相同。")
    elif success == 403:
        await bot.send(event, "该用户禁止了其他人获取数据。")
    else:
        await bot.send(event, 
        "[CQ:image,file=base64://" + str(image_to_base64(img), encoding='utf-8') + "]"
        )

async def b50(event, bot):
    if event.message[:3] != 'b50':
        return False
    if not id_func(event, 'b40'):
        return True
    print('[ ] 触发b50')
    username = event.message[3:].strip()
    if username == "":
        payload = {'qq': str(event.user_id), 'b50': True}
    else:
        payload = {'username': username, 'b50': True}
    img, success = await generate50(payload)
    if success == 400:
        await bot.send(event, "未找到此玩家，请确保此玩家的用户名和查分器中的用户名相同。")
    elif success == 403:
        await bot.send(event, "该用户禁止了其他人获取数据。")
    else:
        await bot.send(event, 
        "[CQ:image,file=base64://" + str(image_to_base64(img), encoding='utf-8') + "]"
        )