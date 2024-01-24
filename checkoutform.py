class Checkoutform:

    def __init__(self, block, unitno, street, city, postalcode):
        self.__block = block
        self.__unitno = unitno
        self.__street = street
        self.__city = city
        self.__postalcode = postalcode

    def get_block(self):
        return self.__block

    def get_unitno(self):
        return self.__unitno

    def get_street(self):
        return self.__street

    def get_city(self):
        return self.__city

    def get_postalcode(self):
        return self.__postalcode
