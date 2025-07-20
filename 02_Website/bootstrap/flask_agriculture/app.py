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
    session.pop('member_id', None)
    session.pop('login_id', None)
    session.pop('nickname', None)
    session.pop('name', None)
    flash('로그아웃되었습니다.', 'success')
    return redirect(url_for('home'))


@app.route('/api/latest_weeks', methods=['GET'])
def get_latest_weeks():
    conn = get_connection()
    query = """
        SELECT DISTINCT weekno FROM fact_trade_weekly
        ORDER BY weekno DESC LIMIT 14
    """
    with conn.cursor() as cursor:
        cursor.execute(query)
        weeks = [row['weekno'] for row in cursor.fetchall()]
    conn.close()

    if not weeks:
        return jsonify({'start_week': '', 'end_week': ''})

    return jsonify({'start_week': weeks[-1], 'end_week': weeks[0]})


@app.route('/api/weekly_trade', methods=['GET'])
def get_weekly_trade():
    item_code = request.args.get('item_code')
    crop_full_code = request.args.get('crop_full_code')
    grade = request.args.get('grade')
    sanji_code = request.args.get('sanji_cd')
    start_week = request.args.get('start_week')
    end_week = request.args.get('end_week')

    if not item_code:
        return jsonify({'error': 'item_code is required'}), 400

    # WHERE
    where_clause = "LEFT(wt.crop_full_code, 4) = %s"
    params = [item_code]
    if crop_full_code:
        where_clause += " AND wt.crop_full_code = %s"
        params.append(crop_full_code)
    if grade:
        where_clause += " AND wt.grade_label = %s"
        params.append(grade)
    if sanji_code:
        where_clause += " AND wt.j_sanji_cd = %s"
        params.append(sanji_code)
    if start_week:
        where_clause += " AND wt.weekno >= %s"
        params.append(start_week)
    if end_week:
        where_clause += " AND wt.weekno <= %s"
        params.append(end_week)

    # SELECT & GROUP BY
    group_by = ['wt.weekno', 'LEFT(wt.crop_full_code, 4)']
    select_parts = [
        'wt.weekno',
        'LEFT(wt.crop_full_code, 4) AS item_code',
        'MAX(mcv.gds_mclsf_nm) AS gds_mclsf_nm'
    ]



    # crop_full_code(품종) 선택 시만 추가
    if crop_full_code:
        group_by.append('wt.crop_full_code')
        group_by.append('mcv.gds_sclsf_nm')
        select_parts.append('wt.crop_full_code')
        select_parts.append('mcv.gds_sclsf_nm')
    else:
        select_parts.append("'' AS gds_sclsf_nm")

    # grade 선택시만 추가
    if grade:
        group_by.append('wt.grade_label')
        select_parts.append('wt.grade_label AS grd_cd')
        select_parts.append('wt.grade_label AS grd_nm')

    # sanji 선택시만 추가
    if sanji_code:
        group_by.append('wt.j_sanji_cd')
        select_parts.append('wt.j_sanji_cd')
        select_parts.append('MAX(mrs.j_sanji_nm) AS j_sanji_nm')

    # 집계 컬럼
    select_parts.append('ROUND(SUM(wt.unit_tot_qty), 0) AS unit_tot_qty')
    select_parts.append('ROUND(AVG(wt.avg_prc), 0) AS avg_price')

    select_sql = ',\n    '.join(select_parts)
    group_by_sql = ', '.join(group_by)

    query = f"""
        SELECT
            {select_sql}
        FROM fact_trade_weekly wt
        JOIN master_crop_variety mcv ON wt.crop_full_code = mcv.crop_full_code
        LEFT JOIN (
            SELECT DISTINCT j_sanji_cd, j_sanji_nm
            FROM map_region_weather_station
        ) mrs ON wt.j_sanji_cd = mrs.j_sanji_cd
        WHERE {where_clause}
        GROUP BY {group_by_sql}
        ORDER BY wt.weekno
    """

    # 실행 및 반환
    conn = get_connection()
    with conn.cursor() as cursor:
        cursor.execute(query, params)
        rows = cursor.fetchall()
    conn.close()
    print('--------------------')
    print('실행 쿼리:')
    print(query)
    print('파라미터:', params)
    print('--------------------')
    return jsonify(rows)


@app.route('/api/items', methods=['GET'])
def get_items():
    conn = get_connection()
    query = """
        SELECT DISTINCT item_code, gds_mclsf_nm
        FROM master_crop_variety
        ORDER BY item_code
    """
    with conn.cursor() as cursor:
        cursor.execute(query)
        rows = cursor.fetchall()
    conn.close()
    return jsonify(rows)

@app.route('/api/varieties', methods=['GET'])
def get_varieties():
    item_code = request.args.get('item_code')
    if not item_code:
        return jsonify({'error': 'item_code is required'}), 400

    conn = get_connection()
    query = """
        SELECT crop_full_code, gds_sclsf_nm
        FROM master_crop_variety
        WHERE item_code = %s
        ORDER BY crop_full_code
    """
    with conn.cursor() as cursor:
        cursor.execute(query, (item_code,))
        rows = cursor.fetchall()
    conn.close()
    return jsonify(rows)


@app.route('/api/sanjis', methods=['GET'])
def get_sanjis():
    conn = get_connection()
    query = """
        SELECT DISTINCT j_sanji_cd, j_sanji_nm
        FROM map_region_weather_station
        ORDER BY j_sanji_cd
    """
    with conn.cursor() as cursor:
        cursor.execute(query)
        rows = cursor.fetchall()
    conn.close()
    return jsonify(rows)

if __name__ == '__main__':
    app.run(debug=True)
