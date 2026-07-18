from smartmoney.bootstrap import create_live_scheduler


def main():

    scheduler = create_live_scheduler()

    scheduler.start()


if __name__ == "__main__":
    main()