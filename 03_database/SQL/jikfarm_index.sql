-- 기존 인덱스 삭제 후 재생성
-- fact_trade
DROP INDEX idx_trd_clcln_ymd ON fact_trade;
DROP INDEX idx_fact_trade_date ON fact_trade;
DROP INDEX idx_crop_date ON fact_trade;
DROP INDEX idx_j_sanji_cd ON fact_trade;

-- fact_trade_weekly
DROP INDEX crop_full_code ON fact_trade_weekly;
DROP INDEX idx_item_code_weekno ON fact_trade_weekly;
DROP INDEX idx_j_sanji_cd ON fact_trade_weekly;

-- 신규 인덱스 생성
-- fact_trade
CREATE INDEX idx_itemcode_date ON fact_trade (item_code, trd_clcln_ymd);
CREATE INDEX idx_itemcode_crop_grade_date ON fact_trade (item_code, crop_full_code, grade_label, trd_clcln_ymd);
CREATE INDEX idx_j_sanji_cd_date ON fact_trade (j_sanji_cd, trd_clcln_ymd);

-- fact_trade_weekly
CREATE INDEX idx_itemcode_weekno ON fact_trade_weekly (item_code, weekno);
CREATE INDEX idx_cropfullcode_weekno_grade ON fact_trade_weekly (crop_full_code, weekno, grade_label);
CREATE INDEX idx_itemcode_crop_grade_weekno ON fact_trade_weekly (item_code, crop_full_code, grade_label, weekno);
CREATE INDEX idx_j_sanji_cd_weekno ON fact_trade_weekly (j_sanji_cd, weekno);

