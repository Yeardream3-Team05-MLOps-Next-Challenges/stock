# Dockerfile

# 파이썬 공식 이미지를 베이스 이미지로 사용
FROM python:3.10

# 작업 디렉토리 설정
WORKDIR /app

# 현재 디렉토리의 파일을 컨테이너의 /app으로 복사
COPY . /app

# 필요한 파이썬 패키지 설치
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

ENV APP_KEY=api_key
ENV APP_SECRET=fluentd_url
ENV HTS_ID=INFO
ENV SERVER_HOST=host

# Prefect 에이전트 실행
CMD ["prefect", "agent", "start", "--work-queue", "docker-agent"]
