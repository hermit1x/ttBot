'''
该模块预计有如下几个功能
1. 生成以星期-从早到晚-人数为轴的三维瀑布图
2. 输出总的统计数据，包括记录的范围、总计入条数、平均人数、最高人数、0人时长等等


'''
from plugins.identify import id_func
import json, os
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from mpl_toolkits.mplot3d import Axes3D

time_format = '%Y-%m-%d %H:%M:%S'
logpath = 'data/maihc.log'
figpath = 'data/maiWaterFall.png'
granularity = 10 # n. 颗粒度，单位（分钟），表示要以多精细的尺度来处理信息

def CalcTimeToLocation(t) -> tuple:
    # 输入datetime类型，返回在两个np矩阵里对应的坐标
    a = t.weekday()
    openTime = datetime.strptime(
        str(t.date()) + ' 10:00:00', 
        time_format
    )
    
    if (t - openTime).days < 0:
        seconds = 0
    else:
        seconds = (t - openTime).seconds
    minutes = seconds // 60
    b = minutes // granularity
    return (a, b)


def GetDataFromLog():
    '''
    初始化各个记录变量，从文件中读取数据并处理
    '''
    earlistRecordTime = ''
    latestRecordTime = ''
    headCount = np.zeros((7, 12 * 60 // granularity), dtype=np.int)
    dayCount = np.zeros((7), dtype=np.int)
    resMat = np.zeros(headCount.shape)
    lineCount = 0
    maxRec = { 'time': '', 'headcount': 0 }
    maxAve = { 'pos': '', 'headcount': 0 }
    minAve = { 'pos': '', 'headcount': 100 }
    

    preWD = -1
    preDT = 0
    preHC = 0

    f = open(logpath, 'r')
    line = f.readline()
    # 特殊处理最早的记录
    earlistRecordTime = json.loads(line)['time']

    while line:
        lineCount += 1
        record = json.loads(line)
        recordTime = datetime.strptime(record['time'], time_format)
        recordHC = record['headcount']
        weekDay, dayTime = CalcTimeToLocation(recordTime)

        if recordHC > maxRec['headcount']:
            maxRec = record

        # 四种情况
        # 1. 相邻的两条记录落到同一个loc里
        # 2. 两条记录是同一天，但是跨了好几个loc
        # 3. 两条记录跨天
        # 4. 没有“前一条”
        if preWD == -1:
            headCount[weekDay, dayTime] += recordHC
            dayCount[weekDay] += 1
        elif weekDay == preWD and dayTime == preDT:
            if preHC > recordHC:
                recordHC = preHC
                # 等于是跳过了这条记录
            else:
                headCount[weekDay, dayTime] += recordHC - preHC
                # 补差价
        elif weekDay == preWD and dayTime > preDT:
            for i in range(preDT + 1, dayTime):
                # 是一个 [pre + 1, daytime - 1] 的循环
                headCount[weekDay, i] += preHC
            headCount[weekDay, dayTime] += recordHC
        elif weekDay != preWD:
            for i in range(preDT + 1, 12 * 60 // granularity):
                # 处理前一天最后一条记录到闭店
                headCount[weekDay, i] += preHC
            headCount[weekDay, dayTime] += recordHC
            dayCount[weekDay] += 1
        else:
            print('[!!!] something wrong with mai analyse')

        preWD, preDT = weekDay, dayTime
        preHC = recordHC

        line = f.readline()
        if line == '':
            latestRecordTime = record['time']
    for i in range(7):
        resMat[i, :] = headCount[i, :] / dayCount[i]
        for j in range(resMat.shape[1]):
            if resMat[i, j] > maxAve['headcount']:
                maxAve = { 'pos': (i, j), 'headcount': resMat[i, j]}
            if resMat[i, j] < minAve['headcount']:
                minAve = { 'pos': (i, j), 'headcount': resMat[i, j]}

    # pos to time for maxAve and minAve
    weeklist = ['一', '二', '三', '四', '五', '六', '日']
    
    pos = maxAve['pos']
    weekDay = '星期' + weeklist[pos[0]] + ' '
    dayTime = str(10 + pos[1] * 10 // 60) + ':' + str(pos[1] * 10 % 60)
    maxAve['time'] = weekDay + dayTime

    pos = minAve['pos']
    weekDay = '星期' + weeklist[pos[0]] + ' '
    dayTime = str(10 + pos[1] * 10 // 60) + ':' + str(pos[1] * 10 % 60)
    minAve['time'] = weekDay + dayTime

    f.close()
    return {
        'lineCount': lineCount,
        'earliest': earlistRecordTime,
        'latest': latestRecordTime,
        'res': resMat,
        'mean': resMat.mean(),
        'maxRec': maxRec,
        'maxAve': maxAve,
        'minAve': minAve
    }

def waterfall_plot(fig,ax,X,Y,Z):
    '''
    Make a waterfall plot
    Input:
        fig,ax : matplotlib figure and axes to populate
        Z : n,m numpy array. Must be a 2d array even if only one line should be plotted
        X,Y : n,m array
    '''
    # Set normalization to the same values for all plots
    norm = plt.Normalize(Z.min().min(), Z.max().max())
    # Check sizes to loop always over the smallest dimension
    n,m = Z.shape
    if n>m:
        X=X.T; Y=Y.T; Z=Z.T
        m,n = n,m

    for j in range(n):
        # reshape the X,Z into pairs 
        points = np.array([X[j,:], Z[j,:]]).T.reshape(-1, 1, 2)
        segments = np.concatenate([points[:-1], points[1:]], axis=1)        
        lc = LineCollection(segments, cmap='plasma', norm=norm)
        # Set the values used for colormapping
        lc.set_array((Z[j,1:]+Z[j,:-1])/2)
        lc.set_linewidth(2) # set linewidth a little larger to see properly the colormap variation
        line = ax.add_collection3d(lc,zs=(Y[j,1:]+Y[j,:-1])/2, zdir='y') # add line to axes
    fig.colorbar(lc) # add colorbar, as the normalization is the same for all, it doesent matter which of the lc objects we use

def draw(data):
    res = data['res']
    x = np.arange(0, res.shape[1])
    y = np.arange(0, res.shape[0])
    X,Y = np.meshgrid(x,y)
    Z = res

    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.view_init(elev=65, azim=-30)
    waterfall_plot(fig,ax,X,Y,Z) 
    ax.set_xlabel('') ; ax.set_xlim3d(0,72)
    ax.set_ylabel('') ; ax.set_ylim3d(-1,7)
    ax.set_zlabel('') ; ax.set_zlim3d(2,6)

    ax.set_xticks(np.arange(0, 72, 6))
    ax.set_xticklabels(['10:00', '11:00', '12:00', '13:00', '14:00', '15:00', '16:00', '17:00', '18:00', '19:00', '20:00', '21:00', '22:00'])

    ax.set_yticks([0, 1, 2, 3, 4, 5, 6])
    ax.set_yticklabels(['Mon', 'Tue', 'Wen', 'Thu', 'Fri', 'Sat', 'Sun'])

    plt.savefig(figpath)

async def maianalyse(event, bot):
    data = GetDataFromLog()
    msg = '从{}起，至{}为止.\n'.format(data['earliest'][:-3], data['latest'][:-3])
    msg += '糖糖二号机总共记录 {} 条菲游乐人数数据.\n'.format(data['lineCount'])
    msg += '平均同时排队人数为 {:.2f} 人.\n'.format(data['mean'])
    msg += '平均人数最多的时段为{}，有 {:.2f} 人.\n'.format(data['maxAve']['time'], data['maxAve']['headcount'])
    msg += '平均人数最少的时段为{}，有 {:.2f} 人.\n'.format(data['minAve']['time'], data['minAve']['headcount'])
    msg += '最多同时排队人数为 {} 人，出现在{}.\n'.format(data['maxRec']['headcount'], data['maxRec']['time'][:-3])
    msg += '最少同时排队人数为 0 人，出现在敲警钟的时候.\n'
    msg += '下面是根据各个时段的平均人数绘制的曲线图'
    await bot.send(event, msg)
    print('[=] 消息发送完成')
    draw(data)
    print('[=] 图片绘制完成')
    img_path = os.getcwd() + '/' + figpath
    await bot.send(event, f'[CQ:image,file=files:///{img_path}]')
    print('[-] 图片发送完成')


async def anal(event, bot):
    if id_func(event, 'maianalyse') == False:
        return False
    if event.message == '统计':
        print('[+] maimai人数分析')
        await maianalyse(event, bot)
        return True