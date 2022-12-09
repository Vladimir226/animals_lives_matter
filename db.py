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
        # self.set_select_functions()

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
        phone_number numeric(10) PRIMARY KEY,
        id serial NOT NULL UNIQUE,
        surname text NOT NULL,
        name text NOT NULL,
        patronymic text,
        qualification text NOT NULL,
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
        CREATE OR REPLACE FUNCTION insert_client(
        new_phone_number numeric(10),
        new_surname text,
        new_name text,
        new_patronymic text)
        RETURNS text AS
        $func$
        BEGIN
        IF EXISTS (SELECT 1 FROM client WHERE phone_number = new_phone_number) THEN
           RETURN 'User already exists';
        ELSE
           INSERT INTO client (phone_number, surname, name, patronymic)
           VALUES (new_phone_number, new_surname, new_name, new_patronymic);
           RETURN 'Successfully';
        END IF;
        END
        $func$ LANGUAGE plpgsql;
        """
        self.cursor.execute(query_create)

        query_create = """
        CREATE OR REPLACE FUNCTION insert_animal(
        new_owner_phone_number numeric(10),
        new_nickname text,
        new_gender varchar(6),
        new_age numeric(2),
        new_type text,
        new_breed text,
        new_color text)
        RETURNS text AS
        $func$
        BEGIN
        IF EXISTS (SELECT 1 FROM client WHERE phone_number = new_owner_phone_number) THEN
           INSERT INTO animal
           (owner_phone_number, nickname, gender, age, type, breed, color)
           VALUES 
           (new_owner_phone_number, new_nickname, new_gender, new_age, new_type, new_breed, new_color);
           RETURN 'Successfully';
        ELSE
           RETURN 'Owner does not exist';
        END IF;
        END
        $func$ LANGUAGE plpgsql;
        """
        self.cursor.execute(query_create)

        query_create = """
        CREATE OR REPLACE FUNCTION insert_doctor(
        new_phone_number numeric(10),
        new_surname text,
        new_name text,
        new_patronymic text,
        new_qualification text,
        new_password text)
        RETURNS text AS
        $func$
        BEGIN
        IF EXISTS (SELECT 1 FROM doctor WHERE phone_number = new_phone_number) THEN
            RETURN 'Doctor already exists';
        ELSE
            INSERT INTO doctor (phone_number, surname, name, patronymic, qualification, password)
            VALUES (new_phone_number, new_surname, new_name, new_patronymic, new_qualification,
            new_password);
            RETURN 'Successfully';
        END IF;
        END
        $func$ LANGUAGE plpgsql;
        """
        self.cursor.execute(query_create)

        query_create = """
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
        $func$
        BEGIN
        IF EXISTS (SELECT 1 FROM doctor WHERE doctor.id = new_doctor_id) THEN
            IF EXISTS (SELECT 1 FROM animal WHERE animal.id = new_animal_id) THEN
                INSERT INTO reception (animal_id, doctor_id, date, time, 
                description, research, diagnosis, recommendations)
                VALUES (new_animal_id, new_doctor_id, new_date, new_time, new_description, 
                new_research, new_diagnosis, new_recommendations);
                RETURN 'Successfully';
            ELSE
                RETURN 'Animal does not exist';
        END IF;
        ELSE
            RETURN 'Doctor does not exist';
        END IF;
        END
        $func$ LANGUAGE plpgsql;
        """
        self.cursor.execute(query_create)

    def insert_end(self, result):
        for i in result:
            result = i
            break
        if result[0] == 'Successfully':
            self.cursor.execute('COMMIT;')
        else:
            self.cursor.execute('ROLLBACK;')
        return result[0]

    def processing_null(self, string):
        if string == '':
            return 'NULL'
        else:
            return f"'{string}'"

    def insert_user(self, phone_number, surname, name, patronymic=''):
        patronymic = self.processing_null(patronymic)
        query_create = f"""
        BEGIN;
        SELECT insert_client({phone_number}, '{surname}', '{name}', {patronymic});
        """
        result = self.cursor.execute(query_create)
        return self.insert_end(result)

    def insert_animal(self, owner_phone_number, nickname, gender, age, type, breed='', color=''):
        breed = self.processing_null(breed)
        color = self.processing_null(color)
        if gender not in ['male', 'female']:
            return 'Incorrect gender (select male or female)'
        query_create = f"""
        BEGIN;
        SELECT insert_animal({owner_phone_number}, '{nickname}', '{gender}', {age}, '{type}', {breed}, {color});
        """
        result = self.cursor.execute(query_create)
        return self.insert_end(result)

    def insert_doctor(self, phone_number, qualification, password, surname, name, patronymic=''):
        patronymic = self.processing_null(patronymic)
        query_create = f"""
        BEGIN;
        SELECT insert_doctor({phone_number}, '{surname}', '{name}', {patronymic}, '{qualification}', '{password}');
        """
        result = self.cursor.execute(query_create)
        return self.insert_end(result)

    def insert_reception(self, animal_id, doctor_id, date, time, description='', research='', diagnosis='',
                         recommendations=''):
        description = self.processing_null(description)
        research = self.processing_null(research)
        diagnosis = self.processing_null(diagnosis)
        recommendations = self.processing_null(recommendations)
        query_create = f"""
        BEGIN;
        SELECT insert_reception({animal_id}, {doctor_id}, '{date}', '{time}', 
        {description}, {research}, {diagnosis}, {recommendations});
        """
        result = self.cursor.execute(query_create)
        return self.insert_end(result)

    # ПЕРЕДЕЛАТЬ ЧЕРЕЗ ПРОЦЕДУРЫ
    def get_all_clients(self):
        query_create = """
        SELECT * FROM client;
        """
        result = self.cursor.execute(query_create)
        clients = []
        for i in result:
            clients.append(dict(i))
        return clients

    # ПЕРЕДЕЛАТЬ ЧЕРЕЗ ПРОЦЕДУРЫ
    def get_animals(self, phone_number):
        query_create = f"""
        SELECT * FROM animal WHERE owner_phone_number = {phone_number};
        """
        result = self.cursor.execute(query_create)
        animals = []
        for i in result:
            animals.append(dict(i))
        return animals

    # ПЕРЕДЕЛАТЬ ЧЕРЕЗ ПРОЦЕДУРЫ
    def get_animal_receptions(self, id):
        query_create = f"""
        SELECT * FROM reception WHERE animal_id={id};
        """
        result = self.cursor.execute(query_create)
        receptions = []
        for i in result:
            receptions.append(dict(i))
        return receptions

    # ПЕРЕДЕЛАТЬ ЧЕРЕЗ ПРОЦЕДУРЫ
    def get_reception(self, id):
        query_create = f"""
        SELECT * FROM client JOIN animal on client.phone_number=animal.owner_phone_number JOIN reception on
        animal.id = reception.animal_id JOIN doctor on reception.doctor_id = doctor.id WHERE reception.id = {id};
        """
        result = self.cursor.execute(query_create)
        receptions = {}
        for i in result:
            receptions['client'] = dict(
                zip(['phone_number', 'surname', 'name', 'patronymic', 'receptions_number'], i[:6]))
            receptions['animal'] = dict(
                zip(['owner_phone_number', 'nickname', 'gender', 'age', 'type', 'breed', 'color', 'photo', 'receptions_number'], i[6:15]))
            receptions['reception'] = dict(zip(['id', 'animal_id', 'doctor_id', 'date', 'time',
                                                'description', 'research', 'diagnosis', 'recommendations'], i[15:24]))
            receptions['doctor'] = dict(
                zip(['phone_number', 'id', 'surname', 'name', 'patronymic', 'qualification', 'receptions_number', 'password', 'photo'], i[24:]))
            print(i[:5], i[5:15])

        return receptions


# db = ALM("postgres", "123456", "localhost", "5432")
# print(db.insert_user(9998886600, 'Петров', 'Петр', 'Петрович'))
# print(db.insert_user(9998886601, 'Иванов', 'Петр', 'Петрович'))
# print(db.insert_animal(9998886600, 'Тузик', 'male', 3, 'Собака', 'Дворняга', 'Черный'))
# print(db.insert_animal(9998886600, 'Барсик', 'male', 2, 'Кот', '', 'Рыжий'))
# print(db.insert_animal(9998886601, 'Рекс', 'male', 1, 'Собака', 'Такса'))
# print(db.insert_doctor(8005553535, 'Терапевт', 'xxx', 'Мартыненко', 'Владимир', 'Александрович'))
# print(db.insert_doctor(8005553500, 'Терапевт', 'xxx', 'Сидоров', 'Петр', 'Аркадьевич'))
# print(db.insert_reception(2,1,'2022-12-08','20:30:00'))
# print(db.insert_reception(1,2,'2022-12-08','20:30:00'))
# print(db.insert_reception(1,2,'2022-12-08','20:30:00'))
# print(db.insert_reception(3,1,'2022-12-08','20:30:00'))
# print(db.get_all_clients())
# print(db.get_animals(9998886600))
# print(db.get_animal_receptions(1))
# print(db.get_reception(4))
