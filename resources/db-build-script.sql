CREATE DATABASE
IF NOT EXISTS cgav;
USE cgav;

-- TABLES

CREATE TABLE
IF NOT EXISTS users
(
    id INT NOT NULL AUTO_INCREMENT,
    email VARCHAR
(255),
    password VARCHAR
(80),
    Fname VARCHAR
(100),
    Lname VARCHAR
(100),
    user_role INT,
    PRIMARY KEY
(id)
);

CREATE TABLE IF NOT EXISTS api_config (
    id INT NOT NULL AUTO_INCREMENT,
    user_id INT NOT NULL,  -- Assuming each user can have their own API URL
    api_url VARCHAR(255),
    PRIMARY KEY (id),
    FOREIGN KEY (user_id) REFERENCES users(id)
);



CREATE TABLE
IF NOT EXISTS template
(
    template_id INT NOT NULL AUTO_INCREMENT,
    id INT,
    template_name VARCHAR
(255),
    template_image VARCHAR
(320),
   is_active BOOLEAN DEFAULT true,
    PRIMARY KEY
(template_id),
    FOREIGN KEY
(id) REFERENCES users
(id)
);

CREATE TABLE
IF NOT EXISTS Event_type
(
    event_type_id INT NOT NULL AUTO_INCREMENT,
    event_type_name VARCHAR
(255),
    is_active BOOLEAN DEFAULT true,
    PRIMARY KEY
(event_type_id)
);

CREATE TABLE
IF NOT EXISTS recipient
(
    recipient_id VARCHAR
(255) NOT NULL,
    first_name VARCHAR
(255),
    middle_name VARCHAR
(255),
    last_name VARCHAR
(255),
    gender VARCHAR
(10),
    email VARCHAR
(255),
    phone_number VARCHAR
(20),
    PRIMARY KEY
(recipient_id)
);

CREATE TABLE
IF NOT EXISTS instructor
(
    instructor_id VARCHAR
(255) NOT NULL,
    first_name VARCHAR
(255),
    middle_name VARCHAR
(255),
    last_name VARCHAR
(255),
    gender VARCHAR
(5),
    email VARCHAR
(255),
    phone_number VARCHAR
(20),
    PRIMARY KEY
(instructor_id)
);

CREATE TABLE
IF NOT EXISTS CertificateCustomizations
(
    customization_id INT NOT NULL AUTO_INCREMENT,
    template_id INT,
    id INT,
    items_positions JSON,
    PRIMARY KEY (customization_id),
    FOREIGN KEY (template_id) REFERENCES template(template_id),
    FOREIGN KEY(id) REFERENCES users(id)
);

CREATE TABLE
IF NOT EXISTS addCertificate
(
    certificate_event_id INT AUTO_INCREMENT NOT NULL,
    created_by INT NOT NULL,
    certificate_title VARCHAR
(255),
    form_type VARCHAR
(255),
    event_type_id INT,
    template_path VARCHAR
(255),
    intro VARCHAR
(255),
intro_en VARCHAR
(255),
    female_recipient_title VARCHAR
(255),
female_recipient_title_en VARCHAR
(255),
    male_recipient_title VARCHAR
(255),
male_recipient_title_en VARCHAR
(255),
    customization_id INT,
    template_id INT,
    instructor_id VARCHAR
(255),
    presenter_name VARCHAR
(255),
    secret_phrase VARCHAR
(255),
    event_date DATETIME,
    certificate_description_female TEXT,
    certificate_description_female_en TEXT,
    certificate_description_male TEXT,
    certificate_description_male_en TEXT,
    file_path VARCHAR
(255),
    first_Signatory_Name VARCHAR
(255),
    first_Signatory_Position VARCHAR
(255),
    first_Signatory_Path VARCHAR
(255),
    second_Signatory_Name VARCHAR
(255),
    second_Signatory_Position VARCHAR
(255),
    second_Signatory_Path VARCHAR
(255),
    greeting_female TEXT,
    greeting_female_en TEXT,
    greeting_male TEXT,
    greeting_male_en TEXT,
    sended BOOLEAN DEFAULT FALSE,   -- New field for tracking if the certificate is sent
    downloaded BOOLEAN DEFAULT FALSE,  -- New field for tracking if the certificate is downloaded
    generated_ BOOLEAN DEFAULT FALSE,  -- New field for tracking if the certificate is generated
    progress INT DEFAULT 0 , -- Counter for progress bar 
    total INT DEFAULT 0 , -- Total certificate for progress bar
    PRIMARY KEY
(certificate_event_id),
    FOREIGN KEY
(created_by) REFERENCES users
(id),
    FOREIGN KEY
(template_id) REFERENCES template
(template_id),
    FOREIGN KEY
(event_type_id) REFERENCES Event_type
(event_type_id),
    FOREIGN KEY
(customization_id) REFERENCES CertificateCustomizations
(customization_id),
    FOREIGN KEY
(instructor_id) REFERENCES instructor
(instructor_id)
);


CREATE TABLE
IF NOT EXISTS Certificate_table
(
    certificate_hash VARCHAR
(25) NOT NULL,
    recipient_id VARCHAR
(255),
    certificate_event_id INT,
    PRIMARY KEY
(certificate_hash),
    FOREIGN KEY
(recipient_id) REFERENCES recipient
(recipient_id),
    FOREIGN KEY
(certificate_event_id) REFERENCES addCertificate
(certificate_event_id)
);


CREATE TABLE
IF NOT EXISTS demo
(
    ID INTEGER PRIMARY KEY,
    Name VARCHAR
(20),
    Hint TEXT
);

-- INDEX

-- TRIGGER

-- VIEW
