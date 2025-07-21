from flask import Flask, request, jsonify, render_template
import os
import pymysql
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# DB 정보
user = os.getenv("DB_USER", "root")  # .env 파일에 DB_USER 설정해도 됨
host = os.getenv("DB_HOST", "localhost")
password = os.getenv("DB_PW")  # DB_pw → 대소문자 주의 (env 키명)
port = int(os.getenv("DB_PORT", 3306))
db = os.getenv("DB_NAME", "jikfarm_db")


def get_connection():
    return pymysql.connect(
        host=host,
        user=user,
        password=password,
        database=db,
        port=port,
        cursorclass=pymysql.cursors.DictCursor
    )

@app.route('/')
def test_page():
    return render_template('test_weekly_trade.html')


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
