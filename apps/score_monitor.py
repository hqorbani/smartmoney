
from smartmoney.bootstrap import create_analysis_scheduler


def main():
    scheduler = create_analysis_scheduler()
    scheduler.start()


if __name__ == "__main__":
    main()
