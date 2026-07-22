from database.database import initialize_database
from gui.main_window import MainWindow
import traceback


def main():
    try:
        initialize_database()

        app = MainWindow()
        app.run()

    except Exception:
        traceback.print_exc()
        input("Press Enter...")


if __name__ == "__main__":
    main()