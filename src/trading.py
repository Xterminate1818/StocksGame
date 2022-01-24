import mechanicalsoup
import getpass
import bs4
import selenium


def _convert_symbol(dec: str):
    mult = 1
    if dec.find("M") != -1:
        mult = 1000000
    elif dec.find("B") != -1:
        mult = 1000000000
    dec = dec.replace("M", "")
    dec = dec.replace("B", "")
    dec = dec.replace(",", "")
    return float(dec) * mult


def _convert_decimal(dec: str):
    dec = dec.replace("%", "")
    return float(dec) / 100


def _sum_total(stocks: list[dict]):
    ret = 0
    for s in stocks:
        ret += s["price"] * s["amount"]
    return ret


def _most_expensive(stocks: list[dict]):
    if len(stocks) == 0:
        return 0
    largest = 0
    index = 0
    for s in range(len(stocks)):
        if stocks[s]["price"] >= largest:
            largest = stocks[s]["price"]
            index = s
    return index


def _least_expensive(stocks: list[dict]):
    if len(stocks) == 0:
        return 0
    smallest = 9999999999
    index = 0
    for s in range(len(stocks)):
        if stocks[s]["price"] <= smallest:
            smallest = stocks[s]["price"]
            index = s
    return index


class StockAnalyzer(mechanicalsoup.StatefulBrowser):
    def __init__(self):
        super().__init__(user_agent="Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:47.0) Gecko/20100101 Firefox/47.0")

    def recommend_buy(self, budget):
        budget = float(budget)
        data = []
        self.open("https://finance.yahoo.com/u/yahoo-finance/watchlists/fiftytwo-wk-low")
        table = self.page.find("table", {"class": "cwl-symbols W(100%)"})
        for item in table.find_all("td"):
            data.append(item.get_text())
        count = len(data) / 9
        companies = []
        cart = []
        for i in range(int(count)):
            start = i * 9
            company = {
                "symbol": data[start + 0],
                "name": data[start + 1],
                "price": float(data[start + 2]),
                "change-absolute": float(data[start + 3]),
                "change-relative": _convert_decimal(data[start + 4]),
                "market-cap": _convert_symbol(data[start + 8]),
                "amount": 1
            }
            if company["price"] >= budget / 2:
                continue
            companies.append(company)
            prediction = self.get_prediction(company["symbol"])
            if prediction == "up":
                cart.append(company)

        total = _sum_total(cart)
        while total > budget:
            i = _most_expensive(cart)
            cart.pop(i)
            total = _sum_total(cart)
        while total + cart[_least_expensive(cart)]["price"] < budget:
            for stock in cart:
                if total + stock["price"] <= budget:
                    stock["amount"] += 1
                    total = _sum_total(cart)
        return cart

    def get_prediction(self, symbol: str):
        status = self.open("https://finance.yahoo.com/quote/" + symbol)
        if not status.ok:
            print("Invalid symbol: " + symbol)
            return "invalid"
        value = self.page.find("div", {"Fw(b) Fl(end)--m Fz(s) C($primaryColor"}).get_text()
        if value == "Near Fair Value":
            return "same"
        if value == "Overvalued":
            return "down"
        if value == "Undervalued":
            return "up"


class TradingBot(mechanicalsoup.StatefulBrowser):
    def __init__(self):
        super().__init__(user_agent="Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:47.0) Gecko/20100101 Firefox/47.0")
        self.logged_in = False
        self.commands = {
            "help": self.help,
            "quit": quit,
            "login": self.login,
            "buy": self.buy,
            "info": self.info,
            "autobuy": self.autobuy
        }
        self.analyzer = StockAnalyzer()

    def help(self):
        print("Unimplemented")

    def interpret_command(self, cmd, *args, **kwargs):
        cmd = cmd.lower()
        if cmd not in self.commands.keys():
            print("Invalid command " + cmd + ", type help for more info")
            return
        return self.commands[cmd](*args, **kwargs)

    def login(self, *args, **kwargs):
        # Navigate to login page
        self.open("https://www.howthemarketworks.com/login")
        self.select_form('form[action="/login"]')
        # Get login info
        _username = args[0] if len(args) > 0 else ""
        _password = args[1] if len(args) > 1 else ""
        for key in kwargs.keys():
            key = key.lower()
            if key == "username" or key == "user":
                _username = kwargs[key]
            if key == "password" or key == "pass":
                _password = kwargs[key]
        if _username == "":
            _username = input("Username: ")
        if _password == "":
            _password = getpass.getpass(prompt="Password: ")
        # Submit form and get result
        self.__setitem__("UserName", _username)
        self.__setitem__("Password", _password)
        result = self.submit_selected()
        self.logged_in = result.ok and self.url == "https://www.howthemarketworks.com/accounting/dashboard"
        if self.logged_in:
            print("Log-in successful")
        else:
            print("Log-in failed")
        return result

    def buy(self, *args, **kwargs):
        if not self.logged_in:
            print("Not logged in")
            return None

        symbol = args[0] if len(args) > 0 else ""
        quantity = args[1] if len(args) > 1 else ""
        for key in kwargs.keys():
            key = key.lower()
            if key == "sym" or key == "symbol":
                symbol = kwargs[key]
            if key == "quantity" or key == "q":
                quantity = kwargs[key]

        if symbol == "":
            symbol = input("Stock Symbol: ")
        if quantity == "":
            quantity = input("Quantity: ")

        self.open("https://www.howthemarketworks.com/trading/equities")
        self.select_form()
        self.__setitem__("Symbol", symbol)
        self.__setitem__("Quantity", quantity)
        result = self.submit_selected()
        if result.ok:
            print("Successfully bought " + str(quantity) + " shares of " + symbol)
        else:
            print("Failed to purchase " + symbol + ". Check that the symbol is correct and funds are sufficient")
        return result

    def info(self):
        if not self.logged_in:
            print("Not logged in")
            return None
        self.open("https://www.howthemarketworks.com/accounting/accountbalance")
        self.launch_browser()

    def autobuy(self, budget=1000):
        print("Analyzing market, this may take time")
        stocks = self.analyzer.recommend_buy(budget)
        total = _sum_total(stocks)
        symbols = []
        print("The following stocks have been selected:")
        for s in stocks:
            symbols.append(s["symbol"])
            print(s["name"] + " (" + s["symbol"] + ") ---- " + str(s["amount"]) + " share(s) totalling: $" + str(round(s["amount"] * s["price"], 2)))
        print("Purchase will total $" + str(round(total, 2)))
        print("Make sure you have sufficient funds before continuing")
        decision = input("Finalize purchase? Y/N - ")
        if decision.lower() != "y":
            print("Cancelled order")
            return
        for s in stocks:
            self.buy(s["symbol"], s["amount"])


if __name__ == "__main__":
    ana = StockAnalyzer()
    stonks = ana.recommend_buy(999999)
    print(stonks)
