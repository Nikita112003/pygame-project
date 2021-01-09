from math import inf
import pygame
from random import randint
import sys


def terminate():
    pygame.quit()
    sys.exit()


def help_screen():
    intro_text = ['ПОМОЩЬ', '', 'R — новая игра',
                  'P — пауза', 'M — включение/выключение звука',
                  'H — помощь']

    font = pygame.font.Font(None, 30)
    text_coord = 10
    for line in intro_text:
        string_rendered = font.render(line, True, pygame.Color('white'))
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
                return  # начинаем игру
        pygame.display.flip()


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
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.board = [[Cell() for _ in range(height)] for _ in range(width)]
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
        while count < 40:
            x, y = randint(0, width - 1), randint(0, height - 1)
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
                        x1, y1 = randint(0, self.width - 1), randint(0, self.height - 1)
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
                    if timer < record:
                        record = timer
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
        all_sprites = pygame.sprite.Group()
        for i, width in zip(range(self.width), range(self.left, self.left + self.width * self.cell_size,
                                                     self.cell_size)):
            for j, height in zip(range(self.height), range(self.top, self.top + self.height * self.cell_size,
                                                           self.cell_size)):
                pygame.draw.rect(screen, pygame.Color('white'), [width, height, self.cell_size, self.cell_size], 1)
                if self[i, j].is_flag() and not self[i, j].is_mine() and not state['in_game']:
                    sprite = pygame.sprite.Sprite(all_sprites)
                    sprite.image = pygame.image.load('data/no_flag.png')
                    sprite.rect = sprite.image.get_rect()
                    sprite.rect.x = width
                    sprite.rect.y = height
                elif self[i, j].is_flag():
                    sprite = pygame.sprite.Sprite(all_sprites)
                    sprite.image = pygame.image.load('data/flag.png')
                    sprite.rect = sprite.image.get_rect()
                    sprite.rect.x = width
                    sprite.rect.y = height
                elif self[i, j].is_opened() and self[i, j].is_mine():
                    sprite = pygame.sprite.Sprite(all_sprites)
                    sprite.image = pygame.image.load('data/boom.png')
                    sprite.rect = sprite.image.get_rect()
                    sprite.rect.x = width
                    sprite.rect.y = height
                elif not state['in_game'] and not state['win'] and self[i, j].is_mine():
                    sprite = pygame.sprite.Sprite(all_sprites)
                    sprite.image = pygame.image.load('data/bomb.png')
                    sprite.rect = sprite.image.get_rect()
                    sprite.rect.x = width
                    sprite.rect.y = height
                elif self[i, j].is_opened():
                    pygame.draw.rect(screen, pygame.Color('gray50'),
                                     (width + 1, height + 1, self.cell_size - 2, self.cell_size - 2))
                    if self[i, j].get_neighbors() > 0:
                        font = pygame.font.Font(None, self.cell_size)
                        text = font.render(str(self[i, j].get_neighbors()), True,
                                           self.COLORS[self[i, j].get_neighbors() - 1])
                        screen.blit(text, (width + self.cell_size / 5, height + self.cell_size / 5))
            all_sprites.draw(screen)

            if self.is_mine_here:
                pygame.draw.rect(screen, pygame.Color('green'), (0, 0, 5, 5))

            if pause:
                font = pygame.font.Font(None, 25)
                text_coord = 10 + cells_y * 30 + 10
                string_rendered = font.render('Пауза. Нажмите P, чтобы продолжить игру', True, pygame.Color('white'))
                pause_screen = string_rendered.get_rect()
                pause_screen.top = text_coord
                pause_screen.x = 10
                screen.blit(string_rendered, pause_screen)

            if not state['in_game']:
                if state['win']:
                    color = pygame.Color('green')
                    text = ['Вы выиграли!', f'Время: {round(timer, 2)}']
                    if timer == record:
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


if __name__ == '__main__':
    pygame.init()
    cells_x = 18
    cells_y = 14
    size = 10 + cells_x * 30 + 10, 10 + cells_y * 30 + 100
    screen = pygame.display.set_mode(size)
    pygame.display.set_caption('Сапер')
    clock = pygame.time.Clock()

    game = Minesweeper(cells_x, cells_y)
    state = {'in_game': True, 'win': False}
    pause = False
    timer = 0
    record = inf
    cheat_mode = False

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
                help_screen_on = False
            if event.type == pygame.MOUSEBUTTONUP:
                if help_screen_on:
                    help_screen_on = False
                else:
                    game.get_click(event.pos, event.button)
            if event.type == pygame.MOUSEMOTION:
                game.is_bomb(event.pos)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_h:
                    help_screen_on = True
                    screen.fill(pygame.Color('black'))
                    help_screen()
                elif event.key == pygame.K_m:
                    mute = not mute
                elif event.key == pygame.K_p:
                    if state['in_game']:
                        pause = not pause
                elif event.key == pygame.K_r:
                    game = Minesweeper(cells_x, cells_y)
                    state = {'in_game': True, 'win': False}
                    pause = False
                    timer = 0
                elif event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_c and event.mod & pygame.KMOD_LSHIFT:
                    cheat_mode = True

        if state['in_game'] and game.game_starts() and not pause:
            timer += clock.tick() / 1000
        screen.fill((0, 0, 0))
        game.render()
        pygame.display.flip()
    pygame.quit()
