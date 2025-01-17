import tkinter as tk
from tkinter import ttk, filedialog
import tkinter.simpledialog as simpledialog
import io
import base64
import requests

from PIL import Image, ImageTk

class DrawingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Advanced Tkinter Drawing App")

        # Canvas setup
        self.canvas_width = 800
        self.canvas_height = 600
        self.canvas = tk.Canvas(
            self.root, width=self.canvas_width, height=self.canvas_height, bg="white"
        )
        self.canvas.pack()

        # Variables for drawing
        self.last_x = None
        self.last_y = None
        self.current_stroke_item_ids = []

        # Undo/Redo stacks
        self.undo_stack = []
        self.redo_stack = []

        # Bind mouse events for drawing
        self.canvas.bind("<ButtonPress-1>", self.on_button_press)
        self.canvas.bind("<B1-Motion>", self.draw)
        self.canvas.bind("<ButtonRelease-1>", self.on_button_release)

        # Bind keyboard shortcuts for undo/redo
        self.root.bind("<Control-z>", self.handle_undo_key)
        self.root.bind("<Control-Shift-z>", self.handle_redo_key)
        self.root.bind("<Control-Z>", self.handle_redo_key)

        # Bottom frame for actions
        bottom_frame = tk.Frame(self.root)
        bottom_frame.pack(side=tk.BOTTOM, pady=5)

        # "Generate" button
        generate_button = tk.Button(bottom_frame, text="Generate", command=self.on_generate)
        generate_button.pack(side=tk.LEFT, padx=10)

        # "Show/Hide History" button
        self.history_visible = False
        toggle_history_button = tk.Button(bottom_frame, text="Show History", 
                                          command=self.toggle_history)
        toggle_history_button.pack(side=tk.LEFT, padx=10)

        # A frame to hold the history of generated images (initially hidden)
        self.history_frame = tk.Frame(self.root)
        # We'll pack/place this frame only when needed.
        
        # A list to hold references to generated images (PIL or PhotoImage).
        self.generated_images = []

    # -----------------------------
    # Drawing logic
    # -----------------------------
    def on_button_press(self, event):
        """When LMB is pressed, start a new stroke."""
        self.current_stroke_item_ids = []
        self.last_x = event.x
        self.last_y = event.y

    def draw(self, event):
        """Draw a continuous line from the last known position to the current mouse position."""
        if self.last_x is not None and self.last_y is not None:
            item_id = self.canvas.create_line(
                self.last_x,
                self.last_y,
                event.x,
                event.y,
                fill="black",
                width=2,
                smooth=True
            )
            self.current_stroke_item_ids.append(item_id)

        self.last_x = event.x
        self.last_y = event.y

    def on_button_release(self, event):
        """When LMB is released, push stroke onto undo stack, clear redo stack."""
        if self.current_stroke_item_ids:
            self.undo_stack.append(self.current_stroke_item_ids)
            self.current_stroke_item_ids = []
        self.redo_stack.clear()
        self.last_x = None
        self.last_y = None

    # -----------------------------
    # Undo/Redo logic
    # -----------------------------
    def undo(self):
        if not self.undo_stack:
            return
        stroke = self.undo_stack.pop()
        for item_id in stroke:
            self.canvas.itemconfig(item_id, state='hidden')
        self.redo_stack.append(stroke)

    def redo(self):
        if not self.redo_stack:
            return
        stroke = self.redo_stack.pop()
        for item_id in stroke:
            self.canvas.itemconfig(item_id, state='normal')
        self.undo_stack.append(stroke)

    def handle_undo_key(self, event=None):
        self.undo()

    def handle_redo_key(self, event=None):
        self.redo()

    # -----------------------------
    # Generating logic
    # -----------------------------
    def on_generate(self):
        """
        1. Capture the canvas as an image (PNG in-memory).
        2. Ask the user for a (large) prompt in a custom popup.
        3. Show a "Loading..." indicator.
        4. Call the (mock) replicate API to get the generated image.
        5. On success, close "Loading..." and display the result in a popup.
        6. Store the image in the history.
        """
        # 1) Capture the canvas as an image
        canvas_img = self.capture_canvas_as_image()

        # 2) Prompt the user for a large text description
        prompt = self.ask_large_text()
        if not prompt:
            return  # user cancelled or typed nothing

        # 3) Show a "Loading..." indicator
        loading_popup = tk.Toplevel(self.root)
        loading_popup.title("Generating...")
        tk.Label(loading_popup, text="Please wait, generating image...").pack(padx=20, pady=20)
        loading_popup.update()

        # 4) Convert canvas image + prompt to base64, call replicate (or any external API)
        #    This is just a placeholder for demonstration.
        #    Replace with your real replicate code:
        try:
            # Encode canvas to base64
            buffer = io.BytesIO()
            canvas_img.save(buffer, format="PNG")
            encoded_canvas = base64.b64encode(buffer.getvalue()).decode('utf-8')
            
            # Here is where you'd form your actual input dict
            # We mimic the replicate call by a custom function:
            generated_img = self.mock_replicate_api(encoded_canvas, prompt)
        except Exception as e:
            loading_popup.destroy()
            tk.messagebox.showerror("Error", f"Failed generating image:\n{e}")
            return

        # 5) Close the "Loading..." dialog
        loading_popup.destroy()

        # 6) Show the generated image in a popup
        self.show_image_popup(generated_img, "Generated Image")

        #   Keep track of it in a local list (for the History)
        self.generated_images.append(generated_img)

        #   If the history is currently shown, update it
        if self.history_visible:
            self.update_history_display()

    def capture_canvas_as_image(self):
        """
        Capture the current drawing on the Tkinter canvas as a PIL Image.
        Approach: 
           1) Use canvas.postscript() to get an .eps file in memory.
           2) Convert the .eps to a PIL Image.
           3) Resize or crop as needed (if there's extra margin).
        """
        # Update the canvas to ensure all drawing is up to date
        self.canvas.update()
        
        # Generate a postscript image
        ps_data = self.canvas.postscript(colormode='color')
        
        # Convert PostScript to PIL Image
        ps_image = Image.open(io.BytesIO(ps_data.encode('utf-8')))
        
        # Sometimes the postscript bounding box might be bigger than the canvas
        # so let's crop it to the actual canvas size:
        ps_image = ps_image.crop((0, 0, self.canvas_width, self.canvas_height))
        
        return ps_image

    def ask_large_text(self):
        """
        A custom popup to ask for a large text input from the user.
        Returns the entered text, or None if canceled.
        """
        dialog = tk.Toplevel(self.root)
        dialog.title("Enter your prompt")

        # Make it modal
        dialog.transient(self.root)
        dialog.grab_set()

        tk.Label(dialog, text="Describe what you've drawn or want to generate:").pack(pady=5)
        
        # A text widget for multi-line input
        text_widget = tk.Text(dialog, width=60, height=10, wrap="word")
        text_widget.pack(padx=10, pady=5)

        # Frame for OK/Cancel
        btn_frame = tk.Frame(dialog)
        btn_frame.pack(pady=5)

        # Variables to store user decision
        user_input = {"text": None}

        def on_ok():
            user_input["text"] = text_widget.get("1.0", tk.END).strip()
            dialog.destroy()

        def on_cancel():
            dialog.destroy()

        ok_btn = tk.Button(btn_frame, text="OK", width=10, command=on_ok)
        ok_btn.pack(side=tk.LEFT, padx=5)
        cancel_btn = tk.Button(btn_frame, text="Cancel", width=10, command=on_cancel)
        cancel_btn.pack(side=tk.LEFT, padx=5)

        dialog.wait_window()
        return user_input["text"]

    def mock_replicate_api(self, encoded_image, prompt):
        """
        A placeholder function to mimic calling Replicate with:
          1) base64-encoded user-drawn image,
          2) prompt text,
          3) and other parameters.
          
        For demonstration, we'll just fetch a placeholder image from the internet
        to simulate a "generated" image. Replace this with your actual code, e.g.:
        """

        import replicate
        input = {
            "image": f"data:application/octet-stream;base64,{encoded_image}",
            "prompt": prompt
        }
        output = replicate.run(
            "jagilley/controlnet-scribble:435061a1b5a4c1e26740464bf786efdfa9cb3a3ac488595a2de23e143fdb0117",
            input=input
        )

        img_data = output.read()
        pil_img = Image.open(io.BytesIO(img_data))
        return pil_img

    def show_image_popup(self, pil_image, title="Image"):
        """
        Shows a PIL image in a new Toplevel window.
        """
        popup = tk.Toplevel(self.root)
        popup.title(title)

        # Convert PIL to PhotoImage
        tk_img = ImageTk.PhotoImage(pil_image)
        lbl = tk.Label(popup, image=tk_img)
        lbl.image = tk_img  # keep reference!
        lbl.pack()

    # -----------------------------
    # History logic
    # -----------------------------
    def toggle_history(self):
        """
        Show or hide the history of generated images.
        """
        self.history_visible = not self.history_visible
        if self.history_visible:
            # Show the frame
            self.history_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=10)
            self.update_history_display()
        else:
            # Hide the frame
            self.history_frame.pack_forget()

    def update_history_display(self):
        """
        Clear the history_frame and re-populate it with thumbnails
        of the generated images. Clicking a thumbnail shows the full image.
        """
        # Clear old widgets
        for widget in self.history_frame.winfo_children():
            widget.destroy()

        if not self.generated_images:
            tk.Label(self.history_frame, text="No generated images yet.").pack()
            return

        # Create thumbnails in a horizontal scrolled frame
        # (For simplicity, we can just pack them in a row)
        # If you have many images, consider a better layout or a canvas-based scroller.
        for idx, img in enumerate(self.generated_images):
            # Make a thumbnail
            thumb = img.copy()
            thumb.thumbnail((80, 80))  # small thumbnail
            tk_thumb = ImageTk.PhotoImage(thumb)

            btn = tk.Button(
                self.history_frame, 
                image=tk_thumb, 
                command=lambda i=img: self.show_image_popup(i, "History Image")
            )
            # We must keep a reference to tk_thumb, otherwise it gets garbage collected
            btn.image = tk_thumb
            btn.pack(side=tk.LEFT, padx=5)


# -----------------------------
# Run the app
# -----------------------------
if __name__ == "__main__":
    root = tk.Tk()
    app = DrawingApp(root)
    root.mainloop()

