import requests
import pandas as pd
from bs4 import BeautifulSoup
import time
import json
import re


def get_services(url):
    time.sleep(2)
    resp = requests.get(url)
    soup = BeautifulSoup(resp.text, 'html.parser')
    # service_data_old = soup.select('div[class="common-ssronly-CsrPortal__portal--2v9IC"]')
    service_data = soup.select('.hotels-hr-about-amenities-AmenityGroup__amenitiesList--3MdFn')
    service_data_new = soup.select('div.amenityCol')
    meta_data = soup.select('script[type="application/ld+json"]')

    service_list = []
    facility_list = []

    try:
        # 幾星飯店
        hotel_star = soup.select('.hotels-hr-about-layout-TextItem__textitem--2JToc')
        hotel_star_new = soup.select('span.ui_star_rating')
        # 舊版介面
        if len(hotel_star) > 0:
            hotel_star_str = re.findall('star_\d+', ''.join(hotel_star[0].span.get('class')))
            hotel_star_int = int(hotel_star_str[0].split('_')[1]) / 10
        else:
            hotel_star_str = re.findall('star_\d+', ''.join(hotel_star_new[0].get('class')))
            hotel_star_int = int(hotel_star_str[0].split('_')[1]) / 10

    except:
        hotel_star_int = None

    # 考量新的版面
    if len(service_data_new) > 0:
        # 客房類型
        for i, room in enumerate(service_data_new):
            if room.get_text() == '客房類型':
                facility_list.append(room.nextSibling('div')[0].get_text())

        # 服務/ 特色
        for i, service in enumerate(service_data_new[0].select('.sub_content.ui_columns.is-multiline.is-gapless.is-mobile')):
            service_list.append(service.select('.entry.ui_column.is-4-tablet.is-6-mobile.is-4-desktop')[0].get_text())

    # FIXME:舊版介面
    if len(service_data) > 0:
        # 設施
        for i, service in enumerate(service_data[0].select('.hotels-hr-about-amenities-Amenity__amenity--3fbBj')):
            facility_list.append(service.get_text())

        if len(service_data) > 1:
            # 房間特色
            for j, room in enumerate(service_data[1].select('.hotels-hr-about-amenities-Amenity__amenity--3fbBj')):
                service_list.append(room.get_text())

        room_style_list = []
        hotel_service_list = []
        # TODO: 更新舊版介面能取得的資訊
        for k, data in enumerate(soup.select('div.ssr-init-26f')):
            room_data = data.get('data-ssrev-handlers')
            # 如果有存data
            if len(room_data) > 0:
                json_room_data = json.loads(room_data)
                if json_room_data:
                    # 如果data裡面包含 @ta/hotels.hr-about-amenities
                    if json_room_data['load'][1] == "@ta/hotels.hr-about-amenities":
                        room_detail = json_room_data['load'][3]
                        # 房型與房內設備
                        # print(len(room_detail['amenities']['highlightedAmenities']['roomAmenities']))
                        for room_style in room_detail['amenities']['highlightedAmenities']['roomAmenities']:
                            room_style_list.append(room_style['amenityNameLocalized'])
                        print(room_style_list)
                        
                        # 飯店硬體設施
                        # print(len(room_detail['amenities']['highlightedAmenities']['propertyAmenities']))
                        for room_service in room_detail['amenities']['highlightedAmenities']['propertyAmenities']:
                            hotel_service_list.append(room_service['amenityNameLocalized'])
                        print(hotel_service_list)

                        # 沒有直接寫在網頁上的
                        # print(len(room_detail['amenities']['nonHighlightedAmenities']['roomAmenities']))
                        for room_style in room_detail['amenities']['nonHighlightedAmenities']['roomAmenities']:
                            room_style_list.append(room_style['amenityNameLocalized'])
                        print(room_style_list)
                        
                        print(len(room_detail['amenities']['nonHighlightedAmenities']['propertyAmenities']))

    try:
        hotel_data = json.loads(meta_data[0].get_text())
    except:
        hotel_data = {}

    try:
        # 飯店國家與縣市
        hotel_city = json.loads(meta_data[1].get_text())
    except:
        hotel_city = {}

    # 降低抓價格的缺值機率
    current_price = soup.select('div.bb_price_text')
    current_price_old = soup.select('div.hotels-hotel-offers-DominantOffer__price--D-ycN')
    current_lowest_price = ''
    # new UI
    if len(current_price) > 0:
        current_lowest_price = current_price[0].get_text()
    # old UI, 沒特價
    elif len(current_price_old) > 0:
        current_lowest_price = current_price_old[0].get_text()
    else:
        # 多筆相同價格/ 有特價, 找特定class開頭
        # https://stackoverflow.com/questions/52842778/find-partial-class-names-in-spans-with-beautiful-soup
        multi_price = soup.select('div[class*="hotels-hotel-offers-DetailChevronOffer__price--"]')
        if len(multi_price) > 0:
            current_lowest_price = multi_price[0].get_text()
            for n, price in enumerate(multi_price):
                # 找最低價格, .hotels-hotel-offers-DetailChevronOffer__xthrough--
                if price.previous_sibling:
                    current_lowest_price = price.get_text()

    gmap_lat = None
    gmap_lng = None
    try:
        RecentJs = soup.findAll(attrs={'type': 'text/javascript'}, string=re.compile(r"taStore.store\('typeahead.recentHistoryList',"))
        for m in RecentJs:
            # 包含飯店GPS的區域
            # print(json.loads(m.text.split("\'typeahead.recentHistoryList\', ")[1].split('taStore.store(\'typeahead.restaurant\'')[0].split(');')[0]))
            geo_data = json.loads(m.text.split("\'typeahead.recentHistoryList\', ")[1].split('taStore.store(\'typeahead.restaurant\'')[0].split(');')[0])
            # 經緯度
            # print(geo_data[0]['coords'])
            gmap_lat = geo_data[0]['coords'].split(',')[0]
            gmap_lng = geo_data[0]['coords'].split(',')[1]
    except:
        pass

    # 回傳飯店小細節的text(可以parser成json)
    return service_list, facility_list, hotel_data, hotel_star_int, hotel_city, current_lowest_price, gmap_lat, gmap_lng


