class Tradeinform:
    tradein_count = 0

    def __init__(self):
        Tradeinform.tradein_count += 1
        self.__trade_id = Tradeinform.tradein_count

    def set_tradein_id(self, trade_id):
        self.__trade_id = trade_id

    def get_tradein_id(self):
        return self.__trade_id
