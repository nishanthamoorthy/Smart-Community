-- ============================================================
-- Smart Community Resource & Volunteer Allocation System
-- Database Schema
-- ============================================================

CREATE DATABASE IF NOT EXISTS smart_community;
USE smart_community;

-- ============================================================
-- Table: issues
-- Stores community problems reported by NGO admins
-- ============================================================
CREATE TABLE IF NOT EXISTS issues (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    location VARCHAR(255) NOT NULL,
    latitude DECIMAL(10, 8) DEFAULT 11.9416,   -- default: Tamil Nadu region
    longitude DECIMAL(11, 8) DEFAULT 77.7178,
    severity ENUM('low', 'medium', 'high') NOT NULL DEFAULT 'low',
    people_affected INT NOT NULL DEFAULT 0,
    priority ENUM('normal', 'high') NOT NULL DEFAULT 'normal',
    status ENUM('open', 'in_progress', 'resolved') DEFAULT 'open',
    category VARCHAR(100) DEFAULT 'general',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- Table: volunteers
-- Stores registered volunteer profiles
-- ============================================================
CREATE TABLE IF NOT EXISTS volunteers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    skill ENUM('doctor', 'driver', 'teacher', 'engineer', 'nurse', 'counselor', 'general') NOT NULL DEFAULT 'general',
    location VARCHAR(255) NOT NULL,
    latitude DECIMAL(10, 8) DEFAULT 11.9416,
    longitude DECIMAL(11, 8) DEFAULT 77.7178,
    phone VARCHAR(20),
    is_available BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- Table: assignments
-- Links volunteers to issues (many-to-many)
-- ============================================================
CREATE TABLE IF NOT EXISTS assignments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    issue_id INT NOT NULL,
    volunteer_id INT NOT NULL,
    assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status ENUM('assigned', 'completed') DEFAULT 'assigned',
    notes TEXT,
    FOREIGN KEY (issue_id) REFERENCES issues(id) ON DELETE CASCADE,
    FOREIGN KEY (volunteer_id) REFERENCES volunteers(id) ON DELETE CASCADE,
    UNIQUE KEY unique_assignment (issue_id, volunteer_id)
);

-- ============================================================
-- Seed Data: Sample issues for demo
-- ============================================================
INSERT INTO issues (title, description, location, latitude, longitude, severity, people_affected, priority, category) VALUES
('Flood Relief Needed', 'Heavy rains caused flooding in low-lying areas. Families displaced.', 'Erode District', 11.3410, 77.7172, 'high', 250, 'high', 'disaster'),
('Medical Camp Required', 'Outbreak of seasonal fever, elderly people need medical attention.', 'Perundurai', 11.2749, 77.5924, 'high', 120, 'high', 'medical'),
('School Supplies Shortage', 'Primary school lacks notebooks and basic supplies for 80 children.', 'Bhavani', 11.4480, 77.6830, 'medium', 80, 'normal', 'education'),
('Drinking Water Issue', 'Contaminated water source affecting village community.', 'Anthiyur', 11.5731, 77.5912, 'high', 60, 'normal', 'water'),
('Road Repair Needed', 'Broken road causes accidents and isolates 30 families.', 'Gobichettipalayam', 11.4540, 77.4350, 'medium', 30, 'normal', 'infrastructure');

-- ============================================================
-- Seed Data: Sample volunteer
-- Password: volunteer123 (bcrypt hashed)
-- ============================================================
INSERT INTO volunteers (name, email, password_hash, skill, location, latitude, longitude, phone) VALUES
('Dr. Priya Rajan', 'priya@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMlJFs0.X/fNkMv.HtYVMnUd4e', 'doctor', 'Erode', 11.3410, 77.7172, '9876543210'),
('Suresh Kumar', 'suresh@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMlJFs0.X/fNkMv.HtYVMnUd4e', 'driver', 'Perundurai', 11.2749, 77.5924, '9876543211'),
('Meena Devi', 'meena@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMlJFs0.X/fNkMv.HtYVMnUd4e', 'teacher', 'Bhavani', 11.4480, 77.6830, '9876543212');
