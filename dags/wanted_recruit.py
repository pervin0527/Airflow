import os
import json
import time
import requests

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException

def find_element_with_retry(driver, by, value, max_retries=1):
    retries = 0
    while retries < max_retries:
        elements = driver.find_elements(by, value)
        if elements:
            return elements[0]
        retries += 1
        time.sleep(0.5)
    return None


def find_elements_with_retry(driver, by, value, max_retries=1):
    retries = 0
    while retries < max_retries:
        elements = driver.find_elements(by, value)
        if elements:
            return elements
        retries += 1
        time.sleep(0.5)
    return []


def fetch_job_data(api_url, url=None):
   try:
       # GET 요청 보내기
       response = requests.get(api_url)
       
       # 요청이 성공적으로 완료되었는지 확인 
       response.raise_for_status()
       
       # JSON 형식으로 응답 데이터를 파싱
       job_data = response.json()

       # share_link가 없거나 null인 경우 url 파라미터 값을 할당
       if 'share_link' not in job_data or job_data['share_link'] is None:
           job_data['share_link'] = url
           
       return job_data

   except requests.exceptions.HTTPError as http_err:
       print(f"HTTP error occurred: {http_err}")
   except Exception as err:
       print(f"An error occurred: {err}")


def save_job_data(data, filename="job_data.json"):
    try:
        if os.path.exists(filename):
            with open(filename, 'r', encoding='utf-8') as f:
                existing_data = json.load(f)
        else:
            existing_data = []
            
        existing_data.append(data)
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(existing_data, f, ensure_ascii=False, indent=2)
            
    except Exception as e:
        print(f"Error saving data: {e}")


def test():
    base_url = "https://www.wanted.co.kr/wd/"

    options = Options()
    options.add_argument("--headless")
    options.add_argument("--window-size=1920,1080")

    ## 403 Forbidden 문제 발생을 해결하기 위함.
    ## 웹사이트가 봇을 탐지하고 접근을 차단하는 것을 방지하기 위해 User-Agent를 설정함.
    options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')


    driver = webdriver.Chrome(options=options)
    driver.get(base_url)

    sc_dir = "./screenshots"
    data_dir = "./data"
    os.makedirs(sc_dir, exist_ok=True)
    os.makedirs(data_dir, exist_ok=True)
    driver.save_screenshot(f"{sc_dir}/debug_0.png")

    sc_idx = 1
    curr_posts = 0
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)
        new_height = driver.execute_script("return document.body.scrollHeight")

        ## CSS Selector
        # selector = ("#__next > div.JobList_JobList__Qj_5c > div.JobList_JobList__contentWrapper__3wwft > ul > li")
        # elements = driver.find_elements(By.CSS_SELECTOR, selector)

        ## CLASS NAME
        job_list = driver.find_element(By.CLASS_NAME, "List_List__Ni_dK")
        elements = job_list.find_elements(By.CLASS_NAME, "Card_Card__WdaEk")
        new_posts = elements[curr_posts:]

        for post in new_posts:
            link = post.find_element(By.TAG_NAME, 'a')
            url = link.get_attribute('href')

            if url and url.startswith(base_url):
                company_code = url[len(base_url):]
                api_url = f"https://www.wanted.co.kr/api/v4/jobs/{company_code}"
                data = fetch_job_data(api_url, url)
                save_job_data(data, "./data/job_data.json")
                time.sleep(0.1)
                curr_posts += 1

                if curr_posts > 10:
                    return

        driver.save_screenshot(f"{sc_dir}/debug_{sc_idx}.png")
        sc_idx += 1
        print(len(elements))
    
        if new_height == last_height:
            print(f"Scrolling stopped. Final page height: {new_height}")
            break
        last_height = new_height

    driver.close()


if __name__ == "__main__":
    test()
