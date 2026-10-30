-- 廢墟版活動報名平台(基本款) 資料庫
-- 匯入方式: mysql -u root -p < database.sql  (或在 phpMyAdmin 使用「匯入」)

CREATE DATABASE IF NOT EXISTS ruins_events
  DEFAULT CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE ruins_events;

-- 先刪子表再刪父表，方便重複匯入
DROP TABLE IF EXISTS registrations;
DROP TABLE IF EXISTS events;

-- 活動表: 對應「新增新的活動」「列出可報名的活動清單」
CREATE TABLE events (
  event_id    INT AUTO_INCREMENT PRIMARY KEY,
  title       VARCHAR(100) NOT NULL COMMENT '活動名稱',
  description TEXT COMMENT '活動說明',
  location    VARCHAR(150) COMMENT '活動地點',
  event_date  DATETIME NOT NULL COMMENT '活動日期時間',
  status      ENUM('open', 'closed') NOT NULL DEFAULT 'open' COMMENT 'open=可報名, closed=截止',
  created_at  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- 報名表: 對應「填寫報名表(姓名、連絡電話)」「查看活動的報名清單」
CREATE TABLE registrations (
  registration_id INT AUTO_INCREMENT PRIMARY KEY,
  event_id        INT NOT NULL COMMENT '報名的活動',
  name            VARCHAR(50) NOT NULL COMMENT '姓名',
  phone           VARCHAR(20) NOT NULL COMMENT '連絡電話',
  created_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_reg_event
    FOREIGN KEY (event_id) REFERENCES events(event_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  INDEX idx_reg_event (event_id)
) ENGINE=InnoDB;

-- 測試資料
INSERT INTO events (title, description, location, event_date, status) VALUES
  ('廢棄工廠夜間探索', '攜帶手電筒與安全帽，由領隊帶領參觀。', '台中舊廠區', '2026-11-15 19:00:00', 'open'),
  ('廢棄學校攝影團',   '適合攝影愛好者，請自備相機。',       '南投舊校舍', '2026-11-22 09:00:00', 'open'),
  ('廢棄車站導覽',     '已額滿截止。',                       '舊車站',     '2026-10-20 14:00:00', 'closed');

INSERT INTO registrations (event_id, name, phone) VALUES
  (1, '王小明', '0912345678'),
  (1, '李小華', '0923456789'),
  (2, '陳大文', '0934567890');

-- 常用查詢範例
-- 1) 列出可報名的活動清單
--    SELECT * FROM events WHERE status = 'open' ORDER BY event_date;
-- 2) 新增報名
--    INSERT INTO registrations (event_id, name, phone) VALUES (1, '姓名', '電話');
-- 3) 查看某活動的報名清單
--    SELECT name, phone, created_at FROM registrations WHERE event_id = 1 ORDER BY created_at;
