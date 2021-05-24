import os
import matplotlib.pyplot as plt
from PIL import Image

""" Save a matplot image """
IMAGE_PATH = os.path.join("images")
os.makedirs(IMAGE_PATH, exist_ok=True)

def save_fig(fig_id, fig_extension="png", tight_layout=True, resolution=300):
    path = os.path.join(IMAGE_PATH, fig_id + "." + fig_extension)
    print("Saving figure", fig_id)
    if tight_layout:
        plt.tight_layout()
    plt.savefig(path, format=fig_extension, dpi=resolution)

""" Convert ps to png """
def convert_ps_to_png(path):
    img = Image.open(path)
    img.save("final_mola_stats.png")