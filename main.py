#
# to package: pyinstaller main.py --onefile --icon=icon.ico --name=helix_survivae
#

import sys, os
import curses
import time
from typing import Final
from math import ceil, floor
import pickle
from random import random, randint
from copy import copy, deepcopy

from Enemy import Enemy

# entity IDs
WALL: Final = 30
DOOR: Final = 10
PLAYER: Final = 9
TRAP_COLLECT: Final = 11
HEALTH_COLLECT: Final = 12
TRAP_SET: Final = 21
TRAP_PLACED: Final = 22
ENEMY_SMALL: Final = 23

OFFSET_START_X: Final = 0
OFFSET_START_Y: Final = 1
OFFSET_END_X: Final = 0
OFFSET_END_Y: Final = 1

TARGET_FPS: Final = 30
GAME_TIME: Final = 1.0 / TARGET_FPS

FLASHER_MAX: Final = 10

HEALTH_MAX: Final = 100
HEALTH_BAR_SIZE: Final = 20

TRAP_DAMAGE: Final = 15
HEAL_AMOUNT: Final = 10
ENEMY_SMALL_DAMAGE: Final = 20

HEALTH_SPAWN_CHANCE: Final = 0.3
ENEMY_SPAWN_CHANCE: Final = 0.4

DESTROY_DELAY: Final = 20


def clamp(val, min_val, max_val):
    return max(min_val, min(max_val, val))


def resize(list2d: list, new_height: int, new_width: int):
    cur_width = len(list2d)
    cur_height = len(list2d[0])

    if cur_width > new_width:
        list2d = list2d[:new_width - cur_width]
    elif cur_width < new_width:
        list2d.extend([[0 for i in range(cur_height)] for j in range(new_width - cur_width)])

    cur_width = len(list2d)

    if cur_height > new_height:
        for i in range(cur_width):
            list2d[i] = list2d[i][:new_height - cur_height]
    elif cur_height < new_height:
        for i in range(cur_width):
            list2d[i].extend([0 for i in range(new_height)])

    return list2d


def is_arrow(key):
    return 258 <= key <= 261


