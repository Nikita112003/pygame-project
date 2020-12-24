import pygame
from random import randint


class Cell:
    def __init__(self):
        self.mine = False
        self.opened = False
        self.neighbors = 0
        self.flag = False

    def get_neighbors(self):
        return self.neighbors

    def is_flag(self):
        return self.flag

    def is_mine(self):
        return self.mine

    def is_opened(self):
        return self.opened

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
        while count < 10:
            x, y = randint(0, width - 1), randint(0, height - 1)
            if not self.board[x][y].is_mine():
                self.board[x][y].set_mine()
                count += 1

    def flag(self, cell):
        x, y = cell
        if not self.board[x][y].is_opened():
            self.board[x][y].set_flag()

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
        if cell:
            if button == 1:
                self.open_cell(cell)
            elif button == 3:
                self.flag(cell)

    def open_cell(self, cell):
        x, y = cell
        if not self.board[x][y].is_opened() and not self.board[x][y].is_flag():
            count = 0
            if x - 1 > -1 and self.board[x - 1][y].is_mine():
                count += 1
            if y - 1 > -1 and self.board[x][y - 1].is_mine():
                count += 1
            if x + 1 < len(self.board) and self.board[x + 1][y].is_mine():
                count += 1
            if y + 1 < len(self.board[x]) and self.board[x][y + 1].is_mine():
                count += 1
            if x - 1 > -1 and y - 1 > -1 and self.board[x - 1][y - 1].is_mine():
                count += 1
            if x - 1 > -1 and y + 1 < len(self.board[x]) and self.board[x - 1][y + 1].is_mine():
                count += 1
            if x + 1 < len(self.board) and y - 1 > -1 and self.board[x + 1][y - 1].is_mine():
                count += 1
            if x + 1 < len(self.board) and y + 1 < len(self.board[x]) and self.board[x + 1][y + 1].is_mine():
                count += 1
            self.board[x][y].set_neighbors(count)
            self.board[x][y].set_opened()
            if count == 0:
                if x - 1 > -1 and not self.board[x - 1][y].is_mine():
                    self.open_cell((x - 1, y))
                if y - 1 > -1 and not self.board[x][y - 1].is_mine():
                    self.open_cell((x, y - 1))
                if x + 1 < len(self.board) and not self.board[x + 1][y].is_mine():
                    self.open_cell((x + 1, y))
                if y + 1 < len(self.board[x]) and not self.board[x][y + 1].is_mine():
                    self.open_cell((x, y + 1))
                if x - 1 > -1 and y - 1 > -1 and not self.board[x - 1][y - 1].is_mine():
                    self.open_cell((x - 1, y - 1))
                if x - 1 > -1 and y + 1 < len(self.board[x]) and not self.board[x - 1][y + 1].is_mine():
                    self.open_cell((x - 1, y + 1))
                if x + 1 < len(self.board) and y - 1 > -1 and not self.board[x + 1][y - 1].is_mine():
                    self.open_cell((x + 1, y - 1))
                if x + 1 < len(self.board) and y + 1 < len(self.board[x]) and not self.board[x + 1][y + 1].is_mine():
                    self.open_cell((x + 1, y + 1))

    def render(self):
        all_sprites = pygame.sprite.Group()
        for i, width in zip(range(self.width), range(self.left, self.left + self.width * self.cell_size,
                                                     self.cell_size)):
            for j, height in zip(range(self.height), range(self.top, self.top + self.height * self.cell_size,
                                                           self.cell_size)):
                pygame.draw.rect(screen, pygame.Color('white'), [width, height, self.cell_size, self.cell_size], 1)
                if self.board[i][j].is_opened() and self.board[i][j].is_mine():
                    pass
                elif self.board[i][j].is_opened():
                    pygame.draw.rect(screen, pygame.Color('gray50'),
                                     (width + 1, height + 1, self.cell_size - 2, self.cell_size - 2))
                    if self.board[i][j].get_neighbors() > 0:
                        font = pygame.font.Font(None, self.cell_size)
                        text = font.render(str(self.board[i][j].get_neighbors()), True,
                                           self.COLORS[self.board[i][j].get_neighbors() - 1])
                        screen.blit(text, (width + self.cell_size / 5, height + self.cell_size / 5))
                elif self.board[i][j].is_flag():
                    sprite = pygame.sprite.Sprite(all_sprites)
                    sprite.image = pygame.image.load('data/flag.png')
                    sprite.rect = sprite.image.get_rect()
                    sprite.rect.x = width
                    sprite.rect.y = height
            all_sprites.draw(screen)


if __name__ == '__main__':
    pygame.init()
    size = [10 + 10 * 30 + 10 for _ in range(2)]
    screen = pygame.display.set_mode(size)
    pygame.display.set_caption('Сапер')
    running = True

    board = Minesweeper(10, 10)
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONUP:
                board.get_click(event.pos, event.button)
        screen.fill((0, 0, 0))
        board.render()
        pygame.display.flip()
    pygame.quit()
