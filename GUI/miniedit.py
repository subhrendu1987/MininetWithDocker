import tkinter as tk

class DragDropApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Drag and Drop App")

        # Toolbar
        self.toolbar = tk.Frame(master, bg="lightgrey")
        self.toolbar.pack(side=tk.TOP, fill=tk.X)

        # Side Pane
        self.side_pane = tk.Frame(master, bg="lightblue", width=200)
        self.side_pane.pack(side=tk.LEFT, fill=tk.Y)

        # Canvas
        self.canvas = tk.Canvas(master, bg="white")
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Add widgets to toolbar
        self.btn_clear = tk.Button(self.toolbar, text="Clear Canvas", command=self.clear_canvas)
        self.btn_clear.pack(side=tk.LEFT)

        # Add widgets to side pane
        self.lbl_items = tk.Label(self.side_pane, text="Draggable Items", bg="lightblue")
        self.lbl_items.pack(pady=10)
        self.item1 = tk.Label(self.side_pane, text="Item 1", bg="white", relief=tk.RAISED)
        self.item1.pack(pady=5)

        # Make side pane items draggable
        self.make_draggable(self.item1)

        # Initialize variables for drag and drop functionality
        self.drag_data = {"x": 0, "y": 0, "item": None}

        # Bind events
        self.canvas.bind("<ButtonPress-1>", self.on_drag_start)
        self.canvas.bind("<B1-Motion>", self.on_drag_motion)
        self.canvas.bind("<ButtonRelease-1>", self.on_drag_release)

    def make_draggable(self, widget):
        widget.bind("<ButtonPress-1>", self.on_drag_start)
        widget.bind("<ButtonRelease-1>", self.on_drag_release)

    def on_drag_start(self, event):
        widget = event.widget
        widget.lift()
        self.drag_data["item"] = widget
        self.drag_data["x"] = event.x
        self.drag_data["y"] = event.y

    def on_drag_motion(self, event):
        widget = self.drag_data["item"]
        x = widget.winfo_x() - self.drag_data["x"] + event.x
        y = widget.winfo_y() - self.drag_data["y"] + event.y
        widget.place(x=x, y=y)

    def on_drag_release(self, event):
        pass

    def clear_canvas(self):
        self.canvas.delete("all")

def main():
    root = tk.Tk()
    app = DragDropApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
