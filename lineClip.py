import tkinter as tk

class CohenSutherlandClipper:
    def __init__(self, master):
        self.master = master
        self.master.title("Cohen-Sutherland Line Clipping")

        # Canvas for drawing
        self.canvas = tk.Canvas(master, width=800, height=600, bg='white')
        self.canvas.pack()

        # Variables to hold the clipping window and drawn lines
        self.clipping_window = None
        self.lines = []

        # Variables to track the starting point for line segments
        self.start_x = None
        self.start_y = None

        # Frame for coordinate inputs
        self.coord_frame = tk.Frame(master)
        tk.Label(self.coord_frame, text="X1:").grid(row=0, column=0)
        self.x1_entry = tk.Entry(self.coord_frame, width=5)
        self.x1_entry.grid(row=0, column=1)

        tk.Label(self.coord_frame, text="Y1:").grid(row=1, column=0)
        self.y1_entry = tk.Entry(self.coord_frame, width=5)
        self.y1_entry.grid(row=1, column=1)

        tk.Label(self.coord_frame, text="X2:").grid(row=0, column=2)
        self.x2_entry = tk.Entry(self.coord_frame, width=5)
        self.x2_entry.grid(row=0, column=3)

        tk.Label(self.coord_frame, text="Y2:").grid(row=1, column=2)
        self.y2_entry = tk.Entry(self.coord_frame, width=5)
        self.y2_entry.grid(row=1, column=3)

        self.define_button = tk.Button(self.coord_frame, text="Define Clipping Window", command=self.define_clipping_window)
        self.define_button.grid(row=2, column=0, columnspan=4)

        self.coord_frame.pack()

        # Bind mouse events to canvas
        self.canvas.bind("<Button-1>", self.on_click)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)

        # Buttons for clipping and resetting
        self.clip_button = tk.Button(master, text="Clip", command=self.clip_lines)
        self.clip_button.pack(side=tk.LEFT)

        self.reset_button = tk.Button(master, text="Reset", command=self.reset)
        self.reset_button.pack(side=tk.LEFT)

    def on_click(self, event):
        if self.clipping_window is None:
            # Set start point for line segment
            self.start_x, self.start_y = event.x, event.y
        else:
            # If clipping window is defined, set start point for line drawing
            self.start_x, self.start_y = event.x, event.y

    def on_release(self, event):
        if self.clipping_window is None:
            # Define clipping window if not already defined
            self.clipping_window = (self.start_x, self.start_y, event.x, event.y)
            self.draw_clipping_window()
        else:
            # Draw a line segment
            self.lines.append((self.start_x, self.start_y, event.x, event.y))
            self.draw_line(self.start_x, self.start_y, event.x, event.y)

    def define_clipping_window(self):
        try:
            # Get coordinates from input fields
            x1 = int(self.x1_entry.get())
            y1 = int(self.y1_entry.get())
            x2 = int(self.x2_entry.get())
            y2 = int(self.y2_entry.get())
            self.clipping_window = (x1, y1, x2, y2)
            self.canvas.delete("all")  # Clear previous drawings
            self.draw_clipping_window()
            self.lines.clear()  # Clear previously drawn lines
        except ValueError:
            print("Please enter valid integer coordinates.")

    def draw_clipping_window(self):
        x1, y1, x2, y2 = self.clipping_window
        self.canvas.create_rectangle(x1, y1, x2, y2, outline='blue', width=2)

    def draw_line(self, x1, y1, x2, y2, color='black'):
        self.canvas.create_line(x1, y1, x2, y2, fill=color, width=2)

    def reset(self):
        self.canvas.delete("all")
        self.clipping_window = None
        self.lines = []
        # Clear input fields
        self.x1_entry.delete(0, tk.END)
        self.y1_entry.delete(0, tk.END)
        self.x2_entry.delete(0, tk.END)
        self.y2_entry.delete(0, tk.END)

    def clip_lines(self):
        if self.clipping_window is None:
            return

        x_min, y_min, x_max, y_max = self.clipping_window
        
        for line in self.lines:
            x1, y1, x2, y2 = line
            code1 = self.compute_code(x1, y1, x_min, y_min, x_max, y_max)
            code2 = self.compute_code(x2, y2, x_min, y_min, x_max, y_max)

            if code1 == 0 and code2 == 0:
                # Line is completely inside
                self.draw_line(x1, y1, x2, y2, 'green')
            elif code1 & code2 != 0:
                # Line is completely outside
                self.draw_line(x1, y1, x2, y2, 'red')
            else:
                # Line is partially clipped
                x1, y1, x2, y2 = self.cohen_sutherland(x1, y1, x2, y2, x_min, y_min, x_max, y_max)
                if (x1, y1, x2, y2) != (None, None, None, None):
                    self.draw_line(x1, y1, x2, y2, 'orange')

        # Draw the legend box after clipping
        self.draw_legend()

    def draw_legend(self):
        # Draw a larger box for the legend
        legend_x, legend_y = 650, 50
        self.canvas.create_rectangle(legend_x, legend_y, legend_x + 150, legend_y + 110,outline='#f7edec', fill='#f7edec')

        # Add text to explain colors
        self.canvas.create_text(legend_x + 10, legend_y + 10, anchor='nw', text="Color Legend:", font=("Arial", 10, "bold"))
        self.canvas.create_text(legend_x + 10, legend_y + 30, anchor='nw', text="Green: Fully Inside", fill='green')
        self.canvas.create_text(legend_x + 10, legend_y + 50, anchor='nw', text="Red: Fully Outside", fill='red')
        self.canvas.create_text(legend_x + 10, legend_y + 70, anchor='nw', text="Orange: Partially Clipped", fill='orange')

    def compute_code(self, x, y, x_min, y_min, x_max, y_max):
        code = 0
        if x < x_min:    # to the left of clip window
            code |= 1
        elif x > x_max:  # to the right of clip window
            code |= 2
        if y < y_min:    # below the clip window
            code |= 4
        elif y > y_max:  # above the clip window
            code |= 8
        return code

    def cohen_sutherland(self, x1, y1, x2, y2, x_min, y_min, x_max, y_max):
        code1 = self.compute_code(x1, y1, x_min, y_min, x_max, y_max)
        code2 = self.compute_code(x2, y2, x_min, y_min, x_max, y_max)

        while True:
            if code1 == 0 and code2 == 0:
                return (x1, y1, x2, y2)  # Both points inside
            elif (code1 & code2) != 0:
                return (None, None, None, None)  # Both points outside
            else:
                code_out = code1 if code1 != 0 else code2
                if code_out & 8:  # Point is above the clip rectangle
                    x = x1 + (x2 - x1) * (y_max - y1) / (y2 - y1)
                    y = y_max
                elif code_out & 4:  # Point is below the clip rectangle
                    x = x1 + (x2 - x1) * (y_min - y1) / (y2 - y1)
                    y = y_min
                elif code_out & 2:  # Point is to the right of clip rectangle
                    y = y1 + (y2 - y1) * (x_max - x1) / (x2 - x1)
                    x = x_max
                elif code_out & 1:  # Point is to the left of clip rectangle
                    y = y1 + (y2 - y1) * (x_min - x1) / (x2 - x1)
                    x = x_min

                if code_out == code1:
                    x1, y1 = x, y
                    code1 = self.compute_code(x1, y1, x_min, y_min, x_max, y_max)
                else:
                    x2, y2 = x, y
                    code2 = self.compute_code(x2, y2, x_min, y_min, x_max, y_max)

