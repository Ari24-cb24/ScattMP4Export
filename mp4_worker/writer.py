import math
import sys

import numpy
from PIL import Image, ImageDraw, ImageFont, ImageChops
import moviepy.editor as mpy

from converter.document_types import ScattShot, ScattTraceElement, TARGET_RADIUS, TARGET_DIAMETER
from mp4_worker.utils import resize_image


class Writer:
    FPS = 144
    WIDTH = 640
    HEIGHT = 640
    TIME_PER_FRAME = 1000 / FPS

    def __init__(self, shot: "ScattShot"):
        self.background_image = resize_image(Image.open("assets/air_rifle_target.png").convert("RGB"), self.WIDTH, self.HEIGHT)
        self.shot = shot

    def run(self):
        frames = []
        font = ImageFont.truetype("assets/fonts/arial.ttf", 20)

        elapsed_millis = 0
        shot_start = self.shot.trace[0].t_relative
        shot_time = sorted(self.shot.trace, key=lambda x: abs(x.t_relative))[0].absolute_time(shot_start) * 1000
        total_millis = self.shot.duration() * 1000
        frame_idx = 0
        last_trace = None

        MAX_FRAMES = total_millis / 1000 * self.FPS

        print(f"Total millis: {total_millis}")
        print(f"Max Frames: {MAX_FRAMES}")

        parent = self.background_image.copy()
        draw = ImageDraw.Draw(parent)

        while elapsed_millis < total_millis:
            sys.stdout.write(f"\rWriting frame {frame_idx}/{MAX_FRAMES}")

            text_overlay = Image.new("RGB", (self.WIDTH, self.HEIGHT), (0, 0, 0))
            text_draw = ImageDraw.Draw(text_overlay)
            text_draw.text((0, 0), f"Time: {str(elapsed_millis).zfill(6)}", (255, 255, 255), font=font)
            text_draw.text((0, 25), f"Frame idx: {str(frame_idx).zfill(4)}", (255, 255, 255), font=font)

            # Get nearest trace element
            trace_element = None

            for element in self.shot.trace:
                if element.absolute_time(shot_start) * 1000 > elapsed_millis:
                    trace_element = element
                    break

            if trace_element:
                if not last_trace:
                    last_trace = trace_element
                else:
                    # all coordinates are a ratio of 45 so make them percentages and multiply by width/height
                    prev_x = last_trace.x_offset(self.WIDTH)
                    prev_y = last_trace.y_offset(self.HEIGHT)
                    curr_x = trace_element.x_offset(self.WIDTH)
                    curr_y = trace_element.y_offset(self.HEIGHT)

                    time_before_shot = shot_time - trace_element.absolute_time(shot_start) * 1000

                    color = (0, 255, 0)

                    if time_before_shot < 1000:
                        color = (255, 255, 0)
                    if time_before_shot < 100:
                        color = (0, 0, 255)
                    if time_before_shot < 0:
                        color = (255, 0, 0)

                    #print(f"Drawing line from ({prev_x}, {prev_y}) to ({curr_x}, {curr_y})")
                    # Draw line from last trace element to current
                    draw.line(
                        (prev_x, prev_y, curr_x, curr_y),
                        fill=color,
                        width=2
                    )
                    last_trace = trace_element

                # check if it is the shot
                if shot_time == trace_element.absolute_time(shot_start) * 1000:
                    # draw a circle with diameter 5 / TARGET_DIAMETER * WIDTH
                    x = trace_element.x_offset(self.WIDTH)
                    y = trace_element.y_offset(self.HEIGHT)
                    diameter = 5 / TARGET_DIAMETER * self.WIDTH

                    draw.ellipse(
                        (x - diameter / 2, y - diameter / 2, x + diameter / 2, y + diameter / 2),
                        fill=(255, 0, 0)
                    )

            frame_img = parent #ImageChops.add(parent, text_overlay)
            frame_img = numpy.array(frame_img)
            frames.append(frame_img)

            elapsed_millis += self.TIME_PER_FRAME
            frame_idx += 1

        print("\nWriting video...")
        clip = mpy.ImageSequenceClip(frames, fps=self.FPS)
        clip.write_videofile("output.mp4", codec="libx264")

