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
        self.status = False
        self.start_connection()

    def start_connection(self):
        self.engine = create_engine(f"postgresql+psycopg2://{self.user}:{self.password}@{self.ip}:{self.port}/postgres")
        self.cursor = self.engine.connect()

        self.create_db()

        self.cursor.close()
        self.engine.dispose()

        self.engine = create_engine(
            f"postgresql+psycopg2://{self.user}:{self.password}@{self.ip}:{self.port}/{self.dbname}")
        self.cursor = self.engine.connect()

        self.status = True
        self.insert_doctor('0000000000', 'Профессор', 'xxx', 'Супер', 'Доктор')

    def check_connection(self):
        if not self.status:
            self.start_connection()

    def create_db(self):
        query_create = f"""
        SELECT f_create_db('{self.dbname}, {self.user}, {self.password}');
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

    def insert_client(self, phone_number, surname, name, patronymic=''):
        self.check_connection()
        patronymic = self.processing_null(patronymic)
        query_create = f"""
        BEGIN;
        SELECT insert_client({phone_number}, '{surname}', '{name}', {patronymic});
        """
        result = self.cursor.execute(query_create)
        return self.insert_end(result)

    def insert_animal(self, owner_id, nickname, gender, age, type, breed='', color=''):
        self.check_connection()
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
        self.check_connection()
        patronymic = self.processing_null(patronymic)
        query_create = f"""
        BEGIN;
        SELECT insert_doctor({phone_number}, '{surname}', '{name}', {patronymic}, '{qualification}', '{generate_password_hash(password)}');
        """
        result = self.cursor.execute(query_create)
        return self.insert_end(result)

    def insert_reception(self, animal_id, doctor_id, date, time, description='', research='', diagnosis='',
                         recommendations=''):
        self.check_connection()
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
                res[i] = ''
        return res

    def get_client(self, check_id):
        self.check_connection()
        query_create = f"""
        SELECT get_client({check_id});
        """
        result = self.cursor.execute(query_create)
        clients = []
        for i, x in enumerate(result):
            data = self.sql_parser(x[0])
            clients.append(dict(zip(self.client_field, data)))
            clients[i]['phone_number'] = int(clients[i]['phone_number'])
            clients[i]['receptions_number'] = int(clients[i]['receptions_number'])
        return clients[0]

    def get_all_clients(self):
        self.check_connection()
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
        self.check_connection()
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
        self.check_connection()
        query_create = f"""
        SELECT get_animal_receptions({id});
        """
        result = self.cursor.execute(query_create)
        receptions = []
        for i, x in enumerate(result):
            data = self.sql_parser(x[0])
            reception = {}
            reception['reception'] = dict(zip(self.reception_field, data[0:9]))
            reception['doctor'] = dict(zip(self.doctor_field, data[9:17]))
            receptions.append(reception)
        return receptions

    def get_reception(self, id):
        self.check_connection()
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
        self.check_connection()
        query_create = f"""
        SELECT get_doctor({phone_number});
        """
        result = self.cursor.execute(query_create)
        doctor = {}
        for i, x in enumerate(result):
            data = self.sql_parser(x[0])
            doctor = dict(zip(self.doctor_field, data))
        return doctor

    def update_doctor_info(self, id, surname, name, patronymic, qualification):
        self.check_connection()
        query_create = f"""
        BEGIN;
        call update_doctor_info({id}, '{surname}', '{name}', '{patronymic}', '{qualification}');
        COMMIT;
        """
        self.cursor.execute(query_create)

    def get_doctor_receptions(self, id):
        self.check_connection()
        query_create = f"""
        SELECT get_doctor_receptions({id});
        """
        result = self.cursor.execute(query_create)
        receptions = []
        for i, x in enumerate(result):
            data = self.sql_parser(x[0])
            reception = {}
            reception['client'] = dict(zip(self.client_field, data[0:6]))
            reception['animal'] = dict(zip(self.animal_field, data[6:15]))
            reception['reception'] = dict(zip(self.reception_field, data[15:24]))
            receptions.append(reception)
        return receptions

    def get_by_last_name(self, to_find):
        self.check_connection()
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

    def delete_all_clients(self):
        self.check_connection()
        query_create = f"""
        BEGIN;
        call delete_all_clients();
        COMMIT;
        """
        self.cursor.execute(query_create)

    def delete_client(self, id):
        self.check_connection()
        query_create = f"""
        BEGIN;
        call delete_client({id});
        COMMIT;
        """
        self.cursor.execute(query_create)

    def get_all_doctors(self):
        self.check_connection()
        query_create = f"""
        SELECT get_all_doctors();
        """
        result = self.cursor.execute(query_create)
        doctor = []
        for i, x in enumerate(result):
            data = self.sql_parser(x[0])
            doctor.append(dict(zip(self.doctor_field, data)))
        return doctor

    def delete_database(self):

        self.cursor.close()
        self.engine.dispose()

        self.engine = create_engine(f"postgresql+psycopg2://{self.user}:{self.password}@{self.ip}:{self.port}/postgres")
        self.cursor = self.engine.connect()

        query_create = f"""
        SELECT f_delete_db('{self.dbname}, {self.user}, {self.password}');
        """
        self.cursor.execute(query_create)

        self.cursor.close()
        self.engine.dispose()
        self.status = False
