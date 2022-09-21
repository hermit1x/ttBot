from plugins.identify import id_func

flash_cache = {} # 遇到闪照就存，每个群存一张
retract_cache = {} # 存撤回过的消息，每群一条
message_cache = {}# 按时间戳来存，超过两分钟就丢

def get_sender(event):
    sender = {}
    sender['id'] = event.user_id
    if event.sender['card'] != '':
        sender['name'] = event.sender['card']
    else:
        sender['name'] = event.sender['nickname']
    return sender

def record_flash(event):
    msg = event.raw_message
    if msg.find(',type=flash') == -1:
        return
    
    msg = msg.replace(',type=flash', '')
    gid = str(event.group_id)
    flash_cache[gid] = {
        'img': msg,
        'sender': get_sender(event)
        }

def record_message(event):
    gid = str(event.group_id)
    time_now = event.time
    if not gid in message_cache:
        message_cache[gid] = []
    message_cache[gid].append({
        'time': event.time, 
        'message_id': event.message_id, 
        'message': event.message, 
        'sender': get_sender(event)
    })
    message_cache[gid] = [x for x in message_cache[gid] if time_now-x['time'] < 130]


def monitor(event):
    # peep = 偷看
    # eavesdrop = 偷听
    if id_func(event, 'peep'):
        record_flash(event)
    if id_func(event, 'eavesdrop'):
        record_message(event)


async def peep(event, bot):
    if not (event.message == '-peep' or event.message == '糖糖偷看'):
        return False
    if not id_func(event, 'peep'):
        return True
    gid = str(event.group_id)
    print('[+] 调用糖糖偷看，来自群聊：' + gid)
    
    img = flash_cache[gid]['img']
    sender_id = flash_cache[gid]['sender']['id']
    sender_name = flash_cache[gid]['sender']['name']
    msg = '偷看来自 ' + sender_name + ' (' + str(sender_id) + ') 的闪照：'
    await bot.send(event, msg)
    await bot.send(event, img)
    return True

# <Event, {
#     'post_type': 'message', 
#     'message_type': 'group', 
#     'time': 1660871091, 
#     'self_id': 3107347416, 
#     'sub_type': 'normal', 
#     'message_seq': 733, 
#     'user_id': 3066749824, 
#     'anonymous': None, 
#     'font': 0, 
#     'raw_message': '[CQ:image,file=3156b3c15b6ed6ac8864e90bea3b45d4.image,subType=0,url=,type=flash]', 
#     'sender': {
#         'age': 0, 
#         'area': '', 
#         'card': '糖糖', 
#         'level': '', 
#         'nickname': '轻语荷', 
#         'role': 'member', 
#         'sex': 'unknown', 
#         'title': '', 
#         'user_id': 3066749824
#     }, 
#     'message_id': 1739862451, 
#     'group_id': 636068836, 
#     'message': '[CQ:image,file=3156b3c15b6ed6ac8864e90bea3b45d4.image,subType=0,url=,type=flash]'}>


def retract_monitor(event):
    event.message_type = 'group'
    if not id_func(event, 'eavesdrop'):
        return
    if not event.notice_type == 'group_recall':
        return
    gid = str(event.group_id)
    print('[+] 监听到撤回消息，群聊：' + gid)
    message_id = event.message_id
    tmp = {}
    for i in message_cache[gid]:
        if i['message_id'] == message_id:
            tmp = {
                'message': i['message'],
                'sender': i['sender']
            }
            break
    retract_cache[gid] = tmp

async def eavesdrop(event, bot):
    if not (event.message == '-eavesdrop' or event.message == '糖糖偷听'):
        return False
    if not id_func(event, 'eavesdrop'):
        return True
    gid = str(event.group_id)
    if not gid in retract_cache:
        await bot.send('糖糖没听到xwx')
        return True
    msg = retract_cache[gid]['message']
    sender_id = retract_cache[gid]['sender']['id']
    sender_name = retract_cache[gid]['sender']['name']
    msg = '偷听 ' + sender_name + ' (' + str(sender_id) + ') 撤回的消息：\n' + msg
    await bot.send(event, msg)
    return True

# <Event, {
#     'post_type': 'notice', 
#     'notice_type': 'group_recall', 
#     'time': 1660874342, 
#     'self_id': 3107347416, 
#     'user_id': 1242291955, 
#     'operator_id': 1242291955, 
#     'message_id': 1189717667, 
#     'group_id': 636068836
#     }>

async def essence(event, bot):
    if event.post_type != 'message' or event.message_type != 'group':
        return False
    if not id_func(event, 'essence'):
        return False

    msg = str(event.message)
    gid = event.group_id
    

    if len(msg) < 13 or str(msg[:13]) != '[CQ:reply,id=':
        return False
    if msg.find(']') == -1:
        return False
    mid = int(msg[13:msg.find(']')])

    if msg.find('糖糖设精') != -1 or msg.find('糖糖射精') != -1:
        await bot.set_essence_msg(message_id = mid)
        print('[+] 精华消息，群', gid)
        return True
    
    if msg.find('糖糖别设') != -1 or msg.find('糖糖别射') != -1:
        await bot.delete_essence_msg(message_id = mid)
        print('[+] 移出精华，群', gid)
        return True
    
    return False
    

    

# <Event, {
#     'post_type': 'message', 
#     'message_type': 'group', 
#     'time': 1663732296, 
#     'self_id': 3107347416, 
#     'sub_type': 'normal', 
#     'message': 'text1', 
#     'raw_message': 'text1', 
#     'sender': {'age': 0, 'area': '', 'card': '', 'level': '', 'nickname': '华华小公主', 'role': 'owner', 'sex': 'unknown', 'title': '', 'user_id': 1242291955}, 
#     'message_id': 1997544749, 
#     'anonymous': None, 
#     'font': 0, 
#     'group_id': 636068836, 
#     'message_seq': 999, 
#     'user_id': 1242291955
#     }>

# <Event, {
#     'post_type': 'message', 
#     'message_type': 'group', 
#     'time': 1663732303, 
#     'self_id': 3107347416, 
#     'sub_type': 'normal', 
#     'anonymous': None, 
#     'message_seq': 1000, 
#     'raw_message': '[CQ:reply,id=1997544749][CQ:at,qq=1242291955] text2', 
#     'message_id': -1428931744, 
#     'font': 0, 
#     'group_id': 636068836, 
#     'message': '[CQ:reply,id=1997544749][CQ:at,qq=1242291955] text2', 
#     'message': '[CQ:reply,id=1997544749][CQ:at,qq=1242291955] [CQ:at,qq=1242291955] text3'
#     'sender': {
#         'age': 0, 
#         'area': '', 
#         'card': '', 
#         'level': '', 
#         'nickname': 
#         '华华小公主', 
#         'role': 'owner', 
#         'sex': 'unknown', 
#         'title': '', 
#         'user_id': 1242291955
#     }, 
#     'user_id': 1242291955
#     }>