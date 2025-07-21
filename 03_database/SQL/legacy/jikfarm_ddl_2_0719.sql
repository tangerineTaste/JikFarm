-- CREATE DATABASE jikfarm_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE jikfarm_db;

-- 0. 기존 테이블 제거
DROP TABLE IF EXISTS fact_trade;
DROP TABLE IF EXISTS factor_external;
DROP TABLE IF EXISTS factor_external_weekly;
DROP TABLE IF EXISTS map_region_weather_station;
DROP TABLE IF EXISTS weather_daily;
DROP TABLE IF EXISTS master_crop_variety;

-- 1. 작물 마스터 테이블 (품종 기준 + 품목 참조 가능)
CREATE TABLE `master_crop_variety` (
  `crop_full_code` varchar(6) PRIMARY KEY COMMENT '대분류+품목+품종 코드 (예: 120101)',
  `item_code` varchar(4) NOT NULL COMMENT '대분류+품목 코드 (예: 1201)',
  `gds_lclsf_cd` varchar(2) COMMENT '대분류 코드',
  `gds_lclsf_nm` varchar(20) COMMENT '대분류명',
  `gds_mclsf_cd` varchar(2) COMMENT '품목 코드',
  `gds_mclsf_nm` varchar(20) COMMENT '품목명',
  `gds_sclsf_cd` varchar(2) COMMENT '품종 코드',
  `gds_sclsf_nm` varchar(20) COMMENT '품종명'
);

-- 2. 산지-관측소 매핑 테이블
CREATE TABLE `map_region_weather_station` (
  `plor_cd` varchar(8) PRIMARY KEY COMMENT '원천 산지코드 (KAMIS)',
  `plor_nm` varchar(30),
  `j_sanji_cd` int COMMENT '직팜 내부 코드',
  `j_sanji_nm` varchar(20),
  `station_cd` varchar(4) COMMENT '기상관측소코드'
);

-- 3. 일별 기상 데이터
CREATE TABLE `weather_daily` (
  `TM` date,
  `STN` varchar(4),
  `TA_AVG` float,
  `TA_MAX` float,
  `TA_MIN` float,
  `HM_AVG` float,
  `RN_DAY` float,
  `RN_60M_MAX` float,
  PRIMARY KEY (`TM`, `STN`)
);

-- 4. 외부 요인 테이블 (품목 단위)
CREATE TABLE `factor_external` (
  `weekno` varchar(6),
  `item_code` varchar(4),
  `holiday_flag` int,
  `holiday_score` float,
  `grow_score` float,
  PRIMARY KEY (`weekno`, `item_code`)
);

-- 5. 원본 거래 데이터 테이블 (산지: plor_cd 기준)
CREATE TABLE `fact_trade` (
  `trd_clcln_ymd` date,
  `crop_full_code` varchar(15),
  `j_sanji_cd` varchar(20),
  `grade_label` varchar(5),
  `unit_tot_qty` float,
  `totprc` float,
  PRIMARY KEY (`trd_clcln_ymd`, `crop_full_code`, `j_sanji_cd`),
  FOREIGN KEY (`crop_full_code`) REFERENCES `master_crop_variety` (`crop_full_code`)
  );

CREATE TABLE `fact_trade_weekly` (
  `weekno` varchar(6),
  `crop_full_code` varchar(15),
  `j_sanji_cd` varchar(20),
  `grade_label` varchar(5),
  `unit_tot_qty` float,
  `avg_prc` float,
  PRIMARY KEY (`weekno`, `crop_full_code`, `j_sanji_cd`),
  FOREIGN KEY (`crop_full_code`) REFERENCES `master_crop_variety` (`crop_full_code`)
  );