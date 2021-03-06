from selenium import webdriver
import pandas as pd
from selenium.common.exceptions import NoSuchElementException #오류가 있을 때 지나간다
import time

options = webdriver.ChromeOptions()
options.add_argument('headless') #크롬 열리는게 안 보임
options.add_argument('disable_gpu')
options.add_argument('lang=ko_KR')

driver = webdriver.Chrome('chromedriver', options=options)
driver.implicitly_wait(3)

names = []
reviews = []

"""
url = https://www.modoodoc.com/hospitals/?search_query={}
category
"""

categories = ['치과', '피부과', '성형외과', '안과', '산부인과', '비뇨기과', '정신건강의학과', '정형외과', '마취통증의학과',
              '신경외과', '재활의학과', '영상의학과', '외과', '신경과', '소아과', '내과', '이비인후과', '가정의학과', '한의원']
# url = f'https://www.modoodoc.com/hospitals/?search_query={categories}'

url_for_login = 'https://www.modoodoc.com/'
driver.get(url_for_login)
# 로그인하기
login_xpath = '//*[@id="open_login_modal"]'
driver.find_element_by_xpath(login_xpath).click()
driver.find_element_by_xpath('//*[@id="email"]').send_keys('mijuna2@naver.com')
driver.find_element_by_xpath('//*[@id="password"]').send_keys('Nahyeon328')
driver.find_element_by_xpath('//*[@id="loginModal"]/div/div/div[2]/form/button').click()
time.sleep(1)

try:
    for category in categories:
        url = 'https://www.modoodoc.com/hospitals/?search_query=%EC%98%81%EC%83%81%EC%9D%98%ED%95%99%EA%B3%BC'
        try:
            driver.get(url)
            print(url)
            # time.sleep(1)
            driver.find_element_by_xpath('/html/body/div[3]/div/div/div[1]/div[3]/nav/ul/li[4]/a').click()
            # time.sleep(0.8)
            last_page = driver.find_element_by_xpath('/html/body/div[3]/div/div/div[1]/div[3]/nav/ul/li[4]/span').text
            last_page = int(last_page)
            print(last_page)
            driver.back()
            for i in range(1,last_page+1):  # 치과만 크롤링 1-1000페이지까지 있음
                url = url + f'&page={i}'
                # time.sleep(0.75)
                for j in range(1,11): # 한 페이지 내의 병원 이름 목록 한페이지에 10개의 병원있음 1-11
                    try: # 병원 이름
                        driver.get(url)
                        # time.sleep(1)
                        hospital_name_fullxpath = f'/html/body/div[3]/div/div/div[1]/div[3]/div[{j}]/a/div/div[2]/div[2]/div[1]/div[1]/div[1]'
                        name = driver.find_element_by_xpath(hospital_name_fullxpath).text
                        print(name)
                        driver.find_element_by_xpath(hospital_name_fullxpath).click()
                        #print(driver.current_url)
                        # time.sleep(1)
                        try: # 리뷰
                            review_len_xpath = '/html/body/div[3]/div/div[4]/div[1]/div[4]/div[1]/div/span'
                            review_len = driver.find_element_by_xpath(review_len_xpath).text
                            review_len = int(review_len)
                            #print(review_len)
                            try:
                                for k in range(1, ((review_len-1) // 10)+2): # 1, ((review_len-1) // 10)+2
                                    url_current = driver.current_url + f'?page={k}'
                                    # time.sleep(1)
                                    for l in range(2,12): # 2-12
                                        # /html/body/div[3]/div/div[4]/div[1]/div[4]/div[5]/div[2]/div/div[2]/div[3]
                                        # review_page_xpath = f'/html/body/div[3]/div/div[4]/div[1]/div[4]/div[5]/nav/ul/li[1]/span'
                                        review_content = f'/html/body/div[3]/div/div[4]/div[1]/div[4]/div[5]/div[{l}]/div/div[2]/div[3]'
                                        # time.sleep(2)
                                        review = driver.find_element_by_xpath(review_content).text
                                        names.append(name)
                                        reviews.append(review)
                                        if l == 10:
                                            print('.', end='')
                                        #print(review)
                                    # df_review = pd.DataFrame({'names': names, 'reviews': reviews})
                                    # # print(df_review.head(20))
                                    # df_review.to_csv(f'./reviews_Hospital_{name}_{k}_page.csv')
                                    # print(k, '번째 페이지 저장 완료') --> 중복저장됨...?? 뭐야
                            except:
                                # time.sleep(1)
                                print('review crawling error')
                        except:
                            print('review list error')
                    except:
                        # time.sleep(1)
                        print('name error')
                print(i, '번째 페이지 완료')

                df_review = pd.DataFrame({'names': names, 'reviews': reviews})
                #print(df_review.head(20))
                df_review.to_csv(f'./reviews_Hospital_{category}_{i}_page.csv')
                print(i, '번째 페이지 저장 완료')
        except NoSuchElementException:
            driver.get(url)
            # time.sleep(1)
            print('NoSuchElementException')
        df_review = pd.DataFrame({'names': names, 'reviews': reviews})
        # print(df_review.head(20))
        df_review.to_csv(f'./reviews_Hospital_{category}.csv')
    df_review = pd.DataFrame({'names': names, 'reviews': reviews})
    df_review.to_csv(f'./reviews_Hospital.csv')
except:
    print('crawling error')
finally:
    driver.close()