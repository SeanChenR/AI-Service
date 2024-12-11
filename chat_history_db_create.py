import time
import pymysql

conn = pymysql.connect(host='localhost',
                        user='root',
                        password='123456')
cursor = conn.cursor()

database = "TEJ_AI_Service_Chat_Memory"
create_db = f"""CREATE DATABASE IF NOT EXISTS {database}"""
cursor.execute(create_db)

cursor.execute("SHOW DATABASES")
for x in cursor:
    print(x)

time.sleep(5)

db = pymysql.connect(
    host="localhost",
    user="root",
    password="123456",
    database=database,
)
cursor_db = db.cursor()

create_members_table = f"""
CREATE TABLE Members (
    member_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""
cursor_db.execute(create_members_table)

create_topics_table = f"""
CREATE TABLE Topics (
    topic_id INT AUTO_INCREMENT PRIMARY KEY,
    member_id INT NOT NULL,
    title varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (member_id) REFERENCES Members(member_id) ON DELETE CASCADE
);
"""
cursor_db.execute(create_topics_table)

create_posts_table = f"""
CREATE TABLE Posts (
    post_id INT AUTO_INCREMENT PRIMARY KEY,
    topic_id INT NOT NULL,
    member_id INT NOT NULL,
    content text CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci NOT NULL,
    parent_post_id INT DEFAULT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (topic_id) REFERENCES Topics(topic_id) ON DELETE CASCADE,
    FOREIGN KEY (member_id) REFERENCES Members(member_id) ON DELETE CASCADE,
    FOREIGN KEY (parent_post_id) REFERENCES Posts(post_id) ON DELETE CASCADE
);
"""
cursor_db.execute(create_posts_table)