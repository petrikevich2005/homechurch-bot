from random import shuffle


class DataProcessing:
    @staticmethod
    def random_users(users: list) -> list:
        if len(users) < 2:
            raise ValueError("Необходимо как минимум 2 пользователя для распределения.")

        santas = users[:]
        shuffle(santas)

        for i in range(len(users)):
            if users[i] == santas[i]:
                if i == 0:
                    santas[i], santas[i + 1] = santas[i + 1], santas[i]
                else:
                    santas[i], santas[i - 1] = santas[i - 1], santas[i]

        return santas
