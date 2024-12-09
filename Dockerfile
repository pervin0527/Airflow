FROM apache/airflow:2.9.0

# root 권한으로 전환
USER root

# 패키지 업데이트 및 필요한 패키지 설치
ENV ACCEPT_EULA=Y

RUN apt-get update -q && \
    apt-get upgrade -y -q && \
    apt-get install -y -q \
    build-essential \
    wget \
    unzip \
    curl \
    gnupg2 \
    ca-certificates \
    libglib2.0-0 \
    libnss3 \
    libgconf-2-4 \
    libfontconfig1 \
    libxi6 \
    libxcursor1 \
    libxss1 \
    libxcomposite1 \
    libasound2 \
    libxdamage1 \
    libxtst6 \
    libatk1.0-0 \
    libgtk-3-0 \
    libdrm2 \
    libgbm1 \
    fonts-liberation \
    libu2f-udev \
    libvulkan1 \
    xdg-utils \
    tini \
    --no-install-recommends && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Google Chrome 설치 (127.0.6533.88 버전)
RUN wget -q https://dl.google.com/linux/chrome/deb/pool/main/g/google-chrome-stable/google-chrome-stable_127.0.6533.88-1_amd64.deb && \
    apt-get update && \
    apt-get install -y ./google-chrome-stable_127.0.6533.88-1_amd64.deb && \
    rm google-chrome-stable_127.0.6533.88-1_amd64.deb && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# 설치된 Chrome 버전 확인
RUN google-chrome --version

# ChromeDriver 설치 (크롬 버전과 일치)
RUN wget -O /tmp/chromedriver.zip https://storage.googleapis.com/chrome-for-testing-public/127.0.6533.88/linux64/chromedriver-linux64.zip && \
    unzip /tmp/chromedriver.zip -d /usr/local/bin/ && \
    chmod +x /usr/local/bin/chromedriver-linux64/chromedriver && \
    rm /tmp/chromedriver.zip

# 설치된 ChromeDriver 버전 확인
RUN /usr/local/bin/chromedriver-linux64/chromedriver --version

# Python 패키지 설치를 위한 requirements.txt 복사
COPY requirements.txt /requirements.txt

# airflow 사용자로 전환 후 Python 패키지 설치
USER airflow
RUN pip install --no-cache-dir -r /requirements.txt

# root 사용자로 다시 전환
USER root

# 환경 변수 설정
ENV AIRFLOW_HOME=/opt/airflow

# 소스 코드와 DAG 파일 복사 및 권한 설정
COPY dags/ $AIRFLOW_HOME/dags/
COPY src/ $AIRFLOW_HOME/src/
RUN mkdir -p $AIRFLOW_HOME/logs
COPY logs/ $AIRFLOW_HOME/logs/
RUN chown -R airflow: $AIRFLOW_HOME/dags $AIRFLOW_HOME/src $AIRFLOW_HOME/logs
RUN chmod -R 777 $AIRFLOW_HOME/logs

# 엔트리포인트 스크립트 권한 설정
RUN chmod +x /entrypoint

# 기본 엔트리포인트 설정
ENTRYPOINT ["/usr/bin/tini", "--", "/entrypoint"]

# airflow 사용자로 전환하여 컨테이너 실행
USER airflow