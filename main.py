from math import inf
import pygame
from PyQt5.QtWidgets import QApplication, QWidget
from level_choose import Ui_Form
import random
import sys

EASY = 'простой'
MEDIUM = 'средний'
HARD = 'сложный'


def terminate():
    pygame.quit()
    sys.exit()


def help_screen():
    w, h = screen.get_size()
    pygame.display.set_mode((330, 330))

    screen.fill(colors['background'])

    intro_text = ['ПОМОЩЬ', '', 'R — новая игра',
                  'P — пауза', 'L — выбор уровня сложности',
                  'M — включение/', 'выключение звука', 'C — смена темы',
                  'Esc — выход из игры', 'H — помощь']

    font = pygame.font.Font(None, 30)
    text_coord = 10
    for line in intro_text:
        string_rendered = font.render(line, True, colors['foreground'])
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 10
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)

    while True:
        for event_ in pygame.event.get():
            if event_.type == pygame.QUIT:
                terminate()
            elif event_.type == pygame.KEYDOWN or \
                    event_.type == pygame.MOUSEBUTTONDOWN:
                pygame.display.set_mode((w, h))
                return  # начинаем / продолжаем игру
        pygame.display.flip()


class LevelChoose(QWidget, Ui_Form):
    def __init__(self):
        super(LevelChoose, self).__init__()
        self.setupUi(self)
        self.ok_button.clicked.connect(self.choose)

    def choose(self):
        global cells_x, cells_y, mines, level

        chooses = {
            EASY: (10, 8, 10),
            MEDIUM: (18, 14, 40),
            HARD: (24, 20, 99)
        }

        cells_x, cells_y, mines = chooses[self.buttonGroup.checkedButton().text().lower()]
        level = self.buttonGroup.checkedButton().text().lower()
        self.close()


class Cell:
    def __init__(self):
        self.mine = False
        self.opened = False
        self.neighbors = 0
        self.flag = False

    def __bool__(self):
        return self.is_mine() and not self.is_opened() or not self.is_mine() and self.is_opened()

    def get_neighbors(self):
        return self.neighbors

    def is_flag(self):
        return self.flag

    def is_mine(self):
        return self.mine

    def is_opened(self):
        return self.opened

    def remove_flag(self):
        self.flag = False

    def remove_mine(self):
        self.mine = False

    def set_flag(self):
        self.flag = not self.flag

    def set_mine(self):
        self.mine = True

    def set_neighbors(self, n):
        self.neighbors = n

    def set_opened(self):
        self.opened = True


