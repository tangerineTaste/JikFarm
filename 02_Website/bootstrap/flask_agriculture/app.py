from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory, jsonify, session
from dotenv import load_dotenv
import os
from db_connection import get_connection
from member import Member
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta

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

                if user and check_password_hash(user['password'], password):# type: ignore
                    session['member_id'] = user['member_id'] # type: ignore
                    session['login_id'] = user['login_id']# type: ignore
                    session['nickname'] = user['nickname']# type: ignore
                    session['name'] = user['name']# type: ignore
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

                # 새로 생성된 member_id 가져오기
                member_id = cursor.lastrowid

                # 주소 정보 가져오기
                postcode = request.form['postcode']
                road_full_addr = request.form['roadAddress']
                addr_detail = request.form['detailAddress']
                si_nm = request.form['siNm']
                sgg_nm = request.form['sggNm']

                # member_addresses 테이블에 주소 정보 삽입
                if member_id:
                    address_sql = "INSERT INTO member_addresses (member_id, road_full_addr, zip_no, addr_detail, si_nm, sgg_nm, created_at) VALUES (%s, %s, %s, %s, %s, %s, NOW())"
                    cursor.execute(address_sql, (member_id, road_full_addr, postcode, addr_detail, si_nm, sgg_nm))
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
        weeks = [row['weekno'] for row in cursor.fetchall()] # type: ignore
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

def to_date_str(row, key):
    if row.get(key) and not isinstance(row[key], str):
        row[key] = row[key].strftime('%Y-%m-%d')

@app.route('/api/daily_trade', methods=['GET'])
def get_daily_trade():
    item_code = request.args.get('item_code')
    crop_full_code = request.args.get('crop_full_code')
    grade = request.args.get('grade')
    sanji_code = request.args.get('sanji_cd')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    if not item_code:
        return jsonify({'error': 'item_code is required'}), 400

    # WHERE
    where_clause = "ft.item_code = %s"
    params = [item_code]

    if crop_full_code:
        where_clause += " AND ft.crop_full_code = %s"
        params.append(crop_full_code)
    if grade:
        where_clause += " AND ft.grade_label = %s"
        params.append(grade)
    if sanji_code:
        where_clause += " AND ft.j_sanji_cd = %s"
        params.append(sanji_code)
    if start_date:
        where_clause += " AND ft.trd_clcln_ymd >= %s"
        params.append(start_date)
    if end_date:
        where_clause += " AND ft.trd_clcln_ymd <= %s"
        params.append(end_date)

    # SELECT & GROUP BY
    group_by = ['ft.trd_clcln_ymd', 'ft.item_code']
    select_parts = [
        'ft.trd_clcln_ymd',
        'ft.item_code AS item_code'
    ]

    if crop_full_code:
        join_crop = "JOIN master_crop_variety mcv ON ft.crop_full_code = mcv.crop_full_code"
        group_by.append('ft.crop_full_code')
        group_by.append('mcv.gds_sclsf_nm')
        select_parts.append('ft.crop_full_code')
        select_parts.append('MAX(mcv.gds_mclsf_nm) AS gds_mclsf_nm')
        select_parts.append('mcv.gds_sclsf_nm')
    else:
        join_crop = "JOIN vw_crop_item_name mcv ON ft.item_code = mcv.item_code"
        group_by.append('mcv.gds_mclsf_nm')
        select_parts.append('mcv.gds_mclsf_nm')
        select_parts.append("'' AS gds_sclsf_nm")

    if grade:
        group_by.append('ft.grade_label')
        select_parts.append('ft.grade_label AS grd_nm')

    if sanji_code:
        group_by.append('ft.j_sanji_cd')
        select_parts.append('ft.j_sanji_cd')
        select_parts.append('MAX(mrs.j_sanji_nm) AS j_sanji_nm')

    # 집계 컬럼 (뷰와 동일 로직)
    select_parts.append('ROUND(SUM(ft.unit_tot_qty), 0) AS unit_tot_qty')
    select_parts.append('ROUND(SUM(ft.totprc) / NULLIF(SUM(ft.unit_tot_qty),0), 0) AS avg_price')

    select_sql = ',\n    '.join(select_parts)
    group_by_sql = ', '.join(group_by)

    query = f"""
        SELECT
            {select_sql}
        FROM fact_trade ft
        {join_crop}
        LEFT JOIN (
            SELECT DISTINCT j_sanji_cd, j_sanji_nm
            FROM map_region_weather_station
        ) mrs ON ft.j_sanji_cd = mrs.j_sanji_cd
        WHERE {where_clause}
        GROUP BY {group_by_sql}
        ORDER BY ft.trd_clcln_ymd
    """

    # 실행 및 반환
    conn = get_connection()
    with conn.cursor() as cursor:
        cursor.execute(query, params)
        rows = cursor.fetchall()
    conn.close()

    # 날짜컬럼 yyyy-MM-dd 변환
    for row in rows:
        to_date_str(row, 'trd_clcln_ymd')

    return jsonify(rows)

