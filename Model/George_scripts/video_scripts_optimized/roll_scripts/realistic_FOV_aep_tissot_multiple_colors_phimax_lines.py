# this script makes lines instead of ellipses that match the phi max values (orientations) of the ommatidia of the first eye (the phi max values should be the negative values of the second eye). Thickness of lines is uniform.

import sys
import numpy as np
import cv2
import matplotlib
import matplotlib.cm as cm
import colorsys
import math

def spherical_to_cartesian(radius, azimuth_deg, elevation_deg):
    s = radius * elevation_deg / 90  # distance from image edge
    azimuth_rad = np.radians(azimuth_deg)
    elevation_rad = np.radians(elevation_deg)
    x = int((radius - s) * np.sin(azimuth_rad))
    y = int(radius - (radius - s) * np.cos(azimuth_rad))
    return x, y

def main(image_path, output_path, azimuth_list, elevation_list, phimax_list):
    try:
        # Open the circular image
        img = cv2.imread(image_path)
        # Calculate the center of the projection
        img_height, img_width, _ = img.shape
        center_x = img_width // 2
        center_y = img_height // 2

        # this is for rotating the image if necessary (bicubic interpolation). Note that it rotates counterclockwise for positive angles
        M = cv2.getRotationMatrix2D((center_y, center_x), 0, 1)  # the format is cv2.getRotationMatrix2D(center, angle, scale)
        img = cv2.warpAffine(img, M, (img_width, img_height), flags=cv2.INTER_CUBIC)

        # Create a blank canvas with a white background
        canvas = np.full_like(img, (255, 255, 255), dtype=np.uint8)  # activate this for white background
        #canvas = np.zeros_like(img) # activate this for transparent canvas (shows the image)

        for azimuth_deg, elevation_deg, phimax_value in zip(azimuth_list, elevation_list, phimax_list):
            # Calculate the pixel coordinates for the projection
            projection_radius = min(center_x, center_y)
            proj_x, proj_y = spherical_to_cartesian(projection_radius, azimuth_deg, elevation_deg)
            proj_x += center_x  # This is to set 0,0 to the north (top of the image)

            # Calculate line endpoints
            line_length = 15  # line length
            angle_rad = np.radians(phimax_value)
            x1 = int(proj_x - line_length * np.cos(angle_rad))
            y1 = int(proj_y - line_length * np.sin(angle_rad))
            x2 = int(proj_x + line_length * np.cos(angle_rad))
            y2 = int(proj_y + line_length * np.sin(angle_rad))


            # Draw the line on the canvas
            cv2.line(canvas, (x1, y1), (x2, y2), color=(0, 0, 0), thickness=2)
        canvas = cv2.cvtColor(canvas, cv2.COLOR_RGB2BGR)
        # Save the resulting image
        cv2.imwrite(output_path, canvas)
        #print(f"Projection image saved to {output_path}")

    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    if len(sys.argv) != 6:
        print("Usage: python script.py <input_image> <output_image> <azimuth_list> <elevation_list> <phimax_list>")
        sys.exit(1)

    input_image = sys.argv[1]
    output_image = sys.argv[2]
    azimuth_list = [float(x.strip('[]')) for x in sys.argv[3].split(',')]
    elevation_list = [float(x.strip('[]')) for x in sys.argv[4].split(',')]
    phimax_list = [float(x.strip('[]')) for x in sys.argv[5].split(',')]

    main(input_image, output_image, azimuth_list, elevation_list, phimax_list)