class MainWindow:
    def __init__(self, master):
        self.master = master
        self.master.geometry("800x600")  # Set window size same as canvas
        self.master.title("Cohen-Sutherland Clipper")
        
        self.icon = tk.PhotoImage(file="scissors.png")  
        self.master.iconphoto(True, self.icon)

        # Centered Text
        self.canvas = tk.Canvas(master, width=800, height=600, bg="#f7edec")
        self.canvas.pack()
        self.canvas.create_text(400, 250, text="Cohen-Sutherland Clipper", font=("Arial", 30, "bold"), fill="black")
        


        # Button to open the second window
        self.open_button = tk.Button(master, text="Get Started", command=self.open_clipper_window)
        self.open_button.place(x=350, y=550)

    def open_clipper_window(self):
        # Open the second window (CohenSutherlandClipper window)
        clipper_window = tk.Toplevel(self.master)
        app = CohenSutherlandClipper(clipper_window)
        
        # Close the first window after opening the second window
        self.master.withdraw()  # Hide the main window 

        # After the second window is closed, destroy the main window
        clipper_window.protocol("WM_DELETE_WINDOW", self.on_clipper_close)

    def on_clipper_close(self):
        # Destroy the main window when the second window is closed
        self.master.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    main_app = MainWindow(root)
    root.mainloop()
