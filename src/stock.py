class StockList:
    def __init__(self):
        self.symbol = []
        self.name = []
        self.price = []
        self.change_absolute = []
        self.change_relative = []
        self.market_cap = []
        self.amount = []
        self.prediction = []

    def sanity_check(self):
        # debug
        assert len(self.symbol) == len(self.name)
        assert len(self.name) == len(self.price)
        assert len(self.price) == len(self.change_absolute)
        assert len(self.change_absolute) == len(self.change_relative)
        assert len(self.change_relative) == len(self.market_cap)
        assert len(self.market_cap) == len(self.amount)
        assert len(self.amount) == len(self.prediction)

    def count(self):
        self.sanity_check()
        return len(self.symbol)

    def total(self):
        total = 0
        for i in range(self.count()):
            total += self.price[i] * self.amount[i]
        return total

    def add_stock(self, data, allow_duplicates=True):
        dupe = data[0] in self.symbol
        if dupe and not allow_duplicates:
            index = self.symbol.index(data[0])
            self.amount[index] += int(data[6])
            return
        self.symbol += [str(data[0])]
        self.name += [str(data[1])]
        self.price += [float(data[2])]
        self.change_absolute += [str(data[3])]
        self.change_relative += [str(data[4])]
        self.market_cap += [str(data[5])]
        self.amount += [int(data[6])]
        self.prediction += [str(data[7])]
        self.sanity_check()

    def concat(self, stocks, allow_duplicates=True):
        for i in range(stocks.count()):
            self.add_stock(stocks.get_stock(i), allow_duplicates)

    def remove_stock(self, index):
        if self.count() <= index:
            print("Out of range")
            return
        self.symbol.pop(index)
        self.name.pop(index)
        self.price.pop(index)
        self.change_absolute.pop(index)
        self.change_relative.pop(index)
        self.market_cap.pop(index)
        self.amount.pop(index)
        self.prediction.pop(index)

    def get_stock(self, index):
        return [
            self.symbol[index],
            self.name[index],
            self.price[index],
            self.change_absolute[index],
            self.change_relative[index],
            self.market_cap[index],
            self.amount[index],
            self.prediction[index]
        ]

    def most_expensive(self):
        index = 0
        highest = 0
        for i in range(self.count()):
            if self.price[i] >= highest:
                index = i
                highest = self.price[i]
        return index

    def least_expensive(self):
        smallest = 9999999999
        index = 0
        for s in range(self.count()):
            if self.price[s] <= smallest:
                smallest = self.price[s]
                index = s
        return index

    def budget(self, budget):
        total = self.total()
        while total > budget:
            i = self.most_expensive()
            self.remove_stock(i)
            total = self.total()
        print(self.name)
        if self.count() == 0:
            print("No stocks found")
            return
        while total + self.price[self.least_expensive()] < budget:
            for stock in range(self.count()):
                if total + self.price[stock] <= budget:
                    self.amount[stock] += 1
                    total = self.total()

    def keep_recommended(self):
        i = 0
        size = self.count()
        while i < size:
            while i < size and self.prediction[i] != "up":
                self.remove_stock(i)
                size = self.count()
            i += 1

