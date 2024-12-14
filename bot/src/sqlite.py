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

    def add_to_database(self, user_id: int, username: str, first_name: str) -> bool:
        with sqlite3.connect(self.file) as cursor:
            cursor.execute(
                "INSERT INTO users VALUES (?, ?, ?, ?, ?, ?, ?)",
                (
                    user_id,
                    username if username is not None else "",
                    first_name,
                    False,
                    None,
                    None,
                    False,
                ),
            )
            return True
        return False

    def get_angel_status(self, user_id: int) -> bool:
        with sqlite3.connect(self.file) as cursor:
            data = cursor.execute(
                "SELECT angel_status FROM users WHERE user_id = ?", (user_id,)
            ).fetchone()
        return data[0]

    def set_angel_status(self, user_id: int, status: bool) -> None:
        with sqlite3.connect(self.file) as cursor:
            cursor.execute("UPDATE users SET angel_status = ? WHERE user_id = ?", (status, user_id))

    def get_data(self, user_id: int) -> dict:
        with sqlite3.connect(self.file) as cursor:
            data = cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)).fetchone()

        data = {
            "user_id": data[0],
            "username": data[1],
            "first_name": data[2],
            "angel_status": data[3],
            "angel": data[4],
            "wish": data[5],
            "admin": data[6],
        }
        return data

    def set_wish(self, user_id: int, wish: str) -> None:
        with sqlite3.connect(self.file) as cursor:
            cursor.execute("UPDATE users SET wish = ? WHERE user_id = ?", (wish, user_id))

    def set_angels(self, users: list, parallel: list) -> None:
        with sqlite3.connect(self.file) as cursor:
            for i in range(len(users)):
                cursor.execute(
                    "UPDATE users SET angel = ? WHERE user_id = ?", (parallel[i], users[i])
                )

    def get_wish(self, user_id: int) -> bool:
        with sqlite3.connect(self.file) as cursor:
            data = cursor.execute("SELECT wish FROM users WHERE user_id = ?", (user_id,)).fetchone()
        return data[0]

    def get_angel(self, user_id: int) -> int:
        with sqlite3.connect(self.file) as cursor:
            data = cursor.execute(
                "SELECT angel FROM users WHERE user_id = ?", (user_id,)
            ).fetchone()
        return data[0]

    def get_admin_status(self, user_id: int) -> bool:
        with sqlite3.connect(self.file) as cursor:
            data = cursor.execute(
                "SELECT admin FROM users WHERE user_id = ?", (user_id,)
            ).fetchone()
        return data[0]

    def get_users_list(self) -> list:
        with sqlite3.connect(self.file) as cursor:
            users = cursor.execute("SELECT user_id FROM users WHERE angel_status = ?", (1,))
        users_list = []
        for user in users:
            users_list.append(user[0])  # noqa: PERF401
        return users_list
