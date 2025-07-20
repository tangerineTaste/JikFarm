import os
import pymysql
import time
from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# DB 정보
user = os.getenv("DB_USER")  # .env 파일에 DB_USER 설정해도 됨
host = os.getenv("DB_HOST")
password = os.getenv("DB_PW")  # DB_pw → 대소문자 주의 (env 키명)
port = int(os.getenv("DB_PORT"))
db = os.getenv("DB_NAME")


def get_connection():
    return pymysql.connect(
        host=host,
        user=user,
        password=password,
        database=db,
        port=port,
        cursorclass=pymysql.cursors.DictCursor
    )

# 홈페이지
@app.route('/')
def test_page():
    return render_template('trade_unified.html')

# 최신 주차(데이터상) 조회
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

# 주간 거래 데이터 조회(그래프용)
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
    where_clause = "wt.item_code = %s"
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

    # 기본 SELECT & GROUP BY 구성
    group_by = ['wt.weekno', 'wt.item_code']
    select_parts = [
        'wt.weekno',
        'wt.item_code AS item_code'
    ]

    # Join 대상 구분
    if crop_full_code:
        join_crop = "JOIN master_crop_variety mcv ON wt.crop_full_code = mcv.crop_full_code"
        group_by.append('wt.crop_full_code')
        group_by.append('mcv.gds_sclsf_nm')
        select_parts.append('wt.crop_full_code')
        select_parts.append('MAX(mcv.gds_mclsf_nm) AS gds_mclsf_nm')
        select_parts.append('mcv.gds_sclsf_nm')
    else:
        join_crop = "JOIN vw_crop_item_name mcv ON wt.item_code = mcv.item_code"
        group_by.append('mcv.gds_mclsf_nm')
        select_parts.append('mcv.gds_mclsf_nm')
        select_parts.append("'' AS gds_sclsf_nm")

    # 등급 선택 시
    if grade:
        group_by.append('wt.grade_label')
        select_parts.append('wt.grade_label AS grd_nm')

    # 산지 선택 시
    if sanji_code:
        group_by.append('wt.j_sanji_cd')
        select_parts.append('wt.j_sanji_cd')
        select_parts.append('MAX(mrs.j_sanji_nm) AS j_sanji_nm')

    # 집계 컬럼
    select_parts.append('ROUND(SUM(wt.unit_tot_qty), 0) AS unit_tot_qty')
    select_parts.append('ROUND(SUM(wt.totprc) / NULLIF(SUM(wt.unit_tot_qty),0), 0) AS avg_price')

    select_sql = ',\n    '.join(select_parts)
    group_by_sql = ', '.join(group_by)

    # 최종 쿼리 조합
    query = f"""
        SELECT
            {select_sql}
        FROM fact_trade_weekly wt
        {join_crop}
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

    return jsonify(rows)

# 최신 일자(데이터상) 조회
@app.route('/api/latest_dates', methods=['GET'])
def get_latest_dates():
    conn = get_connection()
    query = """
        SELECT DISTINCT trd_clcln_ymd
        FROM fact_trade
        ORDER BY trd_clcln_ymd DESC
        LIMIT 14
    """
    with conn.cursor() as cursor:
        cursor.execute(query)
        rows = [row['trd_clcln_ymd'] for row in cursor.fetchall()]
    conn.close()

    if not rows:
        return jsonify({'start_date': '', 'end_date': ''})
    
    # 날짜컬럼 모두 yyyy-MM-dd로 변환
    return jsonify({
        'start_date': rows[-1].strftime('%Y-%m-%d'),
        'end_date': rows[0].strftime('%Y-%m-%d')
        })

# 날짜형 컬럼 변환 함수
def to_date_str(row, key):
    if row.get(key) and not isinstance(row[key], str):
        row[key] = row[key].strftime('%Y-%m-%d')


# 일간 거래 데이터 조회(그래프용)
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


# 품목 리스트 로드
@app.route('/api/items', methods=['GET'])
def get_items():
    conn = get_connection()
    query = """
        SELECT DISTINCT item_code, gds_mclsf_nm
        FROM vw_crop_item_name
        ORDER BY item_code
    """
    with conn.cursor() as cursor:
        cursor.execute(query)
        rows = cursor.fetchall()
    conn.close()
    return jsonify(rows)

# 품종 리스트 로드(품목에 맞게)
@app.route('/api/varieties', methods=['GET'])
def get_varieties():
    item_code = request.args.get('item_code')
    start_week = request.args.get('start_week')  # 주간 또는 일간 모두 받음
    end_week = request.args.get('end_week')

    if not item_code or not start_week or not end_week:
        return jsonify({'error': 'item_code, start_week, end_week are required'}), 400

    # 날짜 자릿수로 주간/일간 판단 (yyyyMM=6, yyyyMMdd=8)
    is_daily = (len(start_week) == 8 and len(end_week) == 8)
    if is_daily:
        date_col = 'ft.trd_clcln_ymd'
    else:
        date_col = 'wt.weekno'

    if is_daily:
        query = f"""
            SELECT DISTINCT mcv.crop_full_code, mcv.gds_sclsf_nm
            FROM master_crop_variety mcv
            JOIN fact_trade ft ON mcv.crop_full_code = ft.crop_full_code
            WHERE mcv.item_code = %s
                AND {date_col} >= %s
                AND {date_col} <= %s
            ORDER BY mcv.crop_full_code
        """
    else:
        query = f"""
            SELECT DISTINCT mcv.crop_full_code, mcv.gds_sclsf_nm
            FROM master_crop_variety mcv
            JOIN fact_trade_weekly wt ON mcv.crop_full_code = wt.crop_full_code
            WHERE mcv.item_code = %s
                AND {date_col} >= %s
                AND {date_col} <= %s
            ORDER BY mcv.crop_full_code
        """

    params = (item_code, start_week, end_week)

    conn = get_connection()
    with conn.cursor() as cursor:
        cursor.execute(query, params)
        rows = cursor.fetchall()
    conn.close()
    return jsonify(rows)


# 산지 리스트 로드(품목 or 품종에 맞게)
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

# 등급 리스트 로드(데이터가 있는것만 보여줌)
@app.route('/api/grades', methods=['GET'])
def get_grades():
    item_code = request.args.get('item_code')
    crop_full_code = request.args.get('crop_full_code')
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
    where_clause = " AND ".join(where)

    query = f"""
        SELECT DISTINCT {grade_col} AS grade
        FROM {table}
        WHERE {where_clause} AND {grade_col} IS NOT NULL
        ORDER BY FIELD({grade_col}, '고', '중', '저'), {grade_col}
    """

    conn = get_connection()
    with conn.cursor() as cursor:
        cursor.execute(query, params)
        rows = [row['grade'] for row in cursor.fetchall() if row['grade']]
    conn.close()
    return jsonify(rows)


if __name__ == '__main__':
    app.run(debug=True)
