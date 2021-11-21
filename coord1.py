from lib.Coordinator import Coordinator


# TODO TURN THIS INTO coordinator.py WITH BASH ARGS
def main():
    coordinator = Coordinator('localhost', '7000', ['localhost:7001', 'localhost:7002'])
    coordinator.start()


main()
