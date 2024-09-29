
from os import environ
environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import pygame
from PIL import Image, ImageTk

class PomodoroTomato:
    
    TITLE = 'TomatoPomodoro'
    VERSION = '3.0'

    TL_INSTR = 'Enter Pomodoro time details below:'
    BREAK_INSTR = 'Enter break period [minutes]'
    WORK_INSTR = 'Enter work period [minutes]'

    NOTIF_TITLE = 'PAUSE WORK!'
    NOTIF_MESSAGE = 'Please have a break.'
    NOTIF_IMAGE = 'breakMode.png'
    WORK_STATUS = 'Working...'
    RUNNING_STATUS = 'Running...'

    def __init__(self, root):
        '''
        Initializes the music, the root window and loops the root window.
        '''
        
        pygame.mixer.init()
        pygame.mixer.music.load('toBeCont.mp3')

        self.root = root
        self.root.iconbitmap('workMode.ico')
        self.root.title(f'{self.TITLE} v{self.VERSION}')
        self.root.geometry('300x200+500+200')
        self.root.resizable(False, False)

        self.TIME = 0
        self.SESSION_NO = 1
        self.ON_WORK = True
        self.IS_RUNNING = True

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

        self.session_label = ttk.Label(self.mainframe, text='')
        self.session_label.grid(column=1, row=6, columnspan=3, rowspan=1)

        self.status_label = ttk.Label(self.mainframe, text='')
        self.status_label.grid(column=1, row=7, columnspan=3, rowspan=1)

        self.work_status_label = ttk.Label(self.mainframe, text='')
        self.work_status_label.grid(column=1, row=8, columnspan=3, rowspan=1)

        self.current_time_label = ttk.Label(self.mainframe,text='')
        self.current_time_label.grid(column=1, row=9, columnspan=3, rowspan=1)

    def update_on_work_status(self):

        self.NOTIF_TITLE = 'PAUSE WORK!' if self.ON_WORK==True \
            else 'RESUME WORk!'
        
        self.NOTIF_MESSAGE = f'Please have a {self.TIME} minute(s) break.'\
            if self.ON_WORK==True else \
            f'Please work for {self.TIME} minute(s).'
        
        self.NOTIF_IMAGE = 'breakMode.png' if self.ON_WORK==True \
            else 'workMode.png'
        
        self.WORK_STATUS = 'Working...' if self.ON_WORK==True \
            else 'On a Break...'
        
        self.RUNNING_STATUS = 'Running...' if self.IS_RUNNING==True \
            else 'Stopped!'

    def update_running_status(self):
        self.RUNNING_STATUS = 'Running...' if self.IS_RUNNING==True \
            else 'Stopped!' 
        
    def playsound(self):
        '''Called whenever it is now break time or work time.'''
        pygame.mixer.music.play()

    def stopsound(self):
        '''Called when the timer_done_message_box is destroyed.'''
        pygame.mixer.music.stop()

    def update_display_status(self):
        self.session_label.config(text=f'Session No.: {self.SESSION_NO}')
        self.status_label.config(text=f'Status: {self.RUNNING_STATUS}')
        self.work_status_label.config(text=f'{self.WORK_STATUS}')
        self.current_time_label.config(text=f'Remaining Time: {self.TIME} sec')
        self.root.update()

    def countdown(self):
        
        if self.IS_RUNNING and self.TIME > 0:
            self.update_on_work_status()
            self.update_display_status()
            self.TIME -= 1
            self.root.after(1000, self.countdown)

        elif self.IS_RUNNING and self.TIME <= 0:
            self.timer_done_message_box()
            if self.ON_WORK:
                self.SESSION_NO += 1

        elif not self.IS_RUNNING:
            self.TIME = 0
            self.update_display_status()

    def timer_done_message_box(self):
        '''
        Shows a notification window whether break time or work time is over.
        '''

        title = self.NOTIF_TITLE
        message = self.NOTIF_MESSAGE
        image = self.NOTIF_IMAGE
        img = Image.open(image).resize((400, 400))

        top = tk.Toplevel(self.root)
        top.title(title)
        top.iconbitmap('workMode.ico')
        
        # Makes the window pop to the topmost level
        top.attributes('-topmost', True)

        # Notification box geometry and label
        screenwidth = self.root.winfo_screenwidth()
        screenheight = self.root.winfo_screenheight()
        mb_reqwidth = top.winfo_reqwidth()
        mb_reqheight = top.winfo_reqheight()
        width = (screenwidth - mb_reqwidth) // 2 
        height = (screenheight - mb_reqheight) // 2
        top.geometry(f'400x500+{width-200}+{height-250}')
        tk.Label(top, text=message).grid(column=0, row=0)

        # The image shown on the notification box
        img = ImageTk.PhotoImage(img)
        img_label = tk.Label(top, image=img)
        img_label.image = img
        img_label.grid(column=0, row=1)

        # Button to close
        tk.Button(top, text="OK", command=top.destroy).grid(column=0, row=2)

        self.playsound()
        top.wait_window()

        self.stopsound()
        self.switch_status()
        self.start()

    def switch_status(self):
        self.ON_WORK = not self.ON_WORK
        self.update_on_work_status()
        self.update_display_status()

    def start(self):
        try:
            work_time_min = self.work_min_entry.get()
            break_time_min = self.break_min_entry.get()
            work_timer = int(float(work_time_min) * 60)
            break_timer = int(float(break_time_min) * 60)

            self.IS_RUNNING = True
         
            self.TIME = work_timer if self.ON_WORK==True else break_timer
            self.countdown()

        except ValueError:
            messagebox.showerror('ERROR', 'Missing or Incorrect values')

    def stop(self):
        self.IS_RUNNING = False
        self.SESSION_NO = 0
        self.update_running_status() 
        self.update_display_status()

if __name__ == '__main__':
    root = tk.Tk()
    app = PomodoroTomato(root)



