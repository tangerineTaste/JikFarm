-- 추출할 테이블/뷰 리스트 (파티션 포함)

-- ==============================
-- fact_trade
-- ==============================
CREATE TABLE `fact_trade` (
  `trd_clcln_ymd` date NOT NULL,
  `crop_full_code` varchar(15) COLLATE utf8mb4_general_ci NOT NULL,
  `item_code` varchar(4) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `j_sanji_cd` varchar(20) COLLATE utf8mb4_general_ci NOT NULL,
  `grade_label` varchar(5) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `unit_tot_qty` float DEFAULT NULL,
  `totprc` float DEFAULT NULL,
  `year_part` int GENERATED ALWAYS AS (cast(year(`trd_clcln_ymd`) as unsigned)) STORED NOT NULL,
  PRIMARY KEY (`year_part`,`trd_clcln_ymd`,`crop_full_code`,`j_sanji_cd`),
  KEY `idx_itemcode_date` (`item_code`,`trd_clcln_ymd`),
  KEY `idx_itemcode_crop_grade_date` (`item_code`,`crop_full_code`,`grade_label`,`trd_clcln_ymd`),
  KEY `idx_j_sanji_cd_date` (`j_sanji_cd`,`trd_clcln_ymd`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci
/*!50100 PARTITION BY RANGE (`year_part`)
(PARTITION p2018 VALUES LESS THAN (2019) ENGINE = InnoDB,
 PARTITION p2019 VALUES LESS THAN (2020) ENGINE = InnoDB,
 PARTITION p2020 VALUES LESS THAN (2021) ENGINE = InnoDB,
 PARTITION p2021 VALUES LESS THAN (2022) ENGINE = InnoDB,
 PARTITION p2022 VALUES LESS THAN (2023) ENGINE = InnoDB,
 PARTITION p2023 VALUES LESS THAN (2024) ENGINE = InnoDB,
 PARTITION p2024 VALUES LESS THAN (2025) ENGINE = InnoDB,
 PARTITION p2025 VALUES LESS THAN (2026) ENGINE = InnoDB,
 PARTITION pMAX VALUES LESS THAN MAXVALUE ENGINE = InnoDB) */;


-- ==============================
-- fact_trade_weekly
-- ==============================
CREATE TABLE `fact_trade_weekly` (
  `weekno` varchar(6) COLLATE utf8mb4_general_ci NOT NULL,
  `crop_full_code` varchar(15) COLLATE utf8mb4_general_ci NOT NULL,
  `item_code` varchar(4) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `j_sanji_cd` varchar(20) COLLATE utf8mb4_general_ci NOT NULL,
  `grade_label` varchar(5) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `unit_tot_qty` float DEFAULT NULL,
  `avg_prc` float DEFAULT NULL,
  `year_part` int NOT NULL,
  `totprc` float DEFAULT NULL COMMENT '전체거래액(원)',
  PRIMARY KEY (`weekno`,`crop_full_code`,`j_sanji_cd`,`year_part`),
  KEY `idx_itemcode_weekno` (`item_code`,`weekno`),
  KEY `idx_cropfullcode_weekno_grade` (`crop_full_code`,`weekno`,`grade_label`),
  KEY `idx_itemcode_crop_grade_weekno` (`item_code`,`crop_full_code`,`grade_label`,`weekno`),
  KEY `idx_j_sanji_cd_weekno` (`j_sanji_cd`,`weekno`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci
/*!50100 PARTITION BY RANGE (`year_part`)
(PARTITION p2018 VALUES LESS THAN (2019) ENGINE = InnoDB,
 PARTITION p2019 VALUES LESS THAN (2020) ENGINE = InnoDB,
 PARTITION p2020 VALUES LESS THAN (2021) ENGINE = InnoDB,
 PARTITION p2021 VALUES LESS THAN (2022) ENGINE = InnoDB,
 PARTITION p2022 VALUES LESS THAN (2023) ENGINE = InnoDB,
 PARTITION p2023 VALUES LESS THAN (2024) ENGINE = InnoDB,
 PARTITION p2024 VALUES LESS THAN (2025) ENGINE = InnoDB,
 PARTITION p2025 VALUES LESS THAN (2026) ENGINE = InnoDB,
 PARTITION pMAX VALUES LESS THAN MAXVALUE ENGINE = InnoDB) */;


-- ==============================
-- factor_external
-- ==============================
CREATE TABLE `factor_external` (
  `weekno` varchar(6) COLLATE utf8mb4_general_ci NOT NULL,
  `item_code` varchar(4) COLLATE utf8mb4_general_ci NOT NULL,
  `holiday_flag` int DEFAULT NULL,
  `holiday_score` float DEFAULT NULL,
  `grow_score` float DEFAULT NULL,
  PRIMARY KEY (`weekno`,`item_code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;


-- ==============================
-- interest_whitelist
-- ==============================
CREATE TABLE `interest_whitelist` (
  `crop_id` varchar(10) COLLATE utf8mb4_general_ci NOT NULL,
  `display_name` varchar(100) COLLATE utf8mb4_general_ci NOT NULL,
  `sort_order` int DEFAULT '0',
  `is_active` tinyint(1) DEFAULT '1',
  PRIMARY KEY (`crop_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;


-- ==============================
-- map_region_weather_station
-- ==============================
CREATE TABLE `map_region_weather_station` (
  `plor_cd` varchar(8) COLLATE utf8mb4_general_ci NOT NULL COMMENT '원천 산지코드 (KAMIS)',
  `plor_nm` varchar(30) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `j_sanji_cd` int DEFAULT NULL COMMENT '직팜 내부 코드',
  `j_sanji_nm` varchar(20) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `station_cd` varchar(4) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '기상관측소코드',
  PRIMARY KEY (`plor_cd`),
  KEY `idx_map_region_j_sanji_cd` (`j_sanji_cd`),
  KEY `idx_j_sanji_cd` (`j_sanji_cd`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;


-- ==============================
-- master_crop_variety
-- ==============================
CREATE TABLE `master_crop_variety` (
  `crop_full_code` varchar(6) COLLATE utf8mb4_general_ci NOT NULL COMMENT '대분류+품목+품종 코드 (예: 120101)',
  `item_code` varchar(4) COLLATE utf8mb4_general_ci NOT NULL COMMENT '대분류+품목 코드 (예: 1201)',
  `gds_lclsf_cd` varchar(2) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '대분류 코드',
  `gds_lclsf_nm` varchar(20) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '대분류명',
  `gds_mclsf_cd` varchar(2) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '품목 코드',
  `gds_mclsf_nm` varchar(20) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '품목명',
  `gds_sclsf_cd` varchar(2) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '품종 코드',
  `gds_sclsf_nm` varchar(20) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '품종명',
  PRIMARY KEY (`crop_full_code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;


-- ==============================
-- member_addresses
-- ==============================
CREATE TABLE `member_addresses` (
  `address_id` bigint NOT NULL AUTO_INCREMENT,
  `member_id` bigint NOT NULL,
  `road_full_addr` varchar(200) COLLATE utf8mb4_general_ci NOT NULL,
  `zip_no` varchar(10) COLLATE utf8mb4_general_ci NOT NULL,
  `addr_detail` varchar(100) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `si_nm` varchar(30) COLLATE utf8mb4_general_ci NOT NULL,
  `sgg_nm` varchar(30) COLLATE utf8mb4_general_ci NOT NULL,
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`address_id`),
  KEY `member_id` (`member_id`),
  CONSTRAINT `member_addresses_ibfk_1` FOREIGN KEY (`member_id`) REFERENCES `members` (`member_id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;


-- ==============================
-- member_crops
-- ==============================
CREATE TABLE `member_crops` (
  `member_crop_id` bigint NOT NULL AUTO_INCREMENT,
  `member_id` bigint NOT NULL,
  `crop_id` varchar(10) COLLATE utf8mb4_general_ci NOT NULL,
  `is_primary` tinyint(1) DEFAULT '0',
  PRIMARY KEY (`member_crop_id`),
  UNIQUE KEY `member_id` (`member_id`,`crop_id`),
  KEY `crop_id` (`crop_id`),
  CONSTRAINT `member_crops_ibfk_1` FOREIGN KEY (`member_id`) REFERENCES `members` (`member_id`),
  CONSTRAINT `member_crops_ibfk_2` FOREIGN KEY (`crop_id`) REFERENCES `interest_whitelist` (`crop_id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;


-- ==============================
-- members
-- ==============================
CREATE TABLE `members` (
  `member_id` bigint NOT NULL AUTO_INCREMENT,
  `login_id` varchar(50) COLLATE utf8mb4_general_ci NOT NULL,
  `nickname` varchar(30) COLLATE utf8mb4_general_ci NOT NULL,
  `name` varchar(30) COLLATE utf8mb4_general_ci NOT NULL,
  `password` varchar(255) COLLATE utf8mb4_general_ci NOT NULL,
  `is_admin` tinyint(1) DEFAULT '0',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`member_id`),
  UNIQUE KEY `login_id` (`login_id`),
  UNIQUE KEY `nickname` (`nickname`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- ==============================
-- weather_daily
-- ==============================
CREATE TABLE `weather_daily` (
  `TM` date NOT NULL,
  `STN` varchar(4) COLLATE utf8mb4_general_ci NOT NULL,
  `TA_AVG` float DEFAULT NULL,
  `TA_MAX` float DEFAULT NULL,
  `TA_MIN` float DEFAULT NULL,
  `HM_AVG` float DEFAULT NULL,
  `RN_DAY` float DEFAULT NULL,
  `RN_60M_MAX` float DEFAULT NULL,
  PRIMARY KEY (`TM`,`STN`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;


-- ==============================
-- v_active_interest_crops
-- ==============================
CREATE ALGORITHM=UNDEFINED DEFINER=`root`@`localhost` SQL SECURITY DEFINER VIEW `v_active_interest_crops` AS select `interest_whitelist`.`crop_id` AS `crop_id`,`interest_whitelist`.`display_name` AS `display_name` from `interest_whitelist` where (`interest_whitelist`.`is_active` = true) order by `interest_whitelist`.`sort_order`;


-- ==============================
-- vw_crop_item_name
-- ==============================
CREATE ALGORITHM=UNDEFINED DEFINER=`jikfarm1`@`%` SQL SECURITY DEFINER VIEW `vw_crop_item_name` AS select distinct `master_crop_variety`.`item_code` AS `item_code`,`master_crop_variety`.`gds_mclsf_nm` AS `gds_mclsf_nm` from `master_crop_variety`;


-- ==============================
-- vw_map_region_sanji
-- ==============================
CREATE ALGORITHM=UNDEFINED DEFINER=`jikfarm1`@`%` SQL SECURITY DEFINER VIEW `vw_map_region_sanji` AS select `map_region_weather_station`.`j_sanji_cd` AS `j_sanji_cd`,max(`map_region_weather_station`.`j_sanji_nm`) AS `j_sanji_nm` from `map_region_weather_station` group by `map_region_weather_station`.`j_sanji_cd`;
