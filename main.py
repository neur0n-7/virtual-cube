#!/usr/bin/env python3

#
#
#   
#    __   __ __   ______  ______  __  __   ______   __           ______   __  __   ______   ______    
#   /\ \ / //\ \ /\  == \/\__  _\/\ \/\ \ /\  __ \ /\ \         /\  ___\ /\ \/\ \ /\  == \ /\  ___\   
#   \ \ \'/ \ \ \\ \  __<\/_/\ \/\ \ \_\ \\ \  __ \\ \ \____    \ \ \____\ \ \_\ \\ \  __< \ \  __\   
#    \ \__|  \ \_\\ \_\ \_\ \ \_\ \ \_____\\ \_\ \_\\ \_____\    \ \_____\\ \_____\\ \_____\\ \_____\ 
#     \/_/    \/_/ \/_/ /_/  \/_/  \/_____/ \/_/\/_/ \/_____/     \/_____/ \/_____/ \/_____/ \/_____/ 
#
#    main.py
#
#   Anish Gupta
#   July 2024
#   https://github.com/neur0n-7/VirtualCube
#
#


# --- IMPORTS -------------------------------------------------------------------------------------------------
from os import environ, path
from random import choice, randint
from time import sleep
import sys

try:
	environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
	import pygame
	import pygame.gfxdraw
	import numpy as np
except (ModuleNotFoundError, ImportError):
	print("Missing one or more required packages.")
	print("Run \"pip install -r requirements.txt\" and then run this file again.")
	sys.exit()
	
# Virtual Cube configuration settings #######################################################################################

# CAMERA SETTINGS
CAMERA_X = 150
CAMERA_Y = 200
FOCAL_LENGTH = 450

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
	"background": (20, 20, 20),
	"button_bg": (230, 230, 230),
	"fps": (255, 255, 255),
	"time": (255, 255, 255),
	"button_fg": (20, 20, 20),
	"border": (0, 0, 0),
	"interior": (50, 50, 50),
	"scrambling": (100, 100, 100)
}


# CUBE SETTINGS
SPIN_FACTOR = 0.9 # Higher = faster and vice versa, between 0 and 1 (when cube is spun with the mouse)
NORMAL_CUBE_TURN_SPEED = 10 # Should be a divisor of 90 (or very close to it)
SCRAMBLE_CUBE_TURN_SPEED = 18 # Should be a divisor of 90 (or very close to it)
SCRAMBLE_RANGE = (20, 30) # Min and max number of times to scramble

# INSTRUCTIONS SETTINGS
INSTRUCTIONS_DELAY_SECS = 0.5 # How long to wait before showing instructions
INSTRUCTIONS_FADE_SECS = 1# How long to fade instructions in
FADE_OUT_SECS = 0.25 # How long to fade instructions out
INSTRUCTION_GAP_FRAMES = 100 # How many frames between each instruction

# RESET SETTINGS
RESET_TYPE = "FADE" # "GLIDE" or "FADE"

if RESET_TYPE == "FADE":
	RESET_FADE_SECONDS = 0.25 # How long to fade out
	RESET_FADE_FRAMES = int(RESET_FADE_SECONDS*FPS)
	RESET_PAUSE_SECONDS = 0.25 # How long to pause after fading out before fading in again


##############################################################################################################################


# --- CONSTANTS ------------------------------------------------------------------------------------------------
ALL_MOVES = ["U", "U'", "D", "D'", "F", "F'", "B", "B'", "L", "L'", "R", "R'"] # MES excluded