class Minesweeper:
    def __init__(self, width_, height_, mines_):
        self.width = width_
        self.height = height_
        self.board = [[Cell() for _ in range(height_)] for _ in range(width_)]
        self.left = 10
        self.top = 10
        self.cell_size = 30

        self.COLORS = [
            pygame.Color('blue'),
            pygame.Color('green'),
            pygame.Color('red'),
            pygame.Color('purple'),
            pygame.Color('maroon'),
            pygame.Color('turquoise'),
            pygame.Color('black'),
            pygame.Color('gray')
        ]
        count = 0
        while count < mines_:
            x, y = random.randint(0, width_ - 1), random.randint(0, height_ - 1)
            if not self[x, y].is_mine():
                self[x, y].set_mine()
                count += 1

        self.is_mine_here = False
        self.first_click = True

    def flag(self, cell):
        x, y = cell
        if not self[x, y].is_opened():
            self[x, y].set_flag()

    def game_starts(self):
        return not self.first_click

    def get_cell(self, mouse_pos):
        for n1, i in zip(range(self.width), range(self.left, self.left + self.width * self.cell_size,
                                                  self.cell_size)):
            for n2, j in zip(range(self.height), range(self.top, self.top + self.height * self.cell_size,
                                                       self.cell_size)):
                if i + self.cell_size > mouse_pos[0] and j + self.cell_size > mouse_pos[1]:
                    return n1, n2
        return None

    def get_click(self, mouse_pos, button):
        cell = self.get_cell(mouse_pos)
        if cell and state['in_game'] and not pause:
            if button == 1:
                self.open_cell(cell)
            elif button == 2:
                self.open_neighbors(cell)
            elif button == 3:
                self.flag(cell)

    def __getitem__(self, item):
        return self.board[item[0]][item[1]]

    def is_bomb(self, mouse_pos):
        cell = self.get_cell(mouse_pos)
        if cell and cheat_mode:
            x, y = cell
            if self[x, y].is_mine():
                self.is_mine_here = True
            else:
                self.is_mine_here = False

    def open_cell(self, cell, open_flag=False):
        global record

        x, y = cell
        if not self[x, y].is_opened() and (not self[x, y].is_flag() or open_flag):
            if self[x, y].is_mine() and not self.first_click:
                state['in_game'] = False
                state['win'] = False
                self[x, y].set_opened()
                if not mute:
                    boom_sound.play()
            else:
                # сработает, только если этот ход - первый
                if self[x, y].is_mine():
                    self[x, y].remove_mine()
                    while True:
                        x1, y1 = random.randint(0, self.width - 1), random.randint(0, self.height - 1)
                        if not self[x1, y1].is_mine() and x1 != x and y1 != y:
                            self[x1, y1].set_mine()
                            break

                count = 0
                if x - 1 > -1 and self[x - 1, y].is_mine():
                    count += 1
                if y - 1 > -1 and self[x, y - 1].is_mine():
                    count += 1
                if x + 1 < len(self.board) and self[x + 1, y].is_mine():
                    count += 1
                if y + 1 < len(self.board[x]) and self[x, y + 1].is_mine():
                    count += 1
                if x - 1 > -1 and y - 1 > -1 and self[x - 1, y - 1].is_mine():
                    count += 1
                if x - 1 > -1 and y + 1 < len(self.board[x]) and self[x - 1, y + 1].is_mine():
                    count += 1
                if x + 1 < len(self.board) and y - 1 > -1 and self[x + 1, y - 1].is_mine():
                    count += 1
                if x + 1 < len(self.board) and y + 1 < len(self.board[x]) and self[x + 1, y + 1].is_mine():
                    count += 1
                self[x, y].set_neighbors(count)
                self[x, y].set_opened()
                self[x, y].remove_flag()
                self.first_click = False
                if count == 0:
                    if x - 1 > -1 and not self[x - 1, y].is_mine():
                        self.open_cell((x - 1, y), True)
                    if y - 1 > -1 and not self[x, y - 1].is_mine():
                        self.open_cell((x, y - 1), True)
                    if x + 1 < len(self.board) and not self[x + 1, y].is_mine():
                        self.open_cell((x + 1, y), True)
                    if y + 1 < len(self.board[x]) and not self[x, y + 1].is_mine():
                        self.open_cell((x, y + 1), True)
                    if x - 1 > -1 and y - 1 > -1 and not self[x - 1, y - 1].is_mine():
                        self.open_cell((x - 1, y - 1), True)
                    if x - 1 > -1 and y + 1 < len(self.board[x]) and not self[x - 1, y + 1].is_mine():
                        self.open_cell((x - 1, y + 1), True)
                    if x + 1 < len(self.board) and y - 1 > -1 and not self[x + 1, y - 1].is_mine():
                        self.open_cell((x + 1, y - 1), True)
                    if x + 1 < len(self.board) and y + 1 < len(self.board[x]) and not self[x + 1, y + 1].is_mine():
                        self.open_cell((x + 1, y + 1), True)

                if all(map(lambda row: all(row), self.board)):
                    state['in_game'] = False
                    state['win'] = True
                    n = 1
                    if timer < record[level]:
                        record[level] = timer
                        n = 3
                    for i in range(n):
                        create_particles((random.randint(0, width), random.randint(0, height)))
                    if not mute:
                        win_sound.play()

                self.first_click = False

    def open_neighbors(self, cell):
        x, y = cell
        if self[x, y].is_opened():
            count = 0
            if x - 1 > -1 and self[x - 1, y].is_flag():
                count += 1
            if y - 1 > -1 and self[x, y - 1].is_flag():
                count += 1
            if x + 1 < len(self.board) and self[x + 1, y].is_flag():
                count += 1
            if y + 1 < len(self.board[x]) and self[x, y + 1].is_flag():
                count += 1
            if x - 1 > -1 and y - 1 > -1 and self[x - 1, y - 1].is_flag():
                count += 1
            if x - 1 > -1 and y + 1 < len(self.board[x]) and self[x - 1, y + 1].is_flag():
                count += 1
            if x + 1 < len(self.board) and y - 1 > -1 and self[x + 1, y - 1].is_flag():
                count += 1
            if x + 1 < len(self.board) and y + 1 < len(self.board[x]) and self[x + 1, y + 1].is_flag():
                count += 1

            if count == self[x, y].get_neighbors():
                if x - 1 > -1:
                    self.open_cell((x - 1, y))
                if y - 1 > -1:
                    self.open_cell((x, y - 1))
                if x + 1 < len(self.board):
                    self.open_cell((x + 1, y))
                if y + 1 < len(self.board[x]):
                    self.open_cell((x, y + 1))
                if x - 1 > -1 and y - 1 > -1:
                    self.open_cell((x - 1, y - 1))
                if x - 1 > -1 and y + 1 < len(self.board[x]):
                    self.open_cell((x - 1, y + 1))
                if x + 1 < len(self.board) and y - 1 > -1:
                    self.open_cell((x + 1, y - 1))
                if x + 1 < len(self.board) and y + 1 < len(self.board[x]):
                    self.open_cell((x + 1, y + 1))

    def render(self):
        all_sprites_ = pygame.sprite.Group()
        for i, width_ in zip(range(self.width), range(self.left, self.left + self.width * self.cell_size,
                                                      self.cell_size)):
            for j, height_ in zip(range(self.height), range(self.top, self.top + self.height * self.cell_size,
                                                            self.cell_size)):
                pygame.draw.rect(screen, colors['foreground'], [width_, height_, self.cell_size, self.cell_size], 1)
                if self[i, j].is_flag() and not self[i, j].is_mine() and not state['in_game']:
                    sprite = pygame.sprite.Sprite(all_sprites_)
                    sprite.image = pygame.image.load('data/no_flag.png')
                    sprite.rect = sprite.image.get_rect()
                    sprite.rect.x = width_
                    sprite.rect.y = height_
                elif self[i, j].is_flag():
                    sprite = pygame.sprite.Sprite(all_sprites_)
                    sprite.image = pygame.image.load('data/flag.png')
                    sprite.rect = sprite.image.get_rect()
                    sprite.rect.x = width_
                    sprite.rect.y = height_
                elif self[i, j].is_opened() and self[i, j].is_mine():
                    sprite = pygame.sprite.Sprite(all_sprites_)
                    sprite.image = pygame.image.load('data/boom.png')
                    sprite.rect = sprite.image.get_rect()
                    sprite.rect.x = width_
                    sprite.rect.y = height_
                elif not state['in_game'] and not state['win'] and self[i, j].is_mine():
                    sprite = pygame.sprite.Sprite(all_sprites_)
                    sprite.image = pygame.image.load('data/bomb.png')
                    sprite.rect = sprite.image.get_rect()
                    sprite.rect.x = width_
                    sprite.rect.y = height_
                elif self[i, j].is_opened():
                    pygame.draw.rect(screen, pygame.Color('gray50'),
                                     (width_ + 1, height_ + 1, self.cell_size - 2, self.cell_size - 2))
                    if self[i, j].get_neighbors() > 0:
                        font = pygame.font.Font(None, self.cell_size)
                        text = font.render(str(self[i, j].get_neighbors()), True,
                                           self.COLORS[self[i, j].get_neighbors() - 1])
                        screen.blit(text, (width_ + self.cell_size / 5, height_ + self.cell_size / 5))
            all_sprites_.draw(screen)

            if self.is_mine_here:
                pygame.draw.rect(screen, pygame.Color('green'), (0, 0, 5, 5))

            if pause:
                font = pygame.font.Font(None, 25)
                text_coord = 10 + cells_y * 30 + 10
                string_rendered = font.render('Пауза. Нажмите P, чтобы продолжить игру', True, colors['foreground'])
                pause_screen = string_rendered.get_rect()
                pause_screen.top = text_coord
                pause_screen.x = 10
                screen.blit(string_rendered, pause_screen)

            if not state['in_game']:
                if state['win']:
                    color = pygame.Color('green')
                    text = ['Вы выиграли!', f'Время: {round(timer, 2)}']
                    if timer == record[level]:
                        text[1] += ' (РЕКОРД!)'
                else:
                    color = pygame.Color('red')
                    text = ['Вы проиграли']
                text.append('Нажмите R для начала новой игры')

                font = pygame.font.Font(None, 25)
                text_coord = 10 + cells_y * 30 + 10
                for line in text:
                    string_rendered = font.render(line, True, color)
                    result_screen = string_rendered.get_rect()
                    text_coord += 10
                    result_screen.top = text_coord
                    result_screen.x = 10
                    text_coord += result_screen.height
                    screen.blit(string_rendered, result_screen)