def setup_colors():
    # start and setup colors
    curses.start_color()
    curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
    curses.init_pair(2, 3, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_WHITE, curses.COLOR_BLACK)
    curses.init_pair(4, 6, curses.COLOR_BLACK)
    curses.init_pair(5, 8, curses.COLOR_BLACK)
    curses.init_pair(6, 9, curses.COLOR_BLACK)
    curses.init_pair(7, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(8, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(9, curses.COLOR_BLUE, curses.COLOR_BLACK)


def get_color_pair_id(obj_id):
    if obj_id == 0:
        return 3
    elif 2 <= obj_id < PLAYER:
        return 4
    elif obj_id == PLAYER:
        return 2
    elif obj_id == WALL:
        return 5
    elif obj_id == DOOR:
        return 6
    elif TRAP_SET <= obj_id < WALL:
        return 7
    elif obj_id == HEALTH_COLLECT:
        return 8
    else:
        return 1


def draw_menu(stdscr):
    char_map = {
        0: " ",
        1: "•",
        2: "•",
        3: "•",
        4: "•",
        5: "•",
        6: "•",
        7: "•",
        8: "@",
        PLAYER: "@",
        DOOR: "D",
        WALL: "W",
        TRAP_COLLECT: "x",
        HEALTH_COLLECT: "+",
        TRAP_SET: "X",
        TRAP_PLACED: "X",
        ENEMY_SMALL: "o"
    }
    k = 0
    cursor_x = 0
    cursor_y = 0
    player_x = 0
    player_y = 0
    tiles = [[0 for i in range(10)] for j in range(10)]
    health = HEALTH_MAX
    score = 0
    hiscore = 0
    is_begin = True
    quitting = False

    if os.path.exists("save"):
        with open("save", "rb") as file:
            (tiles, player_x, player_y, health, score, hiscore) = pickle.loads(file.read())
            is_begin = False

    last_dir = 0

    # Clear and refresh the screen for a blank canvas
    stdscr.clear()
    stdscr.refresh()

    stdscr.nodelay(1)  # set getch() non-blocking

    setup_colors()

    fps = 0
    time_acc = GAME_TIME

    flasher = FLASHER_MAX

    destroy_timer = 0

    running = True
    paused = True

    while running:
        start = time.perf_counter()

        # Frame limiter
        if time_acc >= GAME_TIME:
            fps = 1 / time_acc
            time_acc -= GAME_TIME
            height, width = stdscr.getmaxyx()

            if k == 27:
                paused = not paused
                quitting = False

            if paused:
                stdscr.addstr(3, 3,  "========[MENU]========", curses.color_pair(1))
                stdscr.addstr(4, 3,  "=                    =", curses.color_pair(1))
                stdscr.addstr(5, 3,  "=  [Esc] Continue    =", curses.color_pair(1))
                stdscr.addstr(6, 3,  "=   [Q]  Save&Quit   =", curses.color_pair(1))
                stdscr.addstr(7, 3,  "=   [R]  Restart     =", curses.color_pair(1))
                stdscr.addstr(8, 3,  "=                    =", curses.color_pair(1))
                stdscr.addstr(9, 3,  "=====[Game Facts]=====", curses.color_pair(1))
                stdscr.addstr(10, 3,  "=                    =", curses.color_pair(1))
                stdscr.addstr(11, 3, "=  @ -> that's you   =", curses.color_pair(1))
                stdscr.addstr(12, 3, "=  W -> Wall [W] key =", curses.color_pair(1))
                stdscr.addstr(13, 3, "=  D -> Door [D] key =", curses.color_pair(1))
                stdscr.addstr(14, 3, "=  X -> Trap [X] key =", curses.color_pair(1))
                stdscr.addstr(15, 3, "=  + -> Health       =", curses.color_pair(1))
                stdscr.addstr(16, 3, "=  o -> Bad stuff    =", curses.color_pair(1))
                stdscr.addstr(17, 3, "=  [Space] -> break  =", curses.color_pair(1))
                stdscr.addstr(18, 3, "=                    =", curses.color_pair(1))
                stdscr.addstr(19, 3, "=====[HIGH SCORE]=====", curses.color_pair(1))
                stdscr.addstr(20, 3, f"=     {hiscore:010}     =", curses.color_pair(1))
                stdscr.addstr(21, 3, "======================", curses.color_pair(1))

                if quitting:
                    stdscr.addstr(3, 3, "======[QUITTING]======", curses.color_pair(7))
                    stdscr.addstr(4, 3, "=                    =", curses.color_pair(7))
                    stdscr.addstr(5, 3, "=   ARE YOU SURE?    =", curses.color_pair(7))
                    stdscr.addstr(6, 3, "=  (will save game)  =", curses.color_pair(7))
                    stdscr.addstr(7, 3, "= [Q] yes | [Esc] no =", curses.color_pair(7))
                    stdscr.addstr(8, 3, "=                    =", curses.color_pair(7))
                    if k == ord('q'):
                        running = False
                else:
                    if k == ord('q'):
                        quitting = True
                    elif k == ord('r'):
                        is_begin = True
                        paused = False


                stdscr.move(0, 0)
                stdscr.refresh()
                # get next input
                k = stdscr.getch()
                continue


            # Initialization
            stdscr.clear()

            t_h_max = height - OFFSET_START_Y - OFFSET_END_Y
            t_w_max = width - OFFSET_START_X - OFFSET_END_X

            tiles = resize(tiles, t_h_max, t_w_max)

            if health <= 0:
                is_begin = True

            if is_begin:
                player_x = round(t_w_max / 2)
                player_y = round(t_h_max / 2)
                health = HEALTH_MAX
                score = 0
                tiles = [[0 for i in range(t_h_max)] for j in range(t_w_max)]
                is_begin = False

            target_x, target_y = player_x, player_y
            if k == curses.KEY_DOWN:
                target_y = player_y + 1
            elif k == curses.KEY_UP:
                target_y = player_y - 1
            elif k == curses.KEY_RIGHT:
                target_x = player_x + 1
            elif k == curses.KEY_LEFT:
                target_x = player_x - 1

            target_x = clamp(target_x, 0, t_w_max - 1)
            target_y = clamp(target_y, 0, t_h_max - 1)

            if int(tiles[target_x][target_y]) < WALL:
                player_x, player_y = target_x, target_y
                cursor_x, cursor_y = player_x + OFFSET_START_X, player_y + OFFSET_START_Y

            if is_arrow(k):
                last_dir = k

            # building logic
            if k == ord('w'):
                tiles[player_x][player_y] = WALL
            elif k == ord('d'):
                tiles[player_x][player_y] = DOOR
            elif k == ord('x'):
                tiles[player_x][player_y] = TRAP_PLACED
            elif k == ord(' ') and destroy_timer <= 0:
                tiles[clamp(player_x + 1, OFFSET_START_X, t_w_max - 1)][player_y] = 9
                tiles[clamp(player_x - 1, OFFSET_START_X, t_w_max - 1)][player_y] = 9
                tiles[player_x][clamp(player_y + 1, OFFSET_START_Y, t_h_max - 1)] = 9
                tiles[player_x][clamp(player_y - 1, OFFSET_START_Y, t_h_max - 1)] = 9
                tiles[player_x][player_y] = 9
                destroy_timer = DESTROY_DELAY

            # randomized spawn
            if random() * 100 <= HEALTH_SPAWN_CHANCE:
                x, y = floor(random() * t_w_max), floor(random() * t_h_max)
                if tiles[x][y] < PLAYER:
                    tiles[x][y] = HEALTH_COLLECT
            # fps = ENEMY_SPAWN_CHANCE * (1 + (score/1000))
            if random() * 100 <= ENEMY_SPAWN_CHANCE * (1 + (score / 1000)):
                # 1: top | 2: right | 3: bottom | 4: left
                side = randint(1, 4)
                x, y = 0, 0
                if side == 1:
                    x, y = floor(random() * t_w_max), 0
                elif side == 2:
                    x, y = t_w_max - 1, floor(random() * t_h_max)
                elif side == 3:
                    x, y = floor(random() * t_w_max), t_h_max - 1
                elif side == 4:
                    x, y = 0, floor(random() * t_h_max)
                if int(tiles[x][y]) != ENEMY_SMALL:
                    tiles[x][y] = Enemy(ENEMY_SMALL)

            # enemy movement logic
            for i in range(0, t_w_max):
                for j in range(0, t_h_max):
                    tile = tiles[i][j]
                    if isinstance(tile, Enemy):
                        store = True
                        x, y = i, j
                        if tile.moving_x():
                            t_x = x + tile.get_x_dir()
                            if t_x < 0 or t_w_max - 1 < t_x:
                                tile.flip_x()
                            else:
                                t_id = int(tiles[t_x][y])
                                if t_id == WALL or t_id == DOOR or t_id == ENEMY_SMALL:
                                    tile.flip_x()
                                    if t_id == DOOR:
                                        tiles[t_x][y] = 9
                                elif int(tiles[t_x][y]) < PLAYER or int(tiles[t_x][y]) == TRAP_SET:
                                    x = t_x
                        if tile.moving_y():
                            t_y = y + tile.get_y_dir()
                            if t_y < 0 or t_h_max - 1 < t_y:
                                tile.flip_y()
                            else:
                                t_id = int(tiles[x][t_y])
                                if t_id == WALL or t_id == DOOR or t_id == ENEMY_SMALL:
                                    tile.flip_y()
                                    if t_id == DOOR:
                                        tiles[x][t_y] = 9
                                elif t_id < PLAYER or t_id == TRAP_SET:
                                    y = t_y
                        tiles[i][j] = 8

                        if int(tiles[x][y]) == TRAP_SET:
                            del tile
                            if randint(0, 2) == 0:
                                tiles[x][y] = 9
                            score += 100
                            store = False
                        elif x == player_x and y == player_y:
                            del tile
                            tiles[x][y] = 9
                            health -= ENEMY_SMALL_DAMAGE
                            store = False
                        if store:
                            tiles[x][y] = tile

            # damage logic
            if 0 <= int(tiles[player_x][player_y]) <= PLAYER:
                tiles[player_x][player_y] = PLAYER
            elif int(tiles[player_x][player_y]) == TRAP_SET:
                health -= TRAP_DAMAGE
                tiles[player_x][player_y] = PLAYER
            elif int(tiles[player_x][player_y]) == HEALTH_COLLECT:
                health = min(health + HEAL_AMOUNT, HEALTH_MAX)
                tiles[player_x][player_y] = PLAYER

            # health and inventory eventually
            player_info = f"HP: [{'#' * ceil(health / HEALTH_MAX * HEALTH_BAR_SIZE)}{'-' * floor((HEALTH_MAX - health) / HEALTH_MAX * HEALTH_BAR_SIZE)}] {health:03}"
            score_bar = f" | SCORE: {score:010}"
            destroy_bar = f" | BREAK: [{'#' * ceil(destroy_timer / DESTROY_DELAY * 6)}{'-' * floor((DESTROY_DELAY - destroy_timer) / DESTROY_DELAY * 6)}]"

            if width < len(player_info) + len(destroy_bar) + len(destroy_bar) + 3:
                stdscr.addstr(3, 3, "====[ALERT]=====", curses.color_pair(1))
                stdscr.addstr(4, 3, "=   PLEASE     =", curses.color_pair(1))
                stdscr.addstr(5, 3, "=   MAKE       =", curses.color_pair(1))
                stdscr.addstr(6, 3, "=   WINDOW     =", curses.color_pair(1))
                stdscr.addstr(7, 3, "=   WIDER     =", curses.color_pair(1))
                stdscr.addstr(8, 3, "================", curses.color_pair(1))

                stdscr.move(0, 0)
                stdscr.refresh()
                # get next input
                k = stdscr.getch()
                continue

            stdscr.addstr(0, 1, player_info, curses.color_pair(8))
            stdscr.addstr(0, len(player_info) + 1, destroy_bar, curses.color_pair(9))
            stdscr.addstr(0, len(player_info) + len(destroy_bar) + 1, score_bar, curses.color_pair(3))
            destroy_timer = max(0, destroy_timer - 1)
            # debug info maybe?
            status_bar = f"Width: {width}, Height: {height}, fps: {fps:.2f} (target is {TARGET_FPS})"
            stdscr.addstr(height - 1, 0, status_bar, curses.color_pair(1))

            # draw map
            for i in range(0, t_w_max):
                for j in range(0, t_h_max):
                    tile_id = int(tiles[i][j])
                    # tile state decrement
                    if 0 < tile_id <= PLAYER or (tile_id == TRAP_PLACED and (i != player_x or j != player_y)):
                        tiles[i][j] = tile_id - 1
                        tile_id = int(tiles[i][j])
                    stdscr.addstr(j + OFFSET_START_Y, i + OFFSET_START_X, char_map[tile_id],
                                  curses.color_pair(get_color_pair_id(tile_id)))

            if flasher > 2:
                stdscr.addstr(cursor_y, cursor_x, char_map[PLAYER], curses.color_pair(get_color_pair_id(PLAYER)))
            flasher = flasher - 1 if flasher > 0 else FLASHER_MAX

            if hiscore < score:
                hiscore = score

            stdscr.move(0, 0)

            # Refresh the screen
            stdscr.refresh()

            # get next input
            k = stdscr.getch()

        time.sleep(0.0001)
        frame_time = time.perf_counter() - start
        time_acc += frame_time

    with open("save", "wb") as file:
        file.write(pickle.dumps((tiles, player_x, player_y, health, score, hiscore)))


def main():
    curses.wrapper(draw_menu)


if __name__ == "__main__":
    main()
