import json
from operator import is_
import os
import shutil

func_list = {'group': {}, 'private': {}}
# {'群聊': {'功能1': {
#                   'name': '名字',
#                   'command': '',
#                   'enable': TF/}}, 
#  '私聊': {'功能': {
#                   'name': '名字',
#                   'command': ,
#                   'enable': TF/}},
# }}

group_enabled = {}
# {'群号': True/False}

config = {'private': {}}
# {'群号':{
#       功能:{名称：TF}, 
#       管理员：list
#       }，
#  '私聊'：{功能：开关}
# }

black_list = []
# [(long)账号, ]

SU = []

dir_path = os.getcwd() + '/data/configs/'



def init():
    global func_list, group_enabled, config, black_list, SU, dir_path
    # 先初始化除了config之外的所有
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)

    try:
        f = open(dir_path + 'func_list.json', 'r', encoding = 'utf-8')
        func_list = json.load(f); f.close()
    except FileNotFoundError:
        f = open(dir_path + 'func_list.json', 'w', encoding = 'utf-8')
        json.dump(func_list, f); f.close()
    
    try:
        f = open(dir_path + 'group_enabled.json', 'r', encoding = 'utf-8')
        group_enabled = json.load(f); f.close()
    except FileNotFoundError:
        f = open(dir_path + 'group_enabled.json', 'w', encoding = 'utf-8')
        json.dump(group_enabled, f); f.close()

    try:
        f = open(dir_path + 'black_list.json', 'r', encoding = 'utf-8')
        black_list = json.load(f); f.close()
    except FileNotFoundError:
        f = open(dir_path + 'black_list.json', 'w', encoding = 'utf-8')
        json.dump(black_list, f); f.close()

    try:
        f = open(dir_path + 'SU.json', 'r', encoding = 'utf-8')
        SU = json.load(f); f.close()
    except FileNotFoundError:
        f = open(dir_path + 'SU.json', 'w', encoding = 'utf-8')
        json.dump(SU, f); f.close()

    # 初始化config的私聊
    for func in func_list['private']:
        config['private'][func] = func_list['private'][func]['enable']


    # 初始化群文件夹
    if not os.path.exists(dir_path + 'groups/'):
        os.makedirs(dir_path + 'groups/')
    for gid in group_enabled:
        if group_enabled[gid] == False:
            continue
        gpath = dir_path + 'groups/' + gid + '/'
        if os.path.exists(gpath + 'func_config.json'):
            f = open(gpath + 'func_config.json', 'r', encoding = 'utf-8')
            group_config = json.load(f)
            f.close()
            config[gid] = group_config
        else:
            os.makedirs(gpath)
            f = open(gpath + 'func_config.json', 'w', encoding = 'utf-8')
            new_config = {}
            new_config['admins'] = SU
            new_config['func'] = {}
            for func in func_list['group']:
                new_config['func'][func] = func_list['group'][func]['enable']
            json.dump(new_config, f)
            f.close()
            config[gid] = new_config
    
    print('[+] identify组件初始化成功')

init()

def write_json():
    global func_list, group_enabled, config, black_list, SU, dir_path
    with open(dir_path + 'func_list.json', 'w', encoding = 'utf-8') as f:
        json.dump(func_list, f)
    f = open(dir_path + 'group_enabled.json', 'w', encoding = 'utf-8')
    json.dump(group_enabled, f); f.close()
    f = open(dir_path + 'black_list.json', 'w', encoding = 'utf-8')
    json.dump(black_list, f); f.close()
    f = open(dir_path + 'SU.json', 'w', encoding = 'utf-8')
    json.dump(SU, f); f.close()
    if os.path.exists(dir_path + 'private_help.png'):
        os.remove(dir_path + 'private_help.png')

def enable_group(gid):
    global func_list, group_enabled, config, black_list, SU, dir_path
    # 一个新的group从disable到enable，创建文件夹并添加到config
    # 判断合理性交给外层判断
    group_enabled[gid] = True
    gpath = dir_path + 'groups/' + gid + '/'
    os.makedirs(gpath)
    f = open(gpath + 'func_config.json', 'w', encoding = 'utf-8')
    new_config = {}
    new_config['admins'] = SU
    new_config['func'] = {}
    for func in func_list['group']:
        new_config['func'][func] = func_list['group'][func]['enable']
    json.dump(new_config, f)
    f.close()
    config[gid] = new_config
    write_json()

