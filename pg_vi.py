"""
    COMMAND
    'cd ..' :   back to the parent directory.
    'cd':       back to home
    'lsfile' :  list all the files under the current location.
    'lsdir' :   list all the directory under the current location.
    'man':      list the instructions 
    'mkfile' :  create a new file.
    'exit' :    shut down the procedure.

"""

import sys

import urwid

from pathlib import Path

import os

from os import walk, listdir

from os.path import isfile, join, isdir



class LineWalker(urwid.ListWalker):
    """ListWalker-compatible class for lazily reading file contents."""

    def __init__(self, name):
        self.file = open(name)
        self.lines = []
        self.focus = 0

    def get_focus(self):
        return self._get_at_pos(self.focus)

    def set_focus(self, focus):
        self.focus = focus
        self._modified()

    def get_next(self, start_from):
        return self._get_at_pos(start_from + 1)

    def get_prev(self, start_from):
        return self._get_at_pos(start_from - 1)

    def read_next_line(self):
        """Read another line from the file."""

        next_line = self.file.readline()

        if not next_line or next_line[-1:] != '\n':
            # no newline on last line of file
            self.file = None
        else:
            # trim newline characters
            next_line = next_line[:-1]

        expanded = next_line.expandtabs()
        edit = urwid.Edit("", expanded, allow_tab=True)
        edit.set_edit_pos(0)
        edit.original_text = next_line
        self.lines.append(edit)

        return next_line


    def _get_at_pos(self, pos):
        """Return a widget for the line number passed."""

        if pos < 0:
            # line 0 is the start of the file, no more above
            return None, None

        if len(self.lines) > pos:
            # we have that line so return it
            return self.lines[pos], pos

        if self.file is None:
            # file is closed, so there are no more lines
            return None, None

        assert pos == len(self.lines), "out of order request?"

        self.read_next_line()

        return self.lines[-1], pos

    def split_focus(self):
        """Divide the focus edit widget at the cursor location."""

        focus = self.lines[self.focus]
        pos = focus.edit_pos
        edit = urwid.Edit("",focus.edit_text[pos:], allow_tab=True)
        edit.original_text = ""
        focus.set_edit_text(focus.edit_text[:pos])
        edit.set_edit_pos(0)
        self.lines.insert(self.focus+1, edit)

    def combine_focus_with_prev(self):
        """Combine the focus edit widget with the one above."""

        above, ignore = self.get_prev(self.focus)
        if above is None:
            # already at the top
            return

        focus = self.lines[self.focus]
        above.set_edit_pos(len(above.edit_text))
        above.set_edit_text(above.edit_text + focus.edit_text)
        del self.lines[self.focus]
        self.focus -= 1

    def combine_focus_with_next(self):
        """Combine the focus edit widget with the one below."""

        below, ignore = self.get_next(self.focus)
        if below is None:
            # already at bottom
            return

        focus = self.lines[self.focus]
        focus.set_edit_text(focus.edit_text + below.edit_text)
        del self.lines[self.focus+1]


class EditDisplay:
    palette = [
        ('body','default', 'default'),
        ('foot','dark cyan', 'black', 'bold'),
        ('key','light cyan', 'black', 'underline'),
        ]

    footer_text = ('foot', [
        "Text Editor    ",
        ('key', "F5"), " save  ",
        ('key', "F8"), " quit",
        ])

    def __init__(self, name):
        self.save_name = name
        self.walker = LineWalker(name)
        self.listbox = urwid.ListBox(self.walker)
        self.footer = urwid.AttrWrap(urwid.Text(self.footer_text),
            "foot")
        self.view = urwid.Frame(urwid.AttrWrap(self.listbox, 'body'),
            footer=self.footer)

    def main(self):
        self.loop = urwid.MainLoop(self.view, self.palette,
            unhandled_input=self.unhandled_keypress)
        self.loop.run()

    def unhandled_keypress(self, k):
        """Last resort for keypresses."""

        if k == "f5":
            self.save_file()
        elif k == "f8":
            raise urwid.ExitMainLoop()
        elif k == "delete":
            # delete at end of line
            self.walker.combine_focus_with_next()
        elif k == "backspace":
            # backspace at beginning of line
            self.walker.combine_focus_with_prev()
        elif k == "enter":
            # start new line
            self.walker.split_focus()
            # move the cursor to the new line and reset pref_col
            self.loop.process_input(["down", "home"])
        elif k == "right":
            w, pos = self.walker.get_focus()
            w, pos = self.walker.get_next(pos)
            if w:
                self.listbox.set_focus(pos, 'above')
                self.loop.process_input(["home"])
        elif k == "left":
            w, pos = self.walker.get_focus()
            w, pos = self.walker.get_prev(pos)
            if w:
                self.listbox.set_focus(pos, 'below')
                self.loop.process_input(["end"])
        else:
            return
        return True


    def save_file(self):
        """Write the file out to disk."""

        l = []
        walk = self.walker
        for edit in walk.lines:
            # collect the text already stored in edit widgets
            if edit.original_text.expandtabs() == edit.edit_text:
                l.append(edit.original_text)
            else:
                l.append(re_tab(edit.edit_text))

        # then the rest
        while walk.file is not None:
            l.append(walk.read_next_line())

        # write back to disk
        outfile = open(self.save_name, "w")

        prefix = ""
        for line in l:
            outfile.write(prefix + line)
            prefix = "\n"


