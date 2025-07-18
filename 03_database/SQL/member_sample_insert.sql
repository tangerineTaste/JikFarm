-- 샘플 데이터 삽입

INSERT INTO members (login_id, nickname, name, password, is_admin)
VALUES
('farmer01@example.com', '농부철수', '김철수', 'hashed_password_123', FALSE),
('farmer02@example.com', '농부영희', '이영희', 'hashed_password_456', FALSE),
('admin01@test.com', '테스트', '테스트', 'hashed_password_789', TRUE);

INSERT INTO interest_whitelist (crop_id, display_name, sort_order, is_active)
VALUES
(1201, '양파', 1, TRUE),
(1001, '배추', 2, TRUE),
(1005, '상추', 3, TRUE),
(1101, '무', 4, TRUE),
(901, '오이', 5, TRUE),
(1004, '양배추', 6, TRUE),
(601, '사과', 7, TRUE),
(602, '배', 8, TRUE),
(1202, '대파', 9, TRUE),
(1209, '마늘', 10, TRUE),
(804, '딸기', 11, TRUE),
(806, '방울토마토', 12, TRUE),
(501, '감자', 13, TRUE),
(502, '고구마', 14, TRUE),
(9999, '기타', 99, TRUE);

INSERT INTO member_addresses (member_id, road_full_addr, zip_no, addr_detail, si_nm, sgg_nm)
VALUES
(1, '경기도 수원시 팔달구 정조로 123', '16459', '203동 302호', '경기도', '수원시'),
(2, '서울특별시 강남구 테헤란로 456', '06236', '5층', '서울특별시', '강남구'),
(3, '서울특별시 관악구 신림로 456', '12345', '5층', '서울특별시', '관악구');

INSERT INTO member_crops (member_id, crop_id, is_primary)
VALUES
(1, '1201', TRUE),
(1, '1101', FALSE),
(2, '1001', TRUE);