import os
import re
import json
import pytz
import openai
import asyncio
import datetime

from glob import glob

from pathlib import Path
from dotenv import load_dotenv

root_dir = Path(__file__).parents[4]
env_path = root_dir / 'keys.env'
print(env_path)
load_dotenv(dotenv_path=env_path)
api_key = os.getenv("OPENAI_API_KEY")
openai_client = openai.AsyncOpenAI(api_key=api_key)

default_prompt = '''
### Input Format
채용 공고 텍스트 데이터

### Output Format
JSON 형식의 구조화된 데이터:
{
    "welfare": [
        {
            "name": str,  // 복리 후생 명칭
            "description": str  // 복리 후생 설명 (200자 이내)
        }
    ],
    "career_start": int | None,  // 경력 시작 연수
    "career_end": int | None,    // 경력 종료 연수
    "career_type": enum str,     // 경력 유형
    "work_type": enum str,       // 고용 형태
    "education_type": enum str,  // 학력 요구사항
    "workday_content": str       // 근무 형태
}

### Constraints
1. career_type 가능 값:
   - EXPERIENCED: "경력"
   - EXECUTIVE: "임원"
   - ENTRY_EXPERIENCED: "신입 또는 경력"
   - UNTIL_HIRED: "경력 무관"

2. work_type 가능 값:
   - FULL_TIME: "정규직"
   - CONTRACT: "계약직"
   - INTERN: "인턴"

3. education_type 가능 값:
   - NO_PREFERENCE: "학력 무관"
   - LOW_SCHOOL_DEGREE: "초졸 이하"
   - MIDDLE_SCHOOL_DEGREE: "중졸"
   - HIGH_SCHOOL_DEGREE: "고졸"
   - ASSOCIATE_DEGREE: "전문학사"
   - BACHELOR_DEGREE: "학사"
   - MASTER_DEGREE: "석사"
   - DOCTORAL_DEGREE: "박사"
'''

system_prompt = '''
### Instruction
채용 공고 텍스트에서 핵심 정보를 추출하여 지정된 JSON 형식으로 변환하시오.

### Rules
1. 모든 출력은 반드시 JSON 형식이어야 함
2. 데이터 타입 규칙:
   - null 값은 "None"이 아닌 null로 표기
   - 숫자는 문자열이 아닌 숫자형으로 표기
   - 문자열은 큰따옴표(") 사용
3. 경력 연수 처리:
   - "1~5년" → career_start: 1, career_end: 5
   - "1년 이상" → career_start: 1, career_end: null
   - 명시되지 않은 경우 → null
4. welfare는 각각 독립된 객체로 분리하여 배열에 추가

### Example
Input: 
"신입/경력 채용, 4년제 대졸 이상, 정규직, 주5일 근무, 식대지원, 4대보험"

Output:
{
    "welfare": [
        {
            "name": "식대지원",
            "description": "식대 지원"
        },
        {
            "name": "4대보험",
            "description": "4대보험 가입"
        }
    ],
    "career_start": null,
    "career_end": null,
    "career_type": "ENTRY_EXPERIENCED",
    "work_type": "FULL_TIME",
    "education_type": "BACHELOR_DEGREE",
    "workday_content": "주5일 근무"
}
'''

def generate_wanted_prompts(sample_data, all_text):
    messages = [
        {
            "role": "system",
            "content": f"""
### Task Definition
{default_prompt}

### Instructions
{system_prompt}

### Reference Example
{sample_data}
"""
        },
        {
            "role": "user",
            "content": f"""
### Input
{all_text}

### Task
위 채용공고 내용을 JSON 형식으로 변환하시오.
"""
        }
    ]
    return messages



async def chatgpt_response(prompt):
    response = await openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=prompt,
        seed=123,
        temperature=0.001,
    )

    # print(response)  # response 객체를 출력하여 구조를 확인합니다
    result = response.choices[0].message.content   # 올바르게 데이터에 접근합니다
    return result  # 성공적인 응답 반환


def create_wanted_sample_data():
    sample_data = {
        "welfare": [
            {
                "name": None,
                "description": None
            }
        ],
        "career_start": 0,  # 경력 시작값
        "career_end": 0,  # 경력 종료값 (최소값만 주어진 경우 None으로 설정)
        "career_type": None,
        "work_type": None,
        "education_type": None,
        "workday_content": None,
    }

    return sample_data


