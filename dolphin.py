"""
COMMAND
'exit' : close the program
'lsdir' : list all the directory under the current path
'lsfile' : list all the files under the current path
'man': list the command menu 
'cd ..' : back to the parent directory
"""


from pathlib import Path
import os
from os import walk, listdir
from os.path import isfile, join, isdir
from subprocess import call


class Filepath:
    def __init__(self):
        #self.default_path = Path.home()
        #初始化路徑
        self.default_path = Path.cwd()
        #初始化暫存檔案內容
        self.temp_file_content = '' 

    def is_exists(self,path):
        temp_path = self.default_path /path
        if temp_path.exists():
            return True
        else:
            return False

    #判斷是否檔案還是路徑
    def is_files(self,path):
        # path = 初始路徑/輸入的路徑
        temp_path = self.default_path /path
        # 判斷路徑是否存在
        if temp_path.is_file():
            return True
        else:
            self.default_path = temp_path
            return False

    #判斷是否為指令
    def is_command(self, user_command):
        command_list = ['cd ..', 'lsfile', 'lsdir', 'exit','man', 'mkdir']
        for command in command_list:
            if command == user_command :
                return True
            else:
                continue
            
    #指令集
    def operate_command(self, command):
        #上一個目錄
        if command == 'cd ..':
            self.default_path = Path(os.path.abspath(os.path.dirname(self.default_path)+os.path.sep+"."))
        #列出目錄下的所有檔案
        elif command == 'lsfile':
            onlyfiles = [f for f in listdir(self.default_path) if isfile(join(self.default_path, f))]
            print("======================================")
            for file in onlyfiles:
                print("檔案："+ file)
            print("======================================")
        #列出目錄下所有目錄
        elif command =='lsdir':
            onlydir = [x for x in listdir(self.default_path) if isdir(join(self.default_path, x))]
            print("======================================")
            for directory in onlydir:
                print("目錄：" + directory)
            print("======================================")

        #列出指令表
        elif command == 'man':
            print(__doc__)

        elif command == 'exit':
            choice = input("確定要終止程式嗎?(y/[n])")
            if choice == 'y':
                os._exit(0)
            else:
                return False
 
    def read_file(self,file_name):
        n = 0
        with open(self.default_path/file_name, mode='r') as fid:
            print(''.join([str(x+1)+' '+ y for (x,y) in list(enumerate(fid.readlines()))]))


    def if_open_file(self, option):
        if option == 'y':
            return True
        else:
            return False    


    def get_file_name(self):
        return self.default_path.name




if __name__ == '__main__':
    test = Filepath()
    os.system('cls' if os.name == 'nt' else 'clear')
    print(__doc__)

    while True:
        print("目前所在絕對路徑:")
        print(test.default_path)

        dir_name_or_command = input("請輸入檔案目錄下之檔名或目錄名稱或操作指令：").strip()
        #判斷是復為指令
        if test.is_command(dir_name_or_command):
            os.system('cls' if os.name == 'nt' else 'clear')
            command = dir_name_or_command
            test.operate_command(command)
        else:
            os.system('cls' if os.name == 'nt' else 'clear')
            #是檔案或目錄
            dir_name=dir_name_or_command
            #判斷是否為檔案目錄
            if test.is_exists(dir_name):
                #是檔案
                if test.is_files(dir_name):
                    #選擇開啟或不開啟檔案
                    if test.if_open_file(input("是否要開啟"+dir_name+"（y/[n]）")):
                        test.read_file(dir_name)
                        break
        
    #編輯模式


            else:
                os.system('cls' if os.name == 'nt' else 'clear')
                print('\u26A0WARNING\u26A0:檔案目錄下沒有此檔案或路徑\n')


    
