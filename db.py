from sqlalchemy import create_engine
from werkzeug.security import generate_password_hash


class ALM:
    client_field = ['phone_number', 'id', 'surname', 'name', 'patronymic', 'receptions_number']
    animal_field = ['id', 'owner_id', 'nickname', 'gender', 'age', 'type', 'breed', 'color',
                    'receptions_number']
    reception_field = ['id', 'animal_id', 'doctor_id', 'date', 'time', 'description', 'research', 'diagnosis',
                       'recommendations']
    doctor_field = ['phone_number', 'id', 'surname', 'name', 'patronymic', 'qualification', 'receptions_number',
                    'password']

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
        self.set_select_functions()
        self.set_update_function()

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
        
        CREATE INDEX IF NOT EXISTS owner_id ON animal(owner_id);

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
        
        CREATE INDEX IF NOT EXISTS animal_id ON reception(animal_id);
        CREATE INDEX IF NOT EXISTS doctor_id ON reception(doctor_id);
        
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
            WHERE client.id = 
            ANY (SELECT owner_id from animal WHERE animal.id = NEW.animal_id);
        
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
        new_owner_id integer,
        new_nickname text,
        new_gender varchar(6),
        new_age numeric(2),
        new_type text,
        new_breed text,
        new_color text)
        RETURNS text AS
        $func$
        BEGIN
        IF EXISTS (SELECT 1 FROM client WHERE id = new_owner_id) THEN
           INSERT INTO animal
           (owner_id, nickname, gender, age, type, breed, color)
           VALUES 
           (new_owner_id, new_nickname, new_gender, new_age, new_type, new_breed, new_color);
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

    def insert_animal(self, owner_id, nickname, gender, age, type, breed='', color=''):
        breed = self.processing_null(breed)
        color = self.processing_null(color)
        if gender not in ['male', 'female']:
            return 'Incorrect gender (select male or female)'
        query_create = f"""
        BEGIN;
        SELECT insert_animal({owner_id}, '{nickname}', '{gender}', {age}, '{type}', {breed}, {color});
        """
        result = self.cursor.execute(query_create)
        return self.insert_end(result)

    def insert_doctor(self, phone_number, qualification, password, surname, name, patronymic=''):
        patronymic = self.processing_null(patronymic)
        query_create = f"""
        BEGIN;
        SELECT insert_doctor({phone_number}, '{surname}', '{name}', {patronymic}, '{qualification}', '{generate_password_hash(password)}');
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

    @staticmethod
    def sql_parser(str):
        if str[0] == '(':
            str = str[1:]
        if str[-1] == ')':
            str = str[:-1]
        open_quote = 0
        cur_block = 0
        res = [[]]
        for i in range(len(str)):
            if str[i] != '"' and str[i] != ",":
                res[cur_block].append(str[i])
            else:
                if str[i] == ",":
                    if open_quote % 2 == 0:
                        res.append([])
                        cur_block += 1
                    else:
                        res[cur_block].append(str[i])
                if str[i] == '"':
                    res[cur_block].append(str[i])
                    open_quote += 1
        for i in range(len(res)):
            if len(res[i]):
                if res[i][0] == '"':
                    res[i] = res[i][1:]
                if res[i][-1] == '"':
                    res[i] = res[i][:-1]
                res[i] = ''.join(res[i])
                res[i] = res[i].replace('""', '"')
            else:
                res[i] = None
        return res

    def set_select_functions(self):
        query_create = """
        CREATE OR REPLACE FUNCTION get_all_clients()
        RETURNS SETOF client
        AS $$
        SELECT * FROM client;
        $$ LANGUAGE SQL;        
        """
        self.cursor.execute(query_create)

        query_create = """
        CREATE OR REPLACE FUNCTION get_animals(check_id integer)
        RETURNS TABLE(
        id integer,
        owner_id integer,
        nickname text,
        gender varchar(6),
        age numeric(2),
        type text,
        breed text,
        color text,
        receptions_number integer
        )
        AS $$
        SELECT 
        animal.id,
        animal.owner_id,
        animal.nickname,
        animal.gender,
        animal.age,
        animal.type,
        animal.breed,
        animal.color,
        animal.receptions_number
        FROM animal WHERE owner_id = check_id;
        $$ LANGUAGE SQL;        
        """
        self.cursor.execute(query_create)

        query_create = """
        CREATE OR REPLACE FUNCTION get_animal_receptions(check_id integer)
        RETURNS SETOF reception
        AS $$
        SELECT * FROM reception WHERE animal_id=check_id ORDER BY id DESC;
        $$ LANGUAGE SQL;        
        """
        self.cursor.execute(query_create)

        query_create = """
        CREATE OR REPLACE FUNCTION get_reception(check_id integer)
        RETURNS TABLE (
        phone_number1 numeric(10),
        id1 integer,
        surname1 text,
        name1 text,
        patronymic1 text,
        receptions_number1 integer,
        
        id2 integer,
        owner_id2 numeric(10),
        nickname2 text,
        gender2 varchar(6),
        age2 numeric(2),
        type2 text,
        breed2 text,
        color2 text,
        receptions_number2 integer,
        
        id3 integer,
        animal_id3 integer,
        doctor_id3 integer,
        date3 date,
        time3 time,
        description3 text,
        research3 text,
        diagnosis3 text,
        recommendations3 text,
        
        phone_number4 numeric(10),
        id4 integer,
        surname4 text,
        name4 text,
        patronymic4 text,
        qualification4 text,
        receptions_number4 integer,
        password4 text
        )
        AS $$
        SELECT 
        
        client.phone_number,
        client.id,
        client.surname,
        client.name,
        client.patronymic,
        client.receptions_number,
        
        animal.id,
        animal.owner_id,
        animal.nickname,
        animal.gender,
        animal.age,
        animal.type,
        animal.breed,
        animal.color,
        animal.receptions_number,
        
        reception.id,
        reception.animal_id,
        reception.doctor_id,
        reception.date,
        reception.time,
        reception.description,
        reception.research,
        reception.diagnosis,
        reception.recommendations,
        
        doctor.phone_number,
        doctor.id,
        doctor.surname,
        doctor.name,
        doctor.patronymic,
        doctor.qualification,
        doctor.receptions_number,
        doctor.password
        
        FROM client JOIN animal on client.id=animal.owner_id JOIN reception on
        animal.id = reception.animal_id JOIN doctor on reception.doctor_id = doctor.id WHERE reception.id = check_id;
        $$ LANGUAGE SQL;        
        """
        self.cursor.execute(query_create)

        query_create = """
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
        SELECT 
        doctor.phone_number,
        doctor.id,
        doctor.surname,
        doctor.name,
        doctor.patronymic,
        doctor.qualification,
        doctor.receptions_number,
        doctor.password
        FROM doctor WHERE doctor.phone_number=check_number;
        $$ LANGUAGE SQL;        
        """
        self.cursor.execute(query_create)

        query_create = """
        CREATE OR REPLACE FUNCTION get_doctor_receptions(check_id integer)
        RETURNS TABLE (
        phone_number1 numeric(10),
        id1 integer,
        surname1 text,
        name1 text,
        patronymic1 text,
        receptions_number1 integer,

        id2 integer,
        owner_id2 numeric(10),
        nickname2 text,
        gender2 varchar(6),
        age2 numeric(2),
        type2 text,
        breed2 text,
        color2 text,
        receptions_number2 integer,

        id3 integer,
        animal_id3 integer,
        doctor_id3 integer,
        date3 date,
        time3 time,
        description3 text,
        research3 text,
        diagnosis3 text,
        recommendations3 text
        )
        AS $$
        SELECT 

        client.phone_number,
        client.id,
        client.surname,
        client.name,
        client.patronymic,
        client.receptions_number,

        animal.id,
        animal.owner_id,
        animal.nickname,
        animal.gender,
        animal.age,
        animal.type,
        animal.breed,
        animal.color,
        animal.receptions_number,

        reception.id,
        reception.animal_id,
        reception.doctor_id,
        reception.date,
        reception.time,
        reception.description,
        reception.research,
        reception.diagnosis,
        reception.recommendations

        FROM client JOIN animal on client.id=animal.owner_id JOIN reception on
        animal.id = reception.animal_id 
        WHERE reception.doctor_id=check_id ORDER BY reception.id DESC;
        $$ LANGUAGE SQL;        
        """
        self.cursor.execute(query_create)


        query_create = """
        CREATE OR REPLACE FUNCTION get_by_last_name(to_find text)
        RETURNS SETOF client
        AS $$
        SELECT * FROM client WHERE surname LIKE to_find || '%%';
        $$ LANGUAGE SQL;
        """
        self.cursor.execute(query_create)

    def get_all_clients(self):
        query_create = """
        SELECT get_all_clients();
        """
        result = self.cursor.execute(query_create)
        clients = []
        for i, x in enumerate(result):
            data = self.sql_parser(x[0])
            clients.append(dict(zip(self.client_field, data)))
            clients[i]['phone_number'] = int(clients[i]['phone_number'])
            clients[i]['receptions_number'] = int(clients[i]['receptions_number'])
        return clients

    def get_animals(self, id):
        query_create = f"""
        SELECT get_animals({id});
        """
        result = self.cursor.execute(query_create)
        animals = []
        for i, x in enumerate(result):
            data = self.sql_parser(x[0])
            animals.append(dict(zip(self.animal_field, data)))
            animals[i]['id'] = int(animals[i]['id'])
            animals[i]['owner_id'] = int(animals[i]['owner_id'])
            animals[i]['age'] = int(animals[i]['age'])
            animals[i]['receptions_number'] = int(animals[i]['receptions_number'])
        return animals

    def get_animal_receptions(self, id):
        query_create = f"""
        SELECT get_animal_receptions({id});
        """
        result = self.cursor.execute(query_create)
        receptions = []
        for i, x in enumerate(result):
            data = self.sql_parser(x[0])
            receptions.append(dict(zip(self.reception_field, data)))
        return receptions

    def get_reception(self, id):
        query_create = f"""
        SELECT get_reception({id});
        """
        result = self.cursor.execute(query_create)
        reception = {}
        for i, x in enumerate(result):
            data = self.sql_parser(x[0])
            reception['client'] = dict(zip(self.client_field, data[0:6]))
            reception['animal'] = dict(zip(self.animal_field, data[6:15]))
            reception['reception'] = dict(zip(self.reception_field, data[15:24]))
            reception['doctor'] = dict(zip(self.doctor_field, data[24:32]))
        return reception

    def get_doctor(self, phone_number):
        query_create = f"""
        SELECT get_doctor({phone_number});
        """
        result = self.cursor.execute(query_create)
        doctor = {}
        for i, x in enumerate(result):
            data = self.sql_parser(x[0])
            doctor = dict(zip(self.doctor_field, data))
        return doctor

    def set_update_function(self):
        query_create = """
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
        """
        self.cursor.execute(query_create)

    def update_doctor_info(self, id, surname, name, patronymic, qualification):
        query_create = f"""
        BEGIN;
        call update_doctor_info({id}, '{surname}', '{name}', '{patronymic}', '{qualification}');
        COMMIT;
        """
        self.cursor.execute(query_create)

    def get_doctor_receptions(self, id):
        query_create = f"""
                SELECT get_doctor_receptions({id});
                """
        result = self.cursor.execute(query_create)
        receptions = []
        for i, x in enumerate(result):
            data = self.sql_parser(x[0])
            reception={}
            reception['client'] = dict(zip(self.client_field, data[0:6]))
            reception['animal'] = dict(zip(self.animal_field, data[6:15]))
            reception['reception'] = dict(zip(self.reception_field, data[15:24]))
            receptions.append(reception)
        return receptions

    def get_by_last_name(self, to_find):
        query_create = f"""
        SELECT get_by_last_name('{to_find}');
        """
        result = self.cursor.execute(query_create)
        clients = []
        for i, x in enumerate(result):
            data = self.sql_parser(x[0])
            clients.append(dict(zip(self.client_field, data)))
            clients[i]['phone_number'] = int(clients[i]['phone_number'])
            clients[i]['receptions_number'] = int(clients[i]['receptions_number'])
        return clients


db = ALM("postgres", "123456", "localhost", "5432")
# print(db.insert_user(9998886600, 'Петров', 'Петр', 'Петрович'))
# print(db.insert_user(9998886601, 'Иванов', 'Петр', 'Петрович'))
# print(db.insert_user(9998886605, 'Ивановский', 'Петр', 'Петрович'))
# print(db.insert_animal(1, 'Тузик', 'male', 3, 'Собака', 'Дворняга', 'Черный'))
# print(db.insert_animal(2, 'Барсик', 'male', 2, 'Кот', '', 'Рыжий'))
# print(db.insert_animal(2, 'Рекс', 'male', 1, 'Собака', 'Такса'))
# print(db.insert_doctor(8005553535, 'Терапевт', 'xxx', 'Мартыненко', 'Владимир', 'Александрович'))
# print(db.insert_doctor(8005553500, 'Терапевт', 'xxx', 'Сидоров', 'Петр', 'Аркадьевич'))
# print(db.insert_reception(2, 1, '2022-12-08', '20:30:00'))
# print(db.insert_reception(1, 2, '2022-12-08', '20:30:00'))
# print(db.insert_reception(1, 2, '2022-12-08', '20:30:00'))
# print(db.insert_reception(3, 1, '2022-12-08', '20:30:00'))
# print(db.get_all_clients())
# print(db.get_animals(1))
# print(db.get_animal_receptions(1))
# print(db.get_reception(4))
# print(db.get_doctor(8005553500))
# print(db.get_doctor_receptions(1))
# print(db.get_by_last_name('Иванов'))
# print(db.get_doctor_receptions(2))
