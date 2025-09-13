def build_gui(self):
    self.master.geometry("800x600")
    self.master.resizable(False, False)

    # Load the background image for entire window
    bg_image = Image.open("background.png")
    self.bg_photo = ImageTk.PhotoImage(bg_image)

    # Put the background image on a label that fills the whole window
    self.bg_label = tk.Label(self.master, image=self.bg_photo)
    self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)

    # Now create your other widgets ON TOP of bg_label
    self.text_area = scrolledtext.ScrolledText(self.master, wrap=tk.WORD, bg="white")
    self.text_area.place(x=20, y=20, width=760, height=450)

    self.msg_entry = tk.Entry(self.master)
    self.msg_entry.place(x=20, y=500, width=650, height=30)

    self.send_btn = tk.Button(self.master, text="Send", command=self.send_message)
    self.send_btn.place(x=680, y=500, width=100, height=30)