class Filepath:
    def __init__(self):
        #self.default_path = Path.home()
        #initial path
        self.default_path = Path.cwd()

    '''
        These are a bunch of commands that can be usable

        'cd ..' :   back to the parent directory.
        'cd':       back to home
        'lsfile' :  list all the files under the current location.
        'lsdir' :   list all the directory under the current location.
        'man':      list the instructions 
        'mkfile' :  create a new file.
        'exit' :    shut down the procedure.

    '''        

    def is_command(self, user_command):
        for key in Filepath._command_defaults.keys():
            if user_command == key:
                return True
            else:
                continue


    def execute_command(self, user_command):
        Filepath._command_defaults.get(user_command, lambda: 'Invalid')(self)


    def pre_folder(self):
        self.default_path = Path(os.path.abspath(os.path.dirname(self.default_path)+os.path.sep+"."))

    
    def back_to_home(self):
        self.default_path = Path.home()


    def list_all_file(self):
        onlyfiles = [f for f in listdir(self.default_path) if isfile(join(self.default_path, f))]
        print("="*30)
        for file in onlyfiles:
            print("檔案："+ file)
        print("="*30)


    def list_all_dir(self):
        onlydir = [x for x in listdir(self.default_path) if isdir(join(self.default_path, x))]
        print("="*30)
        for directory in onlydir:
            print("目錄：" + directory)
        print("="*30)


    def display_command_details(self):
        print(__doc__)

    
    def create_new_file(self):
        name = input("請輸入新建檔案名稱( example.txt ):")
        if name == 'exit':
            return False
        else:
            if Filepath.is_exists(self,name):
                print("\n\u26A0WARNING\u26A0==檔案已存在==\u26A0WARNING\u26A0 \n")
                return False
            else:
                option = input("確定新建 "+name+ " 嗎？(y/[n])")
                if option == 'y':
                    Filepath.create_new_file(self, name)
                    os.system('cls' if os.name == 'nt' else 'clear')
                    print("="*20+"\n"+ name +" 新建成功！\n"+"="*20+"\n")
                else:
                    return False


    def exit_the_program(self):
        choice = input("確定要終止程式嗎?(y/[n])")
        if choice == 'y':
            os._exit(0)
        else:
            return False


    _command_defaults = {
        'cd ..':pre_folder,
        'cd':back_to_home,
        'lsfile':list_all_file,
        'lsdir':list_all_dir,
        'man':display_command_details,
        'mkfile':create_new_file,
        'exit':exit_the_program,
    }


    def is_exists(self,path):
        temp_path = self.default_path /path
        if temp_path.exists():
            return True
        else:
            return False


    # is file or path
    def is_files(self,path):
        # path = initial path / diretory's name or file name
        temp_path = self.default_path /path
        if temp_path.is_file():
            return True
        else:
            self.default_path = temp_path
            return False


    def read_file(self,filename):
        with open(self.default_path/filename, mode='r') as fid:
            headers = [line for line in fid ]
        print('\n'.join(headers))


    def create_new_file(self,filename):
        with open(self.default_path/filename, mode='w') as fiw:
            return


    def if_open_file(self, option):
        if option == 'y':
            return True
        else:
            return False    


    def get_file_name(self):
        return self.default_path.name


    def get_fullpath(self, fname):
        print(self.default_path/fname)
        return self.default_path/fname



def re_tab(s):
    """Return a tabbed string from an expanded one."""
    l = []
    p = 0
    for i in range(8, len(s), 8):
        if s[i-2:i] == "  ":
            # collapse two or more spaces into a tab
            l.append(s[p:i].rstrip() + "\t")
            p = i

    if p == 0:
        return s
    else:
        l.append(s[p:])
        return "".join(l)



def main():
    print(__doc__)
    test = Filepath()
    while True:
        print("目前所在絕對路徑:")
        print(test.default_path)

        dir_name_or_command = input("請輸入檔案目錄下之檔名或目錄名稱或操作指令：").strip()
        #if is (command) else is (path/file)
        if test.is_command(dir_name_or_command):
            os.system('cls' if os.name == 'nt' else 'clear')
            command = dir_name_or_command
            test.execute_command(command)
        else:
            os.system('cls' if os.name == 'nt' else 'clear')

            dir_name=dir_name_or_command
            #if (file) or (path) is exist
            if test.is_exists(dir_name):
                if test.is_files(dir_name):
                    #if open file or not
                    if test.if_open_file(input("是否要開啟"+dir_name+"（y/[n]）")):
                        try:
                            #name = sys.argv[1]
                            name = test.get_fullpath(dir_name)
                            assert open(name, "a")
                        except:
                            sys.stderr.write(__doc__)
                            return
                        EditDisplay(name).main()


            else:
                os.system('cls' if os.name == 'nt' else 'clear')
                print('\u26A0WARNING\u26A0==檔案目錄下沒有此檔案或路徑==\u26A0WARNING\u26A0 \n')



if __name__=="__main__":
    main()