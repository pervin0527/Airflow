import os
import logging
import logging.handlers
import datetime
import pytz
import traceback

from settings.dev import DevConfig
from settings.prod import ProdConfig

from dotenv import load_dotenv


class KSTFormatter(logging.Formatter):
    def formatTime(self, record, datefmt=None):
        kst = pytz.timezone('Asia/Seoul')
        ct = datetime.datetime.fromtimestamp(record.created, kst)
        return ct.strftime(datefmt) if datefmt else ct.isoformat()

    def formatException(self, ei):
        return ''.join(traceback.format_exception(*ei))

def setup_logger(name):
    formatter = KSTFormatter('%(asctime)s - %(levelname)s - %(message)s', '%Y-%m-%d %H:%M:%S')
    handler = logging.StreamHandler()  # 콘솔에 로그를 출력하는 핸들러
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(handler)
    return logger


logger = setup_logger(__name__)

# PYTHON_PROFILES_ACTIVE 환경 변수를 직접 os.environ에서 가져옴
environment = os.environ.get("PYTHON_PROFILES_ACTIVE", 'prod')  # 'dev'를 기본값으로 설정

# 환경에 따라 다른 .env 파일 경로 설정
if environment == 'dev':
    env_file = '.env.development'
elif environment == 'prod':
    env_file = '.env.production'
else:
    raise ValueError(f"Unsupported environment setting: {environment}")

print(environment)

# .env 파일의 경로를 상위 폴더 기준으로 설정
dotenv_path = os.path.join(os.path.dirname(__file__), '..', '..', env_file)
logger.debug("Loading .env from: %s", dotenv_path)

# .env 로드 결과를 변수에 저장
load_result = load_dotenv(dotenv_path, override=True)
logger.debug("Load result: %s", load_result)

# 환경변수 로드 후 사용
google_api_key = os.getenv('GOOGLE_API_KEY')
kakao_api_key = os.getenv('KAKAO_API_KEY')
api_url = os.getenv('API_URL')

# 로그 디렉터리 설정은 환경에 상관없이 동일
LOG_DIR = '/home/liam/airflow/logs'

class EnvironmentConfig():
    def __init__(self):
        if environment == 'dev':
            self.config_instance = DevConfig()
        elif environment == 'prod':
            self.config_instance = ProdConfig()
        else:
            raise ValueError("Unsupported environment setting")

    def get(self, key, default=None):
        return self.config_instance.get(key, default)


# 환경 설정 기반의 인스턴스 생성 전에 환경 변수가 올바르게 설정되었는지 확인
if environment not in ['dev', 'prod']:
    raise Exception("Environment not set correctly. Current environment: " + str(environment))
else:
    config = EnvironmentConfig()