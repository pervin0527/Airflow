mkdir -p src
mkdir -p logs
mkdir -p dags

## 도커 이미지 빌드
docker build -t airflow_custom:latest .

## 이미지를 기반으로 컨테이너를 실행
docker run -d --name airflow_container \
  -p 8080:8080 \
  -v $(pwd)/dags:/opt/airflow/dags \
  -v $(pwd)/logs:/opt/airflow/logs \
  -v $(pwd)/src:/opt/airflow/src \
  -e AIRFLOW__CORE__EXECUTOR=SequentialExecutor \
  -e AIRFLOW__DATABASE__SQL_ALCHEMY_CONN=sqlite:////opt/airflow/airflow.db \
  airflow_custom:latest bash -c "airflow db init && airflow webserver"

## airflow 사용자 계정 생성
docker exec -it airflow_container airflow users create \
  --username admin \
  --firstname Admin \
  --lastname User \
  --role Admin \
  --email admin@example.com
