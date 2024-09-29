
from os import environ
environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import pygame
from PIL import Image, ImageTk

class PomodoroTomato:

    TL_INSTR = 'Enter Pomodoro time details below:'
    BREAK_INSTR = 'Enter break period [minutes]'
    WORK_INSTR = 'Enter work period [minutes]'

    BREAK_TITLE = 'WORK PAUSE!'
    WORK_TITLE = 'WORK RESUME!'

    BREAK_STATUS = 'On Break'
    WORK_STATUS = 'On Work'
    RUNNING_STATUS = 'Running'

    IS_RUNNING = True
    ON_WORK = True

    ON_WORK_IMAGE = 'workMode.png'
    ON_BREAK_IMAGE = 'breakMode.png'

    def __init__(self, root):
        '''
        Initializes the music, the root window and loops the root window.
        '''

        pygame.mixer.init()
        pygame.mixer.music.load('toBeCont.mp3')

        self.root = root
        self.root.iconbitmap('workMode.ico')
        self.root.title('TomatoPomodoro v.1')
        self.root.geometry('300x150+500+200')
        self.root.resizable(False, False)

        self.mainwindow()
        
        self.root.mainloop()

    def mainwindow(self):
        '''
        Generates the main window consisting of the buttons and entries.
        '''

        self.mainframe = ttk.Frame(root)
        self.mainframe.grid(column=0, row=0, sticky=(tk.N, tk.W, tk.E, tk.S))

        self.top_label = ttk.Label(self.mainframe, text=self.TL_INSTR)
        self.top_label.grid(column=0, row=0, columnspan=2, sticky=tk.N)

        self.break_min_label = ttk.Label(self.mainframe, text=self.BREAK_INSTR)
        self.break_min_label.grid(column=1, row=2, sticky=tk.W)

        self.work_min_label = ttk.Label(self.mainframe, text=self.WORK_INSTR)
        self.work_min_label.grid(column=1, row=3, sticky=tk.W)

        self.break_min = tk.StringVar()
        self.work_min = tk.StringVar()

        self.break_min_entry = ttk.Entry(self.mainframe, 
                                         width=10, 
                                         textvariable=self.break_min)
        self.break_min_entry.grid(column=2, row=2)

        self.work_min_entry = ttk.Entry(self.mainframe, 
                                        width=10, 
                                        textvariable=self.work_min)
        self.work_min_entry.grid(column=2, row=3)

        self.start_button = ttk.Button(self.mainframe, 
                                       text='Start Session', 
                                       command=self.start)
        self.start_button.grid(column=2, row=4, sticky=tk.S)

        self.stop_button = ttk.Button(self.mainframe, 
                                      text='Stop Session', 
                                      command=self.stop)
        self.stop_button.grid(column=2, row=5, sticky=tk.S)

    def playsound(self):
        '''Called whenever it is now break time or work time.'''

        pygame.mixer.music.play()

    def stopsound(self):
        '''Called when the timer_done_message_box is destroyed.'''

        pygame.mixer.music.stop()

    def show_running_time(self, current_time):
        '''Shows the current time of break or work.'''

        status_label = ttk.Label(self.mainframe, 
                                 text=f'Status: {self.RUNNING_STATUS}')
        status_label.grid(column=1, row=6, columnspan=3, rowspan=1)

        current_time_label = ttk.Label(self.mainframe, text=current_time)
        current_time_label.grid(column=1, row=7, columnspan=3, rowspan=1)           

    def timer_done_message_box(self, title, message):
        top = tk.Toplevel(self.root)
        top.title(title)
        top.iconbitmap('workMode.ico')
        
        top.attributes('-topmost', True)

        screenwidth = self.root.winfo_screenwidth()
        screenheight = self.root.winfo_screenheight()
        mb_reqwidth = top.winfo_reqwidth()
        mb_reqheight = top.winfo_reqheight()
        width = (screenwidth - mb_reqwidth) // 2 
        height = (screenheight - mb_reqheight) // 2

        top.geometry(f'400x500+{width-200}+{height-250}')
        tk.Label(top, text=message).grid(column=0, row=0)

        if self.ON_WORK:
            img = Image.open(self.ON_WORK_IMAGE).resize((400, 400))
        else:
            img = Image.open(self.ON_BREAK_IMAGE).resize((400, 400))
            
        img = ImageTk.PhotoImage(img)
        img_label = tk.Label(top, image=img)
        img_label.image = img
        img_label.grid(column=0, row=1)

        tk.Button(top, text="OK", command=top.destroy).grid(column=0, row=2)
        top.wait_window()
        self.stopsound()

    def countdown(self, duration, status, title, message):
        while duration != 0:
            self.show_running_time(f'{status}: {duration} sec')
            duration -= 1
            self.root.after(
                1000, self.root.update()
            )

        self.playsound()
        self.timer_done_message_box(title, message)

    def start(self):
        try:
            work_time_min = self.work_min_entry.get()
            break_time_min = self.break_min_entry.get()
            work_timer = int(float(work_time_min) * 60)
            break_timer = int(float(break_time_min) * 60)

            self.IS_RUNNING = True
            self.RUNNING_STATUS = 'Running'
            self.ON_WORK = True
            
            while self.IS_RUNNING:
                if self.ON_WORK:
                    self.countdown(
                        work_timer,
                        self.WORK_STATUS,
                        self.BREAK_TITLE,
                        f'Please have a {break_time_min} minute(s) break.')
                else:
                    self.ON_WORK = True
                    self.countdown(
                        break_timer,
                        self.BREAK_STATUS,
                        self.WORK_TITLE,
                        f'Please work for {work_time_min} minute(s).')
        except ValueError:
            messagebox.showerror('ERROR', 'Missing or Incorrect values')

    def stop(self):
        self.IS_RUNNING = False
        self.RUNNING_STATUS = 'Not Running'

if __name__ == '__main__':
    root = tk.Tk()
    app = PomodoroTomato(root)


