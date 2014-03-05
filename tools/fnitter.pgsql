CREATE TABLE accounts (
    user_id integer NOT NULL,
    account_data text NOT NULL
);

ALTER TABLE ONLY stalked_users
    ADD CONSTRAINT stalked_users_pkey PRIMARY KEY (user_id);
