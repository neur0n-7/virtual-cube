
"""
Virtual Cube (config.py)
Contains different configuration settings for Virtual Cube.
This file is imported in main.py.
"""


# CAMERA SETTINGS
CAMERA_X = 150
CAMERA_Y = 200
FOCAL_LENGTH = 500

# DISPLAY SETTINGS
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 720
FPS = 60
SHOW_FPS = True

# COLORS
COLORS  = {
	"white": (241,244,237),
	"yellow": (246,241,41),
	"red": (255,57,38),
	"green": (37,219,53),
	"blue": (12,82,241),
	"orange": (250,138,45),
	"background": (220, 220, 220),
	"black": (0, 0, 0),
	"border": (0, 0, 0),
	"interior": (0, 0, 0)
}

# CUBE SETTINGS
SPIN_FACTOR = 0.9 # Higher = faster and vice versa, between 0 and 1
NORMAL_CUBE_TURN_SPEED = 7.5 # Should be a divisor of 90 (or very close to it)
SCRAMBLE_CUBE_TURN_SPEED = 15 # Should be a divisor of 90 (or very close to it)
SCRAMBLE_RANGE = (20, 30) # Min and max number of times to scramble
DRAW_INTERIOR = True # Whether or not to draw the interior of the cube

# INSTRUCTIONS SETTINGS
INSTRUCTIONS_DELAY_SECS = 0.5 # How long to wait before showing instructions
INSTRUCTIONS_FADE_SECS = 0.75 # How long to fade instructions in
FADE_OUT_SECS = 0.25 # How long to fade instructions out
INSTRUCTION_GAP_FRAMES = 100 # How many frames between each instruction

# RESET SETTINGS
RESET_TYPE = "FADE" # "GLIDE" or "FADE"

if RESET_TYPE == "FADE":
	RESET_FADE_SECONDS = 0.25 # How long to fade out
	RESET_FADE_FRAMES = int(RESET_FADE_SECONDS*FPS)
	RESET_PAUSE_SECONDS = 0.25 # How long to pause after fading out before fading in again
