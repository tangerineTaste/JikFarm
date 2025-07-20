-- 실제 데이터 조회용 뷰 생성
-- 데일리 뷰
CREATE VIEW view_crop_trade_daily AS
SELECT 
    ft.trd_clcln_ymd,
    mcv.item_code,
    mcv.gds_mclsf_nm,
    ft.crop_full_code,
    mcv.gds_sclsf_nm,
    ft.grade_label as grd_cd,
    ft.grade_label as grd_nm,  -- 등급명이 별도로 없다면 동일하게
    ft.j_sanji_cd,
    mrs.j_sanji_nm,
    ft.unit_tot_qty,
    CASE 
        WHEN ft.unit_tot_qty > 0 THEN ft.totprc / ft.unit_tot_qty
        ELSE 0 
    END as avg_price
FROM fact_trade ft
JOIN master_crop_variety mcv ON ft.crop_full_code = mcv.crop_full_code
LEFT JOIN map_region_weather_station mrs ON ft.j_sanji_cd = mrs.j_sanji_cd;

-- 위클리 뷰
CREATE VIEW view_crop_chart_weekly AS
SELECT 
    YEAR(ft.trd_clcln_ymd) as year,
    WEEK(ft.trd_clcln_ymd, 1) as week_num,  -- ISO 주차 (월요일 시작)
    CONCAT(YEAR(ft.trd_clcln_ymd), 'W', LPAD(WEEK(ft.trd_clcln_ymd, 1), 2, '0')) as week_id,
    DATE_SUB(ft.trd_clcln_ymd, INTERVAL WEEKDAY(ft.trd_clcln_ymd) DAY) as week_start_date,
    mcv.item_code,
    mcv.gds_mclsf_nm,
    ft.crop_full_code,
    mcv.gds_sclsf_nm,
    ft.grade_label as grd_cd,
    ft.grade_label as grd_nm,
    ft.j_sanji_cd,
    mrs.j_sanji_nm,
    -- 주차별 집계
    SUM(ft.unit_tot_qty) as weekly_total_qty,
    AVG(CASE 
        WHEN ft.unit_tot_qty > 0 THEN ft.totprc / ft.unit_tot_qty
        ELSE 0 
    END) as weekly_avg_price,
    COUNT(DISTINCT ft.trd_clcln_ymd) as trading_days
FROM fact_trade ft
JOIN master_crop_variety mcv ON ft.crop_full_code = mcv.crop_full_code
LEFT JOIN map_region_weather_station mrs ON ft.j_sanji_cd = mrs.j_sanji_cd
GROUP BY 
    YEAR(ft.trd_clcln_ymd),
    WEEK(ft.trd_clcln_ymd, 1),
    mcv.item_code,
    ft.crop_full_code,
    ft.grade_label,
    ft.j_sanji_cd;