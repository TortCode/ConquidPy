from model.state import *
from model.memory import *
from controller import Controller
import tkinter as tk
from boardview import BoardView
import json


ROWS = 15
COLS = 30

root = tk.Tk()
root.title("Conquid")
menubar = tk.Menu(root)
root['menu'] = menubar

#file_menu
menubar.add_cascade(label="File")


# set up board

base1 = ((ROWS - 1) // 2, 5)
base2 = ((ROWS - 1) // 2, COLS - 1 - 5)
hist = History(ROWS, COLS, {1:base1,2:base2})
bdv = BoardView(root)
controller = Controller(hist, bdv)
board = controller.cache.latest
root.geometry(str(board.cols*40)+'x'+str(board.rows*40+30)+'+400+200')
bdv.link_controller(controller)

 #make buttom frame
button_frame = tk.Frame(root)
button_frame.pack(side='bottom', fill='x')
#make buttons
move_btns = {}
move_btns['A'] = tk.Button(button_frame, relief='groove', text='acquire', width=10, command=lambda:controller.button_pressed('A'))
move_btns['C'] = tk.Button(button_frame, relief='groove', text='conquer', width=10, command=lambda:controller.button_pressed('C'))
move_btns['V'] = tk.Button(button_frame, relief='groove', text='vanquish', width=10, command=lambda:controller.button_pressed('V'))
move_btns['Q'] = tk.Button(button_frame, relief='groove', text='conquest', width=10, command=lambda:controller.button_pressed('Q'))
undo_btn = tk.Button(button_frame, relief='groove', text='undo', width=10, command=controller.undo)
confirm_btn = tk.Button(button_frame,relief='groove', text='confirm', width=10, command=controller.confirm)
turn_box = tk.Label(button_frame,text='player 1', width=10)

controller.link_buttons(move_btns, undo_btn, confirm_btn, turn_box)
#pack
move_btns['A'].grid(row=0,column=0)
move_btns['C'].grid(row=0,column=1)
move_btns['V'].grid(row=0,column=2)
move_btns['Q'].grid(row=0,column=3)
confirm_btn.grid(row=0,column=6)
turn_box.grid(row=0,column=4)
undo_btn.grid(row=0, column=5)

root.mainloop()