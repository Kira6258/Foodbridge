CREATE DATABASE IF NOT EXISTS foodbridge;
USE foodbridge;

CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    phone VARCHAR(20),
    role ENUM('donor', 'shelter', 'volunteer', 'admin') NOT NULL,
    lat DECIMAL(10, 8),
    lng DECIMAL(11, 8),
    is_verified BOOLEAN DEFAULT FALSE,
    otp_code VARCHAR(6),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS shelters (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    name VARCHAR(100) NOT NULL,
    address VARCHAR(255) NOT NULL,
    lat DECIMAL(10, 8),
    lng DECIMAL(11, 8),
    capacity INT,
    approved BOOLEAN DEFAULT FALSE,
    contact VARCHAR(100),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS donations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    donor_id INT,
    food_description TEXT NOT NULL,
    quantity VARCHAR(100),
    photo VARCHAR(255),
    lat DECIMAL(10, 8),
    lng DECIMAL(11, 8),
    status ENUM('AVAILABLE', 'CLAIMED', 'PICKED UP', 'DELIVERED') DEFAULT 'AVAILABLE',
    posted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    available_until DATETIME,
    FOREIGN KEY (donor_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS claims (
    id INT AUTO_INCREMENT PRIMARY KEY,
    donation_id INT,
    shelter_id INT,
    claimed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status ENUM('PENDING', 'ACCEPTED', 'RECEIVED') DEFAULT 'PENDING',
    FOREIGN KEY (donation_id) REFERENCES donations(id) ON DELETE CASCADE,
    FOREIGN KEY (shelter_id) REFERENCES shelters(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS deliveries (
    id INT AUTO_INCREMENT PRIMARY KEY,
    donation_id INT,
    volunteer_id INT,
    picked_up_at TIMESTAMP NULL,
    delivered_at TIMESTAMP NULL,
    status ENUM('ASSIGNED', 'PICKED UP', 'ON THE WAY', 'DELIVERED') DEFAULT 'ASSIGNED',
    FOREIGN KEY (donation_id) REFERENCES donations(id) ON DELETE CASCADE,
    FOREIGN KEY (volunteer_id) REFERENCES users(id) ON DELETE CASCADE
);
