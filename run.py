import numpy as np
import cv2
from mss import mss
from PIL import Image
import pyautogui
import time

DETECTION_THRESHOLD = 2000000

CLICK_DELAY = 0.5

SCREEN_WIDTH = pyautogui.size()[0]
SCREEN_HEIGHT = pyautogui.size()[1]
SCREEN_DIMENSIONS = (SCREEN_WIDTH, SCREEN_HEIGHT)

DETECTION_WIDTH_RATIO = 0.5
DETECTION_HEIGHT_RATIO = 0.4

DETECTION_LEFT = int(SCREEN_WIDTH - SCREEN_WIDTH * DETECTION_WIDTH_RATIO)
DETECTION_TOP = int(SCREEN_HEIGHT - SCREEN_HEIGHT * DETECTION_HEIGHT_RATIO)
DETECTION_WIDTH = int(SCREEN_WIDTH * DETECTION_WIDTH_RATIO)
DETECTION_HEIGHT = int(SCREEN_HEIGHT * DETECTION_HEIGHT_RATIO)

WINRATE_BUTTON_OFFSET_X = 20
WINRATE_BUTTON_OFFSET_Y = 0
START_BUTTON_OFFSET_X = -100
START_BUTTON_OFFSET_Y = 0

WINDOW_NAME = "Limbus Pedal"
WINDOW_WIDTH = 500
WINDOW_HEIGHT = 500

IMG_WINRATE_PATH = './assets/winrate.png'
IMG_WINRATE_ORIGINAL_RESOLUTION = (1920, 1080) # this is the og resoltion the screenshot was taken in

SELECTION_COLOR = (0, 0, 255)
SELECTION_THICKNESS = 2

PREVIEW_SCALE = 0.5

screenshot = mss()

selection_start_dimensions = (10, 10)
selection_end_dimensions = (500, 500)

selection_start_dimensions_temp = (0, 0)

screen_preview = None

def selection_click_event(event, x, y, flags, param):
    global selection_start_dimensions, selection_end_dimensions, selection_start_dimensions_temp

    if event == cv2.EVENT_LBUTTONDOWN:
        scaled_x = int(x / PREVIEW_SCALE)
        scaled_y = int(y / PREVIEW_SCALE)
        print(scaled_x, scaled_y)
        selection_start_dimensions_temp = (scaled_x, scaled_y)
    
    if event == cv2.EVENT_LBUTTONUP:
        scaled_x = int(x / PREVIEW_SCALE)
        scaled_y = int(y / PREVIEW_SCALE)

        print("released at: {} {}".format(scaled_x, scaled_y))
        
        selection_start_dimensions = selection_start_dimensions_temp
        selection_end_dimensions = (scaled_x, scaled_y)
        draw_selection_on_screen_preview()

def resize_img_by_new_resolution(img, old_resolution, new_resolution):
    width_scale = new_resolution[0] / old_resolution[0]
    height_scale = new_resolution[1] / old_resolution[1]

    width = int(img.shape[1] * width_scale)
    height = int(img.shape[0] * height_scale)
    dimensions = (width, height)

    return cv2.resize(img, dimensions, interpolation = cv2.INTER_AREA)

# source: https://stackoverflow.com/questions/67826760/how-to-detect-if-an-image-is-in-another-image
def template_location_in_image(img, templ):

    # Template matching using TM_SQDIFF: Perfect match => minimum value around 0.0
    match_result = cv2.matchTemplate(img, templ, cv2.TM_SQDIFF)

    # Get value of best match, i.e. the minimum value
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(match_result)

    # print(min_val)
    detection_threshold = DETECTION_THRESHOLD

    if min_val <= detection_threshold:
        return min_loc
    else:
        return False

def calculate_scaled_selection_dimensions():
    global selection_start_dimensions, selection_end_dimensions

    start_x, start_y = selection_start_dimensions
    end_x, end_y = selection_end_dimensions

    selection_start_dimensions_scaled = (int(start_x * PREVIEW_SCALE), int(start_y  * PREVIEW_SCALE))
    selection_end_dimensions_scaled = (int(end_x * PREVIEW_SCALE), int(end_y  * PREVIEW_SCALE))

    return (selection_start_dimensions_scaled, selection_end_dimensions_scaled)

def draw_selection_on_screen_preview():
    global selection_start_dimensions, selection_end_dimensions, screen_preview

    selection_start_dimensions_scaled, selection_end_dimensions_scaled = calculate_scaled_selection_dimensions()

    img = screen_preview.copy()
    img = cv2.rectangle(img,
                        selection_start_dimensions_scaled,
                        selection_end_dimensions_scaled,
                        SELECTION_COLOR,
                        SELECTION_THICKNESS)
    
    if PREVIEW_SCALE != 1:
        scaled_dimensions = (int(SCREEN_WIDTH * PREVIEW_SCALE), int(SCREEN_HEIGHT * PREVIEW_SCALE))
        img = cv2.resize(img, scaled_dimensions)
    
    cv2.imshow(WINDOW_NAME, img)

