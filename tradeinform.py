tradein_count = 0


class Tradeinform:

    def __init__(self):
        global tradein_count
        tradein_count += 1
        self.__trade_id = tradein_count

    def set_tradein_id(self, trade_id):
        self.__trade_id = trade_id

    def get_tradein_id(self):
        return self.__trade_id
