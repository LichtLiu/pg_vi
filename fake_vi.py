import os
import curses
import time
import re
import threading


# config file
# search
# 快捷鍵


class Editor:
    def __init__(self):
        self.__dir_path = os.getcwd()
        self.__stdscr = curses.initscr()

        curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)
        curses.curs_set(0)

    def main(self):
        menu = [
            "File list in current dir",
            "Create new file",
            "Open other dir",
            "Open ignore file",
            "About",
            "Exit",
        ]

        self.__print_menu(menu)

        # control list
        cursor_idx = 0

        functions = {
            0: self.__display_file_list_page,
            1: self.__display_new_file_page,
            2: self.__display_get_new_file_path_page,
            3: self.__open_ignore_file,
            4: self.__display_about_page,
        }

        while True:
            key = self.__stdscr.getch()

            if key == curses.KEY_UP:
                if cursor_idx == 0:  # hit ceiling
                    cursor_idx = len(menu) - 1
                else:
                    cursor_idx -= 1
            elif key == curses.KEY_DOWN:
                if cursor_idx == len(menu) - 1:  # hit bottom
                    cursor_idx = 0
                else:
                    cursor_idx += 1
            elif key == curses.KEY_ENTER or key in [10, 13]:
                if cursor_idx == 5:
                    break
                else:
                    functions[cursor_idx]()
            else:
                print("\a")

            self.__print_menu(menu, cursor_idx)

    # display functions
    def __run_edit_view_mode(self, file_name, new=False):
        self.__stdscr.clear()

        if new:
            cursor_idx = {"y": -1, "x": -1}
            content = []
        else:
            cursor_idx = {"y": 0, "x": 0}

            with open(os.path.join(self.__dir_path, file_name)) as f:
                content = [
                    (" " if re.match(r"\s+", line) else line.rstrip())
                    for line in f.readlines()
                ]
                content = [[word for word in line] for line in content]

        space = 2

        def blinks_cursor():  # use in other threading
            t = threading.currentThread()

            while getattr(t, "run", True):
                if content:
                    line_num_len = len(str(len(content)))
                    con_x = line_num_len + space

                    x = cursor_idx["x"]
                    y = cursor_idx["y"]

                    line = content[y]
                    cur_word = line[x]

                    self.__stdscr.addstr(y, con_x, "".join(line))
                    self.__stdscr.addstr(y, con_x + x, cur_word)

                    if t.run is False:
                        break
                    elif x == cursor_idx["x"] and y == cursor_idx["y"]:
                        self.__stdscr.refresh()

                        if x == cursor_idx["x"] and y == cursor_idx["y"]:
                            time.sleep(0.4)
                        else:
                            continue
                    else:
                        continue

                    # fix the display delay
                    if t.run is False:
                        break
                    elif x != cursor_idx["x"] or y != cursor_idx["y"]:
                        continue

                    self.__stdscr.addstr(y, con_x, "".join(line))

                    self.__stdscr.attron(curses.color_pair(1))
                    self.__stdscr.addstr(y, con_x + x, cur_word)
                    self.__stdscr.attroff(curses.color_pair(1))

                    if t.run is False:
                        break
                    elif x == cursor_idx["x"] and y == cursor_idx["y"]:
                        self.__stdscr.refresh()

                        if x == cursor_idx["x"] and y == cursor_idx["y"]:
                            time.sleep(0.4)
                        else:
                            continue
                    else:
                        continue
                else:
                    self.__stdscr.addstr(0, 3, " ")
                    self.__stdscr.refresh()
                    time.sleep(0.4)

                    self.__stdscr.attron(curses.color_pair(1))
                    self.__stdscr.addstr(0, 3, " ")
                    self.__stdscr.attroff(curses.color_pair(1))
                    self.__stdscr.refresh()
                    time.sleep(0.4)

        def print_content(cursor_idx):
            self.__stdscr.clear()
            h, w = self.__stdscr.getmaxyx()
            self.__stdscr.addstr(h - 1, 0, "<NORMAL>")
            file_path = os.path.join(self.__dir_path, file_name)
            self.__stdscr.addstr(h - 1, w - 1 - len(file_path), file_path)

            if content:
                line_num_len = len(str(len(content)))
                con_x = line_num_len + space

                for idx, line in enumerate(content):
                    num_x = line_num_len - len(str(idx + 1))

                    if idx == cursor_idx["y"]:
                        self.__stdscr.addstr(idx, con_x, "".join(line))

                        self.__stdscr.attron(curses.color_pair(1))
                        self.__stdscr.addstr(idx, num_x, str(idx + 1))
                        self.__stdscr.addstr(
                            idx, con_x + cursor_idx["x"], line[cursor_idx["x"]]
                        )
                        self.__stdscr.attroff(curses.color_pair(1))
                    else:
                        self.__stdscr.addstr(idx, num_x, str(idx + 1))
                        self.__stdscr.addstr(idx, con_x, "".join(line))

                    self.__stdscr.addstr(idx, con_x - 1, "|")
            else:
                self.__stdscr.attron(curses.color_pair(1))
                self.__stdscr.addstr(0, 0, "1")
                self.__stdscr.attroff(curses.color_pair(1))
                self.__stdscr.addstr(0, 2, "|")

            self.__stdscr.refresh()

        print_content(cursor_idx)

        t = threading.Thread(target=blinks_cursor)
        t.start()

        while True:
            if content:
                row_amount = len(content) - 1
                current_row_len = len(content[cursor_idx["y"]])

                if cursor_idx["y"] > 0:
                    pre_row_len = len(content[cursor_idx["y"] - 1])
                if cursor_idx["y"] < row_amount and cursor_idx["x"] != -1:
                    next_row_len = len(content[cursor_idx["y"] + 1])

            key = self.__stdscr.getch()

            if key == curses.KEY_UP:
                if content:
                    if cursor_idx["y"] == 0:
                        print("\a")
                    else:
                        if cursor_idx["x"] > pre_row_len - 1:
                            cursor_idx["x"] = pre_row_len - 1
                        cursor_idx["y"] -= 1
            elif key == curses.KEY_DOWN:
                if content:
                    if cursor_idx["y"] == row_amount:
                        print("\a")
                    else:
                        if cursor_idx["x"] > next_row_len - 1:
                            cursor_idx["x"] = next_row_len - 1
                        cursor_idx["y"] += 1
            elif key == curses.KEY_LEFT:
                if content:
                    if cursor_idx["x"] == 0:
                        if cursor_idx["y"] == 0:
                            print("\a")
                        else:
                            cursor_idx["x"] = pre_row_len - 1
                            cursor_idx["y"] -= 1
                    else:
                        cursor_idx["x"] -= 1
            elif key == curses.KEY_RIGHT:
                if content:
                    if cursor_idx["x"] == current_row_len - 1:
                        if cursor_idx["y"] == row_amount:
                            print("\a")
                        else:
                            cursor_idx["y"] += 1
                            cursor_idx["x"] = 0
                    else:
                        cursor_idx["x"] += 1
            elif key == 27:  # KEY_ESCAPE
                t.run = False
                t.join()
                break
            elif key == ord("i"):  # insert mode
                self.__run_edit_insert_mode(file_name, content, cursor_idx)
            else:
                print("\a")

            print_content(cursor_idx)

        self.__display_save_window(file_name, content)

    def __run_edit_insert_mode(self, file_name, content, cursor_idx):
        h, w = self.__stdscr.getmaxyx()
        self.__stdscr.addstr(h - 1, 0, "<INSERT>")

        def print_content(cursor_idx):
            self.__stdscr.clear()
            self.__stdscr.addstr(h - 1, 0, "<INSERT>")
            self.__stdscr.addstr(h - 1, w - 1 - len(file_name), file_name)

            if content:
                line_num_len = len(str(len(content)))
                con_x = line_num_len + 2  # 2 = space

                for idx, line in enumerate(content):
                    num_x = line_num_len - len(str(idx + 1))

                    if idx == cursor_idx["y"]:
                        self.__stdscr.addstr(idx, con_x, "".join(line))

                        self.__stdscr.attron(curses.color_pair(1))
                        self.__stdscr.addstr(idx, num_x, str(idx + 1))
                        self.__stdscr.addstr(
                            idx, con_x + cursor_idx["x"], line[cursor_idx["x"]]
                        )
                        self.__stdscr.attroff(curses.color_pair(1))
                    else:
                        self.__stdscr.addstr(idx, num_x, str(idx + 1))
                        self.__stdscr.addstr(idx, con_x, "".join(line))

                    self.__stdscr.addstr(idx, con_x - 1, "|")
            else:
                self.__stdscr.attron(curses.color_pair(1))
                self.__stdscr.addstr(0, 0, "1")
                self.__stdscr.attroff(curses.color_pair(1))
                self.__stdscr.addstr(0, 2, "|")

            self.__stdscr.refresh()

        while True:
            if content:
                row_amount = len(content) - 1
                current_row_len = len(content[cursor_idx["y"]])
                line = content[cursor_idx["y"]]

                if cursor_idx["y"] > 0:
                    pre_row_len = len(content[cursor_idx["y"] - 1])
                if cursor_idx["y"] < row_amount and content:
                    next_row_len = len(content[cursor_idx["y"] + 1])

            key = self.__stdscr.getch()

            if key == curses.KEY_UP:
                if content:
                    if cursor_idx["y"] == 0:
                        print("\a")
                    else:
                        if cursor_idx["x"] > pre_row_len - 1:
                            cursor_idx["x"] = pre_row_len - 1
                        cursor_idx["y"] -= 1
            elif key == curses.KEY_DOWN:
                if content:
                    if cursor_idx["y"] == row_amount:
                        print("\a")
                    else:
                        if cursor_idx["x"] > next_row_len - 1:
                            cursor_idx["x"] = next_row_len - 1
                        cursor_idx["y"] += 1
            elif key == curses.KEY_LEFT:
                if content:
                    if cursor_idx["x"] == 0:
                        if cursor_idx["y"] == 0:
                            print("\a")
                        else:
                            cursor_idx["x"] = pre_row_len - 1
                            cursor_idx["y"] -= 1
                    else:
                        cursor_idx["x"] -= 1
            elif key == curses.KEY_RIGHT:
                if content:
                    if cursor_idx["x"] == current_row_len - 1:
                        if cursor_idx["y"] == row_amount:
                            print("\a")
                        else:
                            cursor_idx["y"] += 1
                            cursor_idx["x"] = 0
                    else:
                        cursor_idx["x"] += 1
            elif key == curses.KEY_ENTER or key in [10, 13]:
                if content:
                    if cursor_idx["x"] == 0:
                        content.insert(cursor_idx["y"], [" "])
                    else:
                        content.insert(
                            cursor_idx["y"] + 1, [wd for wd in line[cursor_idx["x"] :]]
                        )
                        content[cursor_idx["y"]] = line[: cursor_idx["x"]]
                        cursor_idx["x"] = 0
                    cursor_idx["y"] += 1
                else:
                    content.append([" "])
                    content.append([" "])

                    cursor_idx["x"] = 0
                    cursor_idx["y"] = 1
            elif key == curses.KEY_BACKSPACE or key == 127:
                if content:
                    if cursor_idx["x"] == 0:
                        if len(line) == 1:
                            if cursor_idx["y"] == 0:
                                if "next_row_len" not in locals().keys():
                                    cursor_idx["x"] = -1
                                    cursor_idx["y"] = -1
                            else:
                                cursor_idx["x"] = pre_row_len - 1
                        else:
                            if cursor_idx["y"] == 0:
                                print("\a")
                            else:
                                cur_y_idx = cursor_idx["y"] - 1

                                if content[cur_y_idx] == [" "]:
                                    del content[cur_y_idx][0]
                                    cursor_idx["x"] = 0
                                else:
                                    cursor_idx["x"] = pre_row_len

                                for word in content[cursor_idx["y"]]:
                                    content[cur_y_idx].append(word)

                        if not (cursor_idx["y"] == 0 and current_row_len > 1):
                            del content[cursor_idx["y"]]

                            if not (
                                cursor_idx["y"] == 0
                                and "next_row_len" in locals().keys()
                            ):
                                cursor_idx["y"] -= 1
                    else:
                        del line[cursor_idx["x"] - 1]
                        cursor_idx["x"] -= 1
                else:
                    print("\a")
            elif key == 27:  # KEY_ESCAPE
                break
            else:
                if content:
                    line.insert(cursor_idx["x"], chr(key))
                    cursor_idx["x"] += 1
                else:
                    content.append([chr(key)])
                    cursor_idx["x"] = 0
                    cursor_idx["y"] = 0

            print_content(cursor_idx)

    def __display_about_page(self):
        self.__print_introduction("ㄅㄏ無聊寫的😜(才怪")
        time.sleep(3)

    def __display_file_list_page(self):
        file_list = self.__get_file_list()
        self.__print_menu(file_list)

        cursor_idx = 0

        while True:
            key = self.__stdscr.getch()

            if key == curses.KEY_UP:
                if cursor_idx == 0:  # hit ceiling
                    cursor_idx = len(file_list) - 1
                else:
                    cursor_idx -= 1
            elif key == curses.KEY_DOWN:
                if cursor_idx == len(file_list) - 1:  # hit bottom
                    cursor_idx = 0
                else:
                    cursor_idx += 1
            elif key == curses.KEY_ENTER or key in [10, 13]:
                self.__run_edit_view_mode(file_list[cursor_idx])
            elif key == 27:  # KEY_ESCAPE
                break
            else:
                print("\a")

            self.__print_menu(file_list, cursor_idx)

    def __display_get_new_file_path_page(self):
        while True:
            self.__stdscr.clear()
            self.__stdscr.addstr(0, 0, "Please input new dir path")

            try:
                self.__set_work_dir(self.__get_str())
            except FileNotFoundError:
                self.__stdscr.clear()
                self.__stdscr.addstr(0, 0, "Please input available path!!")
                self.__stdscr.refresh()
                time.sleep(3)
            else:
                break

    def __display_new_file_page(self):
        self.__run_edit_view_mode("unnamed.txt", True)

    # TODO add confirm window
    def __display_save_window(self, file_name, content):
        cursor = 0

        top = "--------------------------------"
        msg = "| Do you want to save changes? |"
        space = "|                              |"
        botton = "--------------------------------"

        options = ["Yes", "No", "Rename"]

        def print_content():
            self.__stdscr.clear()

            h, w = self.__stdscr.getmaxyx()

            y = h // 2
            x = w // 2 - len(msg) // 2

            self.__stdscr.addstr(y - 2, x, top)
            self.__stdscr.addstr(y - 1, x, msg)
            self.__stdscr.addstr(y, x, space)
            self.__stdscr.addstr(y + 1, x, space)
            self.__stdscr.addstr(y + 2, x, botton)

            opt_x = x + 5

            for idx, option in enumerate(options):
                if idx == cursor:
                    self.__stdscr.attron(curses.color_pair(1))
                    self.__stdscr.addstr(y + 1, opt_x - len(option) // 2, option)
                    self.__stdscr.attroff(curses.color_pair(1))
                else:
                    self.__stdscr.addstr(y + 1, opt_x - len(option) // 2, option)
                opt_x += 10

            self.__stdscr.refresh()

        print_content()

        while True:
            key = self.__stdscr.getch()

            if key == curses.KEY_LEFT:
                if cursor > 0:
                    cursor -= 1
                else:
                    cursor = 2
            elif key == curses.KEY_RIGHT:
                if cursor < 2:
                    cursor += 1
                else:
                    cursor = 0
            elif key == curses.KEY_ENTER or key in [10, 13]:
                if cursor == 0:
                    self.__save_file(file_name, content)
                    break
                elif cursor == 1:
                    break
                elif cursor == 2:
                    self.__stdscr.clear()
                    self.__stdscr.addstr(0, 0, "Please inupt new filename")
                    file_name = self.__get_str() + ".txt"
            else:
                print("\a")

            print_content()

    # print functions
    def __print_menu(self, menu, selected_row_idx=0):
        self.__stdscr.clear()
        h, w = self.__stdscr.getmaxyx()

        for idx, row in enumerate(menu):
            y = h // 2 - len(menu) // 2 + idx
            x = w // 2 - len(row) // 2

            if idx == selected_row_idx:
                self.__stdscr.attron(curses.color_pair(1))
                self.__stdscr.addstr(y, x, row)
                self.__stdscr.attroff(curses.color_pair(1))
            else:
                self.__stdscr.addstr(y, x, row)

        self.__stdscr.refresh()

    def __print_introduction(self, content):
        self.__stdscr.clear()
        h, w = self.__stdscr.getmaxyx()

        if type(content) == list:
            for idx, msg in enumerate(content):
                self.__stdscr.addstr(h // 2 + idx, w // 2 - len(msg) // 2, msg)
        elif type(content) == str:
            self.__stdscr.addstr(h // 2, w // 2 - len(content), content)

        self.__stdscr.refresh()

    # set functions
    def __set_work_dir(self, path):
        self.__dir_path = path
        os.chdir(path)

    def __set_ignore_file(self):
        if ".fvignore" not in os.listdir(self.__dir_path):  # file not exsist
            os.system('echo ".fvignore " > .fvignore')

    def __get_file_list(self):
        self.__set_ignore_file()

        with open(os.path.join(self.__dir_path, ".fvignore")) as ig:
            file_list = []
            ignore_list = []
            regex_list = []

            for line in ig.readlines():  # classify using regex or not
                if "*" in line:
                    regex_list.append(line.replace("*", "(.*)").rstrip())
                else:
                    ignore_list.append(line.rstrip())

            for dir in os.listdir(self.__dir_path):
                if os.path.isfile(dir) and dir not in ignore_list:
                    if regex_list:
                        for regex in regex_list:
                            if re.match(regex, dir) is not None:
                                break
                        else:
                            file_list.append(dir)
                    else:
                        file_list.append(dir)

            return file_list

    # else functions
    def __open_ignore_file(self):
        os.system("open .fvignore")

    # TODO fix %
    def __save_file(self, file_name, content):
        if content:
            content = ["".join(line) + "\n" for line in content]
            content[-1] = content[-1][:-1]  # remove extra \n

        with open(os.path.join(self.__dir_path, file_name), "w") as f:
            f.writelines(content)

    def __get_str(self):
        curses.curs_set(1)
        curses.echo()

        string = self.__stdscr.getstr(1, 0)

        curses.noecho()
        curses.curs_set(0)

        return str(string, encoding="utf8")


def main(stdscr):
    test = Editor()
    test.main()


curses.wrapper(main)
