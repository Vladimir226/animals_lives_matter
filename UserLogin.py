from db import *


class UserLogin():
    def fromDB(self, phone_number):
        self.__user = phone_number
        return self

    def create(self, phone_number):
        self.__user = phone_number
        return self

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.__user

