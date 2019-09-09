from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from time import sleep
import sys
import traceback
import pandas as pd
import re

df = pd.read_csv('F:/volume/19\' summer vacation/0821/taipei_tripadvisor_top500_clean.csv')
all_hotel = df['title'].to_list()
all_uri = df['uri'].to_list()

options = Options()
# https://blog.csdn.net/zwq912318834/article/details/78933910
options.add_argument("--incognito --headless")


# 抓取同一間飯店多頁的評論
def get_comments(url_list, start=0):
    data_list = []
    for i, url in enumerate(url_list):
        # 考慮從第幾間飯店開始
        i += start
        sleep(2)
        web = webdriver.Chrome('../chromedriver.exe', options=options)
        # web.implicitly_wait(15)
        try:
            web.get(url)
            soup = BeautifulSoup(web.page_source, 'html.parser')
        except:
            # 紀錄timeout的 url
            with open("./err.txt", "w", encoding='UTF-8') as myfile:
                myfile.write(all_uri[i]+'\n')
            continue

        # 確認留言頁數
        lat_page = soup.select('a.pageNum.last')
        if len(lat_page) > 0:
            try:
                # 新版頁面
                max_page = int(lat_page[0].get('data-page-number'))
            except:
                max_page = 1
        else:
            try:
                # 考慮舊版頁面
                max_page = int(soup.select('a.pageNum')[-1].get_text())
            except:
                max_page = 1

        username = []
        userLink = []

        page_count = 1
        try:
            # 如果還能換頁
            # while 'Hotel_Review' in soup.select('a.ui_button.nav.next.primary')[0].get('href'):
            while True:
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
                        try:
                            rating_str = re.findall('bubble_\d+', ''.join(comment.select('span.ui_bubble_rating')[0].get('class')))
                            # 該評論給飯店幾分 
                            data['rating'] = int(rating_str[0].split('_')[1]) / 10
                        except:
                            pass

                        try:
                            # 哪裡人(不一定會有)
                            data['country'] = comment.select('span.social-member-common-MemberHometown__hometown--3kM9S')[0].get_text()
                        except:
                            pass

                        try:
                            # 幾個人推薦該評論
                            data['recommend_count'] = comment.select('span.social-member-MemberHeaderStats__bold--3z3qh')[1].get_text()
                        except:
                            pass
                        
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
                        try:
                            rating_str = re.findall('bubble_\d+', ''.join(comment.select('span.ui_bubble_rating')[0].get('class')))
                            # 該評論給飯店幾分 
                            data['rating'] = int(rating_str[0].split('_')[1]) / 10
                        except:
                            pass

                        try:
                            # 哪裡人 (新UI可能會有)
                            data['country'] = comment.select('div.userLoc')[0].get_text()
                        except:
                            pass

                        try:
                            # 幾個人推薦該評論
                            data['recommend_count'] = comment.select('span.ui_icon.thumbs-up-fill')[0].nextSibling('span')[0].get_text()
                        except:
                            pass
                        
                        # 複製一份給list
                        page_data.append(data.copy())

                data_list.extend(page_data)

                if page_count >= max_page:
                    print('繁體中文評論頁數: ' + str(page_count))
                    break
                else:
                    # 留言換頁規則
                    web.get('https://www.tripadvisor.com.tw' + soup.select('a.ui_button.nav.next.primary')[0].get('href'))
                    # 取得新頁面的版面配置
                    soup = BeautifulSoup(web.page_source, 'html.parser')

        except Exception as e:
            # print(e)
            error_class = e.__class__.__name__ #取得錯誤類型
            detail = e.args[0] #取得詳細內容
            cl, exc, tb = sys.exc_info() #取得Call Stack
            lastCallStack = traceback.extract_tb(tb)[-1] #取得Call Stack的最後一筆資料
            fileName = lastCallStack[0] #取得發生的檔案名稱
            lineNum = lastCallStack[1] #取得發生的行號
            funcName = lastCallStack[2] #取得發生的函數名稱
            errMsg = "File \"{}\", line {}, in {}: [{}] {}".format(fileName, lineNum, funcName, error_class, detail)
            print(errMsg)
            print(all_hotel[i] + ' 超過總評論頁數')

    web.close()
    return data_list


all_data = get_comments(all_uri[100:200], 100)
new_df = pd.DataFrame.from_dict(all_data)
old_df = pd.read_csv('tapei_tripadvisor_top100hotel_comment.csv')
data_df = pd.concat([new_df, old_df], ignore_index=True, sort=False)
data_df.to_csv('./tapei_tripadvisor_top200hotel_comment.csv', index=False, encoding='utf_8_sig')
