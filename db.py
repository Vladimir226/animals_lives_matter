from sqlalchemy import create_engine


class ALM:
    def __init__(self, user, password, ip, port, dbname="alm"):
        self.user = user
        self.password = password
        self.ip = ip
        self.port = port
        self.dbname = dbname

        self.engine = create_engine(f"postgresql+psycopg2://{user}:{password}@{ip}:{port}/postgres")
        self.cursor = self.engine.connect()

        self.create_db()

        self.engine = create_engine(f"postgresql+psycopg2://{user}:{password}@{ip}:{port}/{dbname}")
        self.cursor = self.engine.connect()

        self.create_tables()
        self.set_triggers()
        self.set_insert_functions()

    def create_db(self):
        query_create = f"""
        CREATE OR REPLACE FUNCTION f_create_db(dbname text)
        RETURNS void AS
        $func$
        BEGIN
        IF EXISTS (SELECT 1 FROM pg_database WHERE datname = dbname) THEN
           RAISE NOTICE 'Database already exists';
        ELSE
           PERFORM dblink_exec('dbname=' || current_database() || ' user={self.user} password={self.password}',
           'CREATE DATABASE ' || quote_ident(dbname));
        END IF;

        END
        $func$ LANGUAGE plpgsql;
        """
        self.cursor.execute(query_create)

        query_create = f"""
        SELECT f_create_db('{self.dbname}');
        """
        self.cursor.execute(query_create)

    def create_tables(self):
        query_create = """
        CREATE OR REPLACE PROCEDURE create_tables()
        AS $$ 
            CREATE TABLE IF NOT EXISTS client(
            phone_number numeric(10) PRIMARY KEY,
            surname text NOT NULL,
            name text NOT NULL,
            patronymic text,
            receptions_number integer
            DEFAULT 0
            CHECK(receptions_number>=0)
            );

            CREATE TABLE IF NOT EXISTS animal(
            id serial PRIMARY KEY,
            owner_phone_number numeric(10) REFERENCES client(phone_number)
            ON UPDATE CASCADE 
            ON DELETE CASCADE,
            nickname text NOT NULL,
            gender varchar(6) NOT NULL CHECK (gender IN ('male', 'female')),
            age numeric(2) NOT NULL CHECK (age>=0 OR age<=30),
            type text NOT NULL,
            breed text,
            color text,
            photo bytea DEFAULT NULL,
            receptions_number integer
            DEFAULT 0
            CHECK(receptions_number>=0)
            );

            CREATE TABLE IF NOT EXISTS doctor(
            id serial PRIMARY KEY,
            surname text NOT NULL,
            name text NOT NULL,
            patronymic text,
            qualification text NOT NULL,
            phone_number numeric(10) NOT NULL,
            receptions_number integer DEFAULT 0 CHECK(receptions_number>=0),
            password text NOT NULL,
            photo bytea DEFAULT NULL
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
        $$ LANGUAGE SQL;
        """
        self.cursor.execute(query_create)

        query_create = f"""
        call create_tables();
        """
        self.cursor.execute(query_create)

    def set_triggers(self):
        query_create = """
        CREATE OR REPLACE FUNCTION counter_function()
        RETURNS trigger AS
        $$
        BEGIN
            UPDATE client SET receptions_number = receptions_number + 1
            WHERE client.phone_number = 
            ANY (SELECT owner_phone_number from animal WHERE animal.id = NEW.animal_id);
        
            UPDATE animal SET receptions_number = receptions_number + 1
            WHERE animal.id = NEW.animal_id;
            
            UPDATE doctor SET receptions_number = receptions_number + 1
            WHERE doctor.id = NEW.doctor_id;
        
            RETURN NEW;	
        END;
        $$
        LANGUAGE 'plpgsql';
        
        CREATE OR REPLACE TRIGGER reception_number 
        AFTER INSERT
        ON reception
        FOR EACH ROW
        EXECUTE PROCEDURE counter_function();
        """
        self.cursor.execute(query_create)

    def set_insert_functions(self):
        query_create = """
        CREATE OR REPLACE PROCEDURE insert_client(
        new_phone_number numeric(10),
        new_surname text,
        new_name text,
        new_patronymic text)
        AS $$
        INSERT INTO client (phone_number, surname, name, patronymic)
        VALUES (new_phone_number, new_surname, new_name, new_patronymic);
        $$ LANGUAGE sql;
        """
        self.cursor.execute(query_create)

    def insert_user(self, phone_number, surname, name, patronymic=''):
        query_create = f"""
        call insert_client({phone_number}, '{surname}', '{name}', '{patronymic}');
        """
        self.cursor.execute(query_create)

db = ALM("usr", "123456", "localhost", "5432")
# db.insert_user('9991382503', 'Мартыненко', 'Владимир', 'Александрович')
# db.cursor.execute('COMMIT')
# db.insert_user('9991382502', 'Мартыненко', 'Владимир')
# db.cursor.execute('COMMIT')
# db.insert_user('9991382505', '', 'Владимир')




