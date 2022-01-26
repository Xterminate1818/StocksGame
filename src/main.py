from trading import TradingBot


if __name__ == "__main__":
    print("*-*-* Logan's Trading Bot *-*-*")
    trader = TradingBot()
    while True:
        _in = input("> ")
        trader.interpret_command(_in.lower())
