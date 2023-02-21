-- migrate:up
CREATE TABLE Users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL
);

-- migrate:down
DROP TABLE Users;
