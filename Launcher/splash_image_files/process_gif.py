# To generate new animated splash screen from an existing animated gif file:
# Process the animated gif for M5 device screen: python process_gif.py imageToProcess.gif splash.gif
# Use image_to_c to convert splash.gif to splash.h (https://github.com/bitbank2/image_to_c)
# Make sure Launcher.ino.bin will fit into test partition (1056K currently), or resize partition if needed
# Replace splash.h in Launcher project and rebuild/reflash

# current splash generated from below source image:
# https://en.wikipedia.org/wiki/Blinkenlights#/media/File:Thinking_Machines_CM-5_LED_pattern_animation.gif

# command used:
# python process_gif.py blinkenlights.gif splash.gif 3800 200,0,0 179,92,0

from PIL import Image, ImageSequence, ImageDraw, ImageFont
import math
import os
import sys

def convert_to_tuple(input_string, separator):
    number_tuple = tuple(int(number.strip()) for number in input_string.split(separator))
    return number_tuple

def color_distance(c1, c2):
    """Calculate the Euclidean distance between two colors in RGB space."""
    return math.sqrt(sum([(a - b) ** 2 for a, b in zip(c1, c2)]))

def shift_color(original_color, target_color, distance, max_distance):
    """
    Shifts `original_color` towards `target_color` based on `distance` from the color to replace.
    The shift is proportional to how close `original_color` is to the color to replace,
    with `max_distance` defining the maximum range of effect.
    """
    factor = max(0, 1 - (distance / max_distance))
    return tuple(round(o + (t - o) * factor) for o, t in zip(original_color, target_color))

def process_gif(input_gif_path, output_gif_path, max_duration_ms = None, color_to_replace = None, replacement_color = None, color_range = None, target_dimensions = None, title_text = None, subtext = None):
    with Image.open(input_gif_path) as img:
        frames = [frame.copy() for frame in ImageSequence.Iterator(img)]
    
    processed_frames = []
    max_distance = color_range
    duration_ms = img.info.get('duration', 100)
    if max_duration_ms != None:
        max_frame_i = max_duration_ms / duration_ms

    # https://www.fontsquirrel.com/fonts/Silkscreen
    title_font = ImageFont.truetype("silkscreen.ttf", 32)
    subtext_font = ImageFont.truetype("silkscreen.ttf", 8)

    for i, frame in enumerate(frames):
        if max_duration_ms != None and i > max_frame_i:
            break

        if frame.mode != 'RGBA':
            frame = frame.convert('RGBA')
        
        # rotate to match target orientation
        target_is_landscape = target_dimensions[0] > target_dimensions[1]
        img_is_landscape = frame.width > frame.height
        if target_is_landscape != img_is_landscape:
            frame = frame.rotate(90, expand=True)
        
        # crop to match target aspect ratio
        img_aspect_ratio = frame.width / frame.height
        target_aspect_ratio = target_dimensions[0] / target_dimensions[1]
        if img_aspect_ratio > target_aspect_ratio:
            new_width = int(frame.height * target_aspect_ratio)
            left = (frame.width - new_width) / 2
            frame = frame.crop((left, 0, left + new_width, frame.height))
        elif img_aspect_ratio < target_aspect_ratio:
            new_height = int(frame.width / target_aspect_ratio)
            top = (frame.height - new_height) / 2
            frame = frame.crop((0, top, frame.width, top + new_height))
        
        # resize to match target dimensions
        frame = frame.resize(target_dimensions)
        
        # draw title and subtext
        draw = ImageDraw.Draw(frame)
        title_width = draw.textlength(title_text, font=title_font)
        subtext_width = draw.textlength(subtext, font=subtext_font)
        title_position = ((target_dimensions[0] - title_width) / 2, 40)
        subtext_position = ((target_dimensions[0] - subtext_width) / 2, target_dimensions[1] - 30)
        if title_text != None:
            draw.text(title_position, title_text, font=title_font, fill=(255,255,255,255))
        if subtext != None:
            draw.text(subtext_position, subtext, font=subtext_font, fill=(255,255,255,255))

        # shift nearby colors from color_to_replace to replacement_color
        if (color_to_replace != None and replacement_color != None and color_range > 0):
            data = list(frame.getdata())
            new_data = []
            for item in data:
                distance = color_distance(item[:3], color_to_replace)
                if distance < max_distance:
                    new_color = shift_color(item[:3], replacement_color, distance, max_distance)
                    new_data.append(new_color + (item[3],))
                else:
                    new_data.append(item)
            frame.putdata(new_data)
        
        # if i == 0:
        #     name, extension = os.path.splitext(output_gif_path)
        #     frame.save(f"{name}_0{extension}", format='GIF')

        processed_frames.append(frame)

    processed_frames[0].save(
        output_gif_path,
        save_all=True,
        append_images=processed_frames[1:],
        loop=0,
        optimize=True,
        duration=duration_ms,
        transparency=img.info.get('transparency', None))


if (len(sys.argv) < 3):
    print("Usage: process_anim_gif.py <input_gif_path> <output_gif_path> [max_duration_ms] [color_to_replace \"r,g,b\"] [replacement_color \"r,g,b\"] [color_range] [target_dimensions \"wxh\"] [title_text] [subtext]")
    sys.exit(1)

# required
input_gif_path = sys.argv[1]
output_gif_path = sys.argv[2]
# optional
max_duration_ms = int(sys.argv[3]) if len(sys.argv) >= 4 else None
color_to_replace = convert_to_tuple(sys.argv[4], ',') if len(sys.argv) >= 5 else None
replacement_color = convert_to_tuple(sys.argv[5], ',') if len(sys.argv) >= 6 else None
target_dimensions = convert_to_tuple(sys.argv[6], 'x') if len(sys.argv) >= 7 else (240,135)
color_range = sys.argv[7] if len(sys.argv) >= 8 else 30
title_text = sys.argv[8] if len(sys.argv) >= 9 else "M5Launcher"
subtext = sys.argv[9] if len(sys.argv) == 10 else "Press enter to load new app"

process_gif(input_gif_path, output_gif_path, max_duration_ms, color_to_replace, replacement_color, color_range, target_dimensions, title_text, subtext)