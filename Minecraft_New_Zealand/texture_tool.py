from PIL import Image
import matplotlib.pyplot as plt
from os import listdir, mkdir, remove
from math import inf

ROTATIONS = {
    "*_log": [90],
    "*_stem": [90],
    "*_trapdoor": [90, 180, 270],
    "*_anvil_top": [90],
    "*_froglight_side": [90],
    "*_glazed_terracotta": [90, 180, 270],
    "bamboo_block": [90],
    "barrel_side": [90],
    "basalt_side": [90],
    "big_dripleaf_top": [90],
    "bone_block_side": [90],
    "calibrated_sculk_sensor": [90],
    "cherry_log": [90],
    "comparator": [90],
    "crimson_stem": [90],
    "deepslate": [90],
    "hay_block_side": [90],
    "loom_top": [90, 180, 270],
    "observer_side": [90, 180, 270],
    "observer_top": [90, 180, 270],
    "piston_side": [90, 180, 270],
    "polished_basalt_side": [90],
    "pumpkin_top": [90, 180, 270],
    "purpur_pillar": [90],
    "quartz_pillar": [90],
    "repeater": [90, 180, 270],
    "stonecutter_top": [90],
}

class TextureTool:
    def __init__(self, texture_dir="./data/minecraft"):
        self.textures = []
        self._get_all_textures(texture_dir)

    def _get_all_textures(self, dir):
        """ Generate all textures that fit the following pattern - solid, partial on solid, transparency on solid """
        # Grab lists of textures
        solid_textures = [f"{dir}/solid/{file}" for file in listdir(dir + "/solid")]
        overlay_textures = [f"{dir}/transparency/{file}" for file in listdir(dir + "/transparency")] + \
            [f"{dir}/partial/{file}" for file in listdir(dir + "/partial")]
        
        self.textures = solid_textures[:]
        
        # Create an empty folder to store the generated textures
        try: 
            mkdir(f"{dir}/temp")
        except(FileExistsError):
            pass
        to_delete = listdir(f"{dir}/temp")
        for file in to_delete:
            remove(f"{dir}/temp/{file}")
        
        # Generate remaining textures
        for fg_location in overlay_textures:
            foreground = load_image(fg_location, as_image=True)
            fg_name = fg_location.split('/')[-1]
            for bg_location in solid_textures:
                background = load_image(bg_location, as_image=True)
                bg_name = bg_location.split('/')[-1]

                background.paste(foreground, (0,0), foreground)
                
                file_name = f"{dir}/temp/{bg_name}_under_{fg_name}"

                background.save(file_name)
                self.textures.append(file_name)

    def find_closest_match(self, data_points, width):
        """ Finds the texture with smallest RMS error from the color data """
        img = _reduce_to_16_by_16(data_points, width)
        best_rmse = inf
        closest_match = None

        for texture in self.textures:
            txt = load_image(texture)
            rmse = _texture_rmse(img, txt)
            if rmse < best_rmse:
                best_rmse = rmse
                closest_match = texture
                if rmse <= 0.01:
                    break
        
        return closest_match

def _reduce_to_16_by_16(data_points, width):
    """ Populate a list with averaged values """
    points_per_pixel = int(width / 16)
    if points_per_pixel != width/16:
        # Uneven pixel handling is not in current scope
        return

    pixels = []
    for row in range(16):
        for col in range(16):
            points = _get_points_in_pixel(data_points, points_per_pixel, row, col)
            pixels.append(_create_pixel_from_points(points)) 
            
    return pixels

def _create_pixel_from_points(points):
    """ Reduces the points into a single pixel by averaging RGB of the points with a uniform mean """
    rgba = [0, 0, 0, 255]
    for point in points:
        for i in range(3):
            rgba[i] += point[i] / len(points)
    
    # Perform rounding
    for i in range(3):
        rgba[i] = round(rgba[i])
    return tuple(rgba)

def _get_points_in_pixel(data_points, points_per_pixel, row, col):
    """ Gets the points of data_points that correlate to pixel (row,col) """
    points = []
    start_index = row*points_per_pixel*16 + col*points_per_pixel
    for j in range(points_per_pixel):
        for i in range(points_per_pixel):
            index = start_index + j*points_per_pixel*16 + i
            points.append(data_points[index])
    return points

def _texture_rmse(texture_1, texture_2):
    """
    Returns a float of the Root Mean Squared Error of the images.

    This is the mean of the squared error between corresponding pixels.
    """
    squared_errors = []

    # Iterating over each pixel, take the RMSE across the RGB values for that pixel.
    for i in range(256):
        error = 0
        for j in range(3):
            error += ((texture_1[i][j] - texture_2[i][j]) ** 2) / 3
        
        # We would sqrt the error before using it, then immediately square it in the following step. Both omitted for clarity.
        squared_errors.append(error / 256)
    
    # Average list - the division is performed in the previous step to avoid creating too large of a number
    return sum(squared_errors) ** 0.5

def load_image(filename, as_image=False):
        try:
            im = Image.open(filename)
        except Exception as e:
            print(filename)
            raise e
        im = im.convert("RGBA")
        if as_image:
            return im
        return list(im.getdata())

def display_image(pixels):
    im = Image.new("RGBA", (16, 16))
    im.putdata(pixels)
    plt.imshow(im)
    plt.show()

# Tests
if __name__ == "__main__":
    tt = TextureTool()
    test_cases = [
        "./data/minecraft/solid/cherry_planks.png",
        "./data/minecraft/solid/moss_block.png",
        "./data/minecraft/temp/acacia_log_top.png_under_gray_candle_lit_4.png",
        "./data/minecraft/temp/moss_block.png_under_green_candle.png",
    ]

    for tc in test_cases:
        data = load_image(tc)
        print(f"Closest texture: {tt.find_closest_match(data, 16)}")