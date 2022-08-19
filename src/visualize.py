from PIL import Image, ImageDraw, ImageFont, ImageOps
import os
import colorsys
import numpy as np


def visualize(data_dict, DepartmentsXY, FileName="visualization.png", useFacility=True, Grouping=False, drawLabels=True):
    """
    This function provides a tool to visualize (and therefore validate) the output of steps like the first or second stage, data import, etc.
    Input parameters are:
        - data_dict: dictionary containing:
            - Departments: DataFrame containing all Departments' name, width, and height
            - Facility: DataFrame containing facility's name, width, and height.
            - DepartmentsDependencies (not needed): transport costs between the departments, using a matrix. Currently unused, but this may change in the future. Originally intended to indicate the dependencies among the departments (with lines or the like).
        - DepartmentsXY: DataFrame containing the name, x- and y-coordinates of the different departments.
        - FileName (optional): String, defines how the generated picture will be named. Preferably ending in ".png". Defaults to "visualization.png".
        - useFacility (optional):
            - True: We draw the facility with a black-white border around the finished image.
            - False: We don't draw the facility. We calculate the width and height of the smallest facility where the departments could fit inside, and its center (not at (0,0), in contrast to when useFacility is True).
        - Grouping: Indicated whether grouping is active or not. Defines which colors will be chosen for the departments.
    """


    ##########################################
    ######  Define necessary variables  ######
    ##########################################
    
    # Get necessary DataFrames
    Departments = data_dict["Departments"]
    Facility = data_dict["Facility"]

    # Getting absolute path of this file
    dir = os.path.dirname(__file__)

    # Import Font
    font = ImageFont.truetype(dir+"/Calibri.ttf", 40)

    # Determine the size and center of the facility
    if useFacility:
        # Extract facility dimensions from the Facility DataFrame
        w_facility = Facility.iloc[0]['w']
        h_facility = Facility.iloc[0]['h']

        # There is no offset, so set it to zero
        center_offset_x = 0
        center_offset_y = 0
    else:
        # There is no facility given, so we calculate what the size of the facility should be so that all departments fit inside
        w_facility = max(DepartmentsXY["x"] + Departments["w"]/2) - min(DepartmentsXY["x"] - Departments["w"]/2)
        h_facility = max(DepartmentsXY["y"] + Departments["h"]/2) - min(DepartmentsXY["y"] - Departments["h"]/2)

        # Because the departments are not necessarily centered inside the determined facility, we calculate how much we need to offset them
        center_offset_x = (max(DepartmentsXY["x"] + Departments["w"]/2) + min(DepartmentsXY["x"] - Departments["w"]/2))/2
        center_offset_y = (max(DepartmentsXY["y"] + Departments["h"]/2) + min(DepartmentsXY["y"] - Departments["h"]/2))/2
        #print(f"This facility's center is at ({center_offset_x},{center_offset_y})")

    # Transparency properties
    opacity = 0.7  # Defines the opacity of the departments. Must be between 0 and 1.
    # Scale opacity to the correct scale
    #opacity = int(255 * opacity) if not useFacility else 255
    opacity = int(255 * opacity)

    # Border thickness of facility walls. Set then to zero if no facility is given.
    if useFacility:
        borderWidth = 20.0
    else:
        borderWidth = 0.0

    # Define size of image
    imageSize = 2000

    # Scale defines how many pixels will correspond to one unit of department dimensions.
    # The scale is exactly the number so that the resulting picture's smaller side will be imageSize pixels. This means the scale must be defined as:
    #   scale = imageSize/min(w_facility, h_facility)
    # , but we also have to account for the border we draw in the end. So we first calculate the ratio by which the resulting imageSize pixels must be shrunk by:
    #   imageSize / (imageSize + borderWidth * 1.5)
    # The "1.5" scalar comes from the fact that we draw two borders, one with width "borderWidth", and one with "borderWidth/2".
    # Then we multiply that ratio by imageSize, and then we divide by the minimum of the height and width of the facility.
    scale = (imageSize / (imageSize + borderWidth * 2 * 1.5)) * imageSize / min(w_facility, h_facility)



    ##########  Create Images  ##########

    # Create new background image and draw on it
    # Its arguments are color space, (x,y) tupel of size, (r, g, b) tupel of RGB values of background color
    # These two cases ensure that no floating point rounding error results in the smaller picture's dimension being 2001 instead of 2000
    if w_facility == min(w_facility, h_facility):
        imageDimensions = (int(imageSize - borderWidth * 2 * 1.5), int(h_facility*scale))
    else:
        imageDimensions = (int(w_facility*scale), int(imageSize - borderWidth * 2 * 1.5))
    background = Image.new('RGB', imageDimensions, (255, 255, 255))
    background = background.convert('RGBA')
    drawBackground = ImageDraw.Draw(background)

    # Create new image to draw the department texts on
    text = Image.new('RGBA', background.size, (255, 255, 255, 0))
    drawText = ImageDraw.Draw(text)

    Departments_merged = Departments.merge(DepartmentsXY)
    numberDepartments = len(Departments_merged)


    ##########  Draw departments on images  ##########

    # Iterate through every [name, row] simultaneously and draw the corresponding rectangle and label
    for index, row in Departments_merged.iterrows():
        name = row["name"]
        x = row["x"]
        y = row["y"]
        w = row["w"]
        h = row["h"]


        # Do arithmetic because the two different coordinate systems work differently:
        #   - Mathematical Model: Origin in the MIDDLE, and positive y-axis goes UP
        #   - Picture: Origin in the TOP LEFT, and positive y-axis goes DOWN
        x0, y0, x1, y1, x2, y2 = convertCoordinates(x, y, w, h, w_facility, h_facility, scale, center_offset_x, center_offset_y)

        # Define color of rectangle by using RGB colors
        #rectangleColor = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        rectangleColor = color(index)
        if Grouping:
            rectangleColor = color(Departments["group"][index], index, numberDepartments, Grouping=Grouping)
        else:
            rectangleColor = color(index, Grouping=Grouping)

        # Draw rectangle corresponding to current department
        departments = Image.new('RGBA', background.size, (255, 255, 255)+(0,))  # Create new image to draw the departments on
        drawDepartments = ImageDraw.Draw(departments)  # Make image drawable
        borderColor = color(Departments["group"][index], Grouping=Grouping) if Grouping else (0,0,0)
        drawDepartments.rectangle((int(x0), int(y0), int(x1), int(y1)), fill=rectangleColor+(opacity,), outline=borderColor, width=6)  # Draw semi-transparent rectangle ...
        background = Image.alpha_composite(background, departments)  # ... and merge it with the background

        # Draw name of department
        textColor = (0,0,0)
        # This function's arguments are: (x,y) tuple of x and y coordinates, name String, 3-tuple RGB color
        if drawLabels:
            drawText.text((x2, y2), name, textColor, font=font, anchor="mm")


    ##########  Images Merging, Borders, Saving  ##########

    # Finally put text image on top of current image (background + departments)
    background = Image.alpha_composite(background, text)

    # Draw borders around image which correspond to the department walls
    background = ImageOps.expand(background,border=int(borderWidth/2),fill='black')
    background = ImageOps.expand(background,border=int(borderWidth),fill='white')

    # Save image
    background.save(FileName, quality=100)

    # Print location of generated image
    print("Successfully generated visualization image and saved at", FileName)

    return





