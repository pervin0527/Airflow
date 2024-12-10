import os
import json
import time
import logging
import requests
import pandas as pd

from datetime import datetime
from requests.exceptions import ConnectionError, RequestException

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException


def make_request_with_retry(
    url: str,
    max_retries: int = 5,
    initial_delay: float = 1,
    max_delay: float = 30,
    backoff_factor: float = 2):
    """
    지정된 URL로 GET 요청을 보내고 실패 시 재시도하는 함수
    
    Args:
        url: 요청할 URL
        max_retries: 최대 재시도 횟수
        initial_delay: 첫 재시도 전 대기 시간(초)
        max_delay: 최대 대기 시간(초)
        backoff_factor: 재시도 간 대기 시간 증가 비율
    
    Returns:
        성공 시 Response 객체, 실패 시 None
    """
    delay = initial_delay
    
    for attempt in range(max_retries):
        try:
            response = requests.get(url)
            response.raise_for_status()  # 4XX, 5XX 에러 체크
            return response
            
        except (ConnectionError, RequestException) as e:
            if attempt == max_retries - 1:  # 마지막 시도였을 경우
                logging.error(f"Maximum retries ({max_retries}) exceeded. Last error: {str(e)}")
                return None
                
            # 다음 재시도까지 대기
            sleep_time = min(delay, max_delay)
            logging.warning(f"Attempt {attempt + 1} failed. Retrying in {sleep_time} seconds... Error: {str(e)}")
            time.sleep(sleep_time)
            delay *= backoff_factor  # 대기 시간을 점진적으로 증가


def wanted_crawling():
    data_dir = "./data"
    os.makedirs(data_dir, exist_ok=True)
    base_url = "https://www.wanted.co.kr/wd/"

    options = Options()
    # options.add_argument("--headless")
    # options.add_argument("--window-size=1920,1080")

    ## 403 Forbidden 문제 발생을 해결하기 위함.
    ## 웹사이트가 봇을 탐지하고 접근을 차단하는 것을 방지하기 위해 User-Agent를 설정함.
    options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')

    driver = webdriver.Chrome(options=options)
    driver.get(base_url)

    n_iter = 0
    curr_posts = 0
    total_data = []
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)
        new_height = driver.execute_script("return document.body.scrollHeight")

        ## CLASS NAME
        job_list = driver.find_element(By.CLASS_NAME, "List_List__Ni_dK")
        elements = job_list.find_elements(By.CLASS_NAME, "Card_Card__WdaEk")
        print(f"Current Post Cards : {len(elements)}")
        
        new_posts = elements[curr_posts:]
        for post in new_posts:
            link = post.find_element(By.TAG_NAME, 'a')
            url = link.get_attribute('href') ## 채용공고 카드 url
            company_name = link.get_attribute("data-company-name") ## 회사명
            data_position_name = link.get_attribute("data-position-name") ## 채용 포지션

            if url and url.startswith(base_url):
                company_code = url[len(base_url):]
                api_url = f"https://www.wanted.co.kr/api/v4/jobs/{company_code}"
                print("=" * 30)
                print(f"{company_name}, {data_position_name}, {company_code}")
                print(f"{url}")
                print(f"{api_url}")

                # response = requests.get(api_url)
                response = make_request_with_retry(api_url)
                response.raise_for_status()
                data = response.json()
                print(data, '\n', "=" * 30, '\n')
                time.sleep(0.1)
                
                total_data.append(data)
                curr_posts += 1
            

        if new_height == last_height:
            print(f"Scrolling stopped. Final page height: {new_height}")
            break

        last_height = new_height
        n_iter += 1

        if n_iter == 3:
            break

    driver.close()

    current_time = datetime.now().strftime("%Y%m%d-%H%M%S")
    output_filename = f"wanted_recruit_data-{current_time}.json"
    output_path = os.path.join(data_dir, output_filename)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(total_data, f, ensure_ascii=False, indent=4)

    print(f"Job data saved to {output_path}")


if __name__ == "__main__":
    wanted_crawling()