def get_hotel(url):

    uri_list = []
    resp = requests.get(url)
    # 每次调用等待两秒, 避免被ban ip
    time.sleep(2)
    soup = BeautifulSoup(resp.text, 'html.parser')

    titles = soup.select('div.listing_title > a[target="_blank"]')
    paimings = soup.select('div.popindex')  # 排名
    prices = soup.select('div[data-sizegroup="mini-meta-price"]')
    # metadata
    metadata = soup.select('#map_wc_dusty_bridge > div')
    hotel30_data = json.loads(metadata[1].get('data-hotels-data'))

    data_list = []

    # https://www.saltycrane.com/blog/2008/04/how-to-use-pythons-enumerate-and-zip-to/
    for i, (title, paiming) in enumerate(zip(titles, paimings)):
        # 放肯定會有的資料
        data = {
            'title': title.get_text(),
            'paiming': paiming.get_text(),
            # 'recommend_price': prices[i+1].get_text(),  # tripadviosr推薦的訂房網站價格，不一定最低
            'uri': 'https://www.tripadvisor.com.tw' + title.get('href'),
        }

        try:
            data['lat'] = hotel30_data['hotels'][i]['geoPoint']['latitude']
            data['lng'] = hotel30_data['hotels'][i]['geoPoint']['longitude']
        except:
            data['lat'] = None
            data['lng'] = None

        # 根據uri抓飯店細節 (新舊版介面共用)
        facility_list, service_list, per_hotel_json, stars, city, pricing, g_lat, g_lng = get_services(data['uri'])
        try:
            # 確保有值
            if pricing:
                data['recommend_price'] = pricing
            else:
                data['recommend_price'] = prices[i + 1].get_text()

        except:
            pass

        try:
            data['hotel_address'] = per_hotel_json['address']['streetAddress']
            data['hotel_star'] = stars
        except:
            pass

        try:
            data['hotel_city'] = city['itemListElement'][2]['item']['name']
            data['hotel_section'] = city['itemListElement'][3]['item']['name']
        except:
            pass

        try:
            data['price_range'] = per_hotel_json['priceRange'].split(' (根據標準客房的平均房價)')[0]
            data['avg_rating'] = per_hotel_json['aggregateRating']['ratingValue']
            data['comment_count'] = per_hotel_json['aggregateRating']['reviewCount']
            data['offical_img_uri'] = per_hotel_json['image']
        except:
            # 真的沒有這些資料
            pass

        data['facility'] = ', '.join(facility_list)
        data['room'] = ', '.join(service_list)

        try:
            get_agoda = prices[i].parent.parent.parent.parent.find_next_siblings('div')[0].select('div[title="Agoda.com"]')
            if get_agoda:
                # agoda有可能不在其他網站名單內
                data['agoda_price'] = get_agoda[0].find_next_siblings('div')[0].get_text()
        except:
            pass

        data['gmap_lat'] = g_lat
        data['gmap_lng'] = g_lng

        uri_list.append(data['uri'])
        data_list.append(data)

    return uri_list, data_list


