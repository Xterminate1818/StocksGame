import mechanicalsoup
from stock import StockList


class StockAnalyzer(mechanicalsoup.StatefulBrowser):
    yahoo_52wk_low = "https://finance.yahoo.com/u/yahoo-finance/watchlists/fiftytwo-wk-low"
    yahoo_52wk_high = "https://finance.yahoo.com/u/yahoo-finance/watchlists/fiftytwo-wk-high"
    yahoo_most_added = "https://finance.yahoo.com/u/yahoo-finance/watchlists/most-added"
    yahoo_active_spacs = "https://finance.yahoo.com/u/yahoo-finance/watchlists/most-active-spacs"
    yahoo_covid = "https://finance.yahoo.com/u/trea/watchlists/the-fight-against-covid19"
    yahoo_small_cap = "https://finance.yahoo.com/u/yahoo-finance/watchlists/most-active-small-cap-stocks"

    def __init__(self):
        super().__init__(user_agent="Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:47.0) Gecko/20100101 Firefox/47.0")

    def get_prediction(self, symbol: str):
        status = self.open("https://finance.yahoo.com/quote/" + symbol)
        if not status.ok:
            print("Invalid symbol: " + symbol)
            return "invalid"
        element = self.page.find("div", {"Fw(b) Fl(end)--m Fz(s) C($primaryColor"})
        if element is None:
            return "same"
        value = element.get_text()
        if value is None:
            return "same"
        if value == "Near Fair Value":
            return "same"
        if value == "Overvalued":
            return "down"
        if value == "Undervalued":
            return "up"

    def grab_yahoo_watchlist(self, link):
        self.open(link)
        table = self.page.find("table", {"class": "cwl-symbols W(100%)"})
        data = []
        for item in table.find_all("td"):
            data.append(item.get_text())
        count = len(data) / 9
        companies = StockList()
        for i in range(int(count)):
            start = i * 9
            # WHY TF ARE THERE 2 SYMBOLS FOR GOOGLE?????
            if data[start + 1] == "GOOGL":
                data[start + 1] = "GOOG"
            company = [
                data[start + 0],
                data[start + 1],
                data[start + 2],
                data[start + 3],
                data[start + 4],
                data[start + 8],
                1,
                self.get_prediction(data[start + 0])
            ]
            companies.add_stock(company)
        return companies

    def recommend_buy(self, budget):
        print("Scanning largest 52 week losses...")
        companies = self.grab_yahoo_watchlist(self.yahoo_52wk_low)
        print("Scanning largest 52 week gains...")
        companies.concat(self.grab_yahoo_watchlist(self.yahoo_52wk_high), False)
        print("Scanning most watched stocks...")
        companies.concat(self.grab_yahoo_watchlist(self.yahoo_most_added), False)
        print("Scanning most active SPAC's...")
        companies.concat(self.grab_yahoo_watchlist(self.yahoo_active_spacs), False)
        print("Scanning COVID-19 related stocks...")
        companies.concat(self.grab_yahoo_watchlist(self.yahoo_covid), False)
        print("Scanning small market cap stocks...")
        companies.concat(self.grab_yahoo_watchlist(self.yahoo_small_cap), False)
        print("Sorting results...")
        companies.keep_recommended()
        print("Budgeting...")
        companies.budget(int(budget))
        return companies