async def process_string_to_json(content):
    start_index = content.find('{')
    print('start_index:', start_index)
    end_index = content.rfind('}') + 1
    print('end_index:', end_index)
    
    if start_index != -1 and end_index != -1:
        json_content = content[start_index:end_index]
        final_data = await decode_custom_json(json_content)
        return final_data
    else:
        print("유효한 JSON 객체를 찾을 수 없습니다.")
        return None


async def decode_custom_json(data):
    try:
        # 먼저 원본 데이터를 사용하여 JSON 디코딩 시도
        return json.loads(data)
    except json.JSONDecodeError:
        # JSON 표준에 맞게 작은따옴표를 큰따옴표로 변환
        # 문자열 내의 작은따옴표는 그대로 둠
        data = re.sub(r"(?<=\{|\,)\s*'(.*?)'\s*:", r'"\1":', data)
        data = re.sub(r":\s*'(.*?)'\s*(?=\,|\})", r': "\1"', data)

        
        data = data.replace("None", "null")
        
        # 큰따옴표로 감싸진 값 중, 내부에 작은따옴표가 있을 때 적절히 이스케이프 처리
        data = re.sub(r'"\s*:\s*"(.*?)(?<!\\)"\s*(?=\,|\})', lambda m: '": "{}"'.format(m.group(1).replace('"', r'\"')), data)

        # 변환된 데이터 출력 (디버깅 용도)
        print(f"JSON 디코딩을 위한 변환된 데이터:\n{data}")

        
        # JSON 디코딩 시도
        decoded_data = json.loads(data)
        
        # 이스케이프된 작은따옴표를 원래 상태로 복원
        decoded_data = json.loads(json.dumps(decoded_data).replace('\\"', "'"))

        return decoded_data


async def process_recruits(content, platform):
    """
    content : 아래 key들로 구성된 딕셔너리
        "requirements"
        "main_tasks"
        "intro"
        "benefits"
        "preferred_points"

    platform : wanted, jobstreet
    """
    try:
        if platform == "wanted":
            ## 비어있는 틀만 만든다.
            ## welfatre(복지), career_start(경력 시작값), career_end(경력 종료값)
            ## career_type, work_type, education_type, workday_content
            recruit_sample_data = create_wanted_sample_data()

            ## 프롬프트에 row data와 비어 있는 틀을 입력하여 프롬프트를 구성함.
            recruit_prompt = generate_wanted_prompts(recruit_sample_data, content)
            print("\nSample Data")
            print("=" * 50)
            print(recruit_sample_data)

            print("\nPrompt")
            print("=" * 50)
            for message in recruit_prompt:
                print(message['content'])
        
        else:
            raise ValueError("Invalid platform specified")            

        ## 프롬프트를 GPT에 전달해서 데이터를 정해진 포맷에 맞게 정제함.
        recruit_response = await chatgpt_response(recruit_prompt)
        recruit_json_data = await process_string_to_json(recruit_response)

        return recruit_json_data   

    except Exception as e:
        print(1)
        raise


def create_categories_list(category_tags):

    categories = []
    for tag in category_tags:
        parent_id = tag.get("parent_id")
        if parent_id is not None:
            categories.append({"id": str(parent_id), "text": None})

        tag_id = tag.get("id")
        if tag_id is not None:
            categories.append({"id": str(tag_id), "text": None})

    return categories


def extract_nested_value(data: dict, path: str, default=None):
    try:
        value = data
        for key in path.split('.'):
            value = value[key]
        return value
    except (KeyError, TypeError):
        return default
    

def create_company_data(data: dict, process_data: dict) -> dict:
    company_fields = {
        'id': ('job.company.id', str),
        'name': ('job.company.name', str),
        'industry': ('job.company.industry_name', str),
        'description': ('job.detail.intro', str),
        'tags': ('job.company_tags', lambda x: [tag["title"] for tag in x] if x else []),
        'address': ('job.address.full_location', str),
        'location': ('job.address.location', str),
        'categories': ('job.category_tags', create_categories_list),
        'logoImage': ('job.title_img.origin', str),
    }
    
    company = {
        field: converter(extract_nested_value(data, path))
        for field, (path, converter) in company_fields.items()
    }
    
    # Add static fields
    company.update({
        'welfare': process_data.get('welfare', []),
        'sectors': None,
        'bizNo': None,
        'ceo': None,
        'averageAnnualSalary': 0,
        'homepage': None
    })
    
    return company


