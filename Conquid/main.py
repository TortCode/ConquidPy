from model.state import *
from model.memory import *
import tkinter as tk
from boardview import BoardView
from controller import Controller
import json


ROWS = 15
COLS = 30

root = tk.Tk()
root.title("Conquid")
#make buttom frame
button_frame = tk.Frame(root)
turn_box = tk.Label(button_frame,text='PLAYER 1 TURN', width=15)
menubar = tk.Menu(root)
root['menu'] = menubar

#file_menu
menubar.add_cascade(label="File")


# set up board
base1 = ((ROWS - 1) // 2, 5)
base2 = ((ROWS - 1) // 2, COLS - 1 - 5)
hist = History(ROWS, COLS, {1:base1,2:base2})
bdv = BoardView(root, turn_box)
controller = Controller()
controller.load_history(hist)
bdv.link_controller(controller)
controller.link_boardview(bdv)

#make buttons
move_btns = {}
move_btns['A'] = tk.Button(button_frame, relief='groove', text='acquire', width=10, command=lambda:controller.button_pressed('A'))
root.bind('<a>', lambda e: move_btns['A'].invoke())
move_btns['C'] = tk.Button(button_frame, relief='groove', text='conquer', width=10, command=lambda:controller.button_pressed('C'))
root.bind('<c>', lambda e: move_btns['C'].invoke())
move_btns['V'] = tk.Button(button_frame, relief='groove', text='vanquish', width=10, command=lambda:controller.button_pressed('V'))
root.bind('<v>', lambda e: move_btns['V'].invoke())
move_btns['Q'] = tk.Button(button_frame, relief='groove', text='conquest', width=10, command=lambda:controller.button_pressed('Q'))
root.bind('<q>', lambda e: move_btns['Q'].invoke())
undo_btn = tk.Button(button_frame, relief='groove', text='undo', width=10, command=controller.undo)
root.bind('<u>', lambda e: undo_btn.invoke())
confirm_btn = tk.Button(button_frame,relief='groove', text='confirm', width=10, command=controller.confirm)
root.bind('<Return>', lambda e: confirm_btn.invoke())

prev_btn = tk.Button(button_frame,relief='groove', text='<<', width=10, command=controller.prev_board)
root.bind('<Left>', lambda e: prev_btn.invoke())
pause_play = tk.Button(button_frame,relief='groove', text='#', width=10, command=controller.pauseplay)
root.bind('<Up>', lambda e: pause_play.invoke())
next_btn = tk.Button(button_frame,relief='groove', text='>>', width=10, command=controller.next_board)
root.bind('<Right>', lambda e: next_btn.invoke())

controller.link_buttons(move_btns, undo_btn, confirm_btn, prev_btn, pause_play, next_btn)

board = controller.cache.latest
root.geometry(str(board.cols*40)+'x'+str(board.rows*40+30)+'+400+200')

#pack
button_frame.pack(side='bottom')
move_btns['A'].grid(row=0, column=0)
move_btns['C'].grid(row=0, column=1)
move_btns['V'].grid(row=0, column=2)
move_btns['Q'].grid(row=0, column=3)
turn_box.grid(row=0, column=4)
undo_btn.grid(row=0, column=5)
confirm_btn.grid(row=0, column=6)
prev_btn.grid(row=0, column=7, ipadx = 5)
pause_play.grid(row=0,column=8, ipadx = 5)
next_btn.grid(row=0, column=9, ipadx = 5)

root.focus()
root.mainloop()