class Particle(pygame.sprite.Sprite):
    star = random.choice(['', 'green_', 'red_', 'blue_'])
    # сгенерируем частицы разного размера
    image = pygame.image.load(f'data/{star}star.png')
    fire = [image]
    for scale in (5, 10, 20):
        fire.append(pygame.transform.scale(fire[0], (scale, scale)))

    def __init__(self, pos, dx, dy):
        super().__init__(all_sprites)
        self.image = random.choice(self.fire)
        self.rect = self.image.get_rect()

        # у каждой частицы своя скорость — это вектор
        self.velocity = [dx, dy]
        # и свои координаты
        self.rect.x, self.rect.y = pos

        # гравитация будет одинаковой (значение константы)
        self.gravity = 1

    def update(self):
        # применяем гравитационный эффект:
        # движение с ускорением под действием гравитации
        self.velocity[1] += self.gravity
        # перемещаем частицу
        self.rect.x += self.velocity[0]
        self.rect.y += self.velocity[1]
        # убиваем, если частица ушла за экран
        if not self.rect.colliderect(screen_rect):
            self.kill()


def create_particles(position):
    # количество создаваемых частиц
    particle_count = 20
    # возможные скорости
    numbers = range(-5, 6)
    for _ in range(particle_count):
        Particle(position, random.choice(numbers), random.choice(numbers))


