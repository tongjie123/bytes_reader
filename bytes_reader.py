from tkinter import *
from tkinter.filedialog import *
import tkinter.colorchooser as tkColorchooser
import math
import re

class my_bytes_reader():
    root = Tk()
    text = Text(master=root, selectforeground='green', selectbackground='yellow')
    scroll = Scrollbar(master=root)
    frame = Frame(master=root, bg='red')

    label_byte = Label(master=frame, text='字节：0/0')
    entry_search = Entry(master=frame)
    button_prev = Button(master=frame, text='后退')
    button_next = Button(master=frame, text='前进')
    label_search = Label(master=frame, text='0/0')

    menubar = Menu(master=root)
    file_menu = Menu(master=menubar, tearoff=False)
    format_menu = Menu(master=menubar, tearoff=False)
    format_flag = IntVar()
    format_flag.set(1)

    byte_arr = []
    tag_flag = 0

    search_arr = []
    search_i = 0
    search_old = ''

    def __init__(self):
        self.root.title('tj-字节阅读器')
        self.root.geometry('600x500+0+0')
        self.root.resizable(0, 0)

        self.text.config(yscrollcommand=self.scroll.set)
        self.scroll.config(command=self.text.yview)
        self.text.place(x=0, y=0, width=580, height=470)
        self.text.bind('<ButtonRelease-1>', self.create_tag)
        self.text.bind('<Button-3>', self.right_menu)
        self.scroll.place(x=580, y=0, width=20, height=470)
        self.frame.place(x=0, y=470, width=600, height=30)

        self.label_byte.place(x=0, y=0, width=150, height=30)
        self.entry_search.place(x=150, y=0, width=300, height=30)
        self.button_prev.place(x=450, y=0, width=30, height=30)
        self.button_prev.bind('<Button-1>', self.search_prev)
        self.button_next.place(x=480, y=0, width=30, height=30)
        self.button_next.bind('<Button-1>', self.search_next)
        self.label_search.place(x=510, y=0, width=90, height=30)

        self.root.config(menu=self.menubar)
        self.menubar.add_cascade(menu=self.file_menu, label='文件')
        self.menubar.add_cascade(menu=self.format_menu, label='格式')
        self.file_menu.add_command(label='打开', command=self.open_file)
        self.format_menu.add_radiobutton(label='十六进制', variable=self.format_flag, value=1, command=self.update_text)
        self.format_menu.add_radiobutton(label='十进制', variable=self.format_flag, value=2, command=self.update_text)

        self.root.mainloop()
    def open_file(self):
        file_path = askopenfilename()
        if file_path != '':
            self.byte_arr.clear()  # 清空存储的字节内容
            file_byte_read = open(file_path, 'rb')
            while True:
                n = file_byte_read.read(1)
                if n == b'':  # 如果读到文件末尾，跳出
                    break
                self.byte_arr.append(ord(n))
            file_byte_read.close()
            self.update_text()
    def update_text(self):
        self.text.delete('1.0', 'end')  # 每次输出，需要先将之前的输出清空
        if self.format_flag.get() == 1:  # 十六进制
            for i in range(len(self.byte_arr)):
                if i % 10 == 0 and i != 0:
                    self.text.insert('end', '\n')
                if self.byte_arr[i] <= 15:
                    self.text.insert('end', '0x0' + hex(self.byte_arr[i])[2] + '  ')
                else:
                    self.text.insert('end', hex(self.byte_arr[i]) + '  ')
        else:  # 十进制
            for i in range(len(self.byte_arr)):
                if i % 10 == 0 and i != 0:
                    self.text.insert('end', '\n')
                if self.byte_arr[i] <= 9:  # 一位数
                    self.text.insert('end', '  ' + str(self.byte_arr[i]) + '   ')
                elif self.byte_arr[i] <= 99:  # 量位数
                    self.text.insert('end', ' ' + str(self.byte_arr[i]) + '   ')
                else:  # 三位数
                    self.text.insert('end', str(self.byte_arr[i]) + '   ')
        self.update_label_byte()
        self.search()
        self.search_i = 0
        self.search_show()
    def create_tag(self, x):
        try:
            self.tag_flag = self.tag_flag + 1
            self.text.tag_add(self.tag_flag, SEL_FIRST, SEL_LAST)
        except:
            print('没有文本被选中')
        finally:
            # 当鼠标左键在text组件点击释放时，更新label_byte组件的信息，由于text的左键释放事件是已经绑定到create_tag方法，
            # 因此在该方法内衔接调用update_label_byte方法，实现同一事件的多方法绑定
            self.update_label_byte()
    def right_menu(self, x):
        right_menu = Menu(master=self.text, tearoff=False)
        right_menu.add_command(label='设置字体颜色', command=self.set_fg)
        right_menu.add_command(label='设置字体背景色', command=self.set_bg)
        right_menu.post(x.x_root, x.y_root)
    def set_bg(self):
        try:
            self.text.selection_get()  # 尝试获取被选中的文本，如果没有，则直接抛出异常跳过try结构后续代码，事实上形成判断选择文本是否为空的功能
            i = tkColorchooser.askcolor()
            self.text.tag_config(self.tag_flag, background=i[1])
        except:
            print('没有文本被选择，无法设置字体颜色')
    def set_fg(self):
        try:
            self.text.selection_get()  # 尝试获取被选中的文本，如果没有，则直接抛出异常跳过try结构后续代码，事实上形成判断选择文本是否为空的功能
            i = tkColorchooser.askcolor()
            self.text.tag_config(self.tag_flag, foreground=i[1])
        except:
            print('没有文本被选择，无法设置字体颜色')
    def update_label_byte(self):
        row_col = self.text.index('insert').split('.')  # 获取当前光标的位置，例如6.2，值为str类型，调用split方法，返回一个数组['6','2']
        row = int(row_col[0])    # 行信息，最小为1
        col = int(row_col[1])    # 列信息，最小为0，在行的开始位置
        num = (row-1)*10 + math.ceil(col/6) # 光标对应的字节数，一行10个字节，列除以6（十进制和十六进制都是以6个字符为为基本表示单位）向上取整表示当前行第几个字节
        self.label_byte.config(text='字节：' + str(num) + '/' + str(len(self.byte_arr)))
    def search_prev(self, x):
        if self.entry_search.get() == '' or self.text.get('0.0', 'end')=='\n':
            self.label_search.config(text='0/0')
            self.text.tag_delete('selection')
            self.search_i = 0
            self.search_arr.clear()
            self.search_old = self.entry_search.get()
        elif self.entry_search.get() != self.search_old:
            self.search()
            self.search_i = 0
            self.search_show()
        elif len(self.search_arr)>0:
            self.search_i = self.search_i-1
            if self.search_i == -1:
                self.search_i = len(self.search_arr)-1
            self.search_show()
    def search_next(self, x):
        if self.entry_search.get() == '' or self.text.get('0.0', 'end') == '\n':
            self.label_search.config(text='0/0')
            self.text.tag_delete('selection')
            self.search_i = 0
            self.search_arr.clear()
            self.search_old = self.entry_search.get()
        elif self.entry_search.get() != self.search_old:
            self.search_old = self.entry_search.get()
            self.search()
            self.search_i = 0
            self.search_show()
        elif len(self.search_arr) > 0:
            self.search_i = self.search_i + 1
            if self.search_i == len(self.search_arr):
                self.search_i = 0
            self.search_show()
    def search(self):# 当搜索前后不相对
        self.search_arr.clear()
        # 对搜索框内容进行处理，预备三种情形的输入，\x05\x3f，0x050x3D，125;0;15，统一处理为一个数组，元素为十进制数
        t_arr = []

        if re.match(r'^(\\[x|X][0-9A-Fa-f]{2})+$', self.search_old) != None:
            for i in range(len(self.search_old) // 4):
                t_arr.append(int(self.search_old[i * 4 + 2:i * 4 + 4], 16))
        elif re.match(r'^(0[x|X][0-9A-Fa-f]{2})+$', self.search_old) != None:
            for i in range(len(self.search_old) // 4):
                t_arr.append(int(self.search_old[i * 4 + 2:i * 4 + 4], 16))
        elif re.match(r'^([0-9]{1,3})+(;[0-9]{1,3})*$', self.search_old) != None:
            t_str = str(self.search_old).split(';')
            for i in range(len(t_str)):
                t_arr.append(int(t_str[i], 10))
        else:
            print('搜索框输入格式不正确')
        if len(t_arr) != 0:
            for i in range(len(self.byte_arr)):
                for j in range(len(t_arr)):
                    if self.byte_arr[i + j] != t_arr[j]:
                        break
                    if j == len(t_arr) - 1 and self.byte_arr[i + j] == t_arr[j]:
                        self.search_arr.append([i, i + j + 1])
    def search_show(self):
        # 根据当前的匹配结果和匹配结果索引进行显示，显示分为两个，更新label_search组件的信息，以及更新text中的匹配文本
        if len(self.search_arr) == 0:
            self.label_search.config(text='0/0')
            self.text.tag_delete('selection')
        else:
            self.label_search.config(text=str(self.search_i+1)+'/'+str(len(self.search_arr)))
            self.text.tag_delete('selection')

            start = self.search_arr[self.search_i][0]
            end = self.search_arr[self.search_i][1]
            self.text.mark_set('insert', str(end // 10 + 1) + '.' + str(end % 10 * 6))
            self.text.see('insert')
            self.text.tag_add('selection', str(start // 10 + 1) + '.' + str(start % 10 * 6),
                              str(end // 10 + 1) + '.' + str(end % 10 * 6))
            self.text.tag_configure('selection', background='green', foreground='white')
if __name__ == '__main__':
    bytes_reader = my_bytes_reader()