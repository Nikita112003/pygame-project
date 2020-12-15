import pygame
from random import randint


class Board:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.board = [[-1] * height for _ in range(width)]
        self.left = 10
        self.top = 10
        self.cell_size = 30

    def get_cell(self, mouse_pos):
        for n1, i in zip(range(self.width), range(self.left, self.left + self.width * self.cell_size,
                                                  self.cell_size)):
            for n2, j in zip(range(self.height), range(self.top, self.top + self.height * self.cell_size,
                                                       self.cell_size)):
                if i + self.cell_size > mouse_pos[0] and j + self.cell_size > mouse_pos[1]:
                    return n1, n2
        return None

    def get_click(self, mouse_pos):
        cell = self.get_cell(mouse_pos)
        if cell:
            pass

    def render(self):
        for i in range(self.left, self.left + self.width * self.cell_size, self.cell_size):
            for j in range(self.top, self.top + self.height * self.cell_size, self.cell_size):
                pygame.draw.rect(screen, pygame.Color('white'), [i, j, self.cell_size, self.cell_size], 1)

    def set_view(self, left, top, cell_size):
        self.left = left
        self.top = top
        self.cell_size = cell_size


class Minesweeper(Board):
    def __init__(self, width, height):
        super().__init__(width, height)
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
            if self.board[x][y] == -1:
                self.board[x][y] = 10
                count += 1

    def get_click(self, mouse_pos):
        cell = self.get_cell(mouse_pos)
        if cell:
            self.open_cell(cell)

    def open_cell(self, cell):
        x, y = cell
        if self.board[x][y] == -1:
            count = 0
            if x - 1 > -1 and self.board[x - 1][y] == 10:
                count += 1
            if y - 1 > -1 and self.board[x][y - 1] == 10:
                count += 1
            if x + 1 < len(self.board) and self.board[x + 1][y] == 10:
                count += 1
            if y + 1 < len(self.board[x]) and self.board[x][y + 1] == 10:
                count += 1
            if x - 1 > -1 and y - 1 > -1 and self.board[x - 1][y - 1] == 10:
                count += 1
            if x - 1 > -1 and y + 1 < len(self.board[x]) and self.board[x - 1][y + 1] == 10:
                count += 1
            if x + 1 < len(self.board) and y - 1 > -1 and self.board[x + 1][y - 1] == 10:
                count += 1
            if x + 1 < len(self.board) and y + 1 < len(self.board[x]) and self.board[x + 1][y + 1] == 10:
                count += 1
            self.board[x][y] = count
            if count == 0:
                if x - 1 > -1 and self.board[x - 1][y] == -1:
                    self.open_cell((x - 1, y))
                if y - 1 > -1 and self.board[x][y - 1] == -1:
                    self.open_cell((x, y - 1))
                if x + 1 < len(self.board) and self.board[x + 1][y] == -1:
                    self.open_cell((x + 1, y))
                if y + 1 < len(self.board[x]) and self.board[x][y + 1] == -1:
                    self.open_cell((x, y + 1))
                if x - 1 > -1 and y - 1 > -1 and self.board[x - 1][y - 1] == -1:
                    self.open_cell((x - 1, y - 1))
                if x - 1 > -1 and y + 1 < len(self.board[x]) and self.board[x - 1][y + 1] == -1:
                    self.open_cell((x - 1, y + 1))
                if x + 1 < len(self.board) and y - 1 > -1 and self.board[x + 1][y - 1] == -1:
                    self.open_cell((x + 1, y - 1))
                if x + 1 < len(self.board) and y + 1 < len(self.board[x]) and self.board[x + 1][y + 1] == -1:
                    self.open_cell((x + 1, y + 1))

    def render(self):
        for i, width in zip(range(self.width), range(self.left, self.left + self.width * self.cell_size,
                                                     self.cell_size)):
            for j, height in zip(range(self.height), range(self.top, self.top + self.height * self.cell_size,
                                                           self.cell_size)):
                pygame.draw.rect(screen, pygame.Color('white'), [width, height, self.cell_size, self.cell_size], 1)
                if self.board[i][j] != -1 and self.board[i][j] != 10:
                    pygame.draw.rect(screen, pygame.Color('gray50'),
                                     (width + 1, height + 1, self.cell_size - 2, self.cell_size - 2))
                    if self.board[i][j] != 0:
                        font = pygame.font.Font(None, self.cell_size)
                        text = font.render(str(self.board[i][j]), True, self.COLORS[self.board[i][j] - 1])
                        screen.blit(text, (width + self.cell_size / 5, height + self.cell_size / 5))


if __name__ == '__main__':
    pygame.init()
    size = 300, 300
    screen = pygame.display.set_mode(size)
    pygame.display.set_caption('Сапер')
    running = True

    board = Minesweeper(10, 10)
    board.set_view(0, 0, 30)
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONUP:
                board.get_click(event.pos)
        screen.fill((0, 0, 0))
        board.render()
        pygame.display.flip()
    pygame.quit()
