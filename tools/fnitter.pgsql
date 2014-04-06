
CREATE TABLE accounts (
    user_id integer NOT NULL,
    account_data text NOT NULL
);

ALTER TABLE ONLY accounts
    ADD CONSTRAINT accounts_pkey PRIMARY KEY (user_id);

CREATE TABLE tweets (
    "time" timestamp without time zone DEFAULT now() NOT NULL,
    user_id integer NOT NULL,
    tweet text NOT NULL
);

ALTER TABLE ONLY tweets
    ADD CONSTRAINT tweets_pkey PRIMARY KEY ("time");

CREATE INDEX tweets_user_id_idx ON tweets USING btree (user_id);
