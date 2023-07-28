import numpy as np
import cv2
from mss import mss
from PIL import Image
import pyautogui
import time

DETECTION_THRESHOLD = 300000

SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080

DETECTION_TOP = 600
DETECTION_LEFT = 0
DETECTION_WIDTH = SCREEN_WIDTH
DETECTION_HEIGHT = 300

WINRATE_BUTTON_OFFSET_X = 20
WINRATE_BUTTON_OFFSET_Y = 0
START_BUTTON_OFFSET_X = -100
START_BUTTON_OFFSET_Y = 0

WINDOW_NAME = "Limbus Pedal"
WINDOW_WIDTH = 500
WINDOW_HEIGHT = 500

screenshot = mss()

# source: https://stackoverflow.com/questions/67826760/how-to-detect-if-an-image-is-in-another-image
def template_location_in_image(img, templ):

    # Template matching using TM_SQDIFF: Perfect match => minimum value around 0.0
    match_result = cv2.matchTemplate(img, templ, cv2.TM_SQDIFF)

    # Get value of best match, i.e. the minimum value
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(match_result)

    detection_threshold = DETECTION_THRESHOLD

    if min_val <= detection_threshold:
        return min_loc
    else:
        return False

def update_screen_preview():
    img = grab_screenshot_colored()
    cv2.imshow(WINDOW_NAME, img)

def get_bounding_box():
    return {'top': DETECTION_TOP, 'left': DETECTION_LEFT, 'width': DETECTION_WIDTH, 'height': DETECTION_HEIGHT}

def grab_screenshot_colored():
    screen_img = screenshot.grab(get_bounding_box())
    screen_img = np.array(screen_img)
    screen_img = cv2.cvtColor(screen_img, cv2.COLOR_RGBA2RGB)

def grab_screenshot_grayscale():
    return cv2.cvtColor(grab_screenshot_colored(), cv2.COLOR_RGB2GRAY)

def create_window():
    pass
    # cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_NORMAL)
    # cv2.resizeWindow(WINDOW_NAME, WINDOW_WIDTH, WINDOW_HEIGHT)
    # cv2.createButton("Update preview",button_update_preview,None,cv2.QT_PUSH_BUTTON,1)

def click(coordinates):
    x, y = coordinates
    pyautogui.click(x, y)

def start_fight(winrate_coords, start_coords):
    click(winrate_coords)
    print("Clicking on WINRATE")
    time.sleep(0.5)
    print("Clicking on START")
    click(start_coords)

def calculate_winrate_coords_from_match_result(match_result):
    x = DETECTION_LEFT + match_result[0] + WINRATE_BUTTON_OFFSET_X
    y = DETECTION_TOP + match_result[1] + WINRATE_BUTTON_OFFSET_Y
    
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
    create_window()

    winrate_img = cv2.imread('Q:/Projects/Python/limbus-pedal/assets/winrate.png')
    winrate_img = cv2.cvtColor(winrate_img, cv2.COLOR_RGB2GRAY)

    print("Active")

    while True:
        screen_img = screenshot.grab(get_bounding_box())
        screen_img = np.array(screen_img)
        screen_img = cv2.cvtColor(screen_img, cv2.COLOR_RGBA2GRAY)

        #cv2.imshow('screen', screen_img)
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