def disable_group(gid):
    global func_list, group_enabled, config, black_list, SU, dir_path
    # 同上，负责删除文件夹和config
    group_enabled[gid] = False
    config.pop(gid)
    gpath = dir_path + 'groups/' + gid + '/'
    shutil.rmtree(gpath)
    write_json()

def update_func_for_private():
    global func_list, group_enabled, config, black_list, SU, dir_path
    config['private'] = {}
    for func in func_list['private']:
        config['private'][func] = func_list['private'][func]['enable']
    save_path = os.getcwd() + '/data/configs/private_help.png'
    if os.path.exists(save_path):
        os.remove(save_path)
    write_json()
    
    

def update_func_for_groups(gid = 0):
    global func_list, group_enabled, config, black_list, SU, dir_path
    # 只重置固定组
    poplist = []
    if gid != 0 and gid in group_enabled:
        for func in config[gid]['func']:
            if not func in func_list['group']:
                poplist.append(func)
        for func in poplist:
            config[gid]['func'].pop(func)
        # 再加入func_list里有的新功能
        for func in func_list['group']:
            if not func in config[gid]['func']:
                config[gid]['func'][func] = func_list['group'][func]['enable']
        
        group_func_config = config[gid]
        gpath = dir_path + 'groups/' + gid + '/'
        f = open(gpath + 'func_config.json', 'w', encoding = 'utf-8')
        json.dump(group_func_config, f)
        f.close()

        if os.path.exists(gpath + 'help.png'):
            os.remove(gpath + 'help.png')
        return
    
    for gid in group_enabled:
        if group_enabled[gid] == False:
            continue
        
        # 先删除func_list里没有的过期功能
        for func in config[gid]['func']:
            if not func in func_list['group']:
                poplist.append(func)
        for func in poplist:
            config[gid]['func'].pop(func)
        # 再加入func_list里有的新功能
        for func in func_list['group']:
            if not func in config[gid]['func']:
                config[gid]['func'][func] = func_list['group'][func]['enable']
        
        group_func_config = config[gid]
        gpath = dir_path + 'groups/' + gid + '/'
        f = open(gpath + 'func_config.json', 'w', encoding = 'utf-8')
        json.dump(group_func_config, f)
        f.close()

        if os.path.exists(gpath + 'help.png'):
            os.remove(gpath + 'help.png')

def message_pre_handle(event):
    if event.message_type == 'private':
        if event.user_id in black_list:
            return 'NO'
        else:
            return 'PRIVATE'
    
    if event.message_type == 'group':
        gid = str(event.group_id)
        if not gid in group_enabled:
            group_enabled[gid] = False
            write_json()
            return 'NO'
        elif group_enabled[gid]:
            return 'GROUP'
        else:
            return 'NO'

def id_func(event, func):
    if event.message_type == 'private':
        if not func in config['private']:
            return False
        return config['private'][func]
    if event.message_type == 'group':
        gid = str(event.group_id)
        if gid in config:
            return config[gid]['func'][func]
        else:
            return False

help_for_set = '-set on/off/add/del/func name/uid/(padd,pdel,gadd,gdel) (funcname) (name) (discribe) (enable)'
error_message = '哪里出错了，怎么会是呢'
ok_message = '搞定啦'

def is_func(gp, func):
    return func in func_list[gp]