if __name__ == '__main__':
    cells_x = cells_y = mines = 0
    level = ''

    app = QApplication(sys.argv)
    widget = LevelChoose()
    widget.show()
    app.exec()
    if cells_x == 0:
        exit()

    pygame.init()
    size = width, height = 10 + cells_x * 30 + 10, 10 + cells_y * 30 + 100
    screen_rect = (0, 0, width, height)
    screen = pygame.display.set_mode(size)
    pygame.display.set_caption('Сапер')
    pygame.display.set_icon(pygame.image.load('data/boom.png'))
    clock = pygame.time.Clock()

    colors = {
        'background': pygame.Color('black'),
        'foreground': pygame.Color('white')
    }

    game = Minesweeper(cells_x, cells_y, mines)
    state = {'in_game': True, 'win': False}
    pause = False
    timer = 0
    record = {
        EASY: inf,
        MEDIUM: inf,
        HARD: inf
    }
    cheat_mode = False

    all_sprites = pygame.sprite.Group()

    mute = False
    boom_sound = pygame.mixer.Sound('data/boom.wav')
    win_sound = pygame.mixer.Sound('data/win.wav')

    running = True
    help_screen_on = True
    help_screen()
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if help_screen_on:
                    help_screen_on = False
                elif state['win']:
                    create_particles(pygame.mouse.get_pos())
            if event.type == pygame.MOUSEBUTTONUP:
                if help_screen_on:
                    help_screen_on = False
                else:
                    game.get_click(event.pos, event.button)
            if event.type == pygame.MOUSEMOTION:
                game.is_bomb(event.pos)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_c and event.mod & pygame.KMOD_LSHIFT:
                    cheat_mode = True
                elif event.key == pygame.K_c:
                    colors['background'], colors['foreground'] = colors['foreground'], colors['background']
                elif event.key == pygame.K_h:
                    help_screen_on = True
                    help_screen()
                elif event.key == pygame.K_l:
                    widget = LevelChoose()
                    widget.show()
                    app.exec()
                    size = 10 + cells_x * 30 + 10, 10 + cells_y * 30 + 100
                    if cells_x == 0:
                        pass
                    else:
                        screen = pygame.display.set_mode(size)
                        game = Minesweeper(cells_x, cells_y, mines)
                elif event.key == pygame.K_m:
                    mute = not mute
                elif event.key == pygame.K_p:
                    if state['in_game']:
                        pause = not pause
                elif event.key == pygame.K_r:
                    game = Minesweeper(cells_x, cells_y, mines)
                    state = {'in_game': True, 'win': False}
                    pause = False
                    timer = 0
                elif event.key == pygame.K_ESCAPE:
                    running = False

        if state['in_game'] and game.game_starts() and not pause:
            timer += clock.tick() / 1000

        screen.fill(colors['background'])
        game.render()
        all_sprites.draw(screen)
        all_sprites.update()
        pygame.display.flip()

    pygame.quit()
