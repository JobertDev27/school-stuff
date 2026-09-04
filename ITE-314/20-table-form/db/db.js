import mysql from "mysql2/promise";

const host = ""
const user = ""
const password = ""
const database = ""

export const db = mysql.createPool({
    host: host,
    user: user,
    password: password,
    database: database,
});

//CREATE TABLE biodata (
//    id INT AUTO_INCREMENT PRIMARY KEY,
//    first_name VARCHAR(100),
//    middle_name VARCHAR(100),
//    last_name VARCHAR(100),
//    birth_date DATE,
//    age INT,
//    gender VARCHAR(20),
//    civil_status VARCHAR(30),
//    nationality VARCHAR(50),
//    religion VARCHAR(50),
//    address VARCHAR(255),
//    city VARCHAR(100),
//    province VARCHAR(100),
//    phone VARCHAR(30),
//    email VARCHAR(150),
//    student_id VARCHAR(50),
//    course VARCHAR(100),
//    year_level INT,
//    school VARCHAR(150),
//    emergency_contact VARCHAR(100),
//    emergency_phone VARCHAR(30)
//);
