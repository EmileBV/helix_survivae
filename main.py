#
# to package: pyinstaller main.py --onefile --icon=icon.ico --name=helix_survivae
#

import sys, os
import curses
import time


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


def is_arrow(key):
    return 258 <= key <= 261


def setup_colors():
    # start and setup colors
    curses.start_color()
    curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
    curses.init_pair(2, 3, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_BLACK)
    curses.init_pair(4, 6, curses.COLOR_BLACK)
    curses.init_pair(5, 8, curses.COLOR_BLACK)


def get_color_pair_id(obj_id):
    if obj_id == 0:
        return 3
    elif 2 <= obj_id < 9:
        return 4
    elif obj_id == 9:
        return 2
    elif obj_id == 10:
        return 5
    else:
        return 1


def draw_menu(stdscr):
    char_map = {
        0: " ",
        1: "*",
        2: "*",
        3: "o",
        4: "o",
        5: "O",
        6: "O",
        7: "0",
        8: "0",
        9: "@",
        10: "W"
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
    frame_time = 0.1
    game_time = 1.0 / 30.0
    time_acc = game_time

    while k != ord('q'):
        start = time.perf_counter()

        # Frame limiter
        if time_acc >= game_time:
            time_acc -= game_time

            # Initialization
            stdscr.clear()
            height, width = stdscr.getmaxyx()

            resize(tiles, height, width)

            if k == curses.KEY_DOWN:
                cursor_y = cursor_y + 1
            elif k == curses.KEY_UP:
                cursor_y = cursor_y - 1
            elif k == curses.KEY_RIGHT:
                cursor_x = cursor_x + 1
            elif k == curses.KEY_LEFT:
                cursor_x = cursor_x - 1

            if is_arrow(k):
                last_dir = k

            if k == ord('W'):
                tiles[cursor_x][cursor_y] = 10

            cursor_x = clamp(cursor_x, 0, width - 1)
            cursor_y = clamp(cursor_y, 0, height - 2)

            # debug info maybe?
            status_bar = f"Width: {width}, Height: {height}, pressed key: {k}, fps: {fps}"
            stdscr.addstr(height - 1, 0, status_bar, curses.color_pair(1))

            # stdscr.move(cursor_y, cursor_x)

            if 0 <= tiles[cursor_x][cursor_y] <= 9:
                tiles[cursor_x][cursor_y] = 9

            for i in range(width):
                for j in range(height - 1):
                    # stdscr.addstr(j, 0, ''.join(map(str, [char_map[i[j]] for i in tiles])), curses.color_pair(2))
                    id = tiles[i][j]
                    stdscr.addstr(j, i, char_map[id], curses.color_pair(get_color_pair_id(id)))

            stdscr.addstr(cursor_y, cursor_x, char_map[9], curses.color_pair(get_color_pair_id(9)))

            # decrement
            tiles = [[max(0, i - 1 if 0 < i <= 9 else i) for i in j] for j in tiles]

            stdscr.move(0, 0)

            # Refresh the screen
            stdscr.refresh()

            # get next input
            k = stdscr.getch()

            fps = 1 / (time.perf_counter() - start)

        time.sleep(0.001)
        frame_time = time.perf_counter() - start
        time_acc += frame_time


def main():
    curses.wrapper(draw_menu)


if __name__ == "__main__":
    main()
    # tiles = [[0 for i in range(10)] for j in range(10)]
    # resize(tiles, 30, 50)
    # resize(tiles, 20, 10)
