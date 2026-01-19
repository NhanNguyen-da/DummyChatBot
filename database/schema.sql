-- Database Schema for Chatbot Triage
-- SQLite Database

-- Conversations table - Stores chat history
CREATE TABLE IF NOT EXISTS conversations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    user_message TEXT NOT NULL,
    bot_response TEXT NOT NULL,
    suggested_department TEXT,
    timestamp TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Index for faster session lookups
CREATE INDEX IF NOT EXISTS idx_conversations_session_id ON conversations(session_id);

-- Departments table - Medical departments information
CREATE TABLE IF NOT EXISTS departments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    description TEXT,
    location TEXT,
    working_hours TEXT,
    phone TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Symptom rules table - Maps symptoms to departments
CREATE TABLE IF NOT EXISTS symptom_rules (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    symptom_keyword TEXT NOT NULL,
    department_id INTEGER NOT NULL,
    priority INTEGER DEFAULT 1,
    FOREIGN KEY (department_id) REFERENCES departments(id)
);

-- Index for faster symptom lookups
CREATE INDEX IF NOT EXISTS idx_symptom_rules_keyword ON symptom_rules(symptom_keyword);

-- Sample departments data
INSERT OR IGNORE INTO departments (name, description, location, working_hours) VALUES
('Khoa Cap Cuu', 'Khoa cap cuu - Xu ly cac truong hop khan cap', 'Tang 1, Toa A', '24/7'),
('Khoa Noi Tong Hop', 'Kham va dieu tri cac benh noi khoa', 'Tang 2, Toa B', '7:00 - 17:00'),
('Khoa Ngoai Tong Hop', 'Phau thuat va dieu tri ngoai khoa', 'Tang 3, Toa B', '7:00 - 17:00'),
('Khoa San Phu Khoa', 'Cham soc suc khoe phu nu va san khoa', 'Tang 4, Toa C', '7:00 - 17:00'),
('Khoa Nhi', 'Kham va dieu tri cho tre em', 'Tang 2, Toa C', '7:00 - 17:00'),
('Khoa Tim Mach', 'Chuyen khoa tim va mach mau', 'Tang 3, Toa A', '7:00 - 17:00'),
('Khoa Than Kinh', 'Chuyen khoa than kinh', 'Tang 4, Toa A', '7:00 - 17:00'),
('Khoa Mat', 'Kham va dieu tri cac benh ve mat', 'Tang 1, Toa D', '7:00 - 17:00'),
('Khoa Tai Mui Hong', 'Kham va dieu tri tai, mui, hong', 'Tang 2, Toa D', '7:00 - 17:00'),
('Khoa Da Lieu', 'Chuyen khoa da lieu', 'Tang 3, Toa D', '7:00 - 17:00');
