from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from time import sleep
import pandas as pd
df = pd.read_csv('../../19\' summer vacation/0806/tapei_tripadvisor_top300.csv')
all_hotel = df['title'].to_list()
all_uri = df['uri'].to_list()

options = Options()
# https://blog.csdn.net/zwq912318834/article/details/78933910
options.add_argument("--incognito --headless")


# 抓取同一間飯店多頁的評論
def get_comments(url_list):
    data_list = []
    for i, url in enumerate(url_list):
        sleep(2)
        web = webdriver.Chrome('../chromedriver.exe', options=options)
        # web.implicitly_wait(15)
        web.get(url)
        soup = BeautifulSoup(web.page_source, 'html.parser')

        # 確認留言頁數
        lat_page = soup.select('a.pageNum.last')
        if len(lat_page) > 0:
            # 新版頁面
            max_page = int(lat_page[0].get('data-page-number'))
        else:
            # 考慮舊版頁面
            max_page = int(soup.select('a.pageNum')[-1].get_text())

        username = []
        userLink = []

        page_count = 1
        try:
            # 如果還能換頁
            while 'Hotel_Review' in soup.select('a.ui_button.nav.next.primary')[0].get('href'):
                page_data = []
                page_count += 1
                # 確保網頁的ui已經跑完
                web.implicitly_wait(2)

                review_section = soup.select('#REVIEWS')
                # 評論內容區塊
                user_comments_old = soup.select('.hotels-community-tab-common-Card__card--ihfZB.hotels-community-tab-common-Card__section--4r93H')
                user_comments_new = soup.select('.review-container')

                if len(user_comments_old) > 0:
                    for j, comment in enumerate(user_comments_old):
                        data = {'hotel_name': all_hotel[i]}
                        # 舊版面的留言title
                        data['comment_title'] = comment.select('div.hotels-review-list-parts-ReviewTitle__reviewTitle--2Fauz')[0].get_text()
                        # 評論日期
                        data['comment_date'] = comment.select('a.ui_header_link.social-member-event-MemberEventOnObjectBlock__member--35-jC')[0].parent.get_text().split('發表了一則評論，')[1]
                        # 住宿日期
                        data['date_of_stay'] = comment.select('div.hotels-community-tab-reviews-ReviewsTabContent__footer--2FHIK')[0].get_text()
                        # 使用者名稱
                        data['userName'] = comment.select('a.ui_header_link.social-member-event-MemberEventOnObjectBlock__member--35-jC')[0].get_text()
                        # profile
                        data['user_profile'] = 'https://www.tripadvisor.com.tw' + comment.select('a.ui_header_link.social-member-event-MemberEventOnObjectBlock__member--35-jC')[0].get('href')

                        # list contains a reference to the original dictionary
                        page_data.append(data)

                if len(user_comments_new) > 0:
                    for j, comment in enumerate(user_comments_new):
                        data = {'hotel_name': all_hotel[i]}
                        # 每則評論的標題
                        data['comment_title'] = comment.select('span.noQuotes')[0].get_text()
                        # 評論日期
                        data['comment_date'] = comment.select('span.ratingDate')[0].get('title')
                        try:
                            # 住宿日期
                            data['date_of_stay'] = comment.select('div.prw_rup.prw_reviews_stay_date_hsx')[0].div.get_text()
                        except:
                            data['date_of_stay'] = ''
                        # userId
                        data['userId'] = comment.select('div.member_info')[0].div.get('id')
                        # username
                        data['userName'] = comment.select('div.info_text')[0].div.get_text()
                        # user profile
                        data['user_profile'] = 'https://www.tripadvisor.com.tw/Profile/' + comment.select('div.info_text')[0].div.get_text()
                        # 複製一份給list
                        page_data.append(data.copy())

                data_list.extend(page_data)

                if page_count == max_page:
                    print('繁體中文評論頁數: ' + str(page_count))
                    break
                else:
                    # 留言換頁規則
                    web.get('https://www.tripadvisor.com.tw' + soup.select('a.ui_button.nav.next.primary')[0].get('href'))
                    # 取得新頁面的版面配置
                    soup = BeautifulSoup(web.page_source, 'html.parser')

        except Exception as e:
            print(e)
            print(all_hotel[i] + ' 超過總評論頁數')
            break

    web.close()
    return data_list

all_data = get_comments([all_uri[2]])
new_df = pd.DataFrame.from_dict(all_data)
print(new_df.head())
# old_df = pd.read_csv('tapei_tripadvisor_top20hotel_comment.csv')
# data_df = pd.concat([new_df, old_df], ignore_index=True)
# data_df.to_csv('./tapei_tripadvisor_top300hotel_comment.csv', index=False, encoding='utf_8_sig')
