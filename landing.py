import cv2  as cv
import numpy as np
import tkinter as tk
from PIL import Image, ImageTk

#CONSTANTS
IMG_GRAY = cv.imread("images/mola_1024x501.png", cv.IMREAD_GRAYSCALE)
IMG_COLOR = cv.imread("images/mola_color_1024x506.png")
RECT_WIDTH_KM = 670
RECT_HT_KM = 335
MAX_ELEV_LIMIT = 55 #Limit to only lighlty cratered flat terrain
NUM_CANDIDATES = 20
MARS_CIRCUM = 21344

#CONSTANTS: Derived

IMG_HT, IMG_WIDTH = IMG_GRAY.shape #(501(# px in rows), 1024(# px in columns))
PIXELS_PER_KM = IMG_WIDTH / MARS_CIRCUM #Convert dims from km to px
RECT_WIDTH = int(PIXELS_PER_KM * RECT_WIDTH_KM) #Convert width to px
RECT_HT = int(PIXELS_PER_KM * RECT_HT_KM) #Convert height to px
LAT_30_N = int(IMG_HT / 3) #Limit search for warmest and sunniest areas 
LAT_30_S = LAT_30_N * 2 #Limit search for warmest and sunniest areas 
STEP_X = int(RECT_WIDTH / 2) #How far our rectangle box will move on the X axis
STEP_Y = int(RECT_HT / 2) #How far our rectangle box will move on the Y axis

#Initialize tkinter screen and draw on canvas
screen = tk.Tk()
canvas = tk.Canvas(screen, width=IMG_WIDTH, height=IMG_HT + 130)