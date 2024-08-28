import tkinter as tk
from PIL import Image, ImageTk
import numpy as np
import threading
import cv2
from threading import Event


import tkinter as tk
from tkinter import ttk
import queue

class PlayerGUI:
    def __init__(self, player_images, player_names, substrate_name):
        self.player_images = player_images
        self.player_names = player_names
        self.substrate_name = substrate_name
        self.root = tk.Tk()
        self.root.configure(bg='light gray')
        self.frame = tk.Frame(self.root, bg='light gray')
        self.frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.labels = []
        self.img_resolution = (350, 350)
        self.load_images()
        self.create_bottom_space()
        self.create_interaction_panel()  # Create the new interaction panel
        self.queue = queue.Queue()  # Crear una instancia de Queue

        
        self.action_text = tk.StringVar()  # Variable to store the action text
        self.able_to_move = False  # Flag to indicate if the player is able to move
    def load_images(self):
        for img_array in self.player_images:
            img_resized = cv2.resize(img_array, self.img_resolution, interpolation=cv2.INTER_NEAREST)
            img = Image.fromarray(img_resized)
            photo = ImageTk.PhotoImage(image=img)
            label = tk.Label(self.frame, image=photo, borderwidth=5, relief="solid", bg='white')
            label.image = photo
            label.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=5, pady=5)
            self.labels.append(label)

    def update(self, new_images, player_orientations, player_turn, text):
        for i, (label, img_array, orientation) in enumerate(zip(self.labels, new_images, player_orientations)):
            if i == player_turn:
                label.config(borderwidth=5, relief="solid", highlightthickness=5, highlightbackground="green")
            else:
                label.config(borderwidth=5, relief="solid", highlightthickness=0)
                
            img_resized = cv2.resize(img_array, self.img_resolution, interpolation=cv2.INTER_NEAREST)
            if orientation == 1:
                img_resized = np.rot90(img_resized, 3)
            elif orientation == 2:
                img_resized = np.rot90(img_resized, 2)
            elif orientation == 3:
                img_resized = np.rot90(img_resized, 1)
            
            img = Image.fromarray(img_resized)
            photo = ImageTk.PhotoImage(image=img)
            label.configure(image=photo)
            label.image = photo
            
        self.text_scroll.config(state='normal')  # Permite la edición para actualizar el texto
        self.text_scroll.delete(1.0, tk.END)
        self.text_scroll.insert(tk.END, text)
        self.text_scroll.config(state='disabled')  # Desactiva la edición
        self.root.update()

    def create_bottom_space(self):
        self.text_scroll = tk.Text(self.root, height=30, width=100, bg='white', font=('Arial', 10))
        scrollbar = tk.Scrollbar(self.root, command=self.text_scroll.yview)
        self.text_scroll.config(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.text_scroll.pack(side=tk.LEFT, fill=tk.X, expand=True)

    def update_text(self, text):
        self.text_scroll.config(state='normal')  # Habilita la edición del widget Text
        self.text_scroll.delete(1.0, tk.END)  # Borra el contenido actual del Text
        self.text_scroll.insert(tk.END, text)  # Inserta el nuevo texto
        self.text_scroll.config(state='disabled')  # Deshabilita la edición para evitar que el usuario modifique el contenido
        self.root.update()  # Actualiza la interfaz gráfica para reflejar los cambios


    def create_interaction_panel(self):
        self.action_panel = tk.Frame(self.root, bg='gray', height=100)
        self.action_panel.pack(fill=tk.X, expand=False)

        self.left_panel = tk.Frame(self.action_panel, bg='light blue')
        self.left_panel.pack(side=tk.LEFT, fill=tk.Y, expand=True)

        self.right_panel = tk.Text(self.action_panel, bg='white', width=40, height=5)
        self.right_panel.pack(side=tk.RIGHT, fill=tk.Y, expand=False)

        # Add a bottom panel that will contain the button execute action
        self.bottom_panel = tk.Frame(self.root, bg='gray', height=50)
        self.bottom_panel.pack(fill=tk.X, expand=False)
        
        self.add_action_buttons()
        execute_button = tk.Button(self.bottom_panel, text="Execute Action", command=lambda: self.execute_action())
        execute_button.pack(pady=5)
        
    def add_action_buttons(self):
        actions = ["go to", "immobilize player", "explore", "stay put"]
        if self.substrate_name == "clean_up":
            actions.append("clean river")
        for action in actions:
            button = tk.Button(self.left_panel, text=action, command=lambda a=action: self.handle_action(a))
            button.pack(pady=5)
        
    def handle_action(self, action):
        self.right_panel.config(state=tk.NORMAL)
        self.right_panel.delete(1.0, tk.END)
        self.right_panel.insert(tk.END, action)
        self.right_panel.config(state=tk.DISABLED)

        for widget in self.left_panel.winfo_children():
            if isinstance(widget, tk.Button):
                continue
            widget.destroy()

        if action == "go to":
            entry = tk.Entry(self.left_panel)
            entry.pack()
            button = tk.Button(self.left_panel, text="Set position", command=lambda: self.update_action_text(f"{action} {entry.get()}"))
            button.pack()
        elif action == "immobilize player":
            self.listbox = tk.Listbox(self.left_panel)
            for name in self.player_names:
                self.listbox.insert(tk.END, name)
            self.listbox.pack()
            button = tk.Button(self.left_panel, text="Choose Player", command=lambda: self.choose_player(action))
            button.pack()
        elif action == "explore":
            label = tk.Label(self.left_panel, text="Exploring...")
            label.pack()
        elif action == "stay put":
            label = tk.Label(self.left_panel, text="Staying put...")
            label.pack()
        elif action == "clean river":
            entry = tk.Entry(self.left_panel)
            entry.pack()
            button = tk.Button(self.left_panel, text="Set position", command=lambda: self.update_action_text(f"{action} {entry.get()}"))
            button.pack()
            
        self.able_to_move = True

    def update_action_text(self, text):
        self.right_panel.config(state=tk.NORMAL)
        self.right_panel.delete(1.0, tk.END)
        self.right_panel.insert(tk.END, text)
        self.right_panel.config(state=tk.DISABLED)

    def get_action_text(self):
        if not self.able_to_move:
            return None
        return self.action_text.get()
    
    def execute_action(self):
        # Obtener el texto actual de la acción desde el panel derecho y enviarlo a la cola
        action_text = self.right_panel.get("1.0", tk.END).strip()
        self.queue.put(action_text)  # Envía el texto de la acción a la cola
        
        # Resets the handle action panel
        for widget in self.left_panel.winfo_children():
            widget.destroy()
        self.add_action_buttons()
        
        
    def choose_player(self, action):
        player_name = self.listbox.get(self.listbox.curselection())
        self.update_action_text(f"{action} {player_name}")

        # Clean up any existing widgets in the left panel that are not needed
        for widget in self.left_panel.winfo_children():
            if isinstance(widget, tk.Listbox) or isinstance(widget, tk.Button):
                widget.destroy()

        # Display a label and entry for the attack position
        label = tk.Label(self.left_panel, text="Enter position to attack:")
        label.pack()
        entry = tk.Entry(self.left_panel)
        entry.pack()

        # Button to finalize the command with the attack position
        button = tk.Button(self.left_panel, text="Set attack position", command=lambda: self.update_action_text(f"{action} {player_name} at position {entry.get()}"))
        button.pack()
        
    def run(self):
        self.root.mainloop()



    def start_gui_thread(self):
        gui_thread = threading.Thread(target=self.run)
        gui_thread.start()

