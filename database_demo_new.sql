CREATE DATABASE IF NOT EXISTS ruins_events DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE ruins_events;
CREATE TABLE IF NOT EXISTS events (
 event_id INT AUTO_INCREMENT PRIMARY KEY,
 title VARCHAR(100) NOT NULL,
 description TEXT,
 location VARCHAR(150),
 event_date DATETIME NOT NULL,
 registration_deadline DATETIME NULL,
 status ENUM('open','closed') NOT NULL DEFAULT 'open',
 created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;
CREATE TABLE IF NOT EXISTS registrations (
 registration_id INT AUTO_INCREMENT PRIMARY KEY,
 event_id INT NOT NULL,
 name VARCHAR(50) NOT NULL,
 phone VARCHAR(20) NOT NULL,
 created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
 CONSTRAINT fk_reg_event FOREIGN KEY (event_id) REFERENCES events(event_id) ON DELETE CASCADE ON UPDATE CASCADE,
 CONSTRAINT uq_event_name_phone UNIQUE (event_id,name,phone),
 INDEX idx_reg_event (event_id)
) ENGINE=InnoDB;
INSERT INTO events (title,description,location,event_date,registration_deadline,status) VALUES
('搖滾台中樂團交流夜','台中樂團交流與現場表演示範活動。','台中市西屯區（示範地點）','2026-11-15 19:00:00','2026-11-12 23:59:00','open'),
('搖滾新聲試聽會','認識新樂團與原創音樂的示範場次。','台中市北區（示範地點）','2026-11-22 09:00:00','2026-11-20 23:59:00','open'),
('搖滾回顧夜','活動已截止。','台中市中區（示範地點）','2026-10-20 14:00:00','2026-10-18 23:59:00','closed');
INSERT INTO registrations(event_id,name,phone) VALUES (1,'王小明','0912345678'),(1,'李小華','0923456789'),(2,'陳大文','0934567890');
