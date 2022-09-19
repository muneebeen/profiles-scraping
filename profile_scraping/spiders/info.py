import json

import scrapy
from scrapy.crawler import CrawlerProcess
import pandas as pd

class InfoSpider(scrapy.Spider):
    name = 'info'
    start_urls = ['https://nzcca.org.nz/find-a-counsellor/']

    company_data = []

    headers = {
        "authority": "nzcca.org.nz",
        "accept": "text/html, */*; q=0.01",
        "accept-language": "en-US,en;q=0.9",
        "cache-control": "no-cache",
        "pragma": "no-cache",
        "referer": "https://nzcca.org.nz/find-a-counsellor/",
        "sec-ch-ua": "\"Google Chrome\";v=\"105\", \"Not)A;Brand\";v=\"8\", \"Chromium\";v=\"105\"",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "\"Windows\"",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36",
        "x-requested-with": "XMLHttpRequest"
    }

    def parse(self, response):
        res = response.css('[data-target="#ViewCounsellor"]')
        for profile in res:
            name = profile.css('a::text').get()
            data_url = profile.css('[data-url]::attr(data-url)').get()
            yield scrapy.Request(data_url, headers=self.headers, meta={'name':name},
                                 callback=self.profile_parse)

    def profile_parse(self, response):

        list_data = []
        all_fields = response.css('.modal-body .col-12.col-md-7.border-right .row > div')
        data = {all_fields[v].css('strong ::text').extract_first().strip():all_fields[v+1].css('::text').extract_first().strip() for v in range(0, len(all_fields), 2)}

        model_bodies = response.css('.modal-body')

        if len(model_bodies) > 1:
            for num in range(1, len(model_bodies)):
                if response.css('.modal-body div >.col-md-7 h3+p::text'):
                    text = model_bodies[num].css('.modal-body div >.col-md-7 h3+p::text').getall()
                    info_array = []
                    for arr in text:
                        if arr:
                            info_array.append(arr.strip())
                    if info_array and info_array != ' ':
                        list_data.append(' '.join(info_array))
        details = {
            'name': response.css('div.modal-body h1::text').get(),
            'data': data,
            'address': list_data,

        }
        print(len(details))
        self.company_data.append(details)


    def close(spider, reason):
        info_json = json.dumps(spider.company_data)
        h = 1
        with open("sample.json", "w") as outfile:
            outfile.write(info_json)
        # dataframe = pd.DataFrame(spider.company_data)
        # h = 1
        # dataframe.to_json('data.json')



crawler = CrawlerProcess()
crawler.crawl(InfoSpider)
crawler.start()