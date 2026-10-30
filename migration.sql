-- 適用於組員原有資料庫 (不刪資料)。請先備份。
USE ruins_events;
ALTER TABLE events ADD COLUMN registration_deadline DATETIME NULL AFTER event_date;
-- 在新增唯一索引前，先檢查是否已有重複紀錄：
-- SELECT event_id, name, phone, COUNT(*) FROM registrations GROUP BY event_id, name, phone HAVING COUNT(*) > 1;
ALTER TABLE registrations ADD CONSTRAINT uq_event_name_phone UNIQUE(event_id,name,phone);
-- 原有活動的截止日期為 NULL，仍受 status 控制；可手動逐筆補上時間。
