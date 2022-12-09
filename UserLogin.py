from db import *


class UserLogin():
    def fromDB(self, user_phone, database: ALM):
        self.__user = database.get_doctor(user_phone)
        return self

    def create(self, user):
        self.__user = user
        return self

    def if_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.__user['id'])
