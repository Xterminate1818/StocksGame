import mechanicalsoup
import getpass
from picker import StockAnalyzer


class TradingBot(mechanicalsoup.StatefulBrowser):
    def __init__(self):
        super().__init__(user_agent="Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:47.0) Gecko/20100101 Firefox/47.0")
        self.logged_in = False
        self.commands = {
            "quit": quit,
            "login": self.login,
            "buy": self.buy,
            "info": self.info,
            "autobuy": self.autobuy
        }
        self.analyzer = StockAnalyzer()

    def interpret_command(self, cmd):
        if cmd not in self.commands.keys():
            print("Invalid command " + cmd + ", type help for more info")
            return
        return self.commands[cmd]()

    def login(self, _username="", _password=""):
        # Navigate to login page
        self.open("https://www.howthemarketworks.com/login")
        # Get login info
        if _username == "":
            _username = input("Username: ")
        if _password == "":
            _password = getpass.getpass(prompt="Password: ")
        # Submit form and get result
        self.select_form('form[action="/login"]')
        self.__setitem__("UserName", _username)
        self.__setitem__("Password", _password)
        result = self.submit_selected()

        self.logged_in = result.ok and self.url == "https://www.howthemarketworks.com/accounting/dashboard"
        if self.logged_in:
            print("Log-in successful")
        else:
            print("Log-in failed")
        return result

    def buy(self, symbol="", quantity="", t="", stop=0):
        if not self.logged_in:
            print("Not logged in")
            return None
        stop = float(stop)

        if symbol == "":
            symbol = input("Stock Symbol: ")
        if quantity == "":
            quantity = input("Quantity: ")
        if t == "":
            trailing = input("Make order trailing stop? Y/N - ")
            if trailing:
                t = "Trailing Stop %"
                stop = input("What percent of price to stop? __/100 - ")
            else:
                t = "Market"

        self.open("https://www.howthemarketworks.com/trading/equities")
        self.select_form()
        self.__setitem__("Symbol", symbol)
        self.__setitem__("Quantity", quantity)
        self.__setitem__("OrderType", t)
        if t == "Trailing Stop %":
            self.__setitem__("Price", stop)
        result = self.submit_selected()
        if result.ok:
            print("Successfully bought " + str(quantity) + " shares of " + symbol + " with type " + t)
        else:
            print("Failed to purchase " + symbol + ". Check that the symbol is correct and funds are sufficient")
        return result

    def info(self):
        if not self.logged_in:
            print("Not logged in")
            return None
        self.open("https://www.howthemarketworks.com/accounting/accountbalance")
        self.launch_browser()

    def autobuy(self, budget=0):
        if budget == 0:
            budget = input("Budget for autobuy: ")
        print("Analyzing market, this may take time")
        stocks = self.analyzer.recommend_buy(budget)
        total = stocks.total()
        symbols = []
        print("The following stocks have been selected:")
        for s in range(stocks.count()):
            symbols.append(stocks.symbol[s])
            print(stocks.name[s] + " (" + stocks.symbol[s] + ") ---- " + str(stocks.amount[s]) +
                  " share(s) totalling: $" + str(round(stocks.amount[s] * stocks.price[s], 2)))
        print("Purchase will total $" + str(round(total, 2)))
        order_type = "Market"
        percent = 0
        trailing = input("Add trailing stop? Y/N - ")
        if trailing.lower() == "y":
            order_type = "Trailing Stop %"
            percent = input("What percent to put the stop? __/100 - ")
        print("Make sure you have sufficient funds before continuing")
        decision = input("Finalize purchase? Y/N - ")
        if decision.lower() != "y":
            print("Cancelled order")
            return
        for s in range(stocks.count()):
            if order_type == "Market":
                self.buy(stocks.symbol[s], str(stocks.amount[s]), order_type)
            else:
                self.buy(stocks.symbol[s], str(stocks.amount[s]), order_type, percent)


if __name__ == "__main__":
    ana = StockAnalyzer()
    stonks = ana.recommend_buy(999999)
    print(stonks)
