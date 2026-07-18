from database.database import initialize_database
from gui.main_window import MainWindow


def main():
    initialize_database()

    app = MainWindow()
    app.run()


if __name__ == "__main__":
    main()