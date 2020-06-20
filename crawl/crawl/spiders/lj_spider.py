import scrapy
from crawl.items import HouselItem


class LJSpider(scrapy.Spider):
    name = "lj"
    gardenName = ['花园', '院子']
    balconyName = ['露台', '晒台', '阳光房']
    page = 1

    def __init__(self, page):
        self.page = page

    def start_requests(self):
        self.log("crawling page = %s" % self.page)
        url = 'https://su.lianjia.com/ershoufang/gusu/PG' + str(self.page) + 'co32ie1lc1lc3l4l5l6/'
        yield scrapy.Request(url=url, callback=self.parseList)

    def isAbout(self, desc, names):
        for name in names:
            if name in desc:
                return True
        return False

    def isGarden(self, desc):
        return self.isAbout(desc, self.gardenName)

    def isBalcony(self, desc):
        return self.isAbout(desc, self.balconyName)

    def parseList(self, response):
        ids = response.xpath('//div[@class="bigImgList"]/div[@class="item"]/@data-houseid').getall()
        self.log('house ids = %s' % ids)
        for id in ids:
            detailUrl = "https://su.lianjia.com/ershoufang/" + id + ".html"
            yield scrapy.Request(detailUrl, callback=self.parseDetail)
            
    def parseDetail(self, response):
        house = HouselItem()
        house['id'] = response.url.split("/")[-1].split(".")[0]
        house['name'] = response.xpath('//title/text()').get()
        house['listprice'] = response.xpath('//span[@class="total"]/text()').get()
        house['unitprice'] = response.xpath('//span[@class="unitPriceValue"]/text()').get()
        house['roominfo'] = response.xpath('//div[@class="houseInfo"]/div[@class="room"]/div[@class="mainInfo"]/text()').get()
        house['size'] = response.xpath('//div[@class="houseInfo"]/div[@class="area"]/div[@class="mainInfo"]/text()').get().split("平米")[0]
        house['community'] = response.xpath('//div[@class="communityName"]/a[@class="info "]/text()').get()
        house['area'] = response.xpath('//div[@class="areaName"]/span[@class="info"]/a/text()').getall()[1]

        floorinfo = response.xpath('//div[@class="m-content"]//div[@class="introContent"]//div[@class="base"]//div[@class="content"]//li/text()').getall()[1]
        house['floor'] = floorinfo.split("楼层")[0]
        house['totalfloor'] = floorinfo.split("楼层")[1]
        house['onboarddate'] = response.xpath('//div[@class="m-content"]//div[@class="introContent"]//div[@class="transaction"]//div[@class="content"]//li/span/text()').getall()[1]
        house['category'] = response.xpath('//div[@class="m-content"]//div[@class="introContent"]//div[@class="transaction"]//div[@class="content"]//li/span/text()').getall()[7]
        house['gardennum'] = 0
        house['gardensize'] = 0
        house['balconynum'] = 0
        house['balconysize'] = 0

        details = response.xpath('//div[@class="layout"]//div[@class="des"]//div[@id="infoList"]//div[@class="row"]//div[@class="col"]/text()').getall()
        for i in range(0, len(details), 4):
            desc = details[i]
            size = float(details[i + 1].split("平米")[0])

            if self.isGarden(desc):
                house['gardennum'] += 1
                house['gardensize'] += size
            elif self.isBalcony(desc):
                self.log("adding balcony size = %.2f" % size)
                house['balconynum'] += 1
                house['balconysize'] += size

        yield house


