-- migrate:up
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    chat_id BIGINT UNIQUE NOT NULL
);

-- migrate:down
DROP TABLE IF EXISTS users;