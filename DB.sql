CREATE OR REPLACE FUNCTION f_create_db(dbname text, usr text, passwd text)
RETURNS void AS
$func$
BEGIN
IF EXISTS (SELECT 1 FROM pg_database WHERE datname = dbname) THEN
   RAISE NOTICE 'Database already exists';
ELSE
    PERFORM dblink_exec('dbname=' || current_database() || ' user=' || usr || ' password=' || passwd,
    'CREATE DATABASE ' || quote_ident(dbname));
   
    PERFORM dblink_connect('connection', 'dbname=' || quote_ident(dbname) || ' user=' || usr || ' password=' || passwd);
   
    PERFORM dblink_exec('connection', 'BEGIN');

    PERFORM dblink_exec('connection', '
    
    CREATE TABLE IF NOT EXISTS client(
    phone_number numeric(10) PRIMARY KEY,
    id serial NOT NULL UNIQUE,
    surname text NOT NULL,
    name text NOT NULL,
    patronymic text,
    receptions_number integer
    DEFAULT 0
    CHECK(receptions_number>=0)
    );

    CREATE TABLE IF NOT EXISTS animal(
    id serial PRIMARY KEY,
    owner_id integer REFERENCES client(id)
    ON UPDATE CASCADE 
    ON DELETE CASCADE,
    nickname text NOT NULL,
    gender varchar(6) NOT NULL CHECK (gender IN (''male'', ''female'')),
    age numeric(2) NOT NULL CHECK (age>=0 OR age<=30),
    type text NOT NULL,
    breed text,
    color text,
    receptions_number integer
    DEFAULT 0
    CHECK(receptions_number>=0)
    );
    
    CREATE INDEX IF NOT EXISTS owner_id ON animal(owner_id);

    CREATE TABLE IF NOT EXISTS doctor(
    phone_number numeric(10) PRIMARY KEY,
    id serial NOT NULL UNIQUE,
    surname text NOT NULL,
    name text NOT NULL,
    patronymic text,
    qualification text NOT NULL,
    receptions_number integer DEFAULT 0 CHECK(receptions_number>=0),
    password text NOT NULL
    );
    
    CREATE TABLE IF NOT EXISTS reception(
    id serial PRIMARY KEY,
    animal_id integer REFERENCES animal(id)
    ON UPDATE CASCADE
    ON DELETE CASCADE,
    doctor_id integer REFERENCES doctor(id)
    ON UPDATE CASCADE
    ON DELETE CASCADE,
    date date NOT NULL,
    time time NOT NULL,
    description text,
    research text,
    diagnosis text,
    recommendations text
    );

    CREATE INDEX IF NOT EXISTS animal_id ON reception(animal_id);
    CREATE INDEX IF NOT EXISTS doctor_id ON reception(doctor_id);
    
    ');

    PERFORM dblink_exec('connection', '
    CREATE OR REPLACE FUNCTION counter_function()
    RETURNS trigger AS
    $$
    BEGIN
        UPDATE client SET receptions_number = receptions_number + 1
        WHERE client.id = 
        ANY (SELECT owner_id from animal WHERE animal.id = NEW.animal_id);
    
        UPDATE animal SET receptions_number = receptions_number + 1
        WHERE animal.id = NEW.animal_id;
        
        UPDATE doctor SET receptions_number = receptions_number + 1
        WHERE doctor.id = NEW.doctor_id;
        
        RETURN NEW;	
    END;
    $$
    LANGUAGE ''plpgsql'';

    CREATE OR REPLACE TRIGGER reception_number 
    AFTER INSERT
    ON reception
    FOR EACH ROW
    EXECUTE PROCEDURE counter_function();
    ');

    PERFORM dblink_exec('connection', '
    CREATE OR REPLACE FUNCTION insert_client(
    new_phone_number numeric(10),
    new_surname text,
    new_name text,
    new_patronymic text)
    RETURNS text AS
    $$
    BEGIN
    IF EXISTS (SELECT 1 FROM client WHERE phone_number = new_phone_number) THEN
        RETURN ''User already exists'';
    ELSE
        INSERT INTO client (phone_number, surname, name, patronymic)
        VALUES (new_phone_number, new_surname, new_name, new_patronymic);
        RETURN ''Successfully'';
    END IF;
    END;
    $$ LANGUAGE plpgsql;

    CREATE OR REPLACE FUNCTION insert_animal(
    new_owner_id integer,
    new_nickname text,
    new_gender varchar(6),
    new_age numeric(2),
    new_type text,
    new_breed text,
    new_color text)
    RETURNS text AS
    $$
    BEGIN
    IF EXISTS (SELECT 1 FROM client WHERE id = new_owner_id) THEN
        INSERT INTO animal
        (owner_id, nickname, gender, age, type, breed, color)
        VALUES 
        (new_owner_id, new_nickname, new_gender, new_age, new_type, new_breed, new_color);
        RETURN ''Successfully'';
    ELSE
        RETURN ''Owner does not exist'';
    END IF;
    END;
    $$ LANGUAGE plpgsql;
    
    CREATE OR REPLACE FUNCTION insert_doctor(
    new_phone_number numeric(10),
    new_surname text,
    new_name text,
    new_patronymic text,
    new_qualification text,
    new_password text)
    RETURNS text AS
    $$
    BEGIN
    IF EXISTS (SELECT 1 FROM doctor WHERE phone_number = new_phone_number) THEN
        RETURN ''Doctor already exists'';
    ELSE
        INSERT INTO doctor (phone_number, surname, name, patronymic, qualification, password)
        VALUES (new_phone_number, new_surname, new_name, new_patronymic, new_qualification,
        new_password);
        RETURN ''Successfully'';
    END IF;
    END;
    $$ LANGUAGE plpgsql;

    CREATE OR REPLACE FUNCTION insert_reception(
    new_animal_id integer,
    new_doctor_id integer,
    new_date date,
    new_time time,
    new_description text,
    new_research text,
    new_diagnosis text,
    new_recommendations text)
    RETURNS text AS
    $$
    BEGIN
    IF EXISTS (SELECT 1 FROM doctor WHERE doctor.id = new_doctor_id) THEN
        IF EXISTS (SELECT 1 FROM animal WHERE animal.id = new_animal_id) THEN
            INSERT INTO reception (animal_id, doctor_id, date, time, 
            description, research, diagnosis, recommendations)
            VALUES (new_animal_id, new_doctor_id, new_date, new_time, new_description, 
            new_research, new_diagnosis, new_recommendations);
            RETURN ''Successfully'';
        ELSE
            RETURN ''Animal does not exist'';
    END IF;
    ELSE
        RETURN ''Doctor does not exist'';
    END IF;
    END;
    $$ LANGUAGE plpgsql;
    ');

    PERFORM dblink_exec('connection', '
    CREATE OR REPLACE FUNCTION get_all_clients()
    RETURNS SETOF client
    AS $$
    SELECT * FROM client;
    $$ LANGUAGE SQL; 


    CREATE OR REPLACE FUNCTION get_animals(check_id integer)
    RETURNS SETOF animal
    AS $$
    SELECT * FROM animal WHERE owner_id = check_id;
    $$ LANGUAGE SQL;


    CREATE OR REPLACE FUNCTION get_animal_receptions(check_id integer)
    RETURNS TABLE(
    reception_id integer,
    reception_animal_id integer,
    reception_doctor_id integer,
    reception_date date,
    reception_time time,
    reception_description text,
    reception_research text,
    reception_diagnosis text,
    reception_recommendations text,

    doctor_phone_number numeric(10),
    doctor_id integer,
    doctor_surname text,
    doctor_name text,
    doctor_patronymic text,
    doctor_qualification text,
    doctor_receptions_number integer,
    doctor_password text
    )
    AS $$
    SELECT * FROM reception JOIN doctor ON reception.doctor_id = doctor.id 
    WHERE reception.animal_id=check_id ORDER BY reception.id DESC;
    $$ LANGUAGE SQL; 


    CREATE OR REPLACE FUNCTION get_reception(check_id integer)
    RETURNS TABLE (
    client_phone_number numeric(10),
    client_id integer,
    client_surname text,
    client_name text,
    client_patronymic text,
    client_receptions_number integer,
    
    animal_id integer,
    animal_owner_id numeric(10),
    animal_nickname text,
    animal_gender varchar(6),
    animal_age numeric(2),
    animal_type text,
    animal_breed text,
    animal_color text,
    animal_receptions_number integer,
    
    reception_id integer,
    reception_animal_id integer,
    reception_doctor_id integer,
    reception_date date,
    reception_time time,
    reception_description text,
    reception_research text,
    reception_diagnosis text,
    reception_recommendations text,
    
    doctor_phone_number numeric(10),
    doctor_id integer,
    doctor_surname text,
    doctor_name text,
    doctor_patronymic text,
    doctor_qualification text,
    doctor_receptions_number integer,
    doctor_password text
    )
    AS $$
    SELECT * FROM client JOIN animal on client.id=animal.owner_id JOIN reception on
    animal.id = reception.animal_id JOIN doctor on reception.doctor_id = doctor.id WHERE reception.id = check_id;
    $$ LANGUAGE SQL;

    CREATE OR REPLACE FUNCTION get_doctor(check_number numeric(10))
    RETURNS TABLE(
    phone_number numeric(10),
    id integer,
    surname text,
    name text,
    patronymic text,
    qualification text,
    receptions_number integer,
    password text
    )
    AS $$
    SELECT * FROM doctor WHERE doctor.phone_number=check_number;
    $$ LANGUAGE SQL;


    CREATE OR REPLACE FUNCTION get_doctor_receptions(check_id integer)
    RETURNS TABLE (
    client_phone_number numeric(10),
    client_id integer,
    client_surname text,
    client_name text,
    client_patronymic text,
    client_receptions_number integer,

    animal_id integer,
    animal_owner_id numeric(10),
    animal_nickname text,
    animal_gender varchar(6),
    animal_age numeric(2),
    animal_type text,
    animal_breed text,
    animal_color text,
    animal_receptions_number integer,

    reception_id integer,
    reception_animal_id integer,
    reception_doctor_id integer,
    reception_date date,
    reception_time time,
    reception_description text,
    reception_research text,
    reception_diagnosis text,
    reception_recommendations text
    )
    AS $$
    SELECT * FROM client JOIN animal on client.id=animal.owner_id JOIN reception on
    animal.id = reception.animal_id 
    WHERE reception.doctor_id=check_id ORDER BY reception.id DESC;
    $$ LANGUAGE SQL;   

    ');

    PERFORM dblink_exec('connection', '
    
    CREATE OR REPLACE FUNCTION get_by_last_name(to_find text)
    RETURNS SETOF client
    AS $$
    SELECT * FROM client WHERE surname LIKE to_find || ''%'';
    $$ LANGUAGE SQL;

    CREATE OR REPLACE FUNCTION get_client(check_id integer)
    RETURNS SETOF client
    AS $$
    SELECT * FROM client WHERE id=check_id;
    $$ LANGUAGE SQL;
    
    CREATE OR REPLACE FUNCTION get_all_doctors()
    RETURNS SETOF doctor
    AS $$
    SELECT * FROM doctor;
    $$ LANGUAGE SQL;

    ');

    PERFORM dblink_exec('connection', '
    
    CREATE OR REPLACE PROCEDURE update_doctor_info(
    check_id integer,
    new_surname text,
    new_name text,
    new_patronymic text,
    new_qualification text)
    AS $$
    UPDATE doctor SET 
    surname = new_surname,
    name = new_name,
    patronymic = new_patronymic,
    qualification = new_qualification
    WHERE id = check_id;
    $$ LANGUAGE SQL;
    
    ');

    PERFORM dblink_exec('connection', '
    
    CREATE OR REPLACE PROCEDURE delete_all_clients()
    AS $$
    DELETE FROM client;
    $$ LANGUAGE SQL;

    CREATE OR REPLACE PROCEDURE delete_client(check_id integer)
    AS $$
    DELETE FROM client WHERE id = check_id;
    $$ LANGUAGE SQL;
    
    ');

    PERFORM dblink_exec('connection', 'COMMIT');
    PERFORM dblink_disconnect('connection');

END IF;
END;
$func$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION f_delete_db(dbname text, usr text, passwd text)
RETURNS void AS
$$
BEGIN

PERFORM pg_terminate_backend(pg_stat_activity.pid)
    FROM pg_stat_activity
    WHERE pg_stat_activity.datname = dbname
    AND pid <> pg_backend_pid();

IF EXISTS (SELECT 1 FROM pg_database WHERE datname = dbname) THEN
    PERFORM dblink_exec('dbname=' || current_database() || ' user=' || usr || ' password=' || passwd,
    'DROP DATABASE ' || quote_ident(dbname));
ELSE
    RAISE NOTICE 'Database does not exist';
END IF;
END;
$$ LANGUAGE plpgsql;

