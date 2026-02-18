CREATE DATABASE pregnancy_planner;
\connect pregnancy_planner

CREATE TABLE IF NOT EXISTS users (
  id SERIAL PRIMARY KEY,
  username VARCHAR(50) UNIQUE NOT NULL,
  password VARCHAR(255) NOT NULL
);

CREATE TABLE IF NOT EXISTS appointments (
  id SERIAL PRIMARY KEY,
  user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  title VARCHAR(120) NOT NULL,
  date_time TIMESTAMP NOT NULL,
  doctor_name VARCHAR (120) NOT NULL,
  appointment_type VARCHAR (50),
  status VARCHAR (20) NOT NULL,
  location VARCHAR(120),
  notes VARCHAR(1000)
);

--profile--
CREATE TABLE IF NOT EXISTS pregnancy_profiles (
  id SERIAL PRIMARY KEY,
  user_id INTEGER UNIQUE NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  due_date DATE NOT NULL,
  baby_nickname VARCHAR(50)
);
