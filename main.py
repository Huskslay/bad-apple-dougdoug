import cv2, time, keyboard
from cv2.typing import MatLike
from pynput.mouse import Controller, Button

# These are based on the screen and desired output
GRID_SIZE = (10, 5)
CARD_START = (420, 300)
CARD_SIZE = (122, 137)
COLOR_THRESHOLDS = (100, 254)

# Timings used for generation
TIME_PER_FRAME = 3
TIME_PER_PIXEL = 0.01

# Other constants
FRAMES_START, FRAMES_END = 0, 6572
R, G, B = 0, 1, 2
MAX = 255

FULL, HALF, EMPTY = 2, 1, 0


# Gets the path for a bad apple frame
def get_path(index: int) -> str:
   path = "frames/output_"
   frame = str(index)
   while len(frame) < len(str(FRAMES_END)): frame = f"0{frame}" 
   return path + frame + ".jpg"

# Gets a cv2 image for a bad apple frame
def get_image(index: int) -> MatLike:
   path = get_path(index)
   img = cv2.imread(path)
   if img is None: 
      print(f"Failure reading path: {path}")
      exit()
   return img

# Gets the amount of times to click based on the current state of the 'pixel' and the goal state
def get_click_number(current_state: int, goal_state: int) -> int:
   return (goal_state - current_state) % 3

# Draws the new expected image based on what is currently displayed
def draw_image(mouse: Controller, current_image: list[list[int]], goal_image: list[list[int]]) -> None:
   for x in range(GRID_SIZE[0]):
      for y in range(GRID_SIZE[1]):
         # Gets the pixel of current and goal
         current_state = current_image[x][y]
         goal_state = goal_image[x][y]
         # Moves the cursor to the needed position
         mouse.position = (CARD_START[0] + CARD_SIZE[0] * x, CARD_START[1] + CARD_SIZE[1] * y)
         mouse.click(Button.left, get_click_number(current_state, goal_state))
         # Moves the cursor out of the way before sleeping to make the video look a bit nicer
         mouse.position = (-1, -1)
         time.sleep(TIME_PER_PIXEL)

# Main
def main(mouse: Controller) -> None:

   print("# Generating") # All generation done before drawing to not mess with timings

   data: list[list[list[int]]] = [] # Holds all images
   current_image: list[list[int]] = [] # Holds the current frame (starts blank aka all empty)

   for i in range(FRAMES_START + 1, FRAMES_END + 1):
      print(f"{i} / {FRAMES_END}")

      # Get and resize the image
      img = get_image(i)
      img = cv2.resize(img, GRID_SIZE)

      # Create image data
      goal_image: list[list[int]] = []
      for x in range(GRID_SIZE[0]):
         goal_image.append([])
         current_image.append([])
         for y in range(GRID_SIZE[1]):
            # Set based on resized image
            comb = int(img[y][x][R])
            if comb < COLOR_THRESHOLDS[0]: goal_image[-1].append(FULL)
            elif comb < COLOR_THRESHOLDS[1]: goal_image[-1].append(HALF)
            else: goal_image[-1].append(EMPTY) 
            # Set current to blank
            current_image[-1].append(EMPTY)
      # Add image
      data.append(goal_image)


   print("# Playing") # Actually plays the generated pattern

   last_time = time.time()

   for i in range(FRAMES_START, FRAMES_END):
      print(f"{i + 1} / {FRAMES_END}")
      # Get the wanted image
      goal_image = data[i - FRAMES_START]

      # Quit to save potential pains
      if keyboard.is_pressed('q'): 
         print("Force quit")
         return
      
      # Draw the new image based on current, and set new to current
      draw_image(mouse, current_image, goal_image)
      current_image = goal_image

      # Wait timer to keep final output timings consistent
      sleep_time = TIME_PER_FRAME - (time.time() - last_time)
      if sleep_time <= 0:
         print("Warning: Frames are not being given enough time to display")
         sleep_time = 0
      time.sleep(sleep_time)
      last_time = time.time()
   


if __name__ == "__main__":
   if TIME_PER_PIXEL * GRID_SIZE[0] * GRID_SIZE[1] > TIME_PER_FRAME:
      print("Time to draw a frame is longer than time to show a frame for")
   else:
      mouse = Controller()
      main(mouse)