def create_job_data(data: dict, process_data: dict, reg_at: str, close_date: str) -> dict:
    job_fields = {
        'id': ('job.id', str),
        'location': ('job.address.location', str),
        'address': ('job.address.full_location', str),
        'title': ('job.position', str),
        'description': ('job.detail.intro', str),
        'tasks': ('job.detail.main_tasks', str),
        'requirements': ('job.detail.requirements', str),
        'points': ('job.detail.preferred_points', str),
        'infoUrl': ('share_link', str),
        'tags': ('job.company_tags', lambda x: [tag["title"] for tag in x] if x else [])
    }
    
    job = {
        field: converter(extract_nested_value(data, path))
        for field, (path, converter) in job_fields.items()
    }
    
    # Add process data fields
    job.update({
        'activeFlag': True,
        'salaryType': None,
        'minSalary': None,
        'maxSalary': None,
        'regAt': reg_at,
        'closeDate': close_date,
        'careerType': process_data.get('career_type'),
        'careerMin': process_data.get('career_start'),
        'careerMax': process_data.get('career_end'),
        'workType': process_data.get('work_type'),
        'workDescription': extract_nested_value(data, 'job.detail.main_tasks'),
        'educationType': process_data.get('education_type'),
        'workdayContent': process_data.get('workday_content') or "주5일 근무",  # None이면 기본값 설정
        'welfare': process_data.get('welfare', [])
    })
    
    # Ensure infoUrl is properly set
    job['infoUrl'] = None if job['infoUrl'] == "None" else job['infoUrl']
    
    return job



async def transform_wanted_data(data: dict) -> dict:
    job_detail = extract_nested_value(data, 'job.detail', {})
    details = {
        "requirements": job_detail.get("requirements"),
        "main_tasks": job_detail.get("main_tasks"),
        "intro": job_detail.get("intro"),
        "benefits": job_detail.get("benefits"),
        "preferred_points": job_detail.get("preferred_points")
    }

    # Process recruitment data through AI
    process_data = await process_recruits(details, 'wanted')
    
    # Calculate dates
    korea_tz = pytz.timezone('Asia/Seoul')
    reg_at = datetime.datetime.now(korea_tz).strftime('%Y-%m-%dT%H:%M:%S')
    close_date = (datetime.datetime.now(korea_tz) + datetime.timedelta(days=90)).strftime('%Y-%m-%dT%H:%M:%S')
    
    # Create company and job data
    company_data = create_company_data(data, process_data)
    job_data = create_job_data(data, process_data, reg_at, close_date)
    
    # Validate required fields
    required_fields = [
        company_data['id'], 
        company_data['name'], 
        company_data['location'],
        company_data['categories'],
        job_data['id'],
        job_data['location']
    ]
    
    if not all(required_fields):
        print("Missing required fields. Skipping this record.")
        return None
        
    # Construct final format
    return {
        "recruits": [{
            "company": company_data,
            "job": job_data
        }]
    }


async def wanted_recruit_ai_process():
    latest_data_files = sorted(glob("/home/jake/workspace/customize/Airflow/src/projects/wanted_recruit/modules/data/wanted_recruit_data-*.json"))  # 모든 관련 파일 검색
    if not latest_data_files:
        print("No data found for the specified date.")
        return

    latest_data_file = latest_data_files[-1]  # 가장 최신 파일 선택
    print(f"Processing file: {latest_data_file}")

    # JSON 파일 로드
    with open(latest_data_file, 'r', encoding='utf-8') as f:
        latest_data = json.load(f)  # 파일 내용 로드
        
    if latest_data:
        for data in latest_data:
            result = await transform_wanted_data(data)
            print("=" *50)
            print(result)
            break


def run_async_wanted_process():
    asyncio.run(wanted_recruit_ai_process())


if __name__ == "__main__":
    asyncio.run(wanted_recruit_ai_process())