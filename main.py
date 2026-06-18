import random


class BoardOutException(Exception):
    def __init__(self, message="Выстрел за пределы поля!"):
        super().__init__(message)


class DotOccupiedException(Exception):
    def __init__(self, message="Эта клетка уже занята или в нее уже стреляли!"):
        super().__init__(message)


class ShipPlacementError(Exception):
    def __init__(self, message="Невозможно разместить корабль в этом месте!"):
        super().__init__(message)


class InvalidMoveError(Exception):
    def __init__(self, message="Некорректный ход. Попробуйте еще раз."):
        super().__init__(message)


class Dot:
    """Класс, представляющий точку на игровом поле."""

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        if not isinstance(other, Dot):
            return NotImplemented
        return self.x == other.x and self.y == other.y

    def __hash__(self):
        return hash((self.x, self.y))

    def __str__(self):
        return f"({self.x}, {self.y})"


class Ship:
    """Класс, представляющий корабль на игровом поле."""

    def __init__(self, bow: Dot, length: int, orientation: str):
        self.bow = bow
        self.length = length
        self.orientation = orientation
        self.lives = length

    @property
    def dots(self):
        """Возвращает список всех точек, которые занимает корабль."""
        ship_dots = []
        for i in range(self.length):
            current_x, current_y = self.bow.x, self.bow.y
            if self.orientation == 'horizontal':
                current_y += i
            elif self.orientation == 'vertical':
                current_x += i
            ship_dots.append(Dot(current_x, current_y))
        return ship_dots


class Board:
    """Класс, представляющий игровую доску."""

    def __init__(self, size=6, hid=False):
        self.size = size
        self.hid = hid
        self.board = self._create_empty_board()
        self.ships = []
        self.busy_dots = set()
        self.shot_dots = set()
        self.live_ships = 0

    def _create_empty_board(self):
        """Создает пустую доску с заголовками."""
        board_data = [[" ", *range(1, self.size + 1)]]
        for i in range(1, self.size + 1):
            board_data.append([i, *["О"] * self.size])
        return board_data

    def display_board(self):
        """Выводит доску в консоль."""
        col_header = "  " + " | ".join(map(str, self.board[0][1:]))
        print(col_header)
        print("----" * (self.size + 1))

        for row_index in range(1, len(self.board)):
            row_display_elements = []
            for col_index in range(len(self.board[row_index])):
                cell_value = self.board[row_index][col_index]
                if self.hid and cell_value == '■':
                    row_display_elements.append("О")
                else:
                    row_display_elements.append(str(cell_value))
            print(" | ".join(row_display_elements))

    def out(self, dot: Dot):
        """Проверяет, выходит ли точка за пределы поля."""
        return not (1 <= dot.x <= self.size and 1 <= dot.y <= self.size)

    def _is_valid_placement(self, ship: Ship):
        """Проверяет, возможно ли разместить корабль."""
        for d in ship.dots:
            if self.out(d) or d in self.busy_dots:
                return False
        return True

    def add_ship(self, ship: Ship):
        """Ставит корабль на доску."""
        if not self._is_valid_placement(ship):
            raise ShipPlacementError(
                "Корабль пересекается с другими или выходит за границы!"
            )
        for d in ship.dots:
            self.board[d.x][d.y] = '■'
            self.busy_dots.add(d)
        self.ships.append(ship)
        self.contour(ship)
        self.live_ships += 1

    def contour(self, ship: Ship, symbol='.'):
        """Обводит корабль по контуру, помечая соседние клетки."""
        near_coords = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1),  (0, 0),  (0, 1),
            (1, -1),  (1, 0),  (1, 1)
        ]
        for d in ship.dots:
            for dx, dy in near_coords:
                contour_dot = Dot(d.x + dx, d.y + dy)
                if not self.out(contour_dot) and contour_dot not in self.busy_dots:
                    if self.board[contour_dot.x][contour_dot.y] == 'О':
                        self.board[contour_dot.x][contour_dot.y] = symbol
                    self.busy_dots.add(contour_dot)

    def shot(self, dot: Dot):
        """Делает выстрел по доске."""
        if self.out(dot):
            raise BoardOutException("Выстрел за пределы поля!")
        if dot in self.shot_dots:
            raise DotOccupiedException("В эту клетку уже стреляли!")
        self.shot_dots.add(dot)

        for ship in self.ships:
            if dot in ship.dots:
                ship.lives -= 1
                self.board[dot.x][dot.y] = 'X'
                print("Попал!")
                if ship.lives == 0:
                    self.live_ships -= 1
                    print("Корабль уничтожен!")
                    self.contour(ship, symbol='T')
                return True

        self.board[dot.x][dot.y] = 'T'
        print("Промах!")
        return False


