CREATE TABLE predict_price (
    weekno VARCHAR(6) NOT NULL COMMENT '거래주차',
    item_code VARCHAR(4) NOT NULL COMMENT '품목코드',
    current_avg_prc FLOAT COMMENT '현재평균단가(원)',
    last_year_avg_prc FLOAT COMMENT '전년평균단가(원)',
    predict_avg_prc FLOAT COMMENT '예측평균단가(원)',
    PRIMARY KEY (weekno, item_code)
);