-- =========================================================
-- SVVV ALUMNI PLATFORM - RELATIONAL DATABASE SCHEMA
-- Note: This is the raw SQL representation of the models
-- used in the Flask SQLAlchemy configuration.
-- =========================================================

-- 1. USERS TABLE (Student, Alumni, Admin)
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    enrollment_number VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    role ENUM('student', 'alumni', 'admin') DEFAULT 'alumni',
    email VARCHAR(150) UNIQUE,
    phone_number VARCHAR(15),
    
    -- Academic Details
    batch_year INT,
    department VARCHAR(100),
    
    -- Professional Details
    current_company VARCHAR(150),
    job_title VARCHAR(100),
    linkedin_url VARCHAR(255),
    profile_image_url VARCHAR(255),
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. JOB PORTAL TABLE
CREATE TABLE jobs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(150) NOT NULL,
    company VARCHAR(150) NOT NULL,
    location VARCHAR(100),
    job_type ENUM('Full-time', 'Part-time', 'Internship', 'Contract'),
    description TEXT NOT NULL,
    
    -- Foreign Key relation to the Alumni who posted it
    posted_by INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (posted_by) REFERENCES users(id) ON DELETE CASCADE
);

-- 3. EVENTS TABLE
CREATE TABLE events (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    description TEXT NOT NULL,
    event_date DATETIME NOT NULL,
    location VARCHAR(200),
    created_by INT NOT NULL,
    
    FOREIGN KEY (created_by) REFERENCES users(id)
);

-- 4. EVENT RSVP (Junction Table)
CREATE TABLE event_attendees (
    event_id INT,
    user_id INT,
    rsvp_status ENUM('going', 'maybe', 'not_going') DEFAULT 'going',
    
    PRIMARY KEY (event_id, user_id),
    FOREIGN KEY (event_id) REFERENCES events(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 5. NETWORKING (Connections Table)
CREATE TABLE connections (
    requester_id INT,
    receiver_id INT,
    status ENUM('pending', 'accepted', 'rejected') DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    PRIMARY KEY (requester_id, receiver_id),
    FOREIGN KEY (requester_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (receiver_id) REFERENCES users(id) ON DELETE CASCADE
);
