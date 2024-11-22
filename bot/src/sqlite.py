# sqlite
import sqlite3


class SQLite:
    def __init__(self, sql_file: str) -> None:
        self.file = sql_file

    def check_available_user_in_database(self, user_id: int) -> bool:
        with sqlite3.connect(self.file) as cursor:
            data = cursor.execute(
                "SELECT user_id FROM users WHERE user_id = ?", (user_id,)
            ).fetchone()
        return data is not None

    def add_to_database(self, user_id: int, username: str, first_name: str) -> None:
        with sqlite3.connect(self.file) as cursor:
            cursor.execute(
                "INSERT INTO users VALUES (?, ?, ?, ?, ?, ?)",
                (user_id, username, first_name, None, None, False),
            )

    def get_angel_status(self, user_id: int) -> bool:
        with sqlite3.connect(self.file) as cursor:
            data = cursor.execute(
                "SELECT angel FROM users WHERE user_id = ?", (user_id,)
            ).fetchone()
        return data[0]

    def set_angel_status(self, user_id: int, status: bool) -> None:
        with sqlite3.connect(self.file) as cursor:
            cursor.execute("UPDATE users SET angel = ? WHERE user_id = ?", (status, user_id))
