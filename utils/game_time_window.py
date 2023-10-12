import tkinter as tk
from threading import Thread, Event
import queue

class GameTimeWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Game Time")
        self.label = tk.Label(self.root, text="Game Time: 0")
        self.label.pack(padx=20, pady=20)
        
        self.queue = queue.Queue()
        self.root.after(100, self.check_queue)

    def update_time(self, game_time):
        # Put the updated game time into the queue
        self.queue.put(game_time)

    def check_queue(self):
        # Check if there is a new game time in the queue
        try:
            game_time = self.queue.get_nowait()
            self.label.config(text=f"Game Time: {game_time}")
        except queue.Empty:
            pass
        
        self.root.after(100, self.check_queue)

    def run(self):
        self.root.mainloop()
