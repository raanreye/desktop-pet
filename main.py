import tkinter as tk
from pathlib import Path
import random
from platform import system

class Pet:
    def __init__(self):
        self.root = tk.Tk()
        self.delay = 200
        self.pixels_from_right = 200
        self.pixels_from_bottom = 85
        self.move_speed = 6
        self.in_home = False

        self.animation = self._load_animations()

        self._configure_window()
        self._setup_label()
        self._initialize_position()
        self._initialize_state()
        self._create_home()

    def _load_animations(self):
        animations = {
            'idle': 'idle.gif',
            'idle_to_sleep': 'idle-to-sleep.gif',
            'sleep': 'cry.gif',
            'sleep_to_idle': 'idle.gif',
            'walk_left': 'walk_left.gif',
            'walk_right': 'idle.gif',
            'heart': 'heart.gif'
        }
        loaded_animations = {}
        for name, filename in animations.items():
            file_path = Path('gifs', filename)
            if not file_path.exists():
                print(f"Warning: File not found: {file_path}")
                continue
            try:
                frames = []
                img = tk.PhotoImage(file=file_path)
                for i in range(100):  # Arbitrary large number
                    try:
                        frames.append(tk.PhotoImage(file=file_path, format=f'gif -index {i}'))
                    except tk.TclError:
                        break  # No more frames
                if frames:
                    loaded_animations[name] = frames
                else:
                    print(f"Warning: No frames loaded for {filename}")
            except Exception as e:
                print(f"Error loading {filename}: {str(e)}")
        return loaded_animations

    def _configure_window(self):
        self.root.overrideredirect(True)
        if system() == 'Windows':
            self.root.wm_attributes('-transparent', 'black')
        else:
            self.root.wm_attributes('-transparent', True)
            self.root.config(bg='systemTransparent')
        self.root.attributes('-topmost', True)
        self.root.bind("<Button-1>", self.on_left_click)
        self.root.bind("<Button-2>", self.quit)
        self.root.bind("<Button-3>", self.quit)
        self.root.bind("<Key>", self.on_key_press)

    def _setup_label(self):
        self.label = tk.Label(self.root, bd=0, bg='black')
        if system() != 'Windows':
            self.label.config(bg='systemTransparent')
        self.label.pack()

    def _initialize_position(self):
        self.screen_width = self.root.winfo_screenwidth()
        self.screen_height = self.root.winfo_screenheight()
        self.min_width = 10
        self.max_width = self.screen_width - 110
        self.curr_width = self.screen_width - self.pixels_from_right
        self.curr_height = self.screen_height - self.pixels_from_bottom
        self._update_geometry()

    def _initialize_state(self):
        self.prev_cursor_x = self.curr_width
        self.prev_cursor_y = self.curr_height
        self.current_animation = 'idle'
        self.animation_index = 0
        self.sleep_timer = random.randint(10000, 20000)
        self.sleeping = False
        self.heart_timer = 0
        self.in_home = False
        self.home_timer = 0

    def _create_home(self):
        home_width = 60
        home_height = 60
        self.home_x = self.screen_width - home_width - 10
        self.home_y = self.screen_height - home_height - 10
        
        self.home_window = tk.Toplevel(self.root)
        self.home_window.overrideredirect(True)
        self.home_window.attributes('-topmost', True)
        self.home_window.geometry(f"{home_width}x{home_height}+{self.home_x}+{self.home_y}")
        
        home_canvas = tk.Canvas(self.home_window, width=home_width, height=home_height, bg='lightblue', highlightthickness=0)
        home_canvas.pack()
        
        # Draw a simple house shape
        home_canvas.create_polygon(10, 30, 30, 10, 50, 30, fill='red')
        home_canvas.create_rectangle(10, 30, 50, 60, fill='brown')

    def update(self):
        self.root.attributes('-topmost', True)
        self._update_animation()
        self._handle_movement()
        self._handle_sleep()
        self._handle_home()
        
        if not self.in_home and not self.sleeping:
            self._track_cursor()
        
        if self.heart_timer > 0:
            self.heart_timer -= self.delay
        
        self.root.after(self.delay, self.update)

    def _update_animation(self):
        if self.current_animation not in self.animation:
            self.current_animation = 'idle'
            self.animation_index = 0
        frames = self.animation[self.current_animation]
        if 0 <= self.animation_index < len(frames):
            self.label.configure(image=frames[self.animation_index])
            self.animation_index = (self.animation_index + 1) % len(frames)

    def _handle_movement(self):
        if not self.in_home:
            if self.current_animation in ('walk_left', 'walk_right'):
                self._move_window()
            if not self.sleeping:
                self._track_cursor()

    def _handle_sleep(self):
        if not self.sleeping:
            self.sleep_timer -= self.delay
            if self.sleep_timer <= 0:
                self.sleeping = True
                self.current_animation = 'sleep'
        elif self.current_animation == 'sleep' and random.random() < 0.05:
            self.sleeping = False
            self.current_animation = 'sleep_to_idle'
            self.sleep_timer = random.randint(10000, 20000)

    def on_left_click(self, event):
        print("Detected left click")

    def on_key_press(self, event):
        if event.char.lower() == 'l':
            self.quit()

    def _cursor_on_pet(self, cursor_x, cursor_y):
        return (self.curr_width <= cursor_x <= self.curr_width + 40 and
                self.curr_height <= cursor_y <= self.curr_height + 35)

    def _handle_home(self):
        if self.in_home:
            self.home_timer -= self.delay
            if self.home_timer <= 0:
                self.in_home = False
                # Position the pet to the left of the house
                self.curr_width = self.home_x - 50  # 50 pixels to the left of the house
                self.curr_height = self.home_y + 30  # Align vertically with the middle of the house
                self._update_geometry()
                self.current_animation = 'idle'
                self.animation_index = 0
                self.heart_timer = 0  # Reset heart timer
                self.sleep_timer = random.randint(10000, 20000)  # Reset sleep timer
                self.root.deiconify()  # Show the pet
                self._search_for_mouse()
        else:
            home_center_x = self.home_x + 30
            home_center_y = self.home_y + 30
            distance_to_home = ((self.curr_width - home_center_x) ** 2 + (self.curr_height - home_center_y) ** 2) ** 0.5
            if distance_to_home < 50:  # If pet is close to home
                self.in_home = True
                self.home_timer = random.randint(3000, 8000)  # 3-8 seconds in home
                self.root.withdraw()  # Hide the pet

    def _search_for_mouse(self):
        if not self.in_home:
            cursor_x, cursor_y = self.root.winfo_pointerxy()
            if not self._cursor_on_pet(cursor_x, cursor_y):
                self._handle_cursor_movement(cursor_x, cursor_y)
            self.root.after(self.delay, self._search_for_mouse)

    def _go_home(self):
        if not self.in_home:
            home_center_x = self.home_x
            home_center_y = self.home_y + 30
            
            # Calculate direction to home
            dx = home_center_x - self.curr_width
            dy = home_center_y - self.curr_height
            distance = (dx**2 + dy**2)**0.5
            
            if distance > self.move_speed + 50:  # Stop 50 pixels before the house
                # Move towards home
                self.curr_width += int(dx / distance * self.move_speed)
                self.curr_height += int(dy / distance * self.move_speed)
                self._update_geometry()
                
                # Set walking animation
                self.current_animation = 'walk_right' if dx > 0 else 'walk_left'
                
                # Schedule next move
                self.root.after(self.delay, self._go_home)
            else:
                # Close enough to home, enter it
                self.in_home = True
                self.home_timer = random.randint(3000, 8000)  # 3-8 seconds in home
                self.root.withdraw()  # Hide the pet

    def _move_window(self):
        if self.current_animation == 'walk_left':
            self.curr_width = max(self.min_width, self.curr_width - self.move_speed)
        elif self.current_animation == 'walk_right':
            self.curr_width = min(self.max_width, self.curr_width + self.move_speed)
        self._update_geometry()

    def _track_cursor(self):
        cursor_x, cursor_y = self.root.winfo_pointerxy()
        if self._cursor_on_pet(cursor_x, cursor_y):
            self._handle_pet_interaction()
        else:
            self._handle_cursor_movement(cursor_x, cursor_y)

    def _handle_cursor_movement(self, cursor_x, cursor_y):
        if self.heart_timer <= 0:
            if cursor_x != self.prev_cursor_x or cursor_y != self.prev_cursor_y:
                next_animation = 'walk_left' if cursor_x < self.curr_width else 'walk_right'
                if self.current_animation != next_animation:
                    self.current_animation = next_animation
                    self.animation_index = 0
                self.prev_cursor_x, self.prev_cursor_y = cursor_x, cursor_y

    def _handle_pet_interaction(self):
        if self.current_animation != 'heart' and self.heart_timer <= 0:
            self.current_animation = 'heart'
            self.animation_index = 0
            self.heart_timer = 5000
            self.sleep_timer = random.randint(5000, 10000)
            self.root.after(5000, self._start_go_home)  # Schedule going home after 5 seconds

    def _start_go_home(self):
        if self.current_animation == 'heart':
            self._go_home()
        else:
            self.current_animation = 'idle'

        def _handle_cursor_movement(self, cursor_x, cursor_y):
            if self.heart_timer <= 0:
                self.current_animation = 'idle'
            if cursor_x != self.prev_cursor_x or cursor_y != self.prev_cursor_y:
                next_animation = 'walk_left' if cursor_x < self.curr_width else 'walk_right'
                if self.current_animation != next_animation:
                    self.current_animation = next_animation
                    self.animation_index = 0
                self.prev_cursor_x, self.prev_cursor_y = cursor_x, cursor_y

    def _update_geometry(self):
        if not self.in_home:
            self.root.deiconify()  # Show the pet if it's not in home
            self.root.geometry(f'40x35+{self.curr_width}+{self.curr_height}')

    def run(self):
        self.root.after(self.delay, self.update)
        self.root.mainloop()

    def quit(self, event=None):
        try:
            if self.home_window.winfo_exists():
                self.home_window.destroy()
        except:
            pass  # If there's any error destroying the home window, just ignore it
        
        try:
            if self.root.winfo_exists():
                self.root.destroy()
        except:
            pass  # If there's any error destroying the root window, just ignore it
        
        import sys
        sys.exit()  # Ensure the entire application exits

if __name__ == '__main__':
    print('Initializing your desktop pet...')
    print('To quit, right click on the pet')
    pet = Pet()
    pet.run()
