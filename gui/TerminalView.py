import tkinter as tk

class TerminalView(tk.Frame):
    def __init__(self, parent, controller, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        
        self.controller = controller  # Initialize ControlsManager
        self.configure_layout()
        self.grid(row=0, column=0, sticky="nsew")  # Add this line to ensure the frame is placed in the window

    def configure_layout(self):
        # Create a grid layout with 2 rows and 1 column
        self.grid_rowconfigure(0, weight=1, minsize=1)  # for the text area
        self.grid_rowconfigure(1, weight=0)  # for the input box
        self.grid_columnconfigure(0, weight=1)

        # Create a frame for the text area
        frame = tk.Frame(self)
        frame.grid(row=0, column=0, padx=5, pady=10, sticky="nsew")

        # Add scrollbar to the frame
        self.scrollbar = tk.Scrollbar(frame, orient=tk.VERTICAL)

        # Create the textbox for the terminal-like area
        self.textbox = tk.Text(frame, wrap=tk.WORD, yscrollcommand=self.scrollbar.set)
        self.textbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.config(command=self.textbox.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.textbox.config(state=tk.DISABLED)

        # Create the input box at the bottom
        input_frame = tk.Frame(self)
        input_frame.grid(row=1, column=0, padx=5, sticky="ew")

        self.input_box = tk.Entry(input_frame)
        self.input_box.pack(fill=tk.X)

        self.input_box.bind("<Return>", self.on_enter)

    def append_message(self, message):
        """Append a message or list of messages to the textbox and scroll to the bottom."""
        self.textbox.config(state=tk.NORMAL)
        
        # Check if the message is a list of strings
        if isinstance(message, list):
            for msg in message:
                self.textbox.insert(tk.END, msg + "\n")
        else:
            self.textbox.insert(tk.END, message + "\n")
        
        self.textbox.config(state=tk.DISABLED)
        self.textbox.yview(tk.END)

    def on_enter(self, event):
        user_input = self.input_box.get()
        self.input_box.delete(0, tk.END)
        self.append_message(f"> {user_input}")

        # Pass the command to Manager for processing
        self.controller.process_command(user_input)