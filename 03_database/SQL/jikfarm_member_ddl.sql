-- 회원 관련 테이블 생성
USE jikfarm_db;

DROP TABLE IF EXISTS `member_crops`;
DROP TABLE IF EXISTS `member_addresses`;
DROP TABLE IF EXISTS `members`;
DROP TABLE IF EXISTS `interest_whitelist`;
DROP VIEW IF EXISTS `v_active_interest_crops`;
    
CREATE TABLE `members` (
    `member_id`     BIGINT        PRIMARY KEY AUTO_INCREMENT,
    `login_id`      VARCHAR(50)   UNIQUE NOT NULL,
    `nickname`      VARCHAR(30)   UNIQUE NOT NULL,
    `name`          VARCHAR(30)   NOT NULL,
    `password`      VARCHAR(255)  NOT NULL,
    `is_admin`      BOOLEAN       DEFAULT FALSE,
    `created_at`    DATETIME      DEFAULT CURRENT_TIMESTAMP,
    `updated_at`    DATETIME      DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);


CREATE TABLE `interest_whitelist` (
    `crop_id`       VARCHAR(10)   PRIMARY KEY,  -- ex: '1001'
    `display_name`  VARCHAR(100)  NOT NULL,     -- 사용자에게 보여질 이름
    `sort_order`    INT           DEFAULT 0,     -- UI 정렬 순서
    `is_active`     BOOLEAN       DEFAULT TRUE   -- 노출 가능 여부
);

CREATE TABLE `member_addresses` (
    `address_id`      BIGINT        PRIMARY KEY AUTO_INCREMENT,
    `member_id`       BIGINT        NOT NULL,
    `road_full_addr`  VARCHAR(200)  NOT NULL,
    `zip_no`          VARCHAR(10)   NOT NULL,
    `addr_detail`     VARCHAR(100),
    `si_nm`           VARCHAR(30)   NOT NULL,
    `sgg_nm`          VARCHAR(30)   NOT NULL,
    `created_at`      DATETIME      DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (member_id) REFERENCES members(member_id)
);

CREATE TABLE `member_crops` (
    `member_crop_id`  BIGINT        PRIMARY KEY AUTO_INCREMENT,
    `member_id`       BIGINT        NOT NULL,
    `crop_id`         VARCHAR(10)   NOT NULL,  -- FK to interest_whitelist.crop_id
    `is_primary`      BOOLEAN       DEFAULT FALSE,

    FOREIGN KEY (member_id) REFERENCES members(member_id),
    FOREIGN KEY (crop_id)  REFERENCES interest_whitelist(crop_id),
    UNIQUE KEY (member_id, crop_id)  -- 중복 등록 방지
);

-- 관심작물 UI 용
CREATE VIEW `v_active_interest_crops` AS
SELECT crop_id, display_name
FROM interest_whitelist
WHERE is_active = TRUE
ORDER BY sort_order;
