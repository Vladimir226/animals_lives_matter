import unittest
from db import ALM

class TestSQLParser(unittest.TestCase):
    def test_parser(self):
        test = '(17,4,Пушок,male,1,Хомяковые,Сирийский,"Рыжий",0)'
        answer = ['17', '4', 'Пушок', 'male', '1', 'Хомяковые', 'Сирийский', 'Рыжий', '0']
        self.assertEqual(ALM.sql_parser(test), answer)
        
        test = '(18,4,Омега,female,1,Свинья,"Карликовая домашняя",Белая,0)'
        answer = ['18', '4', 'Омега', 'female', '1', 'Свинья', 'Карликовая домашняя', 'Белая', '0']
        self.assertEqual(ALM.sql_parser(test), answer)

        test = '(0,1,Супер,Доктор,,Профессор,4)'
        answer = ['0', '1', 'Супер', 'Доктор','', 'Профессор', '4']
        self.assertEqual(ALM.sql_parser(test), answer)

        test = '(37,13,1,2023-06-21,04:27:00,,,,,0,1,,Доктор,)'
        answer = ['37', '13', '1', '2023-06-21', '04:27:00' , '', '', '', '', '0', '1', '', 'Доктор', '']
        self.assertEqual(ALM.sql_parser(test), answer)

class TestSQLQuery(unittest.TestCase):
    def test_query(self):
        database = ALM("usr", "123456", "localhost", "5432")
        
        test = database.get_client(1)
        del test['receptions_number']
        answer = {'phone_number': 9990000001, 'id': '1', 'surname': 'Петров', 'name': 'Петр', 'patronymic': 'Петрович'}
        self.assertEqual(test, answer)

        test = database.get_client(2)
        del test['receptions_number']
        answer = {'phone_number': 9990000002, 'id': '2', 'surname': 'Иванов', 'name': 'Петр', 'patronymic': 'Петрович'}
        self.assertEqual(test, answer)

        test = database.get_client(3)
        del test['receptions_number']
        answer = {'phone_number': 9990000003, 'id': '3', 'surname': 'Иванов', 'name': 'Петр', 'patronymic': 'Петрович'}
        self.assertEqual(test, answer)

        test = database.get_doctor(8000000003)
        del test['receptions_number']
        del test['password']
        answer = {'phone_number': '8000000003', 'id': '4', 'surname': 'Орлов', 'name': 'Александр', 'patronymic': 'Вячеславович', 'qualification': 'Хирург'}
        self.assertEqual(test, answer)

        test = database.get_doctor(8000000001)
        del test['receptions_number']
        del test['password']
        answer = {'phone_number': '8000000001', 'id': '2', 'surname': 'Лебедев', 'name': 'Аркадий', 'patronymic': 'Иванович', 'qualification': 'Терапевт'}
        self.assertEqual(test, answer)

        test = database.get_doctor(8000000002)
        del test['receptions_number']
        del test['password']
        answer = {'phone_number': '8000000002', 'id': '3', 'surname': 'Попов', 'name': 'Василий', 'patronymic': 'Михайлович', 'qualification': 'Терапевт'}
        self.assertEqual(test, answer)

unittest.main()