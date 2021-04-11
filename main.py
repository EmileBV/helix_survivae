#
# to package: pyinstaller main.py --onefile --icon=icon.ico --name=helix_survivae
#

import sys, os
import curses
import time
from typing import Final
from math import ceil, floor

# entity IDs
WALL: Final = 30
DOOR: Final = 10
PLAYER: Final = 9
TRAP_COLLECT: Final = 11
TRAP_SET: Final = 21

OFFSET_START_X: Final = 0
OFFSET_START_Y: Final = 1
OFFSET_END_X: Final = 0
OFFSET_END_Y: Final = 1

GAME_TIME = 1.0 / 32.0

FLASHER_MAX: Final = 10

HEALTH_MAX: Final = 100


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
        TRAP_SET: "X"
    }
    k = 0
    cursor_x = 0
    cursor_y = 0
    tiles = [[0 for i in range(10)] for j in range(10)]
    last_dir = 0

    # Clear and refresh the screen for a blank canvas
    stdscr.clear()
    stdscr.refresh()

    stdscr.nodelay(1)  # set getch() non-blocking

    setup_colors()

    fps = 0
    time_acc = GAME_TIME

    flasher = FLASHER_MAX

    health = HEALTH_MAX

    while k != ord('q'):
        start = time.perf_counter()

        # Frame limiter
        if time_acc >= GAME_TIME:
            fps = 1 / time_acc
            time_acc -= GAME_TIME

            # Initialization
            stdscr.clear()
            height, width = stdscr.getmaxyx()

            t_h_max = height - OFFSET_START_Y - OFFSET_END_Y+1
            t_w_max = width - OFFSET_START_X - OFFSET_END_X

            tiles = resize(tiles, t_h_max, t_w_max)

            target_x, target_y = cursor_x, cursor_y
            if k == curses.KEY_DOWN:
                target_y = cursor_y + 1
            elif k == curses.KEY_UP:
                target_y = cursor_y - 1
            elif k == curses.KEY_RIGHT:
                target_x = cursor_x + 1
            elif k == curses.KEY_LEFT:
                target_x = cursor_x - 1

            target_x = clamp(target_x, OFFSET_START_X, t_w_max-1)
            target_y = clamp(target_y, OFFSET_START_Y, t_h_max-1)

            if tiles[target_x][target_y] < WALL:
                cursor_x, cursor_y = target_x, target_y

            if is_arrow(k):
                last_dir = k

            if k == ord('w'):
                tiles[cursor_x][cursor_y] = WALL
            elif k == ord('d'):
                tiles[cursor_x][cursor_y] = DOOR
            elif k == ord('x'):
                tiles[cursor_x][cursor_y] = TRAP_SET
            elif k == ord(' '):
                tiles[clamp(cursor_x + 1, OFFSET_START_X, t_w_max-1)][cursor_y] = 9
                tiles[clamp(cursor_x - 1, OFFSET_START_X, t_w_max-1)][cursor_y] = 9
                tiles[cursor_x][clamp(cursor_y + 1, OFFSET_START_Y, t_h_max-1)] = 9
                tiles[cursor_x][clamp(cursor_y - 1, OFFSET_START_Y, t_h_max-1)] = 9

            if 0 <= tiles[cursor_x][cursor_y] <= PLAYER:
                tiles[cursor_x][cursor_y] = PLAYER

            # health and inventory eventually
            player_info = f"HP: [{'#' * ceil(health/10)}{'-' * floor((HEALTH_MAX-health)/10)}] {health:03}"
            stdscr.addstr(0, 1, player_info, curses.color_pair(1))

            # debug info maybe?
            status_bar = f"Width: {width}, Height: {height}, pressed key: {k:03}, fps: {fps:.2f} (target is 30)"
            stdscr.addstr(height - 1, 0, status_bar, curses.color_pair(1))

            # decrement
            tiles = [[max(0, i - 1 if 0 < i <= PLAYER else i) for i in j] for j in tiles]

            # draw map
            for i in range(OFFSET_START_X, t_w_max):
                for j in range(OFFSET_START_Y, t_h_max):
                    tile_id = tiles[i][j]
                    stdscr.addstr(j, i, char_map[tile_id], curses.color_pair(get_color_pair_id(tile_id)))

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


def main():
    curses.wrapper(draw_menu)


if __name__ == "__main__":
    main()
    # tiles = [[0 for i in range(10)] for j in range(10)]
    # resize(tiles, 30, 50)
    # resize(tiles, 20, 10)
