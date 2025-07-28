from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from db_connection import get_connection
import os

auth_bp = Blueprint('auth', __name__)




@auth_bp.route('/login', methods=['GET', 'POST'])
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
                    return redirect(url_for('views.home'))
                else:
                    flash('아이디 또는 비밀번호가 일치하지 않습니다.', 'danger')
        finally:
            conn.close()
            
    return render_template('login.html')

@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        password_confirm = request.form['password-confirm']

        if password != password_confirm:
            flash('비밀번호가 일치하지 않습니다.', 'danger')
            return redirect(url_for('auth.signup'))

        conn = get_connection()
        try:
            with conn.cursor() as cursor:
                # 아이디 중복 확인
                sql = "SELECT * FROM members WHERE login_id=%s"
                cursor.execute(sql, (username,))
                if cursor.fetchone():
                    flash('이미 사용 중인 아이디입니다.', 'danger')
                    return redirect(url_for('auth.signup'))

                # 닉네임 중복 확인
                nickname = request.form['nickname']
                sql = "SELECT * FROM members WHERE nickname=%s"
                cursor.execute(sql, (nickname,))
                if cursor.fetchone():
                    flash('이미 사용 중인 닉네임입니다.', 'danger')
                    return redirect(url_for('auth.signup'))

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
                return redirect(url_for('auth.login'))
        finally:
            conn.close()

    return render_template('signup.html')

@auth_bp.route('/find_password')
@auth_bp.route('/find_password.html')
def find_password():
    return render_template('findPassword.html')

@auth_bp.route('/mypage')
def mypage():
    if 'member_id' not in session:
        flash('로그인이 필요합니다.', 'danger')
        return redirect(url_for('auth.login'))
    
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            sql = "SELECT * FROM members WHERE member_id=%s"
            cursor.execute(sql, (session['member_id'],))
            member_info = cursor.fetchone()
            return render_template('mypage.html', member=member_info)
    finally:
        conn.close()

@auth_bp.route('/logout')
def logout():
    session.pop('member_id', None)
    session.pop('login_id', None)
    session.pop('nickname', None)
    session.pop('name', None)
    flash('로그아웃되었습니다.', 'success')
    return redirect(url_for('views.home'))

@auth_bp.route('/api/member_interest_crops', methods=['GET'])
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

@auth_bp.route('/api/save_member_interest_crops', methods=['POST'])
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

@auth_bp.route('/api/update_profile', methods=['POST'])
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
