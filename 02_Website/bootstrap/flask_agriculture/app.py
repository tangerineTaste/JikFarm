from flask import Flask
from dotenv import load_dotenv
import os
from auth import auth_bp
from api import api_bp
from views import views_bp


# .env 파일 로드
load_dotenv()

app = Flask(__name__)


app.register_blueprint(auth_bp)
app.register_blueprint(api_bp, url_prefix='/api')
app.register_blueprint(views_bp)

if __name__ == '__main__':
    app.run(debug=True)