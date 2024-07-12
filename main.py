import tkinter
import os
import random
from platform import system

class Pet:
    def __init__(self):
        self.root = tkinter.Tk() # create window
        self.delay = 200 # delay in ms
        self.pixels_from_right = 200 # change to move the pet's starting position
        self.pixels_from_bottom = 85 # change to move the pet's starting position
        self.move_speed = 6 # change how fast the pet moves in pixels

        # initialize frame arrays
        self.animation = dict(
            idle = [tkinter.PhotoImage(file=os.path.abspath('gifs/idle.gif'), format = 'gif -index %i' % i) for i in range(5)],
            idle_to_sleep = [tkinter.PhotoImage(file=os.path.abspath('gifs/idle-to-sleep.gif'), format = 'gif -index %i' % i) for i in range(5)],
            sleep = [tkinter.PhotoImage(file=os.path.abspath('gifs/cry.gif'), format = 'gif -index %i' % i) for i in range(8)]*3,
            sleep_to_idle = [tkinter.PhotoImage(file=os.path.abspath('gifs/idle.gif'), format = 'gif -index %i' % i) for i in range(5)],
            walk_left = [tkinter.PhotoImage(file=os.path.abspath('gifs/walk_left.gif'), format = 'gif -index %i' % i) for i in range(5)],
            walk_right = [tkinter.PhotoImage(file=os.path.abspath('gifs/idle.gif'), format = 'gif -index %i' % i) for i in range(5)],
            heart = [tkinter.PhotoImage(file=os.path.abspath('gifs/heart.gif'), format = 'gif -index %i' % i) for i in range(15)]
        )

        # window configuration
        self.root.overrideredirect(True) # remove UI
        if system() == 'Windows':
            self.root.wm_attributes('-transparent','black')
        else: # platform is Mac/Linux
            # https://stackoverflow.com/questions/19080499/transparent-background-in-a-tkinter-window
            self.root.wm_attributes('-transparent', True) # do this for mac, but the bg stays black
            self.root.config(bg='systemTransparent')

        self.root.attributes('-topmost', True) # put window on top
        self.root.bind("<Button-1>", self.onLeftClick)
        self.root.bind("<Button-2>", self.onRightClick)
        self.root.bind("<Button-3>", self.onRightClick)
        self.root.bind("<Key>", self.onKeyPress)
        self.label = tkinter.Label(self.root, bd=0, bg='black') # borderless window
        if system() != 'Windows':
            self.label.config(bg='systemTransparent')
        self.label.pack()

        screen_width = self.root.winfo_screenwidth() # width of the entire screen
        screen_height = self.root.winfo_screenheight() # height of the entire screen
        self.min_width = 10 # do not let the pet move beyond this point
        self.max_width = screen_width-110 # do not let the pet move beyond this point

        # change starting properties of the window
        self.curr_width = screen_width-self.pixels_from_right
        self.curr_height = screen_height-self.pixels_from_bottom
        self.root.geometry('%dx%d+%d+%d' % (40, 35, self.curr_width, self.curr_height))

        # Initialize cursor position tracking
        self.prev_cursor_x = self.curr_width
        self.prev_cursor_y = self.curr_height
        self.current_animation = 'idle'
        self.animation_index = 0

        # Initialize sleep timer
        self.sleep_timer = random.randint(10000, 20000) # time in ms before the pet sleeps
        self.sleeping = False

        # Initialize heart animation timer
        self.heart_timer = 0

    def update(self):
        self.root.attributes('-topmost', True) # put window on top

        # Check if current_animation is valid
        if self.current_animation not in self.animation:
            self.current_animation = 'idle'
            self.animation_index = 0

        # Check if animation_index is within range
        if 0 <= self.animation_index < len(self.animation[self.current_animation]):
            self.label.configure(image=self.animation[self.current_animation][self.animation_index])
            self.animation_index = (self.animation_index + 1) % len(self.animation[self.current_animation])

        # move the pet if needed
        if self.current_animation in ('walk_left', 'walk_right'):
            self.move_window()

        # Track cursor and update animation accordingly if not sleeping
        if not self.sleeping:
            self.track_cursor()

            # Update sleep timer
            self.sleep_timer -= self.delay
            if self.sleep_timer <= 0:
                self.sleeping = True
                self.current_animation = 'sleep'
                #self.animation_index = 0

        # Handle waking up from sleep
        if self.current_animation == 'sleep' and random.random() < 0.05:
            self.sleeping = False
            self.current_animation = 'sleep_to_idle'
            #self.animation_index = 0
            self.sleep_timer = random.randint(10000, 20000)

        self.root.after(self.delay, self.update)

    def onLeftClick(self, event):
        print("detected left click")

    def onRightClick(self, event):
        self.quit()

    def onKeyPress(self, event):
        if event.char in ('q', 'Q'):
            self.quit()

    def move_window(self):
        if self.current_animation == 'walk_left':
            if self.curr_width > self.min_width:
                self.curr_width -= self.move_speed
        elif self.current_animation == 'walk_right':
            if self.curr_width < self.max_width:
                self.curr_width += self.move_speed

        self.root.geometry('%dx%d+%d+%d' % (40, 35, self.curr_width, self.curr_height))

    def track_cursor(self):
        cursor_x, cursor_y = self.root.winfo_pointerx(), self.root.winfo_pointery()

        # Check if cursor is on top of the pet
        if (self.curr_width <= cursor_x <= self.curr_width + 40) and (self.curr_height <= cursor_y <= self.curr_height + 35):
            if self.current_animation != 'heart':
                self.current_animation = 'heart'
                self.animation_index = 0
                self.heart_timer = 5000  # 5 seconds
            self.sleep_timer = random.randint(5000, 10000)  # Reset sleep timer
            return

        # Cursor is away from the pet
        if self.heart_timer <= 0:
            self.current_animation = 'idle'

        if cursor_x != self.prev_cursor_x or cursor_y != self.prev_cursor_y:
            if cursor_x < self.curr_width:
                next_animation = 'walk_left'
            else:
                next_animation = 'walk_right'
            if self.current_animation != next_animation:
                self.current_animation = next_animation
                self.animation_index = 0
            self.prev_cursor_x, self.prev_cursor_y = cursor_x, cursor_y

    def run(self):
        self.root.after(self.delay, self.update) # start animation
        self.root.mainloop()

    def quit(self):
        self.root.destroy()


if __name__ == '__main__':
    print('Initializing your desktop pet...')
    print('To quit, right click on the pet')
    pet = Pet()
    pet.run()