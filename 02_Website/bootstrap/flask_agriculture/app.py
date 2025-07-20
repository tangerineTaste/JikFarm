from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory, jsonify, session
from dotenv import load_dotenv
import os
from db_connection import get_connection
from member import Member
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

# .env 파일 로드
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'your_secret_key')

# 데이터베이스 연결 테스트 라우트
@app.route('/test_db')
def test_db():
    try:
        conn = get_connection()
        conn.close()
        return "Database connection successful!"
    except Exception as e:
        return f"Database connection failed: {e}"

# Handle static file requests from HTML
@app.route('/assets/<path:filename>')
def serve_assets(filename):
    return send_from_directory('static', filename)

@app.route('/static/assets/<path:filename>')
def serve_static_assets(filename):
    return send_from_directory('static', filename)

# Page routes
@app.route('/')
@app.route('/index.html')
def home():
    return render_template('index.html')

@app.route('/about')
@app.route('/about.html')
def about():
    return render_template('about.html')

@app.route('/chart')
@app.route('/chart.html')
def chart():
    return render_template('chart.html')

@app.route('/roadmap')
@app.route('/roadmap.html')
def roadmap():
    return render_template('roadmap.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = get_connection()
        try:
            with conn.cursor() as cursor:
                sql = "SELECT * FROM members WHERE login_id=%s"
                cursor.execute(sql, (username,))
                user = cursor.fetchone()
                print('원래비번 :', user.get('password'))
                print('입력비번 :', password)
                print('맞나 :', user.get('password') == password)


                if user and check_password_hash(user['password'], password):
                    session['member_id'] = user['member_id']
                    session['login_id'] = user['login_id']
                    session['nickname'] = user['nickname']
                    session['name'] = user['name']
                    flash('로그인에 성공했습니다.', 'success')
                    return redirect(url_for('home'))
                else:
                    flash('아이디 또는 비밀번호가 일치하지 않습니다.', 'danger')
        finally:
            conn.close()
            
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        password_confirm = request.form['password-confirm']
        address = f"{request.form['roadAddress']} {request.form['detailAddress']}"

        if password != password_confirm:
            flash('비밀번호가 일치하지 않습니다.', 'danger')
            return redirect(url_for('signup'))

        conn = get_connection()
        try:
            with conn.cursor() as cursor:
                # 아이디 중복 확인
                sql = "SELECT * FROM members WHERE login_id=%s"
                cursor.execute(sql, (username,))
                if cursor.fetchone():
                    flash('이미 사용 중인 아이디입니다.', 'danger')
                    return redirect(url_for('signup'))

                # 닉네임 중복 확인
                nickname = request.form['nickname']
                sql = "SELECT * FROM members WHERE nickname=%s"
                cursor.execute(sql, (nickname,))
                if cursor.fetchone():
                    flash('이미 사용 중인 닉네임입니다.', 'danger')
                    return redirect(url_for('signup'))

                # 비밀번호 해싱 및 사용자 추가
                hashed_password = generate_password_hash(password)
                sql = "INSERT INTO members (login_id, nickname, name, password, is_admin, created_at, updated_at) VALUES (%s, %s, %s, %s, %s, NOW(), NOW())"
                cursor.execute(sql, (username, nickname, request.form['name'], hashed_password, False))
                conn.commit()
                flash('회원가입이 완료되었습니다. 로그인해주세요.', 'success')
                return redirect(url_for('login'))
        finally:
            conn.close()

    return render_template('signup.html')

@app.route('/find_password')
@app.route('/find_password.html')
def find_password():
    return render_template('findPassword.html')

@app.route('/mypage')
def mypage():
    if 'member_id' not in session:
        flash('로그인이 필요합니다.', 'danger')
        return redirect(url_for('login'))
    
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            sql = "SELECT * FROM members WHERE member_id=%s"
            cursor.execute(sql, (session['member_id'],))
            member_info = cursor.fetchone()
            return render_template('mypage.html', member=member_info)
    finally:
        conn.close()

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    flash('로그아웃되었습니다.', 'success')
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)