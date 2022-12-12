from db import *


class UserLogin():
    def fromDB(self, user_phone, database: ALM):
        self.__user = database.get_doctor(user_phone)
        self.__sessiod_id = database.session_id
        return self

    def create(self, user, session_id):
        self.__user = user
        self.__sessiod_id = session_id
        return self

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.__user['phone_number'])

    def get_session_id(self):
        return self.__sessiod_id
