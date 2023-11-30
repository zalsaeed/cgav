CREATE DATABASE
IF NOT EXISTS cgav;
USE cgav;

-- TABLE

CREATE TABLE users
(
    id INT(255) NOT NULL AUTO_INCREMENT,
    user_name VARCHAR(255),
    email VARCHAR(255),
    password VARCHAR(80),
    user_role INT,
    PRIMARY KEY (id)
);

CREATE TABLE Template
(
    template_id VARCHAR(255) NOT NULL,
    template_name VARCHAR(255),
    template_image VARCHAR(320),
    PRIMARY KEY (template_id)
);

CREATE TABLE Event_type
(
    event_type_id VARCHAR(50) NOT NULL,
    event_type_name VARCHAR(255),
    is_active BOOLEAN DEFAULT true,
    PRIMARY KEY (event_type_id)
);

CREATE TABLE recipient
(
    recipient_id VARCHAR(255) NOT NULL,
    first_name VARCHAR(255),
    middle_name VARCHAR(255),
    last_name VARCHAR(255),
    gender VARCHAR(5),
    email VARCHAR(255),
    phone_number VARCHAR(20),
    PRIMARY KEY (recipient_id)
);

CREATE TABLE instructor
(
    instructor_id VARCHAR(255) NOT NULL,
    first_name VARCHAR(255),
    middle_name VARCHAR(255),
    last_name VARCHAR(255),
    gender VARCHAR(5),
    email VARCHAR(255),
    phone_number VARCHAR(20),
    PRIMARY KEY (instructor_id)
);

CREATE TABLE signs
(
    sign_id VARCHAR(255) NOT NULL,
    sign_name VARCHAR(255),
    sign_image VARCHAR(320),
    PRIMARY KEY (sign_id)
);

CREATE TABLE CertificateCustomizations
(
    customization_id VARCHAR(255) NOT NULL,
    template_id VARCHAR(255),
    id INT(255),
    title_position_x INT,
    title_position_y INT,
    recipient_name_position_x INT,
    recipient_name_position_y INT,
    description_position_x INT,
    description_position_y INT,
    logo_position_x INT,
    logo_position_y INT,
    signs JSON,
    PRIMARY KEY (customization_id),
    FOREIGN KEY (template_id) REFERENCES Template(template_id),
    FOREIGN KEY (id) REFERENCES users(id)
);

CREATE TABLE addCertificate
(
    certificate_event_id VARCHAR(255) NOT NULL,
    certificate_title VARCHAR(255),
    event_type_id VARCHAR(255) NULL, -- Allow NULL values for event_type_id
    recipient_id VARCHAR(255),
    customization_id VARCHAR(255),
    template_id VARCHAR(255),
    instructor_id VARCHAR(255),
    event_start_date DATETIME,
    event_end_date DATETIME,
    description VARCHAR(320),
    secret_key VARCHAR(255),
    presenter_name VARCHAR(255),       -- Added column
    secret_phrase VARCHAR(255),        -- Added column
    event_date DATETIME,               -- Added column
    certificate_description TEXT,      -- Changed from VARCHAR to TEXT
    file_path VARCHAR(255),            -- Added column
    PRIMARY KEY (certificate_event_id),
    FOREIGN KEY (template_id) REFERENCES Template(template_id),
    FOREIGN KEY (event_type_id) REFERENCES Event_type(event_type_id), -- This constraint will remain, but can now reference NULL
    FOREIGN KEY (recipient_id) REFERENCES recipient(recipient_id),
    FOREIGN KEY (customization_id) REFERENCES CertificateCustomizations(customization_id),
    FOREIGN KEY (instructor_id) REFERENCES instructor(instructor_id)
);

CREATE TABLE Certificate
(
    hash VARCHAR(25) NOT NULL,
    recipient_id VARCHAR(255),
    certificate_event_id VARCHAR(255),
    PRIMARY KEY (hash),
    FOREIGN KEY (recipient_id) REFERENCES recipient(recipient_id),
    FOREIGN KEY (certificate_event_id) REFERENCES addCertificate(certificate_event_id)
);

CREATE TABLE CertificateSigns
(
    certificate_event_id VARCHAR(255),
    sign_id VARCHAR(255),
    FOREIGN KEY (certificate_event_id) REFERENCES addCertificate(certificate_event_id),
    FOREIGN KEY (sign_id) REFERENCES signs(sign_id)
);

CREATE TABLE demo
(
    ID integer primary key,
    Name varchar(20),
    Hint text
);
 
-- INDEX
 
-- TRIGGER
 
-- VIEW
 
