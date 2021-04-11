#
# to package: pyinstaller main.py --onefile --icon=icon.ico --name=helix_survivae
#

import sys, os
import curses
import time
from typing import Final
from math import ceil, floor
import json
from random import random

# entity IDs
WALL: Final = 30
DOOR: Final = 10
PLAYER: Final = 9
TRAP_COLLECT: Final = 11
HEALTH_COLLECT: Final = 12
TRAP_SET: Final = 21
TRAP_PLACED: Final = 22

OFFSET_START_X: Final = 0
OFFSET_START_Y: Final = 1
OFFSET_END_X: Final = 0
OFFSET_END_Y: Final = 1

GAME_TIME = 1.0 / 32.0

FLASHER_MAX: Final = 10

HEALTH_MAX: Final = 100
HEALTH_BAR_SIZE: Final = 20

TRAP_DAMAGE: Final = 20
HEAL_AMOUNT: Final = 10

HEALTH_SPAWN_CHANCE = 0.3


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
        0: "`",
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
        TRAP_PLACED: "X"
    }
    k = 0
    cursor_x = 0
    cursor_y = 0
    player_x = 0
    player_y = 0
    tiles = [[0 for i in range(10)] for j in range(10)]
    health = HEALTH_MAX
    score = 0
    is_begin = True

    if os.path.exists("save.json"):
        with open("save.json", "r") as file:
            (tiles, player_x, player_y, health, score) = json.loads(file.read())
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

    while k != ord('q'):
        start = time.perf_counter()

        # Frame limiter
        if time_acc >= GAME_TIME:
            fps = 1 / time_acc
            time_acc -= GAME_TIME

            # Initialization
            stdscr.clear()
            height, width = stdscr.getmaxyx()

            t_h_max = height - OFFSET_START_Y - OFFSET_END_Y
            t_w_max = width - OFFSET_START_X - OFFSET_END_X

            tiles = resize(tiles, t_h_max, t_w_max)

            if health <= 0:
                health = HEALTH_MAX
                score = 0
                tiles = [[0 for i in range(t_h_max)] for j in range(t_w_max)]
                is_begin = True

            if is_begin:
                player_x = round(t_w_max/2)
                player_y = round(t_h_max/2)
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

            target_x = clamp(target_x, 0, t_w_max-1)
            target_y = clamp(target_y, 0, t_h_max-1)

            if tiles[target_x][target_y] < WALL:
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
            elif k == ord(' '):
                tiles[clamp(player_x + 1, OFFSET_START_X, t_w_max-1)][player_y] = 9
                tiles[clamp(player_x - 1, OFFSET_START_X, t_w_max-1)][player_y] = 9
                tiles[player_x][clamp(player_y + 1, OFFSET_START_Y, t_h_max-1)] = 9
                tiles[player_x][clamp(player_y - 1, OFFSET_START_Y, t_h_max-1)] = 9

            # randomized spawn
            if random() * 100 <= HEALTH_SPAWN_CHANCE:
                x, y = floor(random() * t_w_max), floor(random() * t_h_max)
                if tiles[x][y] < PLAYER:
                    tiles[x][y] = HEALTH_COLLECT

            # damage logic
            if 0 <= tiles[player_x][player_y] <= PLAYER:
                tiles[player_x][player_y] = PLAYER
            elif tiles[player_x][player_y] == TRAP_SET:
                health -= TRAP_DAMAGE
                tiles[player_x][player_y] = PLAYER
            elif tiles[player_x][player_y] == HEALTH_COLLECT:
                health = min(health + HEAL_AMOUNT, HEALTH_MAX)
                tiles[player_x][player_y] = PLAYER

            # health and inventory eventually
            player_info = f"HP: [{'#' * ceil(health/HEALTH_MAX * HEALTH_BAR_SIZE)}{'-' * floor((HEALTH_MAX-health)/HEALTH_MAX * HEALTH_BAR_SIZE)}] {health:03}"
            score_bar = f" | SCORE: {score:010}"
            stdscr.addstr(0, 1, player_info, curses.color_pair(8))
            stdscr.addstr(0, len(player_info) + 1, score_bar, curses.color_pair(9))

            # debug info maybe?
            status_bar = f"Width: {width}, Height: {height}, pressed key: {k:03}, fps: {fps:.2f} (target is 30), pos: x:{player_x}/y:{player_y}"
            stdscr.addstr(height - 1, 0, status_bar, curses.color_pair(1))

            # draw map
            for i in range(0, t_w_max):
                for j in range(0, t_h_max):
                    tile_id = tiles[i][j]
                    # tile state decrement
                    tiles[i][j] = tile_id - 1 if 0 < tile_id <= PLAYER or (tile_id == TRAP_PLACED and (i != player_x or j != player_y)) else tile_id
                    tile_id = tiles[i][j]
                    stdscr.addstr(j+OFFSET_START_Y, i+OFFSET_START_X, char_map[tile_id], curses.color_pair(get_color_pair_id(tile_id)))

            if flasher > 2:
                stdscr.addstr(cursor_y, cursor_x, char_map[PLAYER], curses.color_pair(get_color_pair_id(PLAYER)))
            flasher = flasher - 1 if flasher > 0 else FLASHER_MAX

            stdscr.move(0, 0)

            # Refresh the screen
            stdscr.refresh()

            # get next input
            k = stdscr.getch()

        time.sleep(0.0001)
        frame_time = time.perf_counter() - start
        time_acc += frame_time

    with open("save.json", "w") as file:
        file.write(json.dumps((tiles, player_x, player_y, health, score)))


def main():
    curses.wrapper(draw_menu)


if __name__ == "__main__":
    main()
