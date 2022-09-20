import json
import os
from PIL import Image, ImageDraw, ImageFont
FONTS_PATH = 'src/fonts'
font_syht_m = ImageFont.truetype(os.path.join(FONTS_PATH, 'SourceHanSansCN-Normal.otf'), 18)
font_hywh_85w = ImageFont.truetype(os.path.join(FONTS_PATH, '汉仪文黑.ttf'), 40)


func_list = {}
group_list = {}

async def help(event, bot):
    if not (event.message == '-help'):
        return False
    with open('data/configs/func_list.json', 'r', encoding = 'utf-8') as f:
        func_list = json.load(f)
    
    line = 1
    if event.message_type == 'private':
        print('[+] 触发私聊help')
        save_path = os.getcwd() + '/data/configs/private_help.png'
        if not os.path.exists(save_path):
            height = 250 + 80 * (len(func_list['private']))
            width = 960
            img = Image.new('RGBA', (width, height), (0x66, 0xcc, 0xff, 255))
            draw = ImageDraw.Draw(img)
            draw.rectangle((0, 80, width, height), fill = (255, 255, 255, 255))
            draw.text((120, 130), f"私聊功能", fill=(6,162,183,255), font=font_hywh_85w)
            line += 1
            on_color = (0, 0, 0, 255)
            off_color = (150, 150, 150, 255)
            for func in func_list['private']:
                font_color = on_color
                if func_list['private'][func]['enable'] == False:
                    font_color = off_color
                draw.text((120, 60+line*80), func_list['private'][func]['name'] ,fill=font_color, font=font_hywh_85w)
                draw.text((360, 60+line*80), f"'{func_list['private'][func]['command']}'", fill=font_color, font=font_hywh_85w)
                line += 1
            img.save(save_path)
        await bot.send(event, f'[CQ:image,file=files:///{save_path}]')


    
    if event.message_type == 'group':
        print('[+] 触发群聊help')
        gid = str(event.group_id)
        cfgpath = os.getcwd() + '/data/configs/groups/' + gid + '/func_config.json'
        save_path = os.getcwd() + '/data/configs/groups/' + gid + '/help.png'
        if not os.path.exists(save_path):
            with open('data/configs/func_list.json', 'r', encoding = 'utf-8') as f:
                func_list = json.load(f)
            with open(cfgpath, 'r', encoding = 'utf-8') as f:
                group_list = json.load(f)
            line = 1

            height = 40 + 80 * (6 + len(func_list['group']) + len(func_list['private']) + len(group_list['admins']))
            width = 960

            img = Image.new('RGBA', (width, height), (0x66, 0xcc, 0xff, 255))
            draw = ImageDraw.Draw(img)
            draw.rectangle((0, 80, width, height), fill = (255, 255, 255, 255))

            draw.text((120, 160), f"群号: {gid}", fill=(0,0,0,255), font=font_hywh_85w)
            draw.text((60, 240), "●", fill=(0x66, 0xcc, 0xff, 255), font=font_hywh_85w)
            draw.text((120, 240), f"群聊功能", fill=(0x66, 0xcc, 0xff, 255), font=font_hywh_85w)
            on_color = (0, 0, 0, 255)
            off_color = (150, 150, 150, 255)
            for func in func_list['group']:
                font_color = on_color
                if group_list['func'][func] == False:
                    font_color = off_color
                draw.text((120, 240+line*80), func_list['group'][func]['name'] ,fill=font_color, font=font_hywh_85w)
                draw.text((360, 240+line*80), f"'{func_list['group'][func]['command']}'", fill=font_color, font=font_hywh_85w)
                line += 1
            

            draw.text((120, 240+line*80), f"群bot管理员", fill=(0x66, 0xcc, 0xff, 255), font=font_hywh_85w)
            line += 1
            for i in group_list['admins']:
                draw.text((120, 240+line*80), f"{i}", fill=(0, 0, 0, 255), font=font_hywh_85w)
                line += 1

            draw.text((60, 240+line*80), "●", fill=(0x66, 0xcc, 0xff, 255), font=font_hywh_85w)
            draw.text((120, 240+line*80), f"私聊功能", fill=(0x66, 0xcc, 0xff, 255), font=font_hywh_85w)
            line += 1
            
            for func in func_list['private']:
                font_color = on_color
                if func_list['private'][func]['enable'] == False:
                    font_color = off_color
                draw.text((120, 240+line*80), func_list['private'][func]['name'] ,fill=font_color, font=font_hywh_85w)
                draw.text((360, 240+line*80), f"'{func_list['private'][func]['command']}'", fill=font_color, font=font_hywh_85w)
                line += 1
            img.save(save_path)
        await bot.send(event, f'[CQ:image,file=files:///{save_path}]')

    return True

        