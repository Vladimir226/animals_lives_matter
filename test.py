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