def update_screen_preview():
    global screen_preview

    scaled_dimensions = (int(SCREEN_WIDTH * PREVIEW_SCALE), int(SCREEN_HEIGHT * PREVIEW_SCALE))

    screen_preview = grab_screenshot_colored(fullScreen=True)
    screen_preview = cv2.resize(screen_preview, scaled_dimensions)

    draw_selection_on_screen_preview()

def calculate_detection_width():
    global selection_start_dimensions, selection_end_dimensions

    start_x = selection_start_dimensions[0]
    end_x = selection_end_dimensions[0]

    return abs(start_x - end_x)

def calculate_detection_height():
    global selection_start_dimensions, selection_end_dimensions

    start_y = selection_start_dimensions[1]
    end_y = selection_end_dimensions[1]

    return abs(start_y - end_y)

def get_detection_box(fullScreen=False):
    '''top = 0 if fullScreen else DETECTION_TOP
    left = 0 if fullScreen else DETECTION_LEFT
    width = SCREEN_DIMENSIONS[0] if fullScreen else DETECTION_WIDTH
    height = SCREEN_DIMENSIONS[1] if fullScreen else DETECTION_HEIGHT'''

    top = 0 if fullScreen else selection_start_dimensions[1]
    left = 0 if fullScreen else selection_start_dimensions[0]
    width = SCREEN_DIMENSIONS[0] if fullScreen else calculate_detection_width()
    height = SCREEN_DIMENSIONS[1] if fullScreen else calculate_detection_height()

    return {'top': top,
            'left': left,
            'width': width,
            'height': height}

def grab_screenshot_colored(fullScreen=False):
    detection_box = get_detection_box(fullScreen=fullScreen)
    screen_img = screenshot.grab(detection_box)
    screen_img = np.array(screen_img)
    screen_img = cv2.cvtColor(screen_img, cv2.COLOR_RGBA2RGB)

    return screen_img

def grab_screenshot_grayscale():
    return cv2.cvtColor(grab_screenshot_colored(), cv2.COLOR_RGB2GRAY)

def create_window():
    pass
    cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(WINDOW_NAME, WINDOW_WIDTH, WINDOW_HEIGHT)
    # cv2.createButton("Update preview",button_update_preview,None,cv2.QT_PUSH_BUTTON,1)

def click(coordinates):
    x, y = coordinates
    pyautogui.click(x, y)

def start_fight(winrate_coords, start_coords):
    click(winrate_coords)
    print("Clicking on WINRATE")
    time.sleep(CLICK_DELAY)
    print("Clicking on START")
    click(start_coords)

def calculate_winrate_coords_from_match_result(match_result):
    selection_x = selection_start_dimensions[0]
    selection_y = selection_start_dimensions[1]
    
    x = selection_x + match_result[0] + WINRATE_BUTTON_OFFSET_X
    y = selection_y + match_result[1] + WINRATE_BUTTON_OFFSET_Y
    
    return (x, y)

def calculate_start_coords_from_winrate_coords(winrate_coords):
    x = winrate_coords[0] + START_BUTTON_OFFSET_X
    y = winrate_coords[1] + START_BUTTON_OFFSET_Y

    return (x, y)

def check_close_window():
    if (cv2.waitKey(1) & 0xFF) == ord('q'):
        cv2.destroyAllWindows()
        return True
    if cv2.getWindowProperty(WINDOW_NAME, cv2.WND_PROP_VISIBLE) < 1:
        cv2.destroyAllWindows()
        return True
    return False

def main():
    # create_window()

    winrate_img = cv2.imread(IMG_WINRATE_PATH)
    winrate_img = cv2.cvtColor(winrate_img, cv2.COLOR_RGB2GRAY)
    winrate_img = resize_img_by_new_resolution(winrate_img, IMG_WINRATE_ORIGINAL_RESOLUTION, SCREEN_DIMENSIONS)
    
    update_screen_preview()
    draw_selection_on_screen_preview()
    cv2.setMouseCallback(WINDOW_NAME, selection_click_event)

    print("Active")

    while True:
        screen_img = screenshot.grab(get_detection_box())
        screen_img = np.array(screen_img)
        screen_img = cv2.cvtColor(screen_img, cv2.COLOR_RGBA2GRAY)

        cv2.imshow('screen', screen_img)
        cv2.waitKey(1)
        #cv2.imshow('winrate', winrate_button)

        match_result = template_location_in_image(screen_img, winrate_img)

        if match_result:
            winrate_button_coords = calculate_winrate_coords_from_match_result(match_result)
            start_button_coords = calculate_start_coords_from_winrate_coords(winrate_button_coords)

            start_fight(winrate_button_coords, start_button_coords)

        # if check_close_window():
        #     break

if __name__ == "__main__":
    main()
