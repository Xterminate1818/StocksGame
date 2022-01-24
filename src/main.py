from trading import TradingBot


if __name__ == "__main__":
    print("*-*-* Logan's Trading Bot *-*-*")
    trader = TradingBot()
    while True:
        _in = input("> ")
        words = _in.split(" ")
        if len(words) == 0:
            continue
        cmd = words.pop(0)
        args = []
        kwargs = {}
        for w in words:
            components = w.split("=")
            if len(components) == 1:
                args.append(w)
            elif len(components) == 2:
                kwargs[components[0]] = components[1]
            else:
                print("Invalid parameter: " + w)
                continue

        trader.interpret_command(cmd, *args, **kwargs)
    # trader.buy("GOOG", 1)