class Player:
    """Базовый класс для игрока."""

    def __init__(self, board: Board, enemy_board: Board):
        self.board = board
        self.enemy_board = enemy_board

    def ask(self):
        raise NotImplementedError(
            "Метод ask должен быть реализован в дочернем классе!"
        )

    def move(self):
        """Делает ход. Возвращает True если попал (нужен повторный ход)."""
        while True:
            try:
                target_dot = self.ask()
                hit = self.enemy_board.shot(target_dot)
                return hit
            except (BoardOutException, DotOccupiedException) as e:
                print(f"Ошибка: {e}")
            except Exception as e:
                print(f"Непредвиденная ошибка: {e}")
                raise


class User(Player):
    """Класс игрока-пользователя."""

    def ask(self):
        while True:
            try:
                raw = input("Ваш ход (строка, столбец): ")
                parts = raw.replace(" ", ",").split(",")
                parts = [p for p in parts if p.strip()]
                if len(parts) != 2:
                    print("Неверный формат. Введите две цифры через запятую, например: 3, 4")
                    continue
                x, y = int(parts[0].strip()), int(parts[1].strip())
                return Dot(x, y)
            except ValueError:
                print("Координаты должны быть числами! Например: 3, 4")


class AI(Player):
    """Класс игрока-компьютера."""

    def __init__(self, board: Board, enemy_board: Board):
        super().__init__(board, enemy_board)
        self.possible_shots = self._generate_all_possible_shots()
        random.shuffle(self.possible_shots)


    def _generate_all_possible_shots(self):
        """Генерирует список всех возможных точек на доске."""
        shots = []
        for x in range(1, self.board.size + 1):
            for y in range(1, self.board.size + 1):
                shots.append(Dot(x, y))
        return shots


    def ask(self):
        """ИИ выбирает случайную клетку, в которую еще не стрелял."""
        while True:
            if not self.possible_shots:
                raise Exception("ИИ исчерпал все возможные ходы!")
            dot = self.possible_shots.pop(0)
            if dot not in self.enemy_board.shot_dots:
                print(f"Ход компьютера: {dot.x}, {dot.y}")
                return dot


class Game:
    """Главный класс игры Морской бой."""

    def __init__(self, size=6):
        self.size = size
        self.player = None
        self.ai = None
        self.player_board = None
        self.ai_board = None
        self.ship_lengths = [3, 2, 2, 1, 1, 1, 1]


    def _create_random_board(self):
        """Генерирует доску со случайно расположенными кораблями."""
        board = None
        attempts = 0
        max_board_attempts = 1000

        while board is None and attempts < max_board_attempts:
            board = Board(size=self.size)
            try:
                for length in sorted(self.ship_lengths, reverse=True):
                    ship_attempts = 0
                    placed = False
                    while not placed and ship_attempts < 100:
                        bow_x = random.randint(1, self.size)
                        bow_y = random.randint(1, self.size)
                        orientation = random.choice(['horizontal', 'vertical'])
                        ship = Ship(Dot(bow_x, bow_y), length, orientation)
                        try:
                            board.add_ship(ship)
                            placed = True
                        except ShipPlacementError:
                            ship_attempts += 1
                    if not placed:
                        board = None
                        break
            except Exception:
                board = None
            attempts += 1

        if board is None:
            raise Exception(
                f"Не удалось сгенерировать доску после "
                f"{max_board_attempts} попыток. Перезапустите игру."
            )
        return board


    def greet(self):
        """Приветствует пользователя и объясняет правила."""
        print("=" * 35)
        print("   Добро пожаловать в Морской бой!")
        print("=" * 35)
        print("Формат ввода: строка, столбец")
        print("Пример: 3, 4")
        print("-" * 35)
        print("Обозначения:")
        print("  О — пустая клетка")
        print("  ■ — ваш корабль")
        print("  X — попадание")
        print("  T — промах")
        print("=" * 35)


    def loop(self):
        """Основной игровой цикл."""
        num_turns = 0
        while True:
            num_turns += 1
            print(f"\n{'=' * 35}")
            print(f"Ход {num_turns}")
            print(f"{'=' * 35}")
            print("\nВаша доска:")
            self.player_board.display_board()
            print("\nДоска компьютера:")
            self.ai_board.display_board()

            print("\n>> Ваш ход!")
            player_hit = self.player.move()
            if self.ai_board.live_ships == 0:
                print("\n🎉 Вы победили! Все корабли противника уничтожены!")
                break
            if player_hit:
                print("Отличный выстрел! Ходите еще раз.")
                continue

            print("\n>> Ход компьютера!")
            ai_hit = self.ai.move()
            if self.player_board.live_ships == 0:
                print("\n💀 Компьютер победил! Ваши корабли уничтожены!")
                break
            if ai_hit:
                print("Компьютер попал! Он ходит еще раз.")
                continue


    def start(self):
        """Запускает игру."""
        self.greet()
        print("\nГенерация досок...")
        try:
            self.player_board = self._create_random_board()
            self.ai_board = self._create_random_board()
            self.ai_board.hid = True
        except Exception as e:
            print(f"Ошибка: {e}")
            return

        self.player = User(self.player_board, self.ai_board)
        self.ai = AI(self.ai_board, self.player_board)

        print("Доски сгенерированы! Начинаем игру!")
        self.loop()


if __name__ == "__main__":
    game = Game()
    game.start()
