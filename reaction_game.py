import tkinter as tk
import random

class ReactionGame:
    def __init__(self, master):
        self.master = master
        self.master.title("Reaction Speed Game")

        # ---- Game variables ----
        self.level = 1
        self.lights_per_level = 10  # Level 1 starts with 10 lights
        self.lights_increment = 5   # Each new level adds 5 lights
        self.sequence_length = 0    # Will be computed for each level
        self.sequence = []          # Stores indices of which key to light
        self.current_index = 0      # Which step in the sequence we are on
        self.is_game_running = False
        self.waiting_for_click = False

        self.key_map = {
            'a': 0,
            's': 1,
            'd': 2,
            'f': 3,
            'j': 4,
            'k': 5,
            'l': 6,
            ';': 7
        }

        # ---- Bind a keypress event to our on_key_press method ----
        self.master.bind("<KeyPress>", self.on_key_press)

        # ---- Layout frames ----
        self.top_frame = tk.Frame(self.master)
        self.top_frame.pack(pady=10)
        
        self.middle_frame = tk.Frame(self.master)
        self.middle_frame.pack(pady=10)
        
        self.bottom_frame = tk.Frame(self.master)
        self.bottom_frame.pack(pady=10)

        # ---- Info Label ----
        self.info_label = tk.Label(self.top_frame, text="Press 'Start' to begin!", font=("Arial", 16))
        self.info_label.pack()

        self.button_labels = ["A", "S", "D", "F", "J", "K", "L", ";"]
        self.key_buttons = []
        
        for i, label in enumerate(self.button_labels):
            btn = tk.Button(
                self.middle_frame,
                text=label,
                width=10,
                height=2,
                bg="gray",
                state="disabled"
            )
            self.key_buttons.append(btn)

        for i, btn in enumerate(self.key_buttons):
            if i < 4:  # left column
                btn.grid(row=i, column=0, padx=10, pady=5)
            else:      # right column
                btn.grid(row=i-4, column=1, padx=10, pady=5)

        self.start_button = tk.Button(
            self.bottom_frame,
            text="Start",
            width=12,
            command=self.start_game
        )
        self.start_button.pack(pady=5)

        self.next_level_button = tk.Button(
            self.bottom_frame,
            text="Next Level",
            width=12,
            state="disabled",
            command=self.next_level
        )
        self.next_level_button.pack(pady=5)

    def start_game(self):
        """Begin the game. Initialize everything for the current level."""
        if self.is_game_running:
            return
        
        self.info_label.config(text=f"Get ready... Level {self.level}")
        self.is_game_running = True
        self.current_index = 0
        self.sequence_length = self.lights_per_level + (self.level - 1) * self.lights_increment
        
        self.next_level_button.config(state="disabled")

        self.sequence = [random.randint(0, 7) for _ in range(self.sequence_length)]
        
        self.master.after(1500, self.light_next_key)

    def light_next_key(self):
        """Lights the next key (in red), waiting for the correct keyboard press."""
        if self.current_index >= self.sequence_length:
            self.finish_level()
            return

        key_idx = self.sequence[self.current_index]
        
        for i, btn in enumerate(self.key_buttons):
            if i == key_idx:
                btn.config(bg="red")
            else:
                btn.config(bg="gray")

        self.waiting_for_click = True

    def on_key_press(self, event):
        """
        When the player presses a key on the keyboard, check if it matches
        the lit key. If correct, turn the button green briefly, then continue.
        """
        if not self.is_game_running or not self.waiting_for_click:
            return
        pressed_char = event.char.lower()
        
        if pressed_char in self.key_map:
            pressed_idx = self.key_map[pressed_char]

            correct_idx = self.sequence[self.current_index]
            
            if pressed_idx == correct_idx:
                self.key_buttons[correct_idx].config(bg="green")
                self.waiting_for_click = False
                self.master.after(300, self.reset_key)
            else:
                self.info_label.config(text="Wrong key! Try again...")

    def reset_key(self):
        """Turn off the green key and proceed to the next in the sequence."""
        correct_idx = self.sequence[self.current_index]
        self.key_buttons[correct_idx].config(bg="gray")

        self.current_index += 1
        self.light_next_key()

    def finish_level(self):
        """Called when all keys in the level have been lit and pressed."""
        self.is_game_running = False
        self.info_label.config(text=f"Level {self.level} complete!")
        
        self.next_level_button.config(state="normal")

        for btn in self.key_buttons:
            btn.config(bg="gray")

    def next_level(self):
        """Moves to the next level."""
        self.level += 1
        self.info_label.config(text=f"Starting Level {self.level}")
        self.start_game()


def main():
    root = tk.Tk()
    game = ReactionGame(root)
    root.mainloop()

if __name__ == "__main__":
    main()