def convertCoordinates(x, y, w, h, w_facility, h_facility, scale, center_offset_x, center_offset_y):
    """This function calculates the coordinates required for drawing the departments on the picture.
    This is needed because the mathematical model and the visualization uses two different coordinate systems:
        - Mathematical Model: Origin in the MIDDLE, and positive y-axis goes UP
        - Picture: Origin in the TOP LEFT, and positive y-axis goes DOWN
    Also the scale of the mathematical model may be in any order of magnitude, and the picture should be such that it can be properly displayed on common monitors.
    
    :param x: x-coordinate of department
    :param y: y-coordinate of department
    :param w: width of department
    :param h: height of department
    :param w_facility: width of the facility
    :param h_facility: height of the facility
    :param scale: defines by how much the department's coordinates should be scaled (compensates for the different orders of magnitudes between the coordinate systems)
    :param center_offset_x: x-coordinate of the facility's center, usually equal to zero
    :param center_offset_y: y-coordinate of the facility's center, usually equal to zero
    :return: tupel (x0, y0, x1, y1, x2, y2), where (x0, y0) / (x1, y1) / (x2, y2) are the coordinates of the top left corner / bottom right / center of the department 
    """

    # Offset the departments according to the center we previously determined
    x -= center_offset_x
    y -= center_offset_y

    # Calculate x and y coordinates of upper left and lower right points of the rectangle corresponding to a department
    x0 = x - w/2
    y0 = -(y + h/2)   # "-" Ensures the previously mentioned different directions of the positive y-axis direction
    x1 = x + w/2
    y1 = -(y - h/2)   # Same as above
    x2 = x
    y2 = -y

    # Subtract offsets (offsets due to different locations of origins)
    x0 += w_facility/2
    y0 += h_facility/2
    x1 += w_facility/2
    y1 += h_facility/2
    x2 += w_facility/2
    y2 += h_facility/2

    # Scale coordinates
    x0 *= scale
    y0 *= scale
    x1 *= scale
    y1 *= scale
    x2 *= scale
    y2 *= scale

    return x0, y0, x1, y1, x2, y2





