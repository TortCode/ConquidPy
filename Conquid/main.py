from model.state import *
from model.memory import *
import tkinter as tk
from tkinter import filedialog
from tkinter import simpledialog
from boardview import BoardView
from controller import Controller
import json

ROWS = 15
COLS = 30



def newcmd():
    rows = simpledialog.askinteger('Input', 'How many rows?', minvalue=3, parent=root)
    cols = simpledialog.askinteger('Input', 'How many columns?', minvalue=14, parent=root)
    bdv.discard_tiles()
    load_history(make_history(rows,cols))

def saveascmd():
    save_file = filedialog.asksaveasfilename()
    with open(save_file, 'w') as sf:
        json.dump(cache.hist.__dict__, sf)

def opencmd():
    open_file = filedialog.askopenfilename()
    with open(open_file) as of:
        histdict = json.load(of)
    bdv.discard_tiles()
    load_history(History(**histdict))

def make_history(rows, cols):
    base1 = ((rows - 1) // 2, 5)
    base2 = ((rows - 1) // 2, cols - 1 - 5)
    return History(rows, cols, [base1,base2], [])

def load_history(history):
    global cache
    cache = Cache(history)
    controller.cache = cache
    board = cache.latest
    root.geometry(str(max(board.cols*40,800))+'x'+str(board.rows*40)+'+400+200')
    bdv.setup(controller, board.rows, board.cols)
    cache.link_gui(controller, bdv)

root = tk.Tk()
root.title("Conquid")
root.option_add('*tearOff', False)
menubar = tk.Menu(root)
root['menu'] = menubar
#file menu creation
filemenu = tk.Menu(menubar)
menubar.add_cascade(menu=filemenu, label="File")
filemenu.add_command(label='New', command=newcmd)
filemenu.add_command(label='Open', command=opencmd)
filemenu.add_command(label='Save As', command=saveascmd)

# controller and boardview setup
button_frame = tk.Frame(root)
turn_box = tk.Label(button_frame,text='PLAYER 1 TURN', width=15)
bdv = BoardView(root, turn_box)
controller = Controller()
controller.boardview = bdv
load_history(make_history(ROWS, COLS))

#make buttons
move_btns = {}
move_btns['A'] = tk.Button(button_frame, relief='groove', text='acquire', width=8, command=lambda:controller.button_pressed('A'))
root.bind('<a>', lambda e: move_btns['A'].invoke())
move_btns['C'] = tk.Button(button_frame, relief='groove', text='conquer', width=8, command=lambda:controller.button_pressed('C'))
root.bind('<c>', lambda e: move_btns['C'].invoke())
move_btns['V'] = tk.Button(button_frame, relief='groove', text='vanquish', width=8, command=lambda:controller.button_pressed('V'))
root.bind('<v>', lambda e: move_btns['V'].invoke())
move_btns['Q'] = tk.Button(button_frame, relief='groove', text='conquest', width=8, command=lambda:controller.button_pressed('Q'))
root.bind('<q>', lambda e: move_btns['Q'].invoke())
undo_btn = tk.Button(button_frame, relief='groove', text='undo', width=8, command=controller.undo)
root.bind('<u>', lambda e: undo_btn.invoke())
confirm_btn = tk.Button(button_frame,relief='groove', text='confirm', width=8, command=controller.confirm)
root.bind('<Return>', lambda e: confirm_btn.invoke())

prev_btn = tk.Button(button_frame,relief='groove', text='<<', width=10, command=controller.prev_board)
root.bind('<Left>', lambda e: prev_btn.invoke())
pause_play = tk.Button(button_frame,relief='groove', text='#', width=10, command=controller.pauseplay)
root.bind('<Up>', lambda e: pause_play.invoke())
next_btn = tk.Button(button_frame,relief='groove', text='>>', width=10, command=controller.next_board)
root.bind('<Right>', lambda e: next_btn.invoke())

controller.link_buttons(move_btns, undo_btn, confirm_btn, prev_btn, pause_play, next_btn)

#pack
button_frame.pack(side='bottom')
move_btns['A'].grid(row=0, column=0)
move_btns['C'].grid(row=0, column=1)
move_btns['V'].grid(row=0, column=2)
move_btns['Q'].grid(row=0, column=3)
turn_box.grid(row=0, column=4)
undo_btn.grid(row=0, column=5)
confirm_btn.grid(row=0, column=6)
prev_btn.grid(row=0, column=7)
pause_play.grid(row=0,column=8)
next_btn.grid(row=0, column=9)

root.focus()
root.mainloop()