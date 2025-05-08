DROP TABLE IF EXISTS user;

CREATE TABLE user (first_name TEXT,
                    last_name TEXT,
                    username TEXT PRIMARY KEY NOT NULL ,
                    email_address TEXT UNIQUE NOT NULL ,
                    employee INTEGER,
                    password TEXT,
                    salt TEXT);



