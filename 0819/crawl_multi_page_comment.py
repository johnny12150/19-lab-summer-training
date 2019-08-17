from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from time import sleep

options = Options()
# https://blog.csdn.net/zwq912318834/article/details/78933910
options.add_argument("--incognito --headless")


# 抓取同一間飯店多頁的評論
def get_comments(url_list):
    for i, url in enumerate(url_list):
        sleep(2)
        web = webdriver.Chrome('../chromedriver.exe', options=options)
        # web.implicitly_wait(15)
        web.get(url)
        soup = BeautifulSoup(web.page_source, 'html.parser')
        # 能不能換頁 (span的表示不能換頁)
        # next_page = soup.select('a.ui_button.nav.next.primary')
        # strict mode
        next_page = soup.select('a[class="ui_button nav next primary"]')
        previous_page = soup.select('.nav previous ui_button secondary')

        # 確認留言頁數

        # 留言換頁規則

        page_count = 1
        try:
            # 如果還能換頁
            while 'Hotel_Review' in soup.select('a.ui_button.nav.next.primary')[0].get('href'):
                print(soup.select('a.ui_button.nav.next.primary')[0].get('href'))
                page_count += 1
                # 確保網頁的ui已經跑完
                web.implicitly_wait(2)
                # 點擊下一頁
                # web.find_element_by_css_selector('a.ui_button.nav.next.primary').click()
                # 重新讀取網頁內容
                # soup = BeautifulSoup(web.page_source, 'html.parser')
                review_section = soup.select('#REVIEWS')
                # 這頁有幾筆評論
                user_comments_old = soup.select('.hotels-community-tab-common-Card__card--ihfZB.hotels-community-tab-common-Card__section--4r93H')
                user_comments_new = soup.select('.review-container')
                # 抓user id
                if len(user_comments_old) > 0:
                    print(len(user_comments_old))
                if len(user_comments_new) > 0:
                    for j, comment in enumerate(user_comments_new):
                        print(comment.select('span.noQuotes')[0].get_text())

                web.get('https://www.tripadvisor.com.tw' + soup.select('a.ui_button.nav.next.primary')[0].get('href'))
                soup = BeautifulSoup(web.page_source, 'html.parser')

        except:
            print('總評論頁數: ' + str(page_count))
            break

    web.close()

get_comments(['https://www.tripadvisor.com.tw/Hotel_Review-g13808853-d12419761-Reviews-CitizenM_Taipei_North_Gate-Zhongzheng_District_Taipei.html'])
