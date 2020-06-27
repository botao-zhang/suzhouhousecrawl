import pandas as pd
import re
import math


def clean(data,house):
    pattern = re.compile(r'\(共(\d+)层\)')
    data['totalfloornum'] = data['totalfloor'].apply(lambda o: int(pattern.findall(o)[0]))

    data['id'] = data['id'].apply(lambda o: str(o))
    house['id'] = house['id'].apply(lambda o: str(o))


def prepare(data):
    data['builtyear'] = data['builtyear'].fillna(value=2000)
    data['additionalfloor'] = data['additionalfloor'].fillna(value=0)
    data['garage'] = data['garage'].fillna(value=0)
    data.loc[data['isinnerring'].isna(), 'isinnerring'] = data.loc[data['isinnerring'].isna()].apply(lambda o: isInInnerRing(o), axis=1)
    data.loc[data['isoldcity'].isna(), 'isoldcity'] = data.loc[data['isoldcity'].isna()].apply(lambda o: isInOldCity(o), axis=1)
    data.loc[data['isfamousarea'].isna(), 'isfamousarea'] = data.loc[data['isfamousarea'].isna()].apply(lambda o: isAreaGreat(o), axis=1)
    data.loc[data['isvilla'].isna(), 'isvilla'] = data.loc[data['isvilla'].isna()].apply(lambda o: isVilla(o), axis=1)
    data.loc[data['istopfloor'].isna(), 'istopfloor'] = data.loc[data['istopfloor'].isna()].apply(lambda o: isTopFloor(o), axis=1)
    data.loc[data['recognizedsize'].isna(), 'recognizedsize'] = data.loc[data['recognizedsize'].isna(), 'size'].apply(lambda o: int(o))

    data.loc[data['hasservice'].isna(), 'hasservice'] = data.loc[data['hasservice'].isna()].apply(lambda o: isMaintained(o), axis=1)


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
    if not math.isnan(house['hasservice']):
        return house['hasservice']

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
    if house['hasservice'] == 0:
        p -= 2000

    p += (house['builtyear'] - 2005) * 100

    return p

def calcHousePrice(house):
    p = 0
    if house['isvilla'] == 1:
        p += 5000
    if house['istopfloor'] == 1:
        if house['recognizedsize'] != house['size']:
            p += (house['areaprice'] + house['communityprice']) * (house['size'] - house['recognizedsize']) / house['size'] / 2
        else:
            p += (house['areaprice'] + house['communityprice']) * 0.1
    if house['balconynum'] >= 1:
        p += 1000
    if house['gardennum'] >= 1:
        p += 1000
    p += (house['balconysize'] + house['gardensize']) / 20 * 1000
    if house['isvilla'] == 0:
        if house['floor'] == '低':
            p += 500
        if house['floor'] == '高':
            p += (3 - house['totalfloornum'] - house['additionalfloor']) * 1000
    return p

def calcBottomPrice(house):
    up = house['bottomunitprice']
    if up * house['recognizedsize'] >= 5000000:
        up -= ((up * house['recognizedsize'] - 5000000) / 1000000 + 1) * 500
    p = house['recognizedsize'] * up
    p /= 10000

    if house['garage'] > 0:
        p += 10
    return p

if __name__ == '__main__':
    pd.options.display.max_columns = None

    print("reading raw")
    data = pd.read_csv("./his/6_27/final_out.csv")
    print(data.shape)

    print("appending special")
    special = pd.read_csv("./input/additional_house.csv")
    data = pd.concat([data, special])
    print(data.shape)

    community = pd.read_csv("./input/community.csv")
    house = pd.read_csv("./input/house.csv")

    print("cleaning data")
    clean(data,house)
    #data = data.loc[data['id'].isin(['107102402966', '107102664327','107102657257','107101517032'])] #兰亭苑 and 闻钟苑 and 唐家巷42 and 华阳花苑
    #data = data.loc[data['id'].isin(['999999999999'])] #兰亭苑 and 闻钟苑 and 唐家巷42 and 华阳花苑
    print("preparing data")
    data = data.merge(community, how="left", left_on="community", right_on="cname")
    data = data.merge(house, how="left", on="id")
    prepare(data)

    data['areaprice'] = data.apply(lambda o: calcAreaPrice(o), axis=1)
    data['communityprice'] = data.apply(lambda o : calcCommunityPrice(o), axis=1)
    data['houseprice'] = data.apply(lambda o: calcHousePrice(o), axis=1)
    data['bottomunitprice'] = data['areaprice'] + data['houseprice'] + data['communityprice']
    data['bottomprice'] = data.apply(lambda o: calcBottomPrice(o), axis=1)

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
    recommended = recommended.loc[recommended['hasservice'] == 1]
    recommended = recommended.loc[recommended['balconysize'] + recommended['gardensize'] >= 20]
    print(recommended.shape)
    recommended.to_csv("analyzed_recommended_result.csv")