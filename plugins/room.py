# 查询自习室
import requests, json, os

class WebRequestError(BaseException):
    def __init__(self, args) -> None:
        self.args = args

class RoomNotFoundError(BaseException):
    pass

'''
返回数据格式：
[{
    name: 东下院405,
    occupied: [1, 2, 5, 6, ...]
},
{...}]
'''

def GetBuild(buildName):
    buildName2Id = {
        '上院': 126,
        '中院': 128,
        '下院': 127,
        '东上院': 122,
        '东中院': 564,
        '东下院': 124,
    }
    buildId = buildName2Id[buildName]

    r = requests.post(
        url = 'https://ids.sjtu.edu.cn/build/findBuildRoomType',
        data = {'buildId': buildId},
        proxies={'http':None, 'https':None},
    )
    return json.loads(r.content.decode())

def HandleSingleRoom(roomData) -> dict:
    result = {}
    result['name'] = roomData['name']
    roomCourseList = roomData['roomCourseList']
    ocp = []
    for course in roomCourseList:
        startSection = course['startSection']
        endSection = course['endSection']
        for t in range(startSection, endSection + 1):
            ocp.append(t)
    result['occupied'] = ocp.copy()
    return result.copy()

def GetWholeFloor(buildData, floor, floor2 = 0) -> list:
    if len(buildData) < floor or floor < 1:
        raise RoomNotFoundError
    floor = floor - 1
    floorData = buildData[floor]['children']
    floorTmp = []
    if floor2 != 0: # 特判东中
        for i in floorData:
            if i['fullName'][-3] == str(floor2):
                floorTmp.append(i)
        floorData = floorTmp
    result = []
    for i in floorData:
        result.append(
            HandleSingleRoom(i)
        )
    return result.copy()
    

def GetSingleRoom(buildData, floor, roomName, floor2 = 0) -> dict:
    floorData = GetWholeFloor(buildData, floor, floor2)
    for i in floorData:
        if i['name'] == roomName:
            return i
    raise RoomNotFoundError

def GetWholeBuild(buildData) -> list:
    result = []
    for floor in buildData:
        for classRoom in floor['children']:
            result.append(HandleSingleRoom(classRoom))
    return result.copy()


def msgFormat(msg) -> list:
    '''
    [{
        build: 东下院,
        type: 'single/floor/build',
        floor: 1/2/3..,
        name: 东下院405,
        floor2: 0
    }, {...}]
    '''
    result = []

    buildList = [
        '上院', '中院', '下院',
        '东上', '东中', '东下',
    ]
    queryList = msg.split('+')
    prevBuild = ""
    for query in queryList:
        buildName = ""
        if query[:2] in buildList:
            buildName = query[:2]
            prevBuild = buildName
        elif prevBuild != "":
            buildName = prevBuild
        else:
            continue
        
        if query in ['东上', '东中', '东下', '上院', '中院', '下院', '东上院', '东中院', '东下院']:
            if buildName in ['东上', '东中', '东下']:
                buildName = buildName + '院'
            result.append({
                'build': buildName,
                'type': 'build',
                'floor': 0,
                'name': '',
                'floor2': 0
            })
            continue

        if buildName in ['东上', '东中', '东下']:
            buildName = buildName + '院'

        if buildName == '东中院':
            tmp = query.split('-')
            floor = int(tmp[0][-1])
            floor2 = int(tmp[1][0])
            name = buildName + str(floor) + '-' + tmp[1]
            if len(tmp[1]) > 1:
                type = 'single'
            else:
                type = 'floor'
            result.append({
                'build': buildName,
                'type': type,
                'floor': floor,
                'name': buildName,
                'floor2': floor2
            })
        else:
            roomId = ""
            for i in range(0, len(query)):
                if query[i].isdigit():
                    roomId = roomId + query[i]
            if len(roomId) > 1:
                type = 'single'
            else:
                type = 'floor'
            floor = int(roomId[0])
            floor2 = 0
            name = buildName + roomId
            result.append({
                'build': buildName,
                'type': type,
                'floor': floor,
                'name': name,
                'floor2': floor2
            })
    return result

from PIL import Image, ImageDraw, ImageFont

font40 = ImageFont.truetype('./src/fonts/SourceHanSansCN-Normal.otf', 40, encoding="utf-8")
font70 = ImageFont.truetype('./src/fonts/SourceHanSansCN-Normal.otf', 70, encoding="utf-8")
font80 = ImageFont.truetype('./src/fonts/SourceHanSansCN-Normal.otf', 80, encoding="utf-8")
font100 = ImageFont.truetype('./src/fonts/SourceHanSansCN-Normal.otf', 100, encoding="utf-8")

