import pandas as pd
import re


def clean(data):
    pattern = re.compile(r'\(共(\d+)层\)')
    data['totalfloornum'] = data['totalfloor'].apply(lambda o: int(pattern.findall(o)[0]))
    data['recognizedsize'] = data['size'].apply(lambda o: int(o))
    data['id'] = data['id'].apply(lambda o: str(o))

def prepare(data):
    data['isinnerring'] = data.apply(lambda o: isInInnerRing(o), axis=1)
    data['isoldcity'] = data.apply(lambda o: isInOldCity(o), axis=1)
    data['isfamousarea'] = data.apply(lambda o: isAreaGreat(o), axis=1)
    data['isvilla'] = data.apply(lambda o: isVilla(o), axis=1)
    data['istopfloor'] = data.apply(lambda o: isTopFloor(o), axis=1)
    data['ismaintained'] = data.apply(lambda o: isMaintained(o), axis=1)

def isInInnerRing(house):
    if '新城' in house['area']:
        return 0
    if house['area'] == '虎丘':
        return 0
    return 1

def isInOldCity(house):
    if not isInInnerRing(house):
        return 0
    if house['area'] == '留园西园' or house['area'] == '胥江' or house['area'] == '苏州大学' or house['area'] == '金门' or house['area'] == '石路' or house['area'] == '葑门':
        return 0
    return 1

def isAreaGreat(house):
    if house['area'] == '十全街' or house['area'] == '平江路' or house['area'] == '齐门' or house['area'] == '桃花坞':
        return 1
    return 0

def isVilla(house):
    if house['category'] == '别墅' or house['totalfloornum'] <= 2:
        return 1
    if '别墅' in house['name'] and house['totalfloornum'] <= 4:
        return 1

    return 0

def isTopFloor(house):
    if house['isvilla'] == 1:
        return 0
    if '顶楼复式' in house['name'] or '顶复' in house['name'] or '阁楼' in house['name']:
        return 1
    return 0

def isMaintained(house):
    if '散盘' in house['name'] or '号' in house['community']:
        return 0
    return 1

def calcAreaPrice(house):
    p = 20000
    if house['isinnerring'] == 0:
        p += -3000
    if house['isoldcity'] == 1:
        p += 1000
    if house['isfamousarea'] == 1:
        p += 2000
    return p

def calcCommunityPrice(house):
    p = 0
    if '私房' in house['name']:
        p -= 50000
    if house['ismaintained'] == 0:
        p -= 2000
    return p

def calcHousePrice(house):
    p = 0
    if house['isvilla'] == 1:
        p += 5000
    if house['istopfloor'] == 1:
        p += 3000
    if house['balconynum'] >= 1:
        p += 1000
    if house['gardennum'] >= 1:
        p += 1000
    p += (house['balconysize'] + house['gardensize']) / 20 * 1000
    if house['isvilla'] == 0:
        if house['floor'] == '低':
            p += 500
        if house['floor'] == '高':
            p += (3 - house['totalfloornum']) * 1000
    return p

def calcBottomPrice(house):
    up = house['bottomunitprice']
    if up * house['recognizedsize'] >= 5000000:
        up -= ((up * house['recognizedsize'] - 5000000) / 1000000 + 1) * 500
    p = house['recognizedsize'] * up
    p /= 10000
    return p

if __name__ == '__main__':
    pd.options.display.max_columns = None
    data = pd.read_csv("./crawl/final_out.csv")

    print("cleaning data")
    clean(data)
    #data = data.loc[data['id'] == '107102222709']
    print("preparing data")
    prepare(data)

    data['areaprice'] = data.apply(lambda o: calcAreaPrice(o), axis=1)
    data['houseprice'] = data.apply(lambda o: calcHousePrice(o), axis=1)
    data['communityprice'] = data.apply(lambda o : calcCommunityPrice(o), axis=1)
    data['bottomunitprice'] = data['areaprice'] + data['houseprice'] + data['communityprice']
    data['bottomprice'] = data.apply(lambda o: calcBottomPrice(o), axis=1)

    print(data.head(10))
    print(data['area'].unique())

    data.to_csv("analyzed_result.csv")
    print("calculating worthy ones")
    worthy = data.loc[data['bottomprice'] + 100 >= data['listprice']]
    worthy.to_csv("analyzed_worthy_result.csv")

    print("calculating recommended ones")
    recommended = worthy.loc[worthy['totalfloornum'] <= 4]
    recommended = recommended.loc[recommended['listprice'] <= 1500]
    recommended = recommended.loc[recommended['isinnerring'] == 1]
    recommended = recommended.loc[recommended['isoldcity'] == 1]
    recommended = recommended.loc[recommended['recognizedsize'] >= 90]
    recommended = recommended.loc[recommended['ismaintained'] == 1]
    recommended = recommended.loc[recommended['balconysize'] + recommended['gardensize'] >= 20]
    print(recommended.shape)
    recommended.to_csv("analyzed_recommended_result.csv")