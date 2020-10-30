-- DROP TABLE IF EXISTS users;
-- DROP TABLE IF EXISTS socialmedia;

CREATE TABLE IF NOT EXISTS users (
    id integer PRIMARY KEY,
    phone_number text NOT NULL);

CREATE TABLE IF NOT EXISTS socialmedia (
	id integer PRIMARY KEY,
	user_id integer NOT NULL, 
	instagram text NOT NULL,
	FOREIGN KEY (user_id) REFERENCES users (id)
);

INSERT INTO users (phone_number)
VALUES ("whatsapp:+14155238886");
INSERT INTO socialmedia (user_id, instagram)
VALUES (1, "IGhandle1");

INSERT INTO users (phone_number)
VALUES ("whatsapp:+43214243214");
INSERT INTO socialmedia (user_id, instagram)
VALUES (2, "IGhandle2");

INSERT INTO users (phone_number)
VALUES ("whatsapp:+535643344");
INSERT INTO socialmedia (user_id, instagram)
VALUES (3, "IGhandle3");

-- SELECT users.id, phone_number, instagram FROM users JOIN socialmedia	ON (socialmedia.id = users.id);
