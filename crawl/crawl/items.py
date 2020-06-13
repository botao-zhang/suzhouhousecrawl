# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class HouselItem(scrapy.Item):
    # define the fields for your item here like:
    id = scrapy.Field()
    name = scrapy.Field()
    listprice = scrapy.Field()
    unitprice = scrapy.Field()
    roominfo = scrapy.Field()
    size = scrapy.Field()
    community = scrapy.Field()
    area = scrapy.Field()
    floor = scrapy.Field()
    totalfloor = scrapy.Field()
    onboarddate = scrapy.Field()
    category = scrapy.Field()
    gardennum = scrapy.Field()
    gardensize = scrapy.Field()
    balconynum = scrapy.Field()
    balconysize = scrapy.Field()
    pass
