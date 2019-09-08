import cv2
from PIL import Image, ImageTk
import kcftracker
import tkinter as tknt
from tkinter.ttk import *
import matplotlib.pyplot as plt
from tkinter import Frame, IntVar, Canvas, Checkbutton, N, S, E, W, Button, filedialog, Label, messagebox, LabelFrame, \
    StringVar, Entry, PhotoImage,RAISED,SUNKEN,SOLID
import matplotlib
import os, os.path

matplotlib.use('TkAgg')
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

class app:

    def __init__(self, window, window_title):
        self.v1 = IntVar()
        self.v2 = IntVar()
        self.v3 = IntVar()
        self.v4 = IntVar()
        self.selection = None
        self.window = window
        self.window.title(window_title)
        self.window.geometry('{}x{}'.format(1500, 1500))

        # create frame
        mycolor2 = '#%02x%02x%02x' % (224, 255, 253)  # set your favourite rgb color
        mycolor = '#%02x%02x%02x' % (204, 238, 255)  # set your favourite rgb color
        self.window.configure(background=mycolor2)
        # all frames
        self.imageFrame = Frame(window, width=1250, height=700, bg=mycolor2)
        self.imageFrame.grid(row=0, column=0)
        self.frame1 = Frame(window, bg=mycolor, width=270, height=100, padx=20,relief=SOLID,borderwidth=2)
        self.frame1.grid(row=0, column=1, padx=20,pady=10)
        self.frame2 = Frame(window, bg=mycolor,height=50,relief=SOLID,borderwidth=2)
        self.frame2.grid(row=1, column=1, padx=50)

        # self.frame4 = Frame(window, bg=mycolor2, width=400, height=400)
        # self.frame4.grid(row=1, column=3)
        # label frames
        self.lb1 = LabelFrame(self.frame1, text="Input:", width=400, height=100, bg=mycolor)
        self.lb1.grid(row=0, column=0, pady=30,padx=40)
        self.lb2 = LabelFrame(self.frame1, text="Tracking Methods:", width=400, height=100, bg=mycolor)
        self.lb2.grid(row=1, column=0, pady=20, padx=10)
        self.lb3 = LabelFrame(self.frame1, width=400, text="Buttoms", height=200, bg=mycolor)
        self.lb3.grid(row=2, column=0, pady=20, padx=10)
        self.lb4 = LabelFrame(self.frame2, bg=mycolor,height=50)
        self.lb4.grid(row=0, column=0, padx=20, pady=20)
        # buttoms

        self.browsebutton1 = Button(self.lb1, text="Load Video", command=self.browseDataSet, bg="light blue",
                                    width=14, height=2,relief=RAISED,borderwidth=5)
        self.browsebutton1.grid(row=0, column=0, sticky="w",padx=20,pady=10)
        self.browsebutton2 = Button(self.lb1, text="Load Ground Truth", command=self.browsegroundtruth,
                                    bg="light green", width=14, height=2,relief=RAISED,borderwidth=5)
        self.browsebutton2.grid(row=1, column=0, sticky="w",padx=20,pady=10)
        # self.e1=Label(self.lb1,width=20,text=self.filename)
        # self.e1.grid(row=0,column=1)
        # check boxes
        self.c1 = Checkbutton(self.lb2, bg='orange', text="KCF", variable=self.v1, onvalue=1, offvalue=0, width=10,relief=RAISED,borderwidth=5)
        self.c1.grid(row=0, column=0, pady=10, sticky="w", padx=25)
        self.c2 = Checkbutton(self.lb2, text="Cam Shift", bg="blue", variable=self.v2, onvalue=1, offvalue=0,width=10,relief=RAISED,borderwidth=5)
        self.c2.grid(row=1, column=0, pady=10, sticky="w", padx=25)
        self.c3 = Checkbutton(self.lb2, text="ground truth", bg="light green", variable=self.v3, onvalue=1, offvalue=0,width=10,relief=RAISED,borderwidth=5)
        self.c3.grid(row=0, column=1, pady=10, sticky="w", padx=25)
        self.c4 = Checkbutton(self.lb2, text="your label", variable=self.v4, onvalue=1, offvalue=0, width=10,relief=RAISED,borderwidth=5)
        self.c4.grid(row=1, column=1, pady=10, sticky="w", padx=25)
        # buttoms
        self.photo1 = PhotoImage(file="pause1.png").subsample(7, 7)
        self.stop1 = Button(self.lb3, text="stop", image=self.photo1, command=self.stopFrames,relief=RAISED,borderwidth=5, bg="light green",width=70, height=70)
        self.stop1.grid(row=0, column=1, padx=5, pady=30)
        self.photo = PhotoImage(file="play-128.png").subsample(2, 2)
        self.play = Button(self.lb3, image=self.photo, text="play", command=self.start, bg="light green", width=70,
                           height=70,relief=RAISED,borderwidth=5)
        self.play.grid(row=0, column=0, padx=5, pady=30)
        self.photo2 = PhotoImage(file="Save.png").subsample(7, 7)
        self.save = Button(self.lb3, image=self.photo2, text="save from current frame", command=self.browseSave,
                           bg="light green",
                           width=70, height=70,relief=RAISED,borderwidth=5)
        self.save.grid(row=0, column=2, padx=5, pady=30)

        self.photo3 = PhotoImage(file="next-128.png").subsample(2, 2)
        self.nextb = Button(self.lb3, text="next", image=self.photo3, bg="light green", command=self.next, height=70,
                            width=70,relief=RAISED,borderwidth=5)
        self.nextb.grid(row=1, column=1, padx=10, pady=10, columnspan=2)
        self.photo4 = PhotoImage(file="previous-128.png").subsample(2, 2)
        self.backb = Button(self.lb3, text="previous", image=self.photo4, bg="light green", command=self.previous,
                            height=70, width=70,relief=RAISED,borderwidth=5)
        self.backb.grid(row=1, column=0, padx=10, pady=10, columnspan=2)
        # labels and entry
        self.currentFrame = Label(self.lb4, text="current frame: ",bg="light green",relief=RAISED,borderwidth=3)
        self.currentFrame.grid(row=0, column=0, pady=20, padx=10, sticky="w")
        self.errorFrame = Label(self.lb4, text="error KCF percentage: ",bg="light green",relief=RAISED,borderwidth=3)
        self.errorFrame.grid(row=1, column=0, pady=20, padx=10, sticky="w")
        self.errorFrame2 = Label(self.lb4, text="error cam Shift percentage: ",bg="light green",relief=RAISED,borderwidth=3)
        self.errorFrame2.grid(row=2, column=0, pady=20, padx=10, sticky="w")

        self.var1 = StringVar()
        self.var2 = StringVar()
        self.var3 = StringVar()
        self.var4 = IntVar()
        self.var4.set(0)
        self.currentFrameInput = Entry(self.lb4, bg="light blue", width=10, textvar=self.var4)
        self.currentFrameInput.grid(row=0, column=1, padx=10)
        self.currentFrameInput.bind("<Key>", self.keyboard)
        self.errorInputKCF = Label(self.lb4, bg="light blue", width=10, textvariable=self.var2)
        self.errorInputKCF.grid(row=1, column=1, padx=30)
        self.errorInputcam = Label(self.lb4, bg="light blue", width=10, textvariable=self.var3)
        self.errorInputcam.grid(row=2, column=1, padx=10)
        ###

        # ########################################
        self.fig = Figure(figsize=(12.8, 3))
        self.fig.patch.set_facecolor(mycolor)
        self.a = self.fig.add_subplot(111)
        self.canvas2 = FigureCanvasTkAgg(self.fig, master=self.window,)
        self.canvas2.get_tk_widget().grid(row=1, column=0, sticky="swn", padx=5, pady=5)
        ############################################################
        # self.speed=Button(window,text="speed",command=pace,)
        # self.slow=Button(window,text="slow",command=pace,)
        self.IsSlow = False
        self.tracker = kcftracker.KCFTracker(False, True, True)
        # self.IsimageStream = True
        self.IsFirstFrame = True
        self.IsCam_KCF_firstframe = True
        self.IsCamshiftFirstFrame = True
        self.running = True
        self.frame = None
        self.IsSave = False
        self.gt = False
        self.idx = 0
        self.IsClicked = False
        self.IsKeyboard = False
        self.cap = cv2.VideoCapture('1.mp4')
        self.groundtruthFile = None
        # self.f=open("/home/soodeh/Downloads/SushilKCF-master/datasets/planestv_1/planestv_6.txt", "r")
        self.canvas = Canvas(window, cursor="cross")
        self.x = self.y = 0
        self.canvas.grid(row=0, column=0, sticky=N + S + E + W, padx=5, pady=5)
        self.canvas.bind("<ButtonPress-1>", self.on_button_press)
        self.canvas.bind("<B1-Motion>", self.on_move_press)
        self.canvas.bind("<ButtonRelease-1>", self.on_button_release)
        self.rect = None
        self.start_x = None
        self.start_y = None
        self.end_y = None
        self.end_x = None
        ##############################
        self.groundTruthAddress = None
        self.filename = None
        self.track_window = None
        self.roi_hist = None
        self.term_crit = None
        self.IsNext = False
        self.IsPrevious = False
        self.IsKCF = False
        self.x1 = None
        self.y1 = None
        self.w1 = None
        self.h1 = None
        self.BB = [None]
        self.fields = [None]
        self.window.mainloop()

    def firstFrame(self):
        frame = cv2.imread(self.filename + "/00001.jpg")
        self.cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
        self.img = Image.fromarray(self.cv2image)
        self.imgtk = ImageTk.PhotoImage(image=self.img)
        self.canvas.create_image(0, 0, image=self.imgtk, anchor="nw")

    def start(self):
        self.stop = self.file_number
        if (self.start_x == None):
            messagebox.showinfo('draw boundingbox', 'You should draw bounding box FIRST!')
        self.running = True
        results = []
        if self.v1.get() == 1:
            results.append("1")
        if (self.v2.get() == 1):
            results.append("2")
        if self.v3.get() == 1:
            results.append("3")
        if self.v4.get() == 1:
            results.append("4")

        self.result = ''.join(results)

        # if (self.var4.get() > self.file_number):
        #     s = 'Your frame numbers are: ' + str(self.file_number) + ' ,please enter number in this area'
        #     messagebox.showinfo('frame', s)
        # if(str(self.var4.get()).isdigit()==False):
        #     messagebox.showinfo('frame', "please enter integer")
        #
        # elif(self.var4.get() > self.file_number):
        #     s = 'Your frame numbers are: ' + str(self.file_number) + ' ,please enter number in this area'
        #     messagebox.showinfo('frame', s)
        try:
            int(self.var4.get())
        except :
            messagebox.showinfo('frame', "please enter integer ")
            print("hh")
        else:
                if(self.var4.get() > self.file_number):
                    s = 'Your frame numbers are: ' + str(self.file_number) + ' ,please enter number in this area'
                    messagebox.showinfo('frame', s)
        # elif (str(self.var4.get()).isdigit() == False):
        #     messagebox.showinfo('frame', "please enter integer")
        #     print("hh")
        # if(self.IsNext==True):
        #     print("jj")
        #     self.frame = cv2.imread(self.filename + "/" + "{number:05}".format(number=int(self.var4.get())+1) + '.jpg')
        if(self.result==""):
            messagebox.showinfo('frames address', 'Select at least one check box')
        if (self.result == "1"):
            self.gt = False
            if (self.filename == None):
                messagebox.showinfo('frames address', 'You should choose frames address FIRST!')
            else:
                self.updateKCF()
        elif (self.result == "2"):
            self.gt = False
            if (self.filename == None):
                messagebox.showinfo('frames address', 'You should choose frames address FIRST!')
            else:
                self.updateCamShift()
        elif (self.result == "3"):
            if (self.groundTruthAddress == None):
                messagebox.showinfo('ground truth address', 'You should choose ground truth address FIRST!')
            else:
                self.groundtruth()
        elif (self.result == "12"):
            self.gt = False
            if (self.filename == None):
                messagebox.showinfo('frames address', 'You should choose frames address FIRST!')
            else:
                self.update_camshift_KCF()
        elif (self.result == "13"):
            self.gt = True
            if (self.groundTruthAddress == None and self.filename == None):
                messagebox.showinfo('frames address', 'You should choose frames address FIRST!')
                messagebox.showinfo('ground truth address', 'You should choose ground truth address FIRST!')
            elif (self.filename == None):
                messagebox.showinfo('frames address', 'You should choose frames address FIRST!')
            elif (self.groundTruthAddress == None):
                messagebox.showinfo('ground truth address', 'You should choose ground truth address FIRST!')
            else:
                self.updateKCF()
        elif (self.result == "23"):
            self.gt = True
            if (self.groundTruthAddress == None and self.filename == None):
                messagebox.showinfo('frames address', 'You should choose frames address FIRST!')
                messagebox.showinfo('ground truth address', 'You should choose ground truth address FIRST!')
            elif (self.filename == None):
                messagebox.showinfo('frames address', 'You should choose frames address FIRST!')
            elif (self.groundTruthAddress == None):
                messagebox.showinfo('ground truth address', 'You should choose ground truth address FIRST!')
            else:
                self.updateCamShift()
        elif (self.result == "123"):
            self.gt = True
            if (self.groundTruthAddress == None and self.filename == None):
                messagebox.showinfo('frames address', 'You should choose frames address FIRST!')
                messagebox.showinfo('ground truth address', 'You should choose ground truth address FIRST!')
            elif (self.filename == None):
                messagebox.showinfo('frames address', 'You should choose frames address FIRST!')
            elif (self.groundTruthAddress == None):
                messagebox.showinfo('ground truth address', 'You should choose ground truth address FIRST!')
            else:
                self.update_camshift_KCF()

    def entry(self):
        if (len(self.var4.get()) != 0 and self.running == True):
            messagebox.showinfo('go to', 'You should stop FIRST!')
        # elif(len(self.gotoInput.get()) != 0)

    def next(self):
        # self.IsNext = True
        print(self.var4.get(), "before")
        self.stop = self.var4.get()
        # self.var4.set(self.var4.get() )
        print(self.stop, "after")
        if(self.result=="1" or self.result=="13"):
           self.window.after(10, self.updateKCF)
        elif(self.result=="2" or self.result=="23"):
            self.window.after(10, self.updateCamShift)
        elif(self.result=="3"):
            self.window.after(10, self.groundtruth)
        elif (self.result == "12" or self.result=="123"):
            self.window.after(10, self.update_camshift_KCF)
        # elif (self.result == "13"):
        #     self.window.after(10, self.update_camshift_KCF)



    def previous(self):
        self.IsPrevious = True
        print(self.var4.get(), "b")
        self.stop = self.var4.get() - 2
        self.var4.set(self.var4.get() - 3)
        print(self.stop, "a")
        if (self.result == "1" or self.result == "13"):
            self.window.after(10, self.updateKCF)
        elif (self.result == "2" or self.result == "23"):
            self.window.after(10, self.updateCamShift)
        elif (self.result == "3"):
            self.window.after(10, self.groundtruth)
        elif (self.result == "12" or self.result == "123"):
            self.window.after(10, self.update_camshift_KCF)

    def stopFrames(self):
        self.stop = self.var4.get()

        if (self.IsClicked == True or self.IsKeyboard == True):
            # self.frame = cv2.imread(self.filename + "/" + "{number:05}".format(number=int(self.var4.get())) + '.jpg')
            self.IsFirstFrame = True
            self.IsCam_KCF_firstframe = True
            self.IsCamshiftFirstFrame = True

    def browsegroundtruth(self):
        self.groundTruthAddress = filedialog.askopenfilename(
            initialdir="/home/soodeh/Downloads/KCFpy-with-conv-nets-master/datasets")
        self.groundtruthFile = open(self.groundTruthAddress, "r")
        self.all_lines = self.groundtruthFile.readlines()
        self.a.cla()

    def browseDataSet(self):
        self.filename = filedialog.askdirectory(
            initialdir="/home/soodeh/Downloads/KCFpy-with-conv-nets-master/datasets")
        self.file_number = len(
            [name for name in os.listdir(self.filename) if os.path.isfile(os.path.join(self.filename, name))])
        self.stop = self.file_number
        self.var4.set(0)
        self.a.cla()
        # self.l1 = Entry(self.lb1, textvar=self.filename, width=60, height=2)
        # self.l1.grid(row=0, column=1)
        self.firstFrame()

    def browseSave(self):
        self.saveAddress = filedialog.askdirectory(
            initialdir="/home/soodeh/Downloads/KCFpy-with-conv-nets-master/my_frames")
        self.IsSave = True

    def groundtruth_and_tracking(self):

        lineList = self.all_lines[self.var4.get()]
        self.fields = lineList.split(",")
        self.fields = list(map(int, self.fields))

    def groundtruth(self):
        print("----")
        if (self.stop >= self.var4.get()):
            self.frame = cv2.imread(
                self.filename + "/" + "{number:05}".format(number=self.var4.get() + 1) + '.jpg')
            lineList = self.all_lines[self.var4.get()]
            self.fields = lineList.split(",")
            self.fields = list(map(int, self.fields))
            cv2.rectangle(self.frame, (self.fields[0], self.fields[1]),
                          (self.fields[0] + self.fields[2], self.fields[1] + self.fields[3]), (0, 255, 0), 2)
            if (self.IsSave == True):
                cv2.imwrite(self.saveAddress + "/" + "plane" + "{number:05}".format(number=self.var4.get()) + '.jpg',
                            self.frame)

            #############################
            self.var4.set(self.var4.get() + 1)
            self.cv2image = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGBA)
            self.img = Image.fromarray(self.cv2image)
            self.imgtk = ImageTk.PhotoImage(image=self.img)
            self.canvas.create_image(0, 0, image=self.imgtk, anchor="nw")
            self.window.after(20, self.groundtruth)

    def update_camshift_KCF(self):
        if (self.stop >= self.var4.get()):
            print("camkcf")
            self.IsClicked = False
            self.frame = cv2.imread(
                self.filename + "/" + "{number:05}".format(number=self.var4.get() + 1) + '.jpg')
            # self.var1.set(self.idx)
            if (self.IsCam_KCF_firstframe == True):
                # if(self.IsKCF==True):
                #     self.start_x=self.BB[0]
                #     self.start_y=self.BB[1]
                #     self.end_x=self.BB[2]
                #     self.end_y=self.BB[3]
                #     print("iskcftrue")
                # print("hereeee")
                print(self.start_x, self.start_y, self.end_x, self.end_y)
                self.roi = self.frame[self.start_y: self.end_y, self.start_x: self.end_x]
                self.roi_hist = cv2.calcHist([self.roi], [0], None, [180], [0, 180])
                self.term_crit = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 1)
                #########################################
                w = self.end_x - self.start_x
                h = self.end_y - self.start_y
                cv2.rectangle(self.frame, (self.start_x, self.start_y), (w, h), (0, 255, 255), 1)
                self.BB = [self.start_x, self.start_y, w, h]
                self.tracker.init([self.start_x, self.start_y, w, h], self.frame)
                self.IsCam_KCF_firstframe = False
            else:
                print("here2")
                mask = cv2.calcBackProject([self.frame], [0], self.roi_hist, [0, 180], 1)
                ret, track_window = cv2.CamShift(mask, (
                    self.start_x, self.start_y, self.end_x - self.start_x, self.end_y - self.start_y), self.term_crit)
                self.BB = track_window
                # cv2.rectangle(frame, (self.start_x, self.start_y), (self.start_x + self.end_x - self.start_x, self.start_y + self.end_y - self.start_y),
                # (255, 0, 0), 2)
                pts = cv2.boxPoints(ret)
                pts = np.int0(pts)
                cv2.polylines(self.frame, [pts], True, 255, 3)

                #######################
                if (self.gt == True):
                    self.groundtruth_and_tracking()
                    cv2.rectangle(self.frame, (self.fields[0], self.fields[1]),
                                  (self.fields[0] + self.fields[2], self.fields[1] + self.fields[3]), (0, 255, 0), 2)
                    self.IOU()
                    print(self.var4.get())
                    self.var3.set(str(format(self.y * 100, '02f')))
                    self.a.scatter(self.var4.get(), self.y, color="blue")
                    self.a.set_title("accuracy of each frame", fontsize=11)
                    self.a.set_ylabel("accuray", fontsize=14)
                    self.a.set_xlabel("frame number", fontsize=14)
                    self.canvas2.draw()

                self.BB = self.tracker.update(self.frame)
                self.BB = list(map(int, self.BB))

                cv2.rectangle(self.frame, (self.BB[0], self.BB[1]),
                              (self.BB[0] + self.BB[2], self.BB[1] + self.BB[3]),(65,130 , 250), 3)
                if (self.gt == True):
                    self.IOU()
                    self.var2.set(str(format(self.y * 100, '02f')))
                    self.a.scatter(self.var4.get(), self.y, color="orange")
                    print(self.var4.get())
                    self.a.set_title("accuracy of each frame", fontsize=11)
                    self.a.set_ylabel("accuray", fontsize=14)
                    self.a.set_xlabel("frame number", fontsize=14)

                    self.canvas2.draw()
                if (self.IsSave == True):
                    cv2.imwrite(
                        self.saveAddress + "/" + "plane" + "{number:05}".format(number=self.var4.get()) + '.jpg',
                        self.frame)

                self.var4.set(self.var4.get() + 1)
                self.cv2image = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGBA)
                self.img = Image.fromarray(self.cv2image)
                self.imgtk = ImageTk.PhotoImage(image=self.img)
                self.canvas.create_image(0, 0, image=self.imgtk, anchor="nw")
                self.window.after(10, self.update_camshift_KCF)

    def updateCamShift(self):
        if (self.stop >= self.var4.get()):
            print("cam")
            self.IsClicked = False
            self.frame = cv2.imread(self.filename + "/" + "{number:05}".format(number=self.var4.get() + 1) + '.jpg')
            # self.var1.set(self.idx)
            if (self.IsCamshiftFirstFrame == True):
                self.roi = self.frame[self.start_y: self.end_y, self.start_x: self.end_x]
                self.roi_hist = cv2.calcHist([self.roi], [0], None, [180], [0, 180])
                self.term_crit = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 1)
                self.IsCamshiftFirstFrame = False
            else:
                mask = cv2.calcBackProject([self.frame], [0], self.roi_hist, [0, 180], 1)
                # apply meanshift to get the new location
                ret, track_window = cv2.CamShift(mask, (
                    self.start_x, self.start_y, self.end_x - self.start_x, self.end_y - self.start_y), self.term_crit)
                self.BB = track_window
                # cv2.rectangle(frame, (self.start_x, self.start_y), (self.start_x + self.end_x - self.start_x, self.start_y + self.end_y - self.start_y),
                # (255, 0, 0), 2)

                # cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
                pts = cv2.boxPoints(ret)
                pts = np.int0(pts)
                cv2.polylines(self.frame, [pts], True, 255, 3)
                if (self.gt == True):
                    self.groundtruth_and_tracking()
                    cv2.rectangle(self.frame, (self.fields[0], self.fields[1]),
                                  (self.fields[0] + self.fields[2], self.fields[1] + self.fields[3]), (0, 255, 0), 2)
                    self.IOU()
                    self.var3.set(str(format(self.y * 100, '02f')))
                    self.a.scatter(self.var4.get(), self.y, color="blue")
                    self.a.set_title("accuracy of each frame", fontsize=11)
                    self.a.set_ylabel("accuray", fontsize=14)
                    self.a.set_xlabel("frame number", fontsize=14)
                    self.canvas2.draw()

                if (self.IsSave == True):
                    cv2.imwrite(
                        self.saveAddress + "/" + "plane" + "{number:05}".format(number=self.var4.get()) + '.jpg',
                        self.frame)

            self.var4.set(self.var4.get() + 1)
            self.cv2image = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGBA)
            self.img = Image.fromarray(self.cv2image)
            self.imgtk = ImageTk.PhotoImage(image=self.img)
            self.canvas.create_image(0, 0, image=self.imgtk, anchor="nw")
            self.window.after(10, self.updateCamShift)

    def updateKCF(self):
        if (self.stop >= self.var4.get()):
            print("kcf")
            self.IsClicked = False
            self.frame = cv2.imread(
                self.filename + "/" + "{number:05}".format(number=self.var4.get() + 1) + '.jpg')
            # self.var1.set(self.idx)
            if (self.IsFirstFrame == True):
                print("if")
                # print(self.start_x, self.start_y, self.end_x, self.end_y)
                w = self.end_x - self.start_x
                h = self.end_y - self.start_y
                # cv2.rectangle(self.frame, (self.start_x, self.start_y), (w, h),(65,130 , 250), 2)
                self.BB = [self.start_x, self.start_y, w, h]
                self.tracker.init([self.start_x, self.start_y, w, h], self.frame)
                self.IsFirstFrame = False

            else:
                print("els")
                self.IsKCF = True
                self.BB = self.tracker.update(self.frame)
                self.BB = list(map(int, self.BB))
                cv2.rectangle(self.frame, (self.BB[0], self.BB[1]), (self.BB[0] + self.BB[2], self.BB[1] + self.BB[3]),
                              (65,130 , 250), 3)
                # cv2.rectangle(self.frame, (self.BB[0], self.BB[1]), (self.BB[0] + self.BB[2], self.BB[1] + self.BB[3]),
                #               (0, 136, 0), 2)
                # cv2.rectangle(self.frame, (self.BB[0], self.BB[1]), (self.BB[0] + self.BB[2], self.BB[1] + self.BB[3]),
                #               (0, 0, 53),2)

                # print(self.BB, " kcf")
            if (self.gt == True):
                self.groundtruth_and_tracking()
                cv2.rectangle(self.frame, (self.fields[0], self.fields[1]),
                              (self.fields[0] + self.fields[2], self.fields[1] + self.fields[3]), (0, 255, 0), 2)

                self.IOU()
                self.var2.set(str(format(self.y * 100, '02f')))
                self.a.scatter(self.var4.get(), self.y, color="orange")
                # self.a.set_title("accuracy of each frame", fontsize=11)
                self.a.set_ylabel("Accuray(IOU)", fontsize=14)
                self.a.set_xlabel("Frame Number", fontsize=14)
                self.canvas2.draw()

            if (self.IsSave == True):
                cv2.imwrite(
                    self.saveAddress + "/" + "plane" + "{number:05}".format(number=self.var4.get()) + '.jpg',
                    self.frame)
            # if(self.IsNext==True):
            #     self.var4.set(self.var4.get() + 1)
            #     print(self.var4.get())
            #     print(self.stop, "b s")
            #     self.stop = self.var4.get() + 5
            #     print(self.stop, "a s")
            #     self.IsNext=False

            # display frame

            print(self.var4.get(), "in")
            print(self.var4.get(), "out")
            self.cv2image = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGBA)
            self.img = Image.fromarray(self.cv2image)
            self.imgtk = ImageTk.PhotoImage(image=self.img)
            self.canvas.create_image(0, 0, image=self.imgtk, anchor="nw")

            # if (self.var4.get() <= self.stop):
            # if (self.IsNext == False and self.IsPrevious == False):
            self.var4.set(self.var4.get() + 1)
                # print("5555555555")
            # self.IsNext = False
            self.window.after(10, self.updateKCF)

    def IOU(self):
        # def IOU()

        x2 = self.fields[0]
        y2 = self.fields[1]
        w2 = self.fields[2]
        h2 = self.fields[3]
        x1 = self.BB[0]
        y1 = self.BB[1]
        w1 = self.BB[2]
        h1 = self.BB[3]

        # x2, y2, w2, h2 = self.fields[0], self.fields[1], self.fields[2], self.fields[3]
        w_intersection = min(x1 + w1, x2 + w2) - max(x1, x2)
        h_intersection = min(y1 + h1, y2 + h2) - max(y1, y2)
        if w_intersection <= 0 or h_intersection <= 0:  # No overlap
            return 0

        I = w_intersection * h_intersection
        U = w1 * h1 + w2 * h2 - I  # Union = Total Area - I
        self.y = I / U

    def on_button_press(self, event):
        # save mouse drag start position
        self.start_x = event.x
        self.start_y = event.y
        # create rectangle if not yet exist
        self.rect = self.canvas.create_rectangle(self.x, self.y, 1, 1, fill="")

    def on_move_press(self, event):
        # global curX,curY
        curX, curY = (event.x, event.y)
        # expand rectangle as you drag the mouse
        self.canvas.coords(self.rect, self.start_x, self.start_y, curX, curY)

    def on_button_release(self, event):
        self.IsClicked = True
        # global end_x,end_y
        self.end_x = event.x
        self.end_y = event.y
        self.stopFrames()
        # self.IsDrawRec=True
        pass

    def keyboard(self, event):
        self.IsKeyboard = True


app(tknt.Tk(), "tracking")