# To be scaled up by 50x for 3D coordinates of each square
SOLVED_CUBE = {
	# Top layer on front (red)
	((0, 4, 0), (2, 4, 0), (2, 6, 0), (0, 6, 0)): COLORS["red"],
	((2, 4, 0), (4, 4, 0), (4, 6, 0), (2, 6, 0)): COLORS["red"],
	((4, 4, 0), (6, 4, 0), (6, 6, 0), (4, 6, 0)): COLORS["red"],
	
	# Middle layer on front (red)
	((0, 2, 0), (2, 2, 0), (2, 4, 0), (0, 4, 0)): COLORS["red"],
	((2, 2, 0), (4, 2, 0), (4, 4, 0), (2, 4, 0)): COLORS["red"],
	((4, 2, 0), (6, 2, 0), (6, 4, 0), (4, 4, 0)): COLORS["red"],
	
	# Bottom layer on front (red)
	((0, 0, 0), (2, 0, 0), (2, 2, 0), (0, 2, 0)): COLORS["red"],
	((2, 0, 0), (4, 0, 0), (4, 2, 0), (2, 2, 0)): COLORS["red"],
	((4, 0, 0), (6, 0, 0), (6, 2, 0), (4, 2, 0)): COLORS["red"],

	# Closest layer on top (white)
	((0, 6, 0), (2, 6, 0), (2, 6, 2), (0, 6, 2)): COLORS["white"],
	((2, 6, 0), (4, 6, 0), (4, 6, 2), (2, 6, 2)): COLORS["white"],
	((4, 6, 0), (6, 6, 0), (6, 6, 2), (4, 6, 2)): COLORS["white"],
	
	# Middle layer on top (white)
	((0, 6, 2), (2, 6, 2), (2, 6, 4), (0, 6, 4)): COLORS["white"],
	((2, 6, 2), (4, 6, 2), (4, 6, 4), (2, 6, 4)): COLORS["white"],
	((4, 6, 2), (6, 6, 2), (6, 6, 4), (4, 6, 4)): COLORS["white"],

	# Farthest layer on top (white)
	((0, 6, 4), (2, 6, 4), (2, 6, 6), (0, 6, 6)): COLORS["white"],
	((2, 6, 4), (4, 6, 4), (4, 6, 6), (2, 6, 6)): COLORS["white"],
	((4, 6, 4), (6, 6, 4), (6, 6, 6), (4, 6, 6)): COLORS["white"],

	# Top layer on right side (blue)
	((6, 4, 2), (6, 6, 2), (6, 6, 0), (6, 4, 0)): COLORS["blue"],
	((6, 4, 4), (6, 6, 4), (6, 6, 2), (6, 4, 2)): COLORS["blue"],
	((6, 4, 6), (6, 6, 6), (6, 6, 4), (6, 4, 4)): COLORS["blue"],

	# Middle layer on right side (blue)
	((6, 2, 2), (6, 4, 2), (6, 4, 0), (6, 2, 0)): COLORS["blue"],
	((6, 2, 4), (6, 4, 4), (6, 4, 2), (6, 2, 2)): COLORS["blue"],
	((6, 2, 6), (6, 4, 6), (6, 4, 4), (6, 2, 4)): COLORS["blue"],

	# Bottom layer on right side (blue)
	((6, 0, 2), (6, 2, 2), (6, 2, 0), (6, 0, 0)): COLORS["blue"],
	((6, 0, 4), (6, 2, 4), (6, 2, 2), (6, 0, 2)): COLORS["blue"],
	((6, 0, 6), (6, 2, 6), (6, 2, 4), (6, 0, 4)): COLORS["blue"],

	# Top layer on left side (green)
	((0, 4, 6), (0, 6, 6), (0, 6, 4), (0, 4, 4)): COLORS["green"],
	((0, 4, 4), (0, 6, 4), (0, 6, 2), (0, 4, 2)): COLORS["green"],
	((0, 4, 2), (0, 6, 2), (0, 6, 0), (0, 4, 0)): COLORS["green"],

	# Middle layer on left side (green)
	((0, 2, 6), (0, 4, 6), (0, 4, 4), (0, 2, 4)): COLORS["green"],
	((0, 2, 4), (0, 4, 4), (0, 4, 2), (0, 2, 2)): COLORS["green"],
	((0, 2, 2), (0, 4, 2), (0, 4, 0), (0, 2, 0)): COLORS["green"],

	# Bottom layer on left side (green)
	((0, 0, 6), (0, 2, 6), (0, 2, 4), (0, 0, 4)): COLORS["green"],
	((0, 0, 4), (0, 2, 4), (0, 2, 2), (0, 0, 2)): COLORS["green"],
	((0, 0, 2), (0, 2, 2), (0, 2, 0), (0, 0, 0)): COLORS["green"],

	# Closest layer on bottom (yellow)
	((0, 0, 0), (2, 0, 0), (2, 0, 2), (0, 0, 2)): COLORS["yellow"],
	((2, 0, 0), (4, 0, 0), (4, 0, 2), (2, 0, 2)): COLORS["yellow"],
	((4, 0, 0), (6, 0, 0), (6, 0, 2), (4, 0, 2)): COLORS["yellow"],

	# Middle layer on bottom (yellow)
	((0, 0, 2), (2, 0, 2), (2, 0, 4), (0, 0, 4)): COLORS["yellow"],
	((2, 0, 2), (4, 0, 2), (4, 0, 4), (2, 0, 4)): COLORS["yellow"],
	((4, 0, 2), (6, 0, 2), (6, 0, 4), (4, 0, 4)): COLORS["yellow"],

	# Farthest layer on bottom (yellow)
	((0, 0, 4), (2, 0, 4), (2, 0, 6), (0, 0, 6)): COLORS["yellow"],
	((2, 0, 4), (4, 0, 4), (4, 0, 6), (2, 0, 6)): COLORS["yellow"],
	((4, 0, 4), (6, 0, 4), (6, 0, 6), (4, 0, 6)): COLORS["yellow"],
	
	# Orange face in order when looking directly at it

	# Top layer on back (orange)
	((4, 4, 6), (6, 4, 6), (6, 6, 6), (4, 6, 6)): COLORS["orange"],
	((2, 4, 6), (4, 4, 6), (4, 6, 6), (2, 6, 6)): COLORS["orange"],
	((0, 4, 6), (2, 4, 6), (2, 6, 6), (0, 6, 6)): COLORS["orange"],

	# Middle layer on back (orange)
	((4, 2, 6), (6, 2, 6), (6, 4, 6), (4, 4, 6)): COLORS["orange"],
	((2, 2, 6), (4, 2, 6), (4, 4, 6), (2, 4, 6)): COLORS["orange"],
	((0, 2, 6), (2, 2, 6), (2, 4, 6), (0, 4, 6)): COLORS["orange"],

	# Bottom layer on back (orange)
	((4, 0, 6), (6, 0, 6), (6, 2, 6), (4, 2, 6)): COLORS["orange"],
	((2, 0, 6), (4, 0, 6), (4, 2, 6), (2, 2, 6)): COLORS["orange"],
	((0, 0, 6), (2, 0, 6), (2, 2, 6), (0, 2, 6)): COLORS["orange"],

}

