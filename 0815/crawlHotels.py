import requests
import pandas as pd
from bs4 import BeautifulSoup
import time
import json

def get_hotel_detail(url):
    time.sleep(2)
    resp = requests.get(url)
    soup = BeautifulSoup(resp.text, 'html.parser')
    meta_data = soup.select('script[type="application/ld+json"]')

    # 回傳飯店小細節的text(可以parser成json)
    return meta_data[0].get_text()


def get_services(url):
    time.sleep(2)
    resp = requests.get(url)
    soup = BeautifulSoup(resp.text, 'html.parser')
    # service_data_old = soup.select('div[class="common-ssronly-CsrPortal__portal--2v9IC"]')
    service_data = soup.select('.hotels-hr-about-amenities-AmenityGroup__amenitiesList--3MdFn')
    service_data_new = soup.select('div.amenityCol')
    #     print(len(service_data))

    service_list = []
    facility_list = []
    service_data_list = []

    #     for data in service_data:
    #         service_data_list.append(data.get('data-csrprops'))

    # todo: 考量新的版面
    if len(service_data_new) > 0:
        # 客房類型
        for i, room in enumerate(service_data_new):
            if room.get_text() == '客房類型':
                facility_list.append(room.nextSibling('div')[0].get_text())

        # 服務/ 特色
        for i, service in enumerate(service_data_new[0].select('.sub_content.ui_columns.is-multiline.is-gapless.is-mobile')):
            service_list.append(service.select('.entry.ui_column.is-4-tablet.is-6-mobile.is-4-desktop')[0].get_text())


    # 舊版介面
    if len(service_data) > 0:
        # 設施
        for i, service in enumerate(service_data[0].select('.hotels-hr-about-amenities-Amenity__amenity--3fbBj')):
            facility_list.append(service.get_text())

        # 房間特色
        for j, room in enumerate(service_data[1].select('.hotels-hr-about-amenities-Amenity__amenity--3fbBj')):
            service_list.append(room.get_text())

    return service_list, facility_list


def get_hotel(url):
    # 每次调用等待两秒, 避免被ban ip
    time.sleep(2)
    uri_list = []
    resp = requests.get(url)
    soup = BeautifulSoup(resp.text, 'html.parser')

    # imgs = soup.select('div.aspect.is-hidden-tablet > div.inner')
    titles = soup.select('div.listing_title > a[target="_blank"]')
    paimings = soup.select('div.popindex')  # 排名
    prices = soup.select('div[data-sizegroup="mini-meta-price"]')

    data_list = []

    # https://www.saltycrane.com/blog/2008/04/how-to-use-pythons-enumerate-and-zip-to/
    for i, (title, paiming, price) in enumerate(zip(titles, paimings, prices)):
        # 放肯定會有的資料
        data = {
            'title': title.get_text(),
            'paiming': paiming.get_text(),
            'recommend_price': price.get_text(),  # tripadviosr推薦的訂房網站價格，不一定最低
            'uri': 'https://www.tripadvisor.com.tw' + title.get('href')
        }

        # 根據uri抓飯店細節 (新舊版介面共用)
        per_hotel_json = json.loads(get_hotel_detail(data['uri']))
        data['hotel_address'] = per_hotel_json['address']['streetAddress']
        try:
            data['price_range'] = per_hotel_json['priceRange'].split(' (根據標準客房的平均房價)')[0]
            data['avg_rating'] = per_hotel_json['aggregateRating']['ratingValue']
            data['comment_count'] = per_hotel_json['aggregateRating']['reviewCount']
            data['offical_img_uri'] = per_hotel_json['image']
        except:
            # 真的沒有這些資料
            print('版面異動導致抓取失敗，略過...')

        try:
            # 抓飯店關於service的內容
            facility_list, service_list = get_services(data['uri'])
        except:
            print('版面異動導致抓取service/ facility失敗，略過...')
            facility_list = []
            service_list = []

        data['facility'] = ', '.join(facility_list)
        data['room'] = ', '.join(service_list)

        get_agoda = prices[i].parent.parent.parent.parent.find_next_siblings('div')[0].select('div[title="Agoda.com"]')
        if (get_agoda):
            # agoda有可能不在其他網站名單內
            data['agoda_price'] = get_agoda[0].find_next_siblings('div')[0].get_text()

        #         print(data)

        uri_list.append(data['uri'])
        data_list.append(data)

    return uri_list, data_list


url_list_taipei = ['https://www.tripadvisor.com.tw/Hotels-g293913-oa{}-Taipei-Hotels.html'.format(str(i)) for i in range(0, 1200, 30)]
url_list_new_taipei = ['https://www.tripadvisor.com.tw/Hotels-g1432365-oa{}-New_Taipei-Hotels.html'.format(str(i)) for i in range(0, 600, 30)]
url_list_taoyuan = ['https://www.tripadvisor.com.tw/Hotels-g297912-oa{}-Taoyuan-Hotels.html'.format(str(i)) for i in range(0, 240, 30)]
url_list_Hsinchu = ['https://www.tripadvisor.com.tw/Hotels-g297906-oa{}-Hsinchu-Hotels.html'.format(str(i)) for i in range(0, 90, 30)]
url_list =['https://www.tripadvisor.com.tw/Hotels-g297909-oa{}-Pingtung-Hotels.html'.format(str(i)) for i in range(0, 1500, 30)]
url_list_Taitung =['https://www.tripadvisor.com.tw/Hotels-g304163-oa{}-Taitung-Hotels.html'.format(str(i)) for i in range(0, 1440, 30)]
all_data = []

for k in range(0, 20):
    hotel_url, hotels_data = get_hotel(url_list[k])
    all_data = all_data + hotels_data

data_df = pd.DataFrame.from_dict(all_data)
data_df.to_csv('./Pingtung_tripadvisor_top500.csv', index=False, encoding='utf_8_sig')
