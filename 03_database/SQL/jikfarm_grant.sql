-- 계정 생성 및 권한 부여

CREATE USER 'jikfarm1'@'%' IDENTIFIED BY 'wlrvkaAI1';
CREATE USER 'jikfarm2'@'%' IDENTIFIED BY 'wlrvkaAI2';
CREATE USER 'jikfarm3'@'%' IDENTIFIED BY 'wlrvkaAI3';
CREATE USER 'jikfarm4'@'%' IDENTIFIED BY 'wlrvkaAI4';

GRANT SELECT, INSERT, UPDATE, DELETE ON jikfarm_db.* TO 'jikfarm1'@'%';
GRANT ALL PRIVILEGES ON *.* TO 'jikfarm1'@'%' WITH GRANT OPTION;
GRANT SELECT, INSERT, UPDATE, DELETE ON jikfarm_db.* TO 'jikfarm2'@'%';
GRANT SELECT, INSERT, UPDATE, DELETE ON jikfarm_db.* TO 'jikfarm3'@'%';
GRANT SELECT, INSERT, UPDATE, DELETE ON jikfarm_db.* TO 'jikfarm4'@'%';

FLUSH PRIVILEGES;