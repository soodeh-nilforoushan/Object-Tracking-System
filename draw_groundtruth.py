import tkinter as tk

def plusten(x):
    i = 0
    while i<x:
        yield i
        yield i+10
        i += 1

def next_item():
    if gen:
        try:
            lbl["text"] = next(gen) #calls the next item of generator
        except StopIteration:
            lbl["text"] = "End of iteration" #if generator is exhausted, write an error
    else:
        lbl["text"] = "start loop by entering a number and pressing start loop button"

def start_gen():
    global gen
    try:
        gen = plusten(int(ent.get()))
        lbl["text"] = "loop started with value: " + ent.get()
    except ValueError:
        lbl["text"] = "Enter a valid value"

gen = None

root = tk.Tk()

ent = tk.Entry()
ent.pack()
tk.Button(root, text="start loop", command=start_gen).pack()

tk.Button(root, text="next item", command=next_item).pack()
lbl = tk.Label(root, text="")
lbl.pack()

root.mainloop()