CREATE EXTENSION IF NOT EXISTS rum;

-- Users table with auto-incrementing primary key
CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    username TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    age INTEGER
);

-- Messages table referencing users.user_id
CREATE TABLE messages (
    message_id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(user_id),
    message TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    fts_vector tsvector GENERATED ALWAYS AS (to_tsvector('english', message)) STORED
);

-- Transactions table referencing users.user_id
CREATE TABLE transactions (
    trans_id SERIAL PRIMARY KEY,
    amount INTEGER NOT NULL,
    user_id INTEGER REFERENCES users(user_id)
);

-- Indexes
CREATE INDEX idx_users_id_username ON users(user_id, username);
CREATE INDEX idx_messages_id_ctat_msg ON messages(user_id, created_at, message);
CREATE INDEX idx_users_username_id ON users(username, user_id);
CREATE INDEX idx_users_username_pwd_id ON users(username, password, user_id);

CREATE INDEX messages_fts_rum_idx
ON messages
USING rum (
    fts_vector rum_tsvector_addon_ops,
    created_at
)  WITH (attach = 'created_at', to = 'fts_vector');
