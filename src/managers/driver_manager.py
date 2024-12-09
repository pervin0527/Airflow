from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.webdriver import WebDriver

from webdriver_manager.chrome import ChromeDriverManager

from managers.header_manager import AdvancedHeaderGenerator

from settings import environment

class WebDriverManager:
    def __init__(self):
        self.driver = None
        
        
    def configure_chrome_options(self) -> Options:
        options = Options()
        # 헤드리스 모드 비활성화 (주석처리 해제)
        if environment != 'dev':
            options.add_argument('--headless')
        # GPU 가속 비활성화
        options.add_argument('--disable-gpu')
        # 샌드박스 모드 비활성화
        options.add_argument('--no-sandbox')
        # /dev/shm 사용 비활성화
        options.add_argument('--disable-dev-shm-usage')
        # 원격 디버깅 포트 설정
        # options.add_argument('--remote-debugging-port=9222')
        # 팝업 차단 비활성화 (필요 시 주석 해제)
        # options.add_argument('--disable-popup-blocking')
        # 정보 바 표시 비활성화
        options.add_argument('--disable-infobars')
        # 개인정보 보호 모드로 실행
        options.add_argument('--incognito')
        
        # SSL 인증서 관련 옵션 추가
        options.add_argument('--ignore-certificate-errors')
        options.add_argument('--ignore-ssl-errors')
        options.add_argument('--allow-insecure-localhost')
        
        # AdvancedHeaderGenerator를 사용하여 User-Agent 설정
        header_generator = AdvancedHeaderGenerator()
        headers = header_generator.generate_headers()
        options.add_argument(f"user-agent={headers['User-Agent']}")
        # options.binary_location = "/usr/bin/google-chrome"
        return options
    
    
    def create_webdriver(self) -> WebDriver:
        options = self.configure_chrome_options()
        
        if environment == 'dev':
            # 개발 환경에서는 ChromeDriverManager 사용
            service = Service(ChromeDriverManager().install())
        else:
            # 프러덕션 환경에서는 Chromedriver를 수동으로 경로 설정
            service = Service('/usr/local/bin/chromedriver-linux64/chromedriver')


        self.driver = webdriver.Chrome(service=service, options=options)
        return self.driver
    
    
    def get_webdriver(self) -> WebDriver:
        if self.driver is None:
            self.driver = self.create_webdriver()
        return self.driver
    
    
    def release_all_drivers(self):
        if self.driver is not None:
            self.driver.quit()
            self.driver = None