def color(hueNum, colorNum=-1, numberDepartments=10, Grouping=False):
    """This function returns a RGB color tuple.
        - hueNum:
            Defines what hue the returned color will have. For example, hueNum=0 will return a red hued color
        - colorNum (optional):
            Defines what variation (in saturation and/or value) of the color with the specified hue will be returned
        - numberDepartments (optional):
            Tells this functions how many departments there are. Will be used to determine how many variations of a color there will be.
        - Grouping (optional):
            Tells this function whether Grouping is active. Decides from which color pool the returned color will be from.
        
    """


    Colors = [
        (255, 255, 0),  # yellow
        (255, 128, 0),  # orange
        (0, 255, 0),    # green2
        (0, 0, 255),    # dark blue
        (0, 255, 255),  # cyan
        (255, 0, 255),  # magenta
        (255, 0, 0),    # red
        (128, 255, 0),  # green1
        (0, 128, 255),  # light blue
        (0, 255, 128),  # green3
        (128, 0, 255),  # purple
        (255, 0, 128)   # rose
    ]

    if colorNum < 0:  
        return Colors[hueNum % len(Colors)]
    
    if not Grouping:  # If grouping is disabled, just return a standard color and exit function.
        return Colors[hueNum % len(Colors)]
        


    # If this part gets executed, we know that grouping is active,
    # and we want to return a color with a specific hue according to the group of the department.

    # Convert color to HSV (hue, saturation, value)
    #normalize
    (r, g, b) = [value / 255 for value in Colors[hueNum % len(Colors)]]
    #convert to hsv
    (h, s, v) = colorsys.rgb_to_hsv(r, g, b)
    

    # Make sure that we deal with a fully saturated color, i.e., saturation and value are 255,
    # or equivalently, ar least one of the r, g, or b value is 255.
    assert (s == 1 and v == 1), f"The color {(r,g,b)=} is not fully saturated, {(h,s,v)=}."

    v = 1  # Set the color to be fully bright
    s = 0.9  # Set the color to be a little bit less saturated

    # Convert hsv back to rgb
    (r, g, b) = colorsys.hsv_to_rgb(h, s, v)
    # Scale it back to its original 0-255 range
    (r, g, b) = (int(255*r), int(255*g), int(255*b))

    return (r, g, b)
