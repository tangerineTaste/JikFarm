CREATE TABLE `production_data` (
  `id` int PRIMARY KEY AUTO_INCREMENT COMMENT '생산 ID',
  `date` date COMMENT '날짜',
  `mid_item_name` varchar(255) COMMENT '상품 중분류 이름',
  `grade` varchar(255) COMMENT '등급 이름',
  `total_price` int COMMENT '총 가격 (원)',
  `total_weight` float COMMENT '총 물량 (kg)',
  `origin_code` varchar(255) COMMENT '산지 코드',
  `origin_name` varchar(255) COMMENT '산지 이름',
  `jikfarm_origin_code` varchar(255) COMMENT '직팜 산지 코드',
  `jikfarm_origin_name` varchar(255) COMMENT '직팜 산지 이름'
);

CREATE TABLE `area_data` (
  `id` int PRIMARY KEY AUTO_INCREMENT COMMENT '면적 ID',
  `date` date COMMENT '날짜',
  `region` varchar(255) COMMENT '지역',
  `item_name` varchar(255) COMMENT '작물명',
  `area_ha` float COMMENT '재배 면적(ha)'
);

CREATE TABLE `climate_data` (
  `id` int PRIMARY KEY AUTO_INCREMENT COMMENT '기후 ID',
  `date` date COMMENT '날짜',
  `province` varchar(255) COMMENT '지역',
  `temp` float COMMENT '평균 기온(°C)',
  `rain` float COMMENT '강수량(mm)',
  `hum` float COMMENT '평균 상대습도(%)'
);

CREATE TABLE `consumption_trend` (
  `id` int PRIMARY KEY AUTO_INCREMENT COMMENT '소비 ID',
  `date` date COMMENT '날짜',
  `region` varchar(255) COMMENT '지역',
  `item_name` varchar(255) COMMENT '작물명',
  `store_name` varchar(255) COMMENT '판매처명',
  `unit` varchar(255) COMMENT '판매단위',
  `price` int COMMENT '가격(원)'
);

CREATE TABLE `export_import_data` (
  `id` int PRIMARY KEY AUTO_INCREMENT COMMENT '수출입 ID',
  `date` date COMMENT '날짜',
  `item_name` varchar(255) COMMENT '작물명',
  `type` varchar(255) COMMENT '수출 or 수입 구분',
  `country` varchar(255) COMMENT '상대국 이름',
  `quantity_ton` float COMMENT '수출입량(톤)',
  `amount_usd` float COMMENT '금액(천달러)'
);

CREATE TABLE `wholesale_data` (
  `id` int PRIMARY KEY AUTO_INCREMENT COMMENT '도매 ID',
  `date` date COMMENT '날짜',
  `market_name` varchar(255) COMMENT '시장명',
  `item_name` varchar(255) COMMENT '작물명',
  `avg_price` int COMMENT '평균가(원/kg)',
  `quantity_ton` float COMMENT '거래량(톤)',
  `origin` varchar(255) COMMENT '산지',
  `unit_price` int COMMENT '단량단 금액(원)'
);

CREATE TABLE `future_prediction` (
  `id` int PRIMARY KEY AUTO_INCREMENT COMMENT '예측 ID',
  `item_name` varchar(255) COMMENT '작물 이름',
  `region` varchar(255) COMMENT '예측 지역',
  `date` date COMMENT '예측 날짜',
  `predicted_price` int COMMENT '예측 단가(원/kg 등)',
  `predicted_demand` float COMMENT '예측 수요량(톤)',
  `model_version` varchar(255) COMMENT '사용한 예측 모델 버전',
  `confidence` float COMMENT '예측 신뢰도 (0~1)',
  `created_at` datetime COMMENT '예측 생성 시각'
);