@app.route('/api/latest_dates', methods=['GET'])
def get_latest_dates():
    conn = get_connection()
    query = "SELECT MAX(trd_clcln_ymd) as max_date FROM fact_trade"
    with conn.cursor() as cursor:
        cursor.execute(query)
        result = cursor.fetchone()
    conn.close()

    if not result or not result['max_date']: # type: ignore
        end_dt = datetime.now()
    else:
        end_dt = result['max_date'] # type: ignore

    start_dt = end_dt - timedelta(days=30)

    return jsonify({
        'start_date': start_dt.strftime('%Y-%m-%d'),
        'end_date': end_dt.strftime('%Y-%m-%d')
    })

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

@app.route('/api/grades', methods=['GET'])
def get_grades():
    item_code = request.args.get('item_code')
    crop_full_code = request.args.get('crop_full_code')
    start_week = request.args.get('start_week')
    end_week = request.args.get('end_week')

    if not item_code or not start_week or not end_week:
        return jsonify({'error': 'item_code, start_week, and end_week are required'}), 400

    is_daily = len(start_week) == 8 and len(end_week) == 8
    table = 'fact_trade' if is_daily else 'fact_trade_weekly'
    date_col = 'trd_clcln_ymd' if is_daily else 'weekno'

    where = [f"item_code = %s", f"{date_col} >= %s", f"{date_col} <= %s"]
    params = [item_code, start_week, end_week]

    if crop_full_code:
        where.append("crop_full_code = %s")
        params.append(crop_full_code)

    where_clause = " AND ".join(where)

    query = f"""
        SELECT DISTINCT grade_label
        FROM {table}
        WHERE {where_clause} AND grade_label IS NOT NULL
        ORDER BY grade_label
    """

    conn = get_connection()
    with conn.cursor() as cursor:
        cursor.execute(query, tuple(params))
        rows = [row['grade_label'] for row in cursor.fetchall()] # type: ignore
    conn.close()
    return jsonify(rows)


@app.route('/api/sanjis', methods=['GET'])
def get_sanjis():
    item_code = request.args.get('item_code')
    crop_full_code = request.args.get('crop_full_code')
    grade = request.args.get('grade')
    start_week = request.args.get('start_week')
    end_week = request.args.get('end_week')

    if not item_code or not start_week or not end_week:
        return jsonify({'error': 'item_code, start_week, end_week are required'}), 400

    is_daily = (len(start_week) == 8 and len(end_week) == 8)
    if is_daily:
        table = 'fact_trade'
        date_col = 'trd_clcln_ymd'
        grade_col = 'grade_label'
    else:
        table = 'fact_trade_weekly'
        date_col = 'weekno'
        grade_col = 'grade_label'

    where = [f"item_code = %s", f"{date_col} >= %s", f"{date_col} <= %s"]
    params = [item_code, start_week, end_week]

    if crop_full_code:
        where.append("crop_full_code = %s")
        params.append(crop_full_code)
    if grade:
        where.append(f"{grade_col} = %s")
        params.append(grade)
    where_clause = " AND ".join(where)

    query = f"""
        SELECT t.j_sanji_cd, s.j_sanji_nm
        FROM (
            SELECT DISTINCT j_sanji_cd
            FROM {table}
            WHERE {where_clause}
                AND j_sanji_cd IS NOT NULL
        ) t
        INNER JOIN vw_map_region_sanji s
            ON s.j_sanji_cd = t.j_sanji_cd
        ORDER BY t.j_sanji_cd
    """

    conn = get_connection()
    with conn.cursor() as cursor:
        cursor.execute(query, tuple(params))
        rows = cursor.fetchall()
    conn.close()
    return jsonify(rows)

