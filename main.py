from kivy.uix.label import Label
from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.uix.widget import Widget
from kivy.vector import Vector
from kivy.properties import ObjectProperty, NumericProperty, StringProperty
from random import randint

# Velikost okna hry
WINDOW_HEIGHT = 500
WINDOW_WIDTH = 500

# Velikost hráče a rychlost hry
PLAYER_SIZE = 20
GAME_SPEED = .1


class Fruit(Widget):
    """Třída představující ovoce, které se objevuje na hrací ploše."""

    def move(self, new_pos):
        self.pos = new_pos


class SnakeTail(Widget):
    """Třída představující článek ocasu hada."""

    def move(self, new_pos):
        self.pos = new_pos


class SnakeHead(Widget):
    """Třída představující hlavu hada."""
    orientation = (PLAYER_SIZE, 0)

    def reset_pos(self):
        """Nastaví pozici hlavy hada na střed hrací plochy."""
        self.pos = [int(WINDOW_WIDTH / 2 - (WINDOW_WIDTH / 2 % PLAYER_SIZE)),
                    int(WINDOW_HEIGHT / 2 - (WINDOW_HEIGHT / 2 % PLAYER_SIZE))]
        self.orientation = (PLAYER_SIZE, 0)

    def move(self):
        """Přesune hlavu hada na novou pozici podle aktuální orientace."""
        self.pos = Vector(*self.orientation) + self.pos


class SmartGrid:
    """Třída reprezentující chytrou mřížku pro sledování obsazení pozic na hrací ploše."""

    def __init__(self):
        self.grid = [[False for _ in range(WINDOW_HEIGHT)] for _ in range(WINDOW_WIDTH)]

    def __getitem__(self, coords):
        return self.grid[coords[0]][coords[1]]

    def __setitem__(self, coords, value):
        self.grid[coords[0]][coords[1]] = value


class SnakeGame(Widget):
    """Třída představující samotnou hru."""
    head = ObjectProperty(None)
    fruit = ObjectProperty(None)
    score = NumericProperty(0)
    player_size = NumericProperty(PLAYER_SIZE)
    game_over = StringProperty("")

    def __init__(self):
        super(SnakeGame, self).__init__()

        # Nastavení velikosti okna
        Window.size = (WINDOW_WIDTH, WINDOW_HEIGHT)
        Window.bind(on_key_down=self.key_action)

        # Kontrola platnosti velikosti hráče
        if PLAYER_SIZE < 3:
            raise ValueError("Velikost hráče musí být alespoň 3 px.")

        # Kontrola platnosti velikosti okna ve srovnání s hráčem
        if WINDOW_HEIGHT < 3 * PLAYER_SIZE or WINDOW_WIDTH < 3 * PLAYER_SIZE:
            raise ValueError("Velikost okna musí být alespoň 3x větší než velikost hráče.")

        # Inicializace hodinového intervalu pro pravidelné obnovení hry
        self.timer = Clock.schedule_interval(self.refresh, GAME_SPEED)

        # Inicializace ocasu a labelu pro zobrazení textu "Game over!"
        self.tail = []
        self.game_over_label = Label(text="", font_size=20, pos=(WINDOW_WIDTH / 2 - 50, WINDOW_HEIGHT / 2))
        self.add_widget(self.game_over_label)

        # Restart hry
        self.restart_game()

    def restart_game(self, dt=None):
        """Restartuje hru a nastaví počáteční stav."""
        self.occupied = SmartGrid()
        self.timer.cancel()
        self.timer = Clock.schedule_interval(self.refresh, GAME_SPEED)
        self.head.reset_pos()
        self.score = 0
        self.game_over_label.text = ""  # Resetuje text na labelu
        self.game_over = ""  # Resetuje zprávu o konci hry

        for block in self.tail:
            self.remove_widget(block)

        self.tail = []
        self.tail.append(SnakeTail(pos=(self.head.pos[0] - PLAYER_SIZE, self.head.pos[1]), size=(self.head.size)))
        self.add_widget(self.tail[-1])
        self.occupied[self.tail[-1].pos] = True

        self.tail.append(SnakeTail(pos=(self.head.pos[0] - 2 * PLAYER_SIZE, self.head.pos[1]), size=(self.head.size)))
        self.add_widget(self.tail[-1])
        self.occupied[self.tail[1].pos] = True

        self.spawn_fruit()

    def show_game_over_message(self):
        """Zobrazí text "Game over!" na střed obrazovky."""
        self.game_over_label.text = "Konec hry! Stiskněte 'r' pro restart."

    def refresh(self, dt):
        """Obnovuje stav hry v pravidelných intervalech."""
        if not (0 <= self.head.pos[0] < WINDOW_WIDTH) or not (0 <= self.head.pos[1] < WINDOW_HEIGHT):
            self.show_game_over_message()
            self.timer.cancel()
            return

        if self.occupied[self.head.pos] is True:
            self.show_game_over_message()
            self.timer.cancel()
            return

        self.occupied[self.tail[-1].pos] = False
        self.tail[-1].move(self.tail[-2].pos)

        for i in range(2, len(self.tail)):
            self.tail[-i].move(new_pos=(self.tail[-(i + 1)].pos))

        self.tail[0].move(new_pos=self.head.pos)
        self.occupied[self.tail[0].pos] = True

        self.head.move()

        if self.head.pos == self.fruit.pos:
            self.score += 1
            self.tail.append(SnakeTail(pos=self.head.pos, size=self.head.size))
            self.add_widget(self.tail[-1])
            self.spawn_fruit()

    def spawn_fruit(self):
        """Umístí nové ovoce na náhodnou neobsazenou pozici."""
        roll = self.fruit.pos
        found = False
        while not found:
            roll = [PLAYER_SIZE * randint(0, int(WINDOW_WIDTH / PLAYER_SIZE) - 1),
                    PLAYER_SIZE * randint(0, int(WINDOW_HEIGHT / PLAYER_SIZE) - 1)]

            if self.occupied[roll] is True or roll == self.head.pos:
                continue

            found = True

        self.fruit.move(roll)

    def key_action(self, *args):
        """Zpracovává stisknuté klávesy a provádí odpovídající akce."""
        command = list(args)[3]

        #pohyb hada na klávesách w a s d a restart hry na klávese r
        if command == 'w':
            self.head.orientation = (0, PLAYER_SIZE)
        elif command == 's':
            self.head.orientation = (0, -PLAYER_SIZE)
        elif command == 'a':
            self.head.orientation = (-PLAYER_SIZE, 0)
        elif command == 'd':
            self.head.orientation = (PLAYER_SIZE, 0)
        elif command == 'r':
            self.restart_game()


class SnakeApp(App):
    def build(self):
        game = SnakeGame()
        return game


if __name__ == '__main__':
    SnakeApp().run()