async def change_config(event, bot):
    cmd = event.message.split()
    if len(cmd) == 0:
        return False
    if cmd[0] != '-set':
        return False

    if event.message_type == 'private':
        if not event.user_id in SU:
            await bot.send(event, '权限不够哦')
            return True

        if len(cmd) > 1 and cmd[1] == 'help':
            await bot.send(event, help_for_set)
            return True

        if len(cmd) > 2:
            if cmd[1] == 'on':
                func = cmd[2]
                if is_func('private', func):
                    if config['private'][func]:
                        await bot.send(event, '此功能已经处于开启状态')
                        return True
                    else:
                        config['private'][func] = True
                        func_list['private'][func]['enable'] = True
                        update_func_for_private()
                        await bot.send(event, ok_message)
                        return True
                else:
                    await bot.send(event, error_message)
                    return True
            elif cmd[1] == 'off':
                func = cmd[2]
                if is_func('private', func):
                    if config['private'][func] == False:
                        await bot.send(event, '此功能已经处于关闭状态')
                        return True
                    else:
                        config['private'][func] = False
                        func_list['private'][func]['enable'] = False
                        update_func_for_private()
                        await bot.send(event, ok_message)
                        return True
                else:
                    await bot.send(event, error_message)
                    return True
            elif cmd[1] == 'add':
                num = eval(cmd[2])
                SU.append(num)
                await bot.send(event, '注意，增加了一位Super_User')
            elif cmd[1] == 'del':
                num = eval(cmd[2])
                SU.pop(SU.index(num))
                await bot.send(event, '注意，删除了一位Super_User')
            elif cmd[1] == 'func':
                if len(cmd) < 4:
                    await bot.send(event, error_message)
                    return True
                func_type = cmd[2]
                func_name = cmd[3]

                if func_type == 'gdel':
                    func_list['group'].pop(func_name)
                    await bot.send(event, ok_message)
                    write_json()
                    update_func_for_groups()
                    return True
                elif func_type == 'pdel':
                    func_list['private'].pop(func_name)
                    await bot.send(event, ok_message)
                    write_json()
                    update_func_for_private()
                    return True

                # 0-set 
                # 1on/off/add/del/func 
                # 2name/uid/(padd,pdel,gadd,gdel) 
                # 3(funcname) 即系统里的func name
                # 4(realname) # 则是介绍出来的func name
                # 5(command) 
                # 6(enable)

                func_real_name = cmd[4]
                func_command = ''
                func_enable = False
                if len(cmd) > 4:
                    func_command = cmd[5]
                if len(cmd) > 5:
                    if cmd[6] == 'on':
                        func_enable = True
                    else:
                        func_enable = False
                
                tmpdict = {
                    'name': func_real_name,
                    'command': func_command,
                    'enable': func_enable
                    }
                
                if func_type == 'gadd':
                    func_list['group'][func_name] = tmpdict
                    await bot.send(event, ok_message)
                    write_json()
                    update_func_for_groups()
                    return True
                elif func_type == 'padd':
                    func_list['private'][func_name] = tmpdict
                    await bot.send(event, ok_message)
                    write_json()
                    update_func_for_private()
                    return True
                else:
                    await bot.send(event, error_message)
                    return True
            else:
                await bot.send(event, error_message)
                return True
            return True

    if event.message_type == 'group':
        gid = str(event.group_id)

        if not gid in group_enabled:
            group_enabled[gid] = False

        if group_enabled[gid] == False:
            if event.user_id in SU and len(cmd) == 2 and cmd[1] == 'enable':
                enable_group(gid)
                await bot.send(event, '糖糖来啦')
                return True
            else:
                return True

        if not event.user_id in config[gid]['admins']:
            await bot.send(event, error_message)
            return True

        if len(cmd) == 2:
            if cmd[1] == 'disable':
                disable_group(gid)
                await bot.send(event, '糖糖走啦')
                return True

        if len(cmd) > 2:
            if cmd[1] == 'on':
                func = cmd[2]
                if is_func('group', func):
                    if config[gid]['func'][func]:
                        await bot.send(event, '已经开着啦')
                        return True
                    else:
                        config[gid]['func'][func] = True
                        await bot.send(event, ok_message)
                        update_func_for_groups(gid)
                        return True
                else:
                    await bot.send(event, error_message)
                    return True
            
            if cmd[1] == 'off':
                func = cmd[2]
                if is_func('group', func):
                    if not config[gid]['func'][func]:
                        await bot.send(event, '本来就没开哦')
                    else:
                        config[gid]['func'][func] = False
                        await bot.send(event, ok_message)
                        update_func_for_groups(gid)
                        return True
                else:
                    await bot.send(event, error_message)
                    return True
            
            if cmd[1] == 'add':
                num = eval(cmd[2])
                config[gid]['admins'].append(num)
                await bot.send(event, ok_message)
                update_func_for_groups(gid)
                return True
            
            if cmd[1] == 'del':
                num = eval(cmd[2])
                config[gid]['admins'].pop(config[gid]['admins'].index(num))
                await bot.send(event, ok_message)
                update_func_for_groups(gid)
                return True

            
            await bot.send(event, error_message)
            return True
            
    return True
