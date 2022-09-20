from plugins.identify import id_func

async def poke(event, bot):

    if not 'sub_type' in event:
        return False
    if not event.sub_type == 'poke':
        return False
    if not event.target_id == event.self_id:
        return False
    if 'group_id' in event:
        event.message_type = 'group'
    else:
        event.message_type = 'private'
    # print(event)
    # event.pop('message_type')
    if not id_func(event, 'poke'):
        return True
    else:
        print('[+] 触发戳一戳')
        await bot.send(event, f'[CQ:poke,qq={event.user_id}]')
        await bot.send(event, f'[CQ:poke,qq={event.user_id}]')
        await bot.send(event, f'[CQ:poke,qq={event.user_id}]')
        return True
