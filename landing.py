import cv2  as cv
import numpy as np
import tkinter as tk
from PIL import Image, ImageTk

#CONSTANTS: Inputs
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

#Search
class Search():
    """ Read the image and identify landing rectangles based on requirement inputs. """
    
    def __init__(self, name):
        self.name = name
        self.rect_coords = {} #Corner points
        self.rect_means = {} #Mean elevation
        self.rect_ptps = {} #Peak to valley, to be consistent with Numpy, we'll use peak to peak
        self.rect_stds = {} #Standard deviation
        self.ptp_filtered = []
        self.std_filtered = []
        self.high_graded_rects = [] #Lowest combined score

    def run_rect_stats(self):
        """ Define rectangular search areas and calculate internal stats. """
        ul_x, ul_y = 0, LAT_30_N #Upper left, X and Y coords
        lr_x, lr_y = RECT_WIDTH, LAT_30_N + RECT_HT #Lower right, X and Y coords
        rect_num = 1 #Keep track of rects

        while True:
            rect_img = IMG_GRAY[ul_y : lr_y, ul_x : lr_x] #From the whole image, slice only the relevant rect
            self.rect_coords[rect_num] = [ul_x, ul_y, lr_x, lr_y] #Store coords into dictionary

            if np.mean(rect_img) <= MAX_ELEV_LIMIT:
                self.rect_means[rect_num] = np.mean(rect_img)
                self.rect_ptps[rect_num] = np.ptp(rect_img)
                self.rect_stds[rect_num] = np.std(rect_img)
            rect_num += 1

            #Move rect
            ul_x += STEP_X
            lr_x = ul_x + RECT_WIDTH
            #If rect extends past the right side of whole image, reset X coord to 0 and move to a new Y row
            if lr_x > IMG_WIDTH:
                ul_x = 0
                ul_y += STEP_Y
                lr_x = RECT_WIDTH
                lr_y += STEP_Y
            if lr_y > LAT_30_S + STEP_Y:
                #Stop if more than half of rect extend below latitude 30 south
                break
    
    def draw_qc_rects(self):
        """ Draw overlapping rectangles on image for quality control. """

        img_copy = IMG_GRAY.copy() #Everything drawn on an image with OpenCV becomes part of the image, so we make a copy of the original copy
        rects_sorted = sorted(self.rect_coords.items(), key=lambda x: x[0]) #Prints coords in numerical order. Returns key=>rect num, val=>list of coords
        print("\nRect number and corner coordinates (ul_x, ul_y, lr_x, lr_y):")
        for k, v in rects_sorted: 
            print("rect: {}, coords: {}".format(k, v))

            #Draw rectangle (img to draw, rect coords, line width)
            cv.rectangle(img_copy,
                        (self.rect_coords[k][0], self.rect_coords[k][1]), #0=upper left x, 1=upper left y
                        (self.rect_coords[k][2], self.rect_coords[k][3]), #2=lower right x, 3=lower right y
                        (255, 0, 0), 1)
            cv.imshow("QC Rects {}".format(self.name). img_copy)
            cv.waitKey(3000) #Leave window open for 3 sec
            cv.destroyAllWindows()
