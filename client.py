import socket
import threading
import tkinter as tk
from tkinter import simpledialog
from PIL import Image, ImageTk
import emoji  # ✅ Added for emoji shortcodes


HOST = '127.0.0.1'
PORT = 5000


class ClientApp:
    def __init__(self, master):
        self.master = master
        self.master.title("💬 messenger")
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.gui_done = False
        self.running = True

        self.connect_to_server()
        self.build_gui()

        receive_thread = threading.Thread(target=self.receive)
        receive_thread.start()

    def connect_to_server(self):
        try:
            self.socket.connect((HOST, PORT))
            msg = self.socket.recv(1024).decode('utf-8')
            if msg == "USERNAME":
                self.username = simpledialog.askstring("Username", "Enter your username:")
                self.socket.send(self.username.encode('utf-8'))
        except Exception as e:
            print(f"Connection error: {e}")
            exit()

    def build_gui(self):
        self.master.geometry("800x1000")
        self.master.resizable(False, False)

        # Load background image
        bg_img = Image.open("4.jpg")
        bg_img = bg_img.resize((770, 950))
        self.chat_bg_photo = ImageTk.PhotoImage(bg_img)

        # Chat area with Canvas
        self.chat_canvas = tk.Canvas(self.master, width=750, height=950)
        self.chat_canvas.place(x=20, y=20)
        self.chat_canvas.create_image(0, 0, image=self.chat_bg_photo, anchor='nw')

        # Frame inside canvas
        self.chat_frame = tk.Frame(self.chat_canvas, bg='', bd=0)
        self.chat_window = self.chat_canvas.create_window((0, 0), window=self.chat_frame, anchor='nw')

        self.chat_frame.bind("<Configure>", lambda e: self.chat_canvas.configure(scrollregion=self.chat_canvas.bbox("all")))

        # Scrollbar
        self.scrollbar = tk.Scrollbar(self.master, command=self.chat_canvas.yview)
        self.scrollbar.place(x=780, y=20, height=530)
        self.chat_canvas.configure(yscrollcommand=self.scrollbar.set)

        # Message input
        # 1. Create Canvas
        # === Capsule Entry Background ===
        # Capsule container canvas
        self.entry_canvas = tk.Canvas(self.master, width=580, height=36, bg="#f0f0f0", highlightthickness=0)
        self.entry_canvas.place(x=30, y=870)

# Clean rounded capsule using `create_oval` for full background
        self.entry_canvas.create_oval(0, 0, 36, 36, fill="#ffffff", outline="#000000")      # Left half-circle
        self.entry_canvas.create_oval(544, 0, 580, 36, fill="#ffffff", outline="#000000")   # Right half-circle
        self.entry_canvas.create_rectangle(18, 0, 562, 36, fill="#ffffff", outline="#cccccc")  # Middle rectangle

# Entry widget placed over it
        self.msg_entry = tk.Entry(self.master, font=("Segoe UI Emoji", 14), bd=0, relief="flat", bg="white")
        self.entry_window = self.entry_canvas.create_window(10, 3, anchor='nw', window=self.msg_entry, width=560, height=30)


# Draw white capsule background
       

# Entry widget placed inside the capsule
        self.msg_entry = tk.Entry(self.master, font=("Segoe UI Emoji", 14), bd=0, relief="flat", bg="white")
        self.entry_window = self.entry_canvas.create_window(10, 3, anchor='nw', window=self.msg_entry, width=560, height=30)


        # Emoji button 😊
        self.emoji_button = tk.Button(
            self.master, text="😊", font=("Arial", 12),
            command=self.open_emoji_picker,
            relief="flat", borderwidth=0
        )
        self.emoji_button.place(x=620, y=870, width=40, height=30)

        # Send button
        self.send_btn = tk.Button(
            self.master, text="Send", command=self.send_message,
            bg="#38eb50", fg="white", font=("Helvetica", 10, "bold"),
            relief="flat", borderwidth=0, padx=15, pady=5
        )
        self.send_btn.place(x=670, y=870, width=90, height=30)

    def send_message(self):
        raw_msg = self.msg_entry.get()

        # ✅ Convert emoji shortcode to actual emoji (e.g., :smile: → 😄)
        msg = emoji.emojize(raw_msg, language='alias')

        if msg:
            formatted = f"{self.username}: {msg}"
            self.socket.send(formatted.encode('utf-8'))
            self.display_message(formatted)
            self.msg_entry.delete(0, tk.END)

    def display_message(self, msg):
        is_own = False
        if hasattr(self, 'username'):
            is_own = msg.startswith(f"{self.username}:")

        outer_frame = tk.Frame(self.chat_frame, bg="")
        outer_frame.pack(fill='x', pady=5)

        bubble = tk.Label(
            outer_frame,
            text=msg,
            bg="#0ed7f1" if is_own else "#e5eaea",
            fg="white" if is_own else "black",
            font=("Segoe UI Emoji", 12, "bold"),
            wraplength=280,
            justify="left",
            padx=12,
            pady=6,
            bd=0
        )

        if is_own:
            bubble.pack(anchor='e', padx=(470, 10))
        else:
            bubble.pack(anchor='w', padx=(10, 470))

        self.chat_canvas.update_idletasks()
        self.chat_canvas.yview_moveto(1.0)

    def open_emoji_picker(self):
        picker = tk.Toplevel(self.master)
        picker.title("Pick Emoji")
        picker.geometry("250x120")
        picker.resizable(False, False)

        emojis = ["😀", "😂", "😍", "😎", "😊", "👍", "🔥", "🎉", "🤔", "❤️", "🥺", "🙏", "😭"]

        for i, em in enumerate(emojis):
            btn = tk.Button(picker, text=em, font=("Segoe UI Emoji", 18), width=5,
                            command=lambda e=em: self.insert_emoji(e))
            btn.grid(row=i // 5, column=i % 5, padx=4, pady=4)

    def insert_emoji(self, emoji_char):
        current_text = self.msg_entry.get()
        self.msg_entry.delete(0, tk.END)
        self.msg_entry.insert(tk.END, current_text + emoji_char)

    def receive(self):
        while self.running:
            try:
                msg = self.socket.recv(1024).decode('utf-8')
                print("Received:", msg)
                self.display_message(msg)
            except Exception as e:
                print("Error receiving message:", e)
                self.socket.close()
                break

    def stop(self):
        self.running = False
        self.socket.close()
        self.master.quit()


if __name__ == "__main__":
    root = tk.Tk()
    app = ClientApp(root)
    root.protocol("WM_DELETE_WINDOW", app.stop)
    root.mainloop()