@app.route('/api/ai_historical_data', methods=['GET'])
def get_ai_historical_data():
    item_code = request.args.get('item_code')
    start_date_str = request.args.get('start_date')
    end_date_str = request.args.get('end_date')

    print(item_code,start_date_str, end_date_str)
    
    if not item_code or not start_date_str or not end_date_str:
        return jsonify({'error': 'item_code, start_date, and end_date are required'}), 400

    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            query = """
                SELECT
                    trd_clcln_ymd,
                    ROUND(SUM(totprc) / NULLIF(SUM(unit_tot_qty), 0), 0) AS avg_price,
                    ROUND(SUM(unit_tot_qty), 0) AS unit_tot_qty
                FROM fact_trade
                WHERE item_code = %s
                  AND trd_clcln_ymd BETWEEN %s AND %s
                GROUP BY trd_clcln_ymd
                ORDER BY trd_clcln_ymd
            """
            cursor.execute(query, (item_code, start_date_str, end_date_str))
            rows = cursor.fetchall()
            
            # 날짜컬럼 yyyy-MM-dd 변환
            for row in rows:
                to_date_str(row, 'trd_clcln_ymd')

            return jsonify(rows)
    finally:
        conn.close()

@app.route('/api/interest_crops', methods=['GET'])
def get_interest_crops():
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            query = "SELECT crop_id, display_name FROM interest_whitelist WHERE is_active = TRUE ORDER BY sort_order"
            cursor.execute(query)
            crops = cursor.fetchall()
            return jsonify(crops)
    finally:
        conn.close()

@app.route('/api/member_interest_crops', methods=['GET'])
def get_member_interest_crops():
    if 'member_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    member_id = session['member_id']
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            query = "SELECT crop_id FROM member_crops WHERE member_id = %s"
            cursor.execute(query, (member_id,))
            member_crops = [row['crop_id'] for row in cursor.fetchall()] # type: ignore
            return jsonify(member_crops)
    finally:
        conn.close()

@app.route('/api/save_member_interest_crops', methods=['POST'])
def save_member_interest_crops():
    if 'member_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    member_id = session['member_id']
    selected_crop_ids = request.json.get('crop_ids', []) # type: ignore

    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            # 기존 관심 품목 삭제
            delete_sql = "DELETE FROM member_crops WHERE member_id = %s"
            cursor.execute(delete_sql, (member_id,))

            # 새로운 관심 품목 삽입
            if selected_crop_ids:
                insert_sql = "INSERT INTO member_crops (member_id, crop_id) VALUES (%s, %s)"
                for crop_id in selected_crop_ids:
                    cursor.execute(insert_sql, (member_id, crop_id))
            conn.commit()
            return jsonify({'message': 'Interest crops saved successfully'}), 200
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

@app.route('/api/update_profile', methods=['POST'])
def update_profile():
    if 'member_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    member_id = session['member_id']
    data = request.get_json()
    nickname = data.get('nickname')
    name = data.get('name')

    if not nickname or not name:
        return jsonify({'error': '닉네임과 이름은 필수입니다.'}), 400

    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            # 닉네임 중복 확인 (자기 자신 제외)
            sql = "SELECT member_id FROM members WHERE nickname = %s AND member_id != %s"
            cursor.execute(sql, (nickname, member_id))
            if cursor.fetchone():
                return jsonify({'error': '이미 사용 중인 닉네임입니다.'}), 400

            # 정보 업데이트
            sql = "UPDATE members SET nickname = %s, name = %s, updated_at = NOW() WHERE member_id = %s"
            cursor.execute(sql, (nickname, name, member_id))
            conn.commit()

            # 세션 정보 업데이트
            session['nickname'] = nickname
            session['name'] = name

            return jsonify({'message': 'Profile updated successfully', 'nickname': nickname, 'name': name}), 200
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

if __name__ == '__main__':
    app.run(debug=True)

