import pygame
import random
from queue import Queue
from sklearn import neighbors
import time
pygame.init()

WIDTH, HEIGHT = 700, 800

win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Minesweeper")

BG_COLOR = "white"
ROWS, COLS = 10, 10
MINES = 10

SIZE = WIDTH / ROWS

NUM_FONT = pygame.font.SysFont('comicsans', 20)
LOST_FONT = pygame.font.SysFont('comicsans', 50)
WIN_FONT = pygame.font.SysFont('comicsans', 30)

NUM_COLORS = {1: "black", 2: "green", 3: "red", 4: "orange", 
                5:"yellow", 6: "purple", 7: "blue", 8: "pink"}
RECT_COLOR = (200, 200, 200)
CLICKED_RECT_COLOR = (140, 140, 140)
FLAG_RECT_COLOR = 'green'
BOMB_COLOR = 'red'

def get_neighbors(row, col, rows, cols):
    neighbors = []
    
    if row > 0: #Up
        neighbors.append((row-1, col))
    if row < rows - 1: #Down
        neighbors.append((row + 1, col))
    if col > 0: # Left
        neighbors.append((row, col - 1))
    if col < cols - 1: # Right
        neighbors.append((row, col + 1))

    if row > 0 and col > 0:
        neighbors.append((row - 1, col - 1))
    if row < rows - 1 and col < cols - 1:
        neighbors.append((row + 1, col + 1))
    if row < rows - 1 and col > 0:
        neighbors.append((row + 1, col - 1))
    if row > 0 and col < cols - 1:
        neighbors.append((row - 1, col + 1))

    return neighbors

    

def create_mine_field(rows, cols, MINES):
    field = [[0 for _ in range(cols)] for _ in range(rows)]
    mine_positions = set()

    while len(mine_positions) < MINES:
        row = random.randrange(0, rows)
        col = random.randrange(0, cols)
        pos = row, col

        if pos in mine_positions:
            continue

        mine_positions.add(pos)
        field[row][col] = -1

    for mine in mine_positions:
        neighbors = get_neighbors(*mine, rows, cols)
        for r, c in neighbors:
            if field[r][c] != -1:
                field[r][c] += 1

    return field

    

def draw(win, field, cover_field):
    win.fill(BG_COLOR)

    for i, row in enumerate(field):
        y = SIZE * i
        for j, value in enumerate(row):
            x = SIZE * j

            is_covered = cover_field[i][j] == 0
            is_flag = cover_field[i][j] == -2
            is_bomb = value == -1

            if is_flag:
                pygame.draw.rect(win, FLAG_RECT_COLOR, (x, y, SIZE, SIZE))
                pygame.draw.rect(win, "black", (x, y, SIZE, SIZE), 2)
                continue

            if is_covered:
                pygame.draw.rect(win, RECT_COLOR, (x, y, SIZE, SIZE))
                pygame.draw.rect(win, "black", (x, y, SIZE, SIZE), 2)
                continue
            else:
                pygame.draw.rect(win, CLICKED_RECT_COLOR, (x, y, SIZE, SIZE))
                pygame.draw.rect(win, "black", (x, y, SIZE, SIZE), 2)
                if is_bomb:
                    pygame.draw.circle(win, BOMB_COLOR, (x + SIZE/2, y + SIZE/2), SIZE/2 - 4)

            if value > 0:
                text = NUM_FONT.render(str(value), 1, NUM_COLORS[value])
                win.blit(text, (x + (SIZE/2 - text.get_width()/2), y + (SIZE/2 - text.get_height()/2)))

    pygame.display.update()

def get_grid_pos(mouse_pos):
    mx, my = mouse_pos
    row = int(my // SIZE)
    col = int(mx // SIZE)

    return row, col

def uncover_from_pos(row, col, cover_field, field):
    q = Queue()
    q.put((row, col))
    visited = set()

    while not q.empty():
        current = q.get()

        neighbors = get_neighbors(*current, ROWS, COLS)
        for r, c in neighbors:
            if (r, c) in visited:
                continue

            value = field[r][c]
            if value == 0 and cover_field[r][c] != -2:
                q.put((r, c))

            if cover_field[r][c] != -2 and field[r][c] != -1:
                cover_field[r][c] = 1
            visited.add((r, c))

def draw_lost(win, text):
    text = LOST_FONT.render(text, 1, 'black')
    win.blit(text, (WIDTH/2 - text.get_width() / 2,
                    HEIGHT - text.get_height()*1.5))
    pygame.display.update()

def draw_win(win, text):
    text = WIN_FONT.render(text, 1, 'black')
    win.blit(text, (WIDTH/2 - text.get_width() / 2,
                    HEIGHT - text.get_height()*1.5))
    pygame.display.update()

def main():
    run = True
    field = create_mine_field(ROWS, COLS, MINES)
    cover_field = [[0 for _ in range(COLS)] for _ in range(ROWS)]
    flags = MINES
    clicks = 0
    lost = False
    winner = False

    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break

            if event.type == pygame.MOUSEBUTTONDOWN:
                row, col = get_grid_pos(pygame.mouse.get_pos())
                if row >= ROWS or col >= COLS:
                    continue
                mouse_pressed = pygame.mouse.get_pressed()
                if mouse_pressed[0] and cover_field[row][col] != -2:
                    cover_field[row][col] = 1

                    if field[row][col] == -1:
                        lost = True

                    if clicks == 0 or field[row][col] == 0:
                        uncover_from_pos(row, col, cover_field, field)
                    clicks += 1 

                elif mouse_pressed[2]:
                    if cover_field[row][col] == -2:
                        cover_field[row][col] = 0
                        flags += 1
                    else:
                        flags -= 1
                        cover_field[row][col] = -2

            equal = 0
            if flags == 0:
                for row in field:
                    for col in row:
                        if col == -1:
                            for list1 in cover_field:
                                for val in list1:
                                    if val == -2:
                                        equal += 1
                                        if equal == MINES:
                                            winner = True


        if winner:
            draw(win, field, cover_field)
            draw_win(win, "Winner! Game will restart. Close to not play again.")
            pygame.time.delay(3250)

            field = create_mine_field(ROWS, COLS, MINES)
            cover_field = [[0 for _ in range(COLS)] for _ in range(ROWS)]
            flags = MINES
            clicks = 0
            winner = False
        
        if lost:
            draw(win, field, cover_field)
            draw_lost(win, "You lost!, Try again...")
            pygame.time.delay(2000)

            field = create_mine_field(ROWS, COLS, MINES)
            cover_field = [[0 for _ in range(COLS)] for _ in range(ROWS)]
            flags = MINES
            clicks = 0
            lost = False

        draw(win, field, cover_field)

    pygame.quit()

if __name__ == "__main__":
    main()