def draw1room(roomData, emptyBlock, notEmptyBlock):
    weight = 1900
    height = 100
    img = Image.new('RGB', (weight, height), (0xff, 0xff, 0xff))
    draw = ImageDraw.Draw(img)
    draw.text((10, 10), roomData['name'], fill=(0, 0, 0), font=font80)

    gap = 10
    offSet = 480
    columnWeight = 95
    for classI in range(1, 15):
        if classI == 5 or classI == 7 or classI == 11:
            offSet = offSet + 20
        if classI in roomData['occupied']:
            img.paste(notEmptyBlock, (offSet + (classI - 1) * columnWeight, gap // 2))
        else:
            img.paste(emptyBlock, (offSet + (classI - 1) * columnWeight, gap // 2))
    return img

def data2img(roomsData):
    # 预处理有课和没课的两个格子
    columnHeight = 100
    g = 10 # gap
    r = 10

    emptyBlock = Image.new('RGB', (columnHeight-g, columnHeight-g), (0xff, 0xff, 0xff))
    drawEmpty = ImageDraw.Draw(emptyBlock)
    emptyColor = (30,144,255)
    drawEmpty.rectangle((r, 0, columnHeight-g-r, 2), emptyColor) # 上
    drawEmpty.rectangle((r, columnHeight-g-3, columnHeight-g-r, columnHeight-g), emptyColor) # 下
    drawEmpty.rectangle((0, r, 2, columnHeight-g-r), emptyColor) # 左
    drawEmpty.rectangle((columnHeight-g-3, r, columnHeight-g, columnHeight-g-r), emptyColor) # 右

    drawEmpty.arc((0, 0, 2 * r, 2 * r), start=180, end=270, fill = emptyColor, width=3) # 左上
    drawEmpty.arc((0, columnHeight-g - 2*r, 2*r, columnHeight-g - 1), start=90, end=180, fill = emptyColor, width=3) # 左下
    drawEmpty.arc((columnHeight-g - 2*r, 0, columnHeight-g - 1, 2*r), start=270, end=360, fill = emptyColor, width=3) # 右上
    drawEmpty.arc((columnHeight-g - 2*r, columnHeight-g - 2*r, columnHeight-g -1, columnHeight-g -1), start=0, end=90, fill = emptyColor, width=3) # 右下
    drawEmpty.text((columnHeight / 2 - 45, columnHeight / 2 - 45), '自', fill=emptyColor, font=font80)


    notEmptyBlock = Image.new('RGB', (columnHeight-g, columnHeight-g), (0xff, 0xff, 0xff))
    drawNotEmpty = ImageDraw.Draw(notEmptyBlock)
    notEmptyColor = (160,35,31)
    drawNotEmpty.rectangle((r, 0, columnHeight-g-r, 2), notEmptyColor) # 上
    drawNotEmpty.rectangle((r, columnHeight-g-3, columnHeight-g-r, columnHeight-g), notEmptyColor) # 下
    drawNotEmpty.rectangle((0, r, 2, columnHeight-g-r), notEmptyColor) # 左
    drawNotEmpty.rectangle((columnHeight-g-3, r, columnHeight-g, columnHeight-g-r), notEmptyColor) # 右

    drawNotEmpty.arc((0, 0, 2 * r, 2 * r), start=180, end=270, fill = notEmptyColor, width=3) # 左上
    drawNotEmpty.arc((0, columnHeight-g - 2*r, 2*r, columnHeight-g - 1), start=90, end=180, fill = notEmptyColor, width=3) # 左下
    drawNotEmpty.arc((columnHeight-g - 2*r, 0, columnHeight-g - 1, 2*r), start=270, end=360, fill = notEmptyColor, width=3) # 右上
    drawNotEmpty.arc((columnHeight-g - 2*r, columnHeight-g - 2*r, columnHeight-g -1, columnHeight-g -1), start=0, end=90, fill = notEmptyColor, width=3) # 右下
    drawNotEmpty.text((columnHeight / 2 - 45, columnHeight / 2 - 45), '课', fill=notEmptyColor, font=font80)

    height = 750 + 100 * len(roomsData)
    weight = 2000
    toLine = 230
    img = Image.new('RGB', (weight, height), color=(0xff,0xff,0xff))
    draw = ImageDraw.Draw(img)
    draw.rectangle((0, 0, weight, 200), fill = (0x6b,0,4))
    draw.text((weight // 2 - 300, 50), '自习教室查询', fill = (0xff, 0xff, 0xff), font = font100)

    margin = 50
    offSet = 480
    columnWeight = 95

    blackColor = (0, 0, 0)
    numBlock = Image.new('RGB', (columnHeight-g, columnHeight-g), (0xff, 0xff, 0xff))
    drawNum = ImageDraw.Draw(numBlock)
    drawNum.rectangle((r, 0, columnHeight-g-r, 2), blackColor) # 上
    drawNum.rectangle((r, columnHeight-g-3, columnHeight-g-r, columnHeight-g), blackColor) # 下
    drawNum.rectangle((0, r, 2, columnHeight-g-r), blackColor) # 左
    drawNum.rectangle((columnHeight-g-3, r, columnHeight-g, columnHeight-g-r), blackColor) # 右

    drawNum.arc((0, 0, 2 * r, 2 * r), start=180, end=270, fill = blackColor, width=3) # 左上
    drawNum.arc((0, columnHeight-g - 2*r, 2*r, columnHeight-g - 1), start=90, end=180, fill = blackColor, width=3) # 左下
    drawNum.arc((columnHeight-g - 2*r, 0, columnHeight-g - 1, 2*r), start=270, end=360, fill = blackColor, width=3) # 右上
    drawNum.arc((columnHeight-g - 2*r, columnHeight-g - 2*r, columnHeight-g -1, columnHeight-g -1), start=0, end=90, fill = blackColor, width=3) # 右下
    for i in range(1, 14+1):
        if i == 5 or i == 7 or i == 11:
            offSet = offSet + 20
        numBlockCopy = numBlock.copy()
        drawCopy = ImageDraw.Draw(numBlockCopy)
        drawCopy.text((columnHeight / 2 - 45, columnHeight / 2 - 45), str(i).zfill(2), fill=blackColor, font=font70)
        img.paste(numBlockCopy, (margin + offSet + (i - 1) * columnWeight, toLine))
    
    toLine += 100
    for i in roomsData:
        lineImg = draw1room(i, emptyBlock, notEmptyBlock)
        img.paste(lineImg, (margin, toLine))
        toLine += 100

    timeTable = [
        '08:00-08:45',
        '08:55-08:40',
        '10:00-10:45',
        '10:55-11:40',
        '12:00-12:45',
        '12-55-13:40',
        '14:00-14:45',
        '14:55-15:40',
        '16:00-16:45',
        '16:55-17:40',
        '18:00-18:45',
        '18:55-19:40',
        '19:50-20:35',
        '20:45-21:30'
    ]
    offSet = 480
    for i in range(1, 14+1):
        if i == 5 or i == 7 or i == 11:
            offSet = offSet + 20
        timeBlock = Image.new('RGB', (370, columnHeight-g), color = (0xff, 0xff, 0xff))
        drawTime = ImageDraw.Draw(timeBlock)
        drawTime.text((0, 10), timeTable[i-1], fill=(130, 130, 130), font=font70)
        timeBlock = timeBlock.transpose(Image.ROTATE_90)
        img.paste(timeBlock, (margin + offSet + (i - 1) * columnWeight, toLine))

    draw.text((margin + 90, toLine + 5), 'Powered By:', fill=(150, 150, 150), font=font40)
    tt = Image.open(os.getcwd() + '/data/room/tt.jpg')
    img.paste(tt, (margin + 20, toLine + 60))
    img_path = os.getcwd() + '/data/room/tmp.png'
    img.save(img_path)
    return img_path


def _room(msg):
    queryList = msgFormat(msg)
    roomsData = []
    for i in queryList:
        webData = GetBuild(i['build'])
        if webData['code'] != 200:
            raise WebRequestError(200)
        buildData = webData['data']['floorList']
        
        try:
            if i['type'] == 'single':
                roomsData.append(GetSingleRoom(buildData, i['floor'], i['name'], i['floor2']))
            if i['type'] == 'floor':
                roomsData = roomsData + GetWholeFloor(buildData, i['floor'], i['floor2'])
            if i['type'] == 'build':
                roomsData = roomsData + GetWholeBuild(buildData)
        except RoomNotFoundError:
            pass
    if len(roomsData) == 0:
        raise RoomNotFoundError
    return data2img(roomsData)

from plugins.identify import id_func

async def room(event, bot):
    if not event.message[:3] == '-js':
        return 
    print('[+] 触发room')
    if not id_func(event, 'room'):
        return True
    try:
        img_path = _room(event.message[4:])
        await bot.send(event, f'[CQ:image,file=files:///{img_path}]')
    except RoomNotFoundError:
        await bot.send(event, '查询教室不能为空')