# used to calculate closest face
SOLVED_CENTERS = {
	((2, 2, 0), (4, 2, 0), (4, 4, 0), (2, 4, 0)): COLORS["red"],
	((2, 6, 2), (4, 6, 2), (4, 6, 4), (2, 6, 4)): COLORS["white"],
	((6, 2, 4), (6, 4, 4), (6, 4, 2), (6, 2, 2)): COLORS["blue"],
	((0, 2, 4), (0, 4, 4), (0, 4, 2), (0, 2, 2)): COLORS["green"],
	((2, 0, 2), (4, 0, 2), (4, 0, 4), (2, 0, 4)): COLORS["yellow"],
	((2, 2, 6), (4, 2, 6), (4, 4, 6), (2, 4, 6)): COLORS["orange"],
}

# --- VARIABLES ------------------------------------------------------------------------------------------------
rubiks_cube = SOLVED_CUBE.copy()
cube_turn_speed = NORMAL_CUBE_TURN_SPEED
centers = SOLVED_CENTERS.copy()

# --- OBJECTS --------------------------------------------------------------------------------------------------
reset_button = pygame.Rect(SCREEN_WIDTH/5, 540, SCREEN_WIDTH/5*3, 70)
scramble_button = pygame.Rect(SCREEN_WIDTH/5, 620, SCREEN_WIDTH/5*3, 70)

# --- FUNCIONS -------------------------------------------------------------------------------------------------
def get_projection(x,y,z):
	# Get the projection of a 3D point on the 2D screen at z=0
	x_proj = ((FOCAL_LENGTH*(x-CAMERA_X))/(FOCAL_LENGTH+z))+CAMERA_X
	y_proj = ((FOCAL_LENGTH*(y-CAMERA_Y))/(FOCAL_LENGTH+z))+CAMERA_Y
	return (x_proj,y_proj)


def real(x,y):
	# Make (0,0) center of screen
	return (x+SCREEN_WIDTH/4, SCREEN_WIDTH-y-SCREEN_WIDTH/4)


def draw_polygon_alpha(surface, color, points):
	# Credit: https://stackoverflow.com/a/64630102
	lx, ly = zip(*points)
	min_x, min_y, max_x, max_y = min(lx), min(ly), max(lx), max(ly)
	target_rect = pygame.Rect(min_x, min_y, max_x - min_x, max_y - min_y)
	shape_surf = pygame.Surface(target_rect.size, pygame.SRCALPHA)
	pygame.draw.polygon(shape_surf, color, [(x - min_x, y - min_y) for x, y in points])
	surface.blit(shape_surf, target_rect)


def is_cube_upside_down():
	if 90<abs(xaxis_rot%360)<270:
		return True
	else:
		return False


def is_cube_backward():
	if 135<abs(yaxis_rot%360)<225:
		return True
	else:
		return False


