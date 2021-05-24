""" A side view from west to east through Olympus Mons. This will allow to extract meaningful insights regarding the smoothness of a surface and visualize its topography."""
from PIL import Image, ImageDraw
import matplotlib.pyplot as plt
from utils import save_fig

#Get x and z val along the horizontal profile, parallel to y coords
y_coord = 202
im = Image.open("images/mola_1024x512_200mp.jpg").convert("L")
width, height = im.size
x_vals = [x for x in range(width)]
z_vals = [im.getpixel((x, y_coord)) for x in x_vals]

#Draw the profile on MOLA img
draw = ImageDraw.Draw(im)
draw.line((0, y_coord, width, y_coord), fill=255, width=3)
draw.text((100, 165), "Olympus Mons", fill=255)
im.save("images/mola_elevation_line.png")
im.show()

#Make an interactive plot for the elevation profile
""" There should be a plateu between x=740 to x=890 """
fig, ax = plt.subplots(figsize=(9, 4))
axes = plt.gca()
axes.set_ylim(0, 400)
ax.plot(x_vals, z_vals, color="black")
ax.set(xlabel="x-coordinates",
      ylabel="Intensity (Height)",
      title="Mars Elevation Profile (y = 202)")
ratio = 0.15 #Reduces vertical exaggeration in profile plot
xleft, xright = ax.get_xlim()
ybase, ytop = ax.get_ylim()
ax.set_aspect(abs((xright-xleft)/(ybase-ytop)) * ratio)
plt.text(0, 310, "WEST", fontsize=10)
plt.text(980, 310, "EAST", fontsize=10)
plt.text(100, 280, "Olympus Mons", fontsize=8)
save_fig("mars_elevation_profile")
plt.show()