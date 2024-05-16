import shutil
import tkinter
from tkinter import filedialog
import os
import threading
import filecmp

src_dir = ''
bak_dir = ''
file_list = []


def src_dir_open():
    _dir = filedialog.askdirectory()
    if _dir:
        global src_dir
        src_dir = _dir
        log_text.insert(tkinter.END, '##### 原始目录 - {}\n'.format(src_dir))


def bak_dir_open():
    _dir = filedialog.askdirectory()
    if _dir:
        global bak_dir
        bak_dir = _dir
        log_text.insert(tkinter.END, '##### 备份目录 - {}\n'.format(bak_dir))


def on_key_press(event):
    return 'break'


def run():
    if src_dir == '':
        log_text.insert(tkinter.END, '##### 未选择原始目录\n')
        return
    if bak_dir == '':
        log_text.insert(tkinter.END, '##### 未选择备份目录\n')
        return
    thread = threading.Thread(target=do_run)
    thread.start()


def do_run():
    try:
        log_text.insert(tkinter.END, '##### 执行开始\n')
        global file_list
        file_list = []
        get_file_list(src_dir)
        log_text.insert(tkinter.END, '##### 原始目录读取完毕\n')
        file_len = len(file_list)
        for i in range(0, file_len):
            file_i = file_list[i]
            if not os.path.exists(file_i):
                continue
            for j in range(i + 1, file_len):
                file_j = file_list[j]
                if not os.path.exists(file_j):
                    continue
                if os.path.dirname(file_i) != os.path.dirname(file_j):
                    continue
                if not filecmp.cmp(file_i, file_j):
                    continue
                log_text.insert(tkinter.END, '① {}\n'.format(file_i))
                log_text.insert(tkinter.END, '② {}\n'.format(file_j))
                if os.path.getmtime(file_i) > os.path.getmtime(file_j):
                    move_file(file_j)
                elif os.path.getmtime(file_i) < os.path.getmtime(file_j):
                    move_file(file_i)
                    break
                else:
                    if file_i > file_j:
                        move_file(file_j)
                    else:
                        move_file(file_i)
                        break
    except Exception as e:
        log_text.insert(tkinter.END, '##### {}\n'.format(e))
    finally:
        log_text.insert(tkinter.END, '##### 执行结束，重复文件已移除并被备份到 {}\n'.format(bak_dir))


def get_file_list(path):
    if os.path.isfile(path):
        file_list.append(path)
    else:
        dir_list = os.listdir(path)
        for _dir in dir_list:
            get_file_list(os.path.join(path, _dir))


def move_file(file):
    os.chmod(file, os.stat(file).st_mode | 0o222)
    path = bak_dir + os.path.dirname(file).replace(src_dir, '')
    if not os.path.exists(path):
        os.makedirs(path)
    shutil.move(file, os.path.join(path, os.path.basename(file)))
    log_text.insert(tkinter.END, '③ 移除 {}\n\n'.format(file))


# 页面布局
root = tkinter.Tk()
root.title('重复文件清理')
root.state('zoomed')

btn_frame = tkinter.Frame(master=root)
btn_frame.pack(side=tkinter.TOP, pady=10)

src_dir_btn = tkinter.Button(master=btn_frame, text='选择原始目录', command=src_dir_open)
src_dir_btn.pack(side=tkinter.LEFT, padx=10)

bak_dir_btn = tkinter.Button(master=btn_frame, text='选择备份目录', command=bak_dir_open)
bak_dir_btn.pack(side=tkinter.LEFT, padx=10)

run_btn = tkinter.Button(master=btn_frame, text='开始执行', command=run)
run_btn.pack(side=tkinter.LEFT, padx=10)

log_text = tkinter.Text(master=root, height=800)
log_text.pack(fill=tkinter.BOTH, expand=True)
log_text.bind('<Key>', on_key_press)

scrollbar = tkinter.Scrollbar(master=log_text)
scrollbar.pack(side=tkinter.RIGHT, fill=tkinter.Y)

scrollbar.config(command=log_text.yview)
log_text.config(yscrollcommand=scrollbar.set)

root.mainloop()