url_list_taipei = ['https://www.tripadvisor.com.tw/Hotels-g293913-oa{}-Taipei-Hotels.html'.format(str(i)) for i in range(0, 1200, 30)]
url_list_new_taipei = ['https://www.tripadvisor.com.tw/Hotels-g1432365-oa{}-New_Taipei-Hotels.html'.format(str(i)) for i in range(0, 600, 30)]
url_list_taoyuan = ['https://www.tripadvisor.com.tw/Hotels-g297912-oa{}-Taoyuan-Hotels.html'.format(str(i)) for i in range(0, 240, 30)]
url_list_Hsinchu = ['https://www.tripadvisor.com.tw/Hotels-g297906-oa{}-Hsinchu-Hotels.html'.format(str(i)) for i in range(0, 90, 30)]
url_list_Pingtung =['https://www.tripadvisor.com.tw/Hotels-g297909-oa{}-Pingtung-Hotels.html'.format(str(i)) for i in range(0, 1500, 30)]
url_list_Taitung =['https://www.tripadvisor.com.tw/Hotels-g304163-oa{}-Taitung-Hotels.html'.format(str(i)) for i in range(0, 1440, 30)]
url_list_Hualien =['https://www.tripadvisor.com.tw/Hotels-g297907-oa{}-Hualien-Hotels.html'.format(str(i)) for i in range(0, 2220, 30)]
url_list_Taichung = ['https://www.tripadvisor.com.tw/Hotels-g297910-oa{}-Taichung-Hotels.html'.format(str(i)) for i in range(0, 870, 30)]
url_list_Kaohsiung = ['https://www.tripadvisor.com.tw/Hotels-g297908-oa{}-Kaohsiung-Hotels.html'.format(str(i)) for i in range(0, 660, 30)]
url_list_Tainan = ['https://www.tripadvisor.com.tw/Hotels-g293912-oa{}-Kaohsiung-Hotels.html'.format(str(i)) for i in range(0, 1140, 30)]
url_list_Yilan = ['https://www.tripadvisor.com.tw/Hotels-g608526-oa{}-Yilan-Hotels.html'.format(str(i)) for i in range(0, 1770, 30)]
url_list_Nantou = ['https://www.tripadvisor.com.tw/Hotels-g304160-oa{}-Nantou-Hotels.html'.format(str(i)) for i in range(0, 990, 30)]
url_list_Keelung = ['https://www.tripadvisor.com.tw/Hotels-g317130-oa{}-Keelung-Hotels.html'.format(str(i)) for i in range(0, 60, 30)]
url_list_Chiayi = ['https://www.tripadvisor.com.tw/Hotels-g297904-oa{}-Chiayi-Hotels.html'.format(str(i)) for i in range(0, 150, 30)]
all_data = []

for k in range(0, 30):
    hotel_url, hotels_data = get_hotel(url_list_taipei[k])
    all_data = all_data + hotels_data

data_df = pd.DataFrame.from_dict(all_data)
# data_df.to_csv('./taipei_tripadvisor_top1500.csv', index=False, encoding='utf_8_sig')