def text(text, x, y, font, size, alpha=255, bold=False, color=(255,255,255), centered=True):
	# Draw text center aligned (vertically and horizontally)
	font = pygame.font.SysFont(font, size, bold=bold)
	surface = font.render(text, True, color)
	surface.set_alpha(alpha)
	text_rect = surface.get_rect(center=(x, y))
	if centered:
		text_rect.topleft = (x - text_rect.width // 2, y - text_rect.height // 2)
	else:
		text_rect.topleft = (x, y)
	screen.blit(surface, text_rect)
	

def rotated_point(x, y, z, xdegrees=0, ydegrees=0, zdegrees=0, center=(150,150,150)):
	def XROT_MATRIX(degrees):
		# Returns the rotation matrix for a certain number of degrees around the x axis
		rads = np.radians(degrees)
		return np.array([
			[1, 0, 0],
			[0, np.cos(rads), -np.sin(rads)],
			[0, np.sin(rads), np.cos(rads)]
		])

	def YROT_MATRIX(degrees):
		# Returns the rotation matrix for a certain number of degrees around the y axis
		rads = np.radians(degrees)
		return np.array([
			[np.cos(rads), 0, np.sin(rads)],
			[0, 1, 0],
			[-np.sin(rads), 0, np.cos(rads)]
		])

	def ZROT_MATRIX(degrees):
		# Returns the rotation matrix for a certain number of degrees around the z axis
		rads = np.radians(degrees)
		return np.array([
			[np.cos(rads), -np.sin(rads), 0],
			[np.sin(rads), np.cos(rads), 0],
			[0, 0, 1]
		])

	# Returns rotated version with the given rotation angles around a certain center point
	rotation_matrix = YROT_MATRIX(ydegrees) @ XROT_MATRIX(xdegrees) @  ZROT_MATRIX(zdegrees)
	rotated = np.array([x-center[0], y-center[1], z-center[2]]) @ rotation_matrix
	return tuple(list(rotated + np.array([*center])))


def scramble():
	global scramble_progress, cube_turn_speed, scrambled, scrambling, solved, mouse_xvel, mouse_yvel

	mouse_xvel = 0
	mouse_yvel = 0

	cube_turn_speed = SCRAMBLE_CUBE_TURN_SPEED

	scramble_progress = 0
	times = randint(*SCRAMBLE_RANGE)
	scrambled = False

	scrambling = True
				
	for i in range(times):

		turn(choice(ALL_MOVES))
		scramble_progress = round((i+1)/times*100, 1)
	
	scrambling = False
	scrambled = True
	solved = False	

	scramble_progress = 100
	cube_turn_speed = NORMAL_CUBE_TURN_SPEED


def closest_face():
	# Rotate centers
	rotated_centers = {}
	for key in SOLVED_CENTERS.keys():
		rotated_center = []
		for coords in key:
			rotated_coords = rotated_point(*coords, xaxis_rot, yaxis_rot, zaxis_rot, center=(150, 150, 150))
			rotated_center.append(rotated_coords)
		rotated_center = tuple(rotated_center)
		rotated_centers[rotated_center]  = SOLVED_CENTERS[key]

	# Find closest face by z value
	keys = list(rotated_centers.keys())
	sorted_list = sorted(keys, key=lambda x: sum(coord[2] for coord in x) / len(x))

	return rotated_centers[sorted_list[0]]
		

def top_face():
	# Rotate centers
	rotated_centers = {}
	for key in SOLVED_CENTERS.keys():
		rotated_center = []
		for coords in key:
			rotated_coords = rotated_point(*coords, xaxis_rot, yaxis_rot, zaxis_rot, center=(150, 150, 150))
			rotated_center.append(rotated_coords)
		rotated_center = tuple(rotated_center)
		rotated_centers[rotated_center]  = SOLVED_CENTERS[key]

	# Find top face by y value
	keys = list(rotated_centers.keys())
	sorted_list = sorted(keys, key=lambda x: sum(coord[1] for coord in x) / len(x))

	return rotated_centers[sorted_list[-1]]


def left_face():
	# Rotate centers
	rotated_centers = {}
	for key in SOLVED_CENTERS.keys():
		rotated_center = []
		for coords in key:
			rotated_coords = rotated_point(*coords, xaxis_rot, yaxis_rot, zaxis_rot, center=(150, 150, 150))
			rotated_center.append(rotated_coords)
		rotated_center = tuple(rotated_center)
		rotated_centers[rotated_center]  = SOLVED_CENTERS[key]

	# Find left face by x value
	keys = list(rotated_centers.keys())
	sorted_list = sorted(keys, key=lambda x: sum(coord[0] for coord in x) / len(x))

	return rotated_centers[sorted_list[0]]


def turn(move):
	global rubiks_cube
	# move is U, U', F, F', etc.
	# to_match = what cubelets to move (and what axis to rotate around)

	move: str = move # type hinting
	backwards_rot = False # rotate around axis by negative amount?


	if move.startswith("U"):
		to_match = ("y", 6)
		backwards_rot = True

	elif move.startswith("D"):
		to_match = ("y", 0)

	elif move.startswith("F"):
		to_match = ("z", 0)
		offset_amount = -0.001

	elif move.startswith("B"):
		to_match = ("z", 6)
		backwards_rot = True

	elif move.startswith("L"):
		to_match = ("x", 0)

	elif move.startswith("R"):
		to_match = ("x", 6)
		backwards_rot = True

		
	if "'" in move: # prime
		backwards_rot = not backwards_rot
	
	# Get cubelets to rotate
	match_index = ["x", "y", "z"].index(to_match[0])
	
	# Get center of rotation
	rotation_center = [3, 3, 3]
	rotation_center[match_index] = to_match[1]

	# Get squares to rotate
	squares_to_rotate = []
	for square in rubiks_cube:

		for coord in square:
			if coord[match_index]==to_match[1]:
				squares_to_rotate.append(square)
				break

	
	# Get degrees to rotate by
	if backwards_rot:
		rotate_degs = -cube_turn_speed
	else:
		rotate_degs = cube_turn_speed

	xrot_degs = 0
	yrot_degs = 0
	zrot_degs = 0

	if to_match[0] == "x":
		xrot_degs = rotate_degs
	elif to_match[0] == "y":
		yrot_degs = rotate_degs
	else:
		zrot_degs = rotate_degs


	# Loop rotation and draw
	times = int(90/cube_turn_speed)

	pygame.event.set_allowed([pygame.QUIT])

	for _ in range(times):
		for index, square in enumerate(squares_to_rotate):
			rotated_square = []
			for x, y, z in square:
				rotated_square.append(rotated_point(x, y, z, xrot_degs, yrot_degs, zrot_degs, rotation_center))

			rotated_square = tuple(rotated_square)

			rubiks_cube[rotated_square] = rubiks_cube.pop(square)

			squares_to_rotate[index] = rotated_square

		draw_all(rubiks_cube)
		
		if pygame.event.peek(pygame.QUIT):
			pygame.quit()
			sys.exit()

	pygame.event.set_allowed([pygame.QUIT, pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP])

	to_add_keys = []
	to_remove_keys = []

	# Snap rubiks_cube to nearest integer (round coords in keys)
	for key in rubiks_cube.keys():
		rounded_key = []
		for coords in key:
			rounded_key.append((round(coords[0]), round(coords[1]), round(coords[2])))

		rounded_key = tuple(rounded_key)
		to_add_keys.append(rounded_key)
		to_remove_keys.append(key)
	
	for add, remove in zip(to_add_keys, to_remove_keys):
		rubiks_cube[add] = rubiks_cube.pop(remove)


def draw_all(cube, cube_opacity=100):
	global average_dists, rotated_cube, pre_start_frames, post_start_frames

	# --- RUBIK'S CUBE ------------------------------------------------------------
	# Rotate the rubiks cube

	rotated_cube = {}
	for vertices, color in cube.items():
		temp = []
		for vertex in vertices:
			temp.append(tuple(rotated_point(vertex[0]*50, vertex[1]*50, vertex[2]*50, 
								   xdegrees=xaxis_rot, ydegrees=yaxis_rot, zdegrees=zaxis_rot, center=(150, 150, 150))))
			
		rotated_cube[tuple(temp)] = color

	# Create list like [(((x, y, z),(x, y, z)), average distance), (((x, y, z),(x, y, z)), average distance), ...] from rotated_cube
	dists = []


	for vertices in rotated_cube.keys():
		avgz = sum([vertex[2] for vertex in vertices])/4
		dists.append((vertices, avgz))
	

	# Sort average_zs by avg z
	dists.sort(key=lambda x: x[1], reverse=True)

	# Draw the rotated cube	
	screen.fill(COLORS["background"])
	for vertices, _ in dists:
		color_to_draw = rotated_cube[vertices]
		real_projections = []
		for vertex in vertices:
			real_projections.append(real(*get_projection(vertex[0], vertex[1], vertex[2])))
		
		if cube_opacity == 100:
			pygame.draw.polygon(screen, color_to_draw, real_projections)
			pygame.draw.aalines(screen, COLORS["border"], True, real_projections, blend=True)
		else:
			draw_polygon_alpha(screen, (*color_to_draw, cube_opacity/100*255), real_projections)
			alpha_lines(screen, (*COLORS["border"], cube_opacity/100*255), True, real_projections)


	# --- RESET BUTTON ------------------------------------------------------------
	pygame.draw.rect(screen, COLORS["button_bg"], reset_button, border_radius=20)
	text("Reset", reset_button.centerx, reset_button.centery, font="verdana", size=20, color=COLORS["button_fg"])

	# --- SCRAMBLE BUTTON ------------------------------------------------------------
	pygame.draw.rect(screen, COLORS["button_bg"], scramble_button, border_radius=20)
	if not scrambling:
		text("Scramble", scramble_button.centerx, scramble_button.centery, font="verdana", size=20, color=COLORS["button_fg"])
	else:
		text(f"Scrambling... ({scramble_progress}%)", scramble_button.centerx, scramble_button.centery, font="verdana", 
			   size=20, color=COLORS["scrambling"])

	# --- START SCREEN ------------------------------------------------------------
	if not started: # Show instructions and title
		draw_polygon_alpha(screen, (0,0,0, 200), ((0, 0), (SCREEN_WIDTH, 0), 
						  (SCREEN_WIDTH, SCREEN_HEIGHT), (0, SCREEN_HEIGHT)))

		text("Virtual Cube", SCREEN_WIDTH/2, SCREEN_HEIGHT/2.5, 
			   font="verdana", size=40, bold=True)

		try:
			instructions_alpha = (pre_start_frames-INSTRUCTIONS_DELAY_SECS*FPS) / \
			(INSTRUCTIONS_FADE_SECS*FPS-INSTRUCTIONS_DELAY_SECS) * 255
		except ZeroDivisionError:
			instructions_alpha = 0

		instructions_alpha = max(instructions_alpha, 0)

		text("Click and drag to rotate", SCREEN_WIDTH/2, SCREEN_HEIGHT/2.5+40,
			   font="verdana", size=20, alpha=min(instructions_alpha, 255))
		
		text("F, B, L, R, U, and D keys to turn", SCREEN_WIDTH/2, SCREEN_HEIGHT/2.5+70,
			   font="verdana", size=20, alpha=min(instructions_alpha, 255+INSTRUCTION_GAP_FRAMES)-INSTRUCTION_GAP_FRAMES)
		
		text("Shift to turn counter-clockwise", SCREEN_WIDTH/2, SCREEN_HEIGHT/2.5+100,
			   font="verdana", size=20, alpha=min(instructions_alpha, 255+INSTRUCTION_GAP_FRAMES*2)-INSTRUCTION_GAP_FRAMES*2)
		
		pre_start_frames += 1

	elif post_start_frames < FADE_OUT_SECS*FPS: # Fade out
		all_alpha = 255 - (post_start_frames / (FADE_OUT_SECS*FPS) * 255)
		all_alpha = max(all_alpha, 0)
		all_alpha = min(all_alpha, 200)

		draw_polygon_alpha(screen, (0,0,0, all_alpha), ((0, 0), (SCREEN_WIDTH, 0), 
						  (SCREEN_WIDTH, SCREEN_HEIGHT), (0, SCREEN_HEIGHT)))

		text("Virtual Cube", SCREEN_WIDTH/2, SCREEN_HEIGHT/2.5, 
			   font="verdana", size=40, bold=True, alpha=all_alpha)
	
		text("Click and drag to rotate", SCREEN_WIDTH/2, SCREEN_HEIGHT/2.5+40,
			   font="verdana", size=20, alpha=all_alpha)
		
		# Write FPS
		
		if SHOW_FPS:
			text(f"FPS: {int(clock.get_fps())}", 20, 20, font="verdana", size=18, color=COLORS["fps"], alpha=200-all_alpha, centered=False)

		post_start_frames += 1

	else:
		# Write FPS
		if SHOW_FPS:
			text(f"FPS: {int(clock.get_fps())}", 20, 20, font="verdana", size=18, color=COLORS["fps"], centered=False)

	# --- TIME ------------------------------------------------------------
	if scrambled and not solved:
		time_passed = (pygame.time.get_ticks() - start_time) / 1000
		minutes = int(time_passed // 60)
		seconds = time_passed - minutes * 60
		text(f"{minutes:02}:{seconds:0>5.2f}", SCREEN_WIDTH/2, 40, font="verdana", size=30, color=COLORS["time"])

	if scrambled and solved:
		minutes = int(final_time // 60)
		seconds = final_time - minutes * 60
		text(f"SOLVED IN {minutes:02}:{seconds:0>5.2f}", SCREEN_WIDTH/2, 40, font="verdana", size=30, color=COLORS["time"])

	# Flip display
	pygame.display.flip()
	
	clock.tick(FPS)


def glide_cube_rot(target_xaxis_rot=0, target_yaxis_rot=0, factor = 0.05):
	global xaxis_rot, yaxis_rot, zaxis_rot

	while abs(xaxis_rot - target_xaxis_rot) > 1 or abs(yaxis_rot - target_yaxis_rot) > 1:
		xaxis_rot = ((1-factor) * xaxis_rot + factor * target_xaxis_rot) % 360
		yaxis_rot = ((1-factor) * yaxis_rot + factor * target_yaxis_rot) % 360

		draw_all(rubiks_cube)
	
	xaxis_rot = target_xaxis_rot
	yaxis_rot = target_yaxis_rot


def is_cube_solved():
	red_squares_coords = []
	orange_squares_coords = []
	white_squares_coords = []
	yellow_squares_coords = []
	green_squares_coords = []
	blue_squares_coords = []

	for square, color in rubiks_cube.items():
		if color == COLORS["red"]:
			red_squares_coords.append(square)
		elif color == COLORS["orange"]:
			orange_squares_coords.append(square)
		elif color == COLORS["white"]:
			white_squares_coords.append(square)
		elif color == COLORS["yellow"]:
			yellow_squares_coords.append(square)
		elif color == COLORS["green"]:
			green_squares_coords.append(square)
		elif color == COLORS["blue"]:
			blue_squares_coords.append(square)
	
	# Check if all zs in red_squares_coords are the same
	red_zs = set()
	for square in red_squares_coords:
		for coords in square:
			red_zs.add(coords[2])
	
	if len(red_zs) != 1:
		# print("red_zs", red_zs)
		return False

	# Check if all zs in orange_squares_coords are the same
	orange_zs = set()
	for square in red_squares_coords:
		for coords in square:
			orange_zs.add(coords[2])
	
	if len(orange_zs) != 1:
		# print("orange_zs", orange_zs)
		return False
	
	# Check if all ys in white_squares_coords are the same
	white_ys = set()
	for square in white_squares_coords:
		for coords in square:
			white_ys.add(coords[1])
	
	if len(white_ys) != 1:
		# print("white_ys", white_ys)
		return False
	
	# Check if all ys in yellow_squares_coords are the same
	yellow_ys = set()
	for square in yellow_squares_coords:
		for coords in square:
			yellow_ys.add(coords[1])
	
	if len(yellow_ys) != 1:
		# print("yellow_ys", yellow_ys)
		return False
	
	# Check if all xs in green_squares_coords are the same
	green_xs = set()
	for square in green_squares_coords:
		for coords in square:
			green_xs.add(coords[0])
	
	if len(green_xs) != 1:
		# print("green_xs", green_xs)
		return False
	
	# Check if all xs in blue_squares_coords are the same
	blue_xs = set()
	for square in blue_squares_coords:
		for coords in square:
			blue_xs.add(coords[0])
	
	if len(blue_xs) != 1:
		# print("blue_xs", blue_xs)
		return False
	
	return True


def alpha_lines(surface, color, closed, points):
    min_x = min(point[0] for point in points)
    max_x = max(point[0] for point in points)
    min_y = min(point[1] for point in points)
    max_y = max(point[1] for point in points)
    
    width = max_x - min_x + 1
    height = max_y - min_y + 1
    temp_surface = pygame.Surface((width, height), pygame.SRCALPHA)
    
    adjusted_points = [(x - min_x, y - min_y) for x, y in points]
    
    pygame.draw.aalines(temp_surface, color, closed, adjusted_points)

    surface.blit(temp_surface, (min_x, min_y))

# --- MAIN -----------------------------------------------------------------------------------------------------
def main():
	global screen, rotated_cube, xaxis_rot, yaxis_rot, zaxis_rot, pre_start_frames, post_start_frames, \
		scrambling, started, rubiks_cube, clock, scrambled, solved, start_time, final_time, \
		mouse_xvel, mouse_yvel

	pygame.init()
	clock = pygame.time.Clock()

	pygame.display.set_icon(pygame.image.load(path.dirname(__file__)+"/icon.png"))

	# Next line triggers NSApplicationDelegate's warning for some reason on Mac
	screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

	pygame.event.set_allowed([pygame.QUIT, pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP])


	running = True

	xaxis_rot = 0
	yaxis_rot = 0

	# zaxis_rot currently not used
	zaxis_rot = 0

	mouse_dragging = False
	initial_mouse_pos = None

	mouse_xvel = 0
	mouse_yvel = 0

	rotated_cube = rubiks_cube.copy()

	started = False
	post_start_frames = 0
	pre_start_frames = 0

	scrambling = False

	solved = False
	scrambled = False
	start_time = None
	final_time = None

	do_glide = False

	while running:
		pygame.display.set_caption(f"Virtual Cube")

		if pygame.event.peek(pygame.QUIT):
			running = False
		elif pygame.event.peek(pygame.MOUSEBUTTONDOWN):
			event = pygame.event.get(pygame.MOUSEBUTTONDOWN)[0]
			if event.button == 1:
				if not started:
					started = True
					mouse_xvel = 0

				if not reset_button.collidepoint(pygame.mouse.get_pos()) and \
					not scramble_button.collidepoint(pygame.mouse.get_pos()):
					mouse_dragging = True
					initial_mouse_pos = pygame.mouse.get_pos()
				else:
					mouse_dragging = False
		elif pygame.event.peek(pygame.MOUSEBUTTONUP):
			event = pygame.event.get(pygame.MOUSEBUTTONUP)[0]
			if event.button == 1:
				mouse_dragging = False

			keys_pressed = pygame.key.get_pressed()
			keys = [pygame.K_f, pygame.K_b, pygame.K_l, pygame.K_r, pygame.K_u, pygame.K_d]
			for key in keys:
				if keys_pressed[key]:
					if not started:
						started = True

		if started:
			post_start_frames += 1

			if mouse_dragging:
				current_mouse_pos = pygame.mouse.get_pos()
				mouse_xvel = (current_mouse_pos[0] - initial_mouse_pos[0]) * 0.4
				mouse_yvel = (current_mouse_pos[1] - initial_mouse_pos[1]) * 0.4
				initial_mouse_pos = current_mouse_pos
			else:
				if abs(mouse_xvel) > 0.005 or abs(mouse_yvel) > 0.005:
					mouse_xvel *= SPIN_FACTOR
					mouse_yvel *= SPIN_FACTOR
				else:
					mouse_xvel = 0
					mouse_yvel = 0

			keys_pressed = pygame.key.get_pressed()

			move = None

			if keys_pressed[pygame.K_f]:
				closest = closest_face()
				if closest == COLORS["red"]:		move = "F"
				elif closest == COLORS["white"]:	move = "U"
				elif closest == COLORS["blue"]:		move = "R"
				elif closest == COLORS["green"]:	move = "L"
				elif closest == COLORS["yellow"]:	move = "D"
				elif closest == COLORS["orange"]:	move = "B"

			elif keys_pressed[pygame.K_b]:
				closest = closest_face()
				if closest == COLORS["red"]:		move = "B"
				elif closest == COLORS["white"]:	move = "D"
				elif closest == COLORS["blue"]:		move = "L"
				elif closest == COLORS["green"]:	move = "R"
				elif closest == COLORS["yellow"]:	move = "U"
				elif closest == COLORS["orange"]:	move = "F"

			elif keys_pressed[pygame.K_u]:
				top = top_face()
				if top == COLORS["white"]:			move = "U"
				elif top == COLORS["blue"]:			move = "R"
				elif top == COLORS["green"]:		move = "L"
				elif top == COLORS["yellow"]:		move = "D"
				elif top == COLORS["orange"]:		move = "B"
				elif top == COLORS["red"]:			move = "F"

			elif keys_pressed[pygame.K_d]:
				top = top_face()
				if top == COLORS["white"]:			move = "D"
				elif top == COLORS["blue"]:			move = "L"
				elif top == COLORS["green"]:		move = "R"
				elif top == COLORS["yellow"]:		move = "U"
				elif top == COLORS["orange"]:		move = "F"
				elif top == COLORS["red"]:			move = "B"

			elif keys_pressed[pygame.K_l]:
				left = left_face()
				if left == COLORS["green"]:			move = "L"
				elif left == COLORS["white"]:		move = "U"
				elif left == COLORS["yellow"]:		move = "D"
				elif left == COLORS["blue"]:		move = "R"
				elif left == COLORS["orange"]:		move = "B"
				elif left == COLORS["red"]:			move = "F"
			
			elif keys_pressed[pygame.K_r]:
				left = left_face()
				if left == COLORS["green"]:			move = "R"
				elif left == COLORS["white"]:		move = "D"
				elif left == COLORS["yellow"]:		move = "U"
				elif left == COLORS["blue"]:		move = "L"
				elif left == COLORS["orange"]:		move = "F"
				elif left == COLORS["red"]:			move = "B"
				
			if move:
				if keys_pressed[pygame.K_LSHIFT] or keys_pressed[pygame.K_RSHIFT]:
					if "'" in move:
						move = move[:-1]
					else:
						move += "'"

				turn(move)
				mouse_xvel = 0
				mouse_yvel = 0
					
		else:
			pre_start_frames += 1
			mouse_xvel = -9/FPS

		draw_all(rubiks_cube)
		
		if reset_button.collidepoint(pygame.mouse.get_pos()):
			if pygame.mouse.get_pressed()[0] and not mouse_dragging:

				if RESET_TYPE == "FADE":
					for alpha in reversed(np.linspace(0, 100, RESET_FADE_FRAMES)):
						draw_all(rubiks_cube, int(alpha))
					sleep(RESET_PAUSE_SECONDS)
				
				mouse_xvel = 0
				mouse_yvel = 0
				rubiks_cube = SOLVED_CUBE.copy()
				solved = False
				start_time = None
				scrambled = False

				if RESET_TYPE == "FADE":
					xaxis_rot = 0
					yaxis_rot = 0
					zaxis_rot = 0

					for alpha in np.linspace(0, 100, RESET_FADE_FRAMES):
						draw_all(rubiks_cube, alpha)
				else:
					glide_cube_rot()


		if scramble_button.collidepoint(pygame.mouse.get_pos()):
			if pygame.mouse.get_pressed()[0] and not mouse_dragging and not scrambling:
				if not started:
					started = True
				scramble()
				start_time = pygame.time.get_ticks()
		
		# --- TIMER ---------------------------------------------------------------------------------------------------
		# Timer starts when cube is scrambled and ends when solved
		if scrambled and not solved:
			if is_cube_solved():
				final_time = (pygame.time.get_ticks() - start_time) / 1000
				do_glide = True
				solved = True

		if do_glide:
			# Glide to target (it looks cool)
			glide_cube_rot(20, 325)

			do_glide = False

		# --- ROTATION -------------------------------------------------------------------------------------------------
		xaxis_rot += mouse_yvel

		if not is_cube_upside_down():
			yaxis_rot += mouse_xvel
		else:
			yaxis_rot -= mouse_xvel

		# 25 -330

		xaxis_rot = xaxis_rot % 360
		yaxis_rot = yaxis_rot % 360
		zaxis_rot = zaxis_rot % 360

	pygame.quit()
	quit()

if __name__ == "__main__":
	main()
