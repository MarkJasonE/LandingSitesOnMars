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
            rect_img = IMG_GRAY[ul_y : lr_y, ul_x : lr_x] #From the whole img, slice only the relevant rect

            self.rect_coords[rect_num] = [ul_x, ul_y, lr_x, lr_y] #Store coords into dictionary

            if np.mean(rect_img) <= MAX_ELEV_LIMIT:
                self.rect_means[rect_num] = np.mean(rect_img)
                self.rect_ptps[rect_num] = np.ptp(rect_img)
                self.rect_stds[rect_num] = np.std(rect_img)
            rect_num += 1

            #Move rect
            ul_x += STEP_X
            lr_x = ul_x + RECT_WIDTH
            #If rect extends past the right side of whole img, reset X coord to 0 and move to a new Y row
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

        img_copy = IMG_GRAY.copy() #Everything drawn on an img with OpenCV becomes part of the img, so we make a copy of the original copy

        rects_sorted = sorted(self.rect_coords.items(), key=lambda x: x[0]) #Prints coords in numerical order. Returns key=>rect num, val=>list of coords

        print("\nRect number and corner coordinates (ul_x, ul_y, lr_x, lr_y):")

        for k, v in rects_sorted: 
            print("rect: {}, coords: {}".format(k, v))

            #Draw rectangle (img to draw, rect coords, line width)
            cv.rectangle(img_copy,
                        (self.rect_coords[k][0], self.rect_coords[k][1]), #0=upper left x, 1=upper left y
                        (self.rect_coords[k][2], self.rect_coords[k][3]), #2=lower right x, 3=lower right y
                        (255, 0, 0), 1)
            cv.imshow("QC Rects {}".format(self.name), img_copy)
            cv.waitKey(10) #Leave window open for 3 sec
            cv.destroyAllWindows()


    def sort_stat(self):
        """ Sort dictionaries by values and create lists of top N keys. """

        ptp_sorted = (sorted(self.rect_ptps.items(), key=lambda x: x[1])) #Sort values (the peak to valley measurements)

        self.ptp_filtered = [x[0] for x in ptp_sorted[:NUM_CANDIDATES]] #Slice only the first 20 rectangles (lowest ptp values) and populate ptp_sorted

        std_sorted = (sorted(self.rect_stds.items(), key=lambda x: x[1])) #Sort values (the standard deviation measurements)

        self.std_filtered = [x[0] for x in std_sorted[:NUM_CANDIDATES]] #Slice only the first 20 rectangles (lowest std values) and populate std_sorted

        #Compare between std_filtered and ptp_filtered and append matches to high_graded_rects
        for rect in self.std_filtered: 
            if rect in self.ptp_filtered:
                self.high_graded_rects.append(rect)

    def draw_filtered_rects(self, image, filtered_rect_list):
        """ Draw rectangels in list on the image, then return the image """

        img_copy = image.copy()

        for k in filtered_rect_list:

            #Draw rectangle (img to draw, rect coords, line width)
            cv.rectangle(img_copy,
                        (self.rect_coords[k][0], self.rect_coords[k][1]), #0=upper left x, 1=upper left y
                        (self.rect_coords[k][2], self.rect_coords[k][3]), #2=lower right x, 3=lower right y
                        (255, 0, 0), 1)
                        
            #Put text on rectangle (img to draw, text, coords (upper left x and lower right x), font, line width, color)
            cv.putText(img_copy, str(k),
                        (self.rect_coords[k][0] + 1, self.rect_coords[k][3] - 1),
                        cv.FONT_HERSHEY_PLAIN, 0.65, (255, 0, 0), 1)

        cv.putText(img_copy, "30 N", (10, LAT_30_N - 7),
                    cv.FONT_HERSHEY_PLAIN, 1, 255)

        #Draw latitude limits for 30 north then 30 south
        #Draw north line (img to draw, coords for start and end (x,y), color, thickness)
        cv.line(img_copy, (0, LAT_30_N), (IMG_WIDTH, LAT_30_N),
                (255, 0, 0), 1)
        cv.line(img_copy, (0, LAT_30_S), (IMG_WIDTH, LAT_30_S),
                (255, 0, 0), 1)
        cv.putText(img_copy, "30 S", (10, LAT_30_S + 16), 
                    cv.FONT_HERSHEY_PLAIN, 1, 255)
        
        return img_copy #Return annotated img

    def make_final_display(self):
        """ Use TK to show map with final rectangles and statistics informatio """

        #Title of the search project
        screen.title("Sites By MOLA Gray STD And PTP {} Rect".format(self.name))

        #Draw final rects on a colored map
        img_color_rects = self.draw_filtered_rects(IMG_COLOR, self.high_graded_rects)

        #To post the new img on tkinter canvas, first convert to a RGB format, then to a compatible photo image
        img_converted = cv.cvtColor(img_color_rects, cv.COLOR_BGR2RGB) #Returns a NumPy array

        #Convert array into a photo image for tkinter
        img_converted = ImageTk.PhotoImage(Image.fromarray(img_converted))

        #Place image into canvas (coords for upper left corners of canvas (0, 0), converted img, north west anchor direction)
        canvas.create_image(0, 0, image=img_converted, anchor=tk.NW)

        #Add summary text for every rect
        #Coords for the bottom left corner of the first txt object
        txt_x = 5
        txt_y = IMG_HT + 20
        for k in self.high_graded_rects:
            #Place txt on canvas (coords (txt_x, txt_y), left justified anchor direction, default font, txt str)
            canvas.create_text(txt_x, txt_y, anchor="w", font=None,
                                text="rect={} mean elev={:.1f} std={:.2f} ptp={}"
                                .format(k, self.rect_means[k], self.rect_stds[k], self.rect_ptps[k]))

            #Increment txt box y coords after drawing each txt object
            txt_y += 15

            #Check if the text greater than the bottom canvas. 
            if txt_y >= int(canvas.cget("height")) - 10:
                #Make new column shifting x coords by 300 and reset y coords by img heihgt + 20
                txt_x += 300
                txt_y = IMG_HT + 20
        
        canvas.pack() #Packing optimizes the placement of objects in the canvas
        screen.mainloop() #mainloop() is an infinite loop that runs tkinter, waits for an event to happen, then processes said event until the window is closed

def main():
    #Instantiate an app object from Search class and pass the rects dims as a name
    app = Search("670x335 km")
    app.run_rect_stats() #Run stats on the rects
    app.draw_qc_rects() #Draw quality control rects
    app.sort_stat() #Sort stats with lowest values (the first 20 vals)
    ptp_img = app.draw_filtered_rects(IMG_GRAY, app.ptp_filtered) #Draw best ptp stats
    std_img = app.draw_filtered_rects(IMG_GRAY, app.std_filtered) #Draw best std stats

    #Show results
    cv.imshow("Sorted by ptp for {} rect".format(app.name), ptp_img)
    cv.waitKey(10)
    cv.imshow("Sorted by std for {} rect".format(app.name), std_img)
    cv.waitKey(10)

    app.make_final_display()

if __name__ == "__main__":
    main()