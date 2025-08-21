import os
import pymysql
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# DB 정보
user = os.getenv("DB_USER", "root")  # .env 파일에 DB_USER 설정해도 됨
host = os.getenv("DB_HOST", "localhost")
password = os.getenv("DB_PW", '')  # DB_pw → 대소문자 주의 (env 키명)
port = int(os.getenv("DB_PORT", 3306))
db = os.getenv("DB_NAME", "jikfarm_db")

def get_connection():
    return pymysql.connect(
        host=host,
        user=user,
        password=password,
        database=db,
        port=port,
        cursorclass=pymysql.cursors.DictCursor # type: ignore
    ) 