import cv2
import mediapipe as mp
import pyautogui
import math
import time
import numpy as np

# PyAutoGUI configurations
pyautogui.FAILSAFE = False
screen_width, screen_height = pyautogui.size()

# MediaPipe configurations
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)
mp_draw = mp.solutions.drawing_utils

# Video capture setup
cap = cv2.VideoCapture(0)
# Default webcam resolutions usually 640x480
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
cam_width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
cam_height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)

# Frame Reduction (Padding for movement box)
frame_r = 100 

# State variables for smoothing
ploc_x, ploc_y = 0, 0
cloc_x, cloc_y = 0, 0
smooth_factor = 5 # Smoothing constant

# State variables for clicking
left_clicked = False
right_clicked = False

# State variables for scrolling
prev_y = 0

def calculate_distance(p1, p2):
    """Calculate Euclidean distance between two MediaPipe landmarks."""
    return math.hypot(p2.x - p1.x, p2.y - p1.y)

# Loop variables
p_time = 0

print("Starting Gesture Control Cursor System...")
print(f"Screen Mapping Resolution: {screen_width}x{screen_height}")
print(f"Camera Resolution: {cam_width}x{cam_height}")

try:
    while cap.isOpened():
        success, img = cap.read()
        if not success:
            break
            
        # Flip the image horizontally for a selfie-view display
        img = cv2.flip(img, 1)
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = hands.process(img_rgb)
        
        # Draw the bounding box for cursor movement
        cv2.rectangle(img, (frame_r, frame_r), 
                      (int(cam_width) - frame_r, int(cam_height) - frame_r), 
                      (255, 0, 255), 2)
        
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                mp_draw.draw_landmarks(img, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                
                # Get relevant landmarks
                index_tip = hand_landmarks.landmark[8]
                thumb_tip = hand_landmarks.landmark[4]
                middle_tip = hand_landmarks.landmark[12]
                ring_tip = hand_landmarks.landmark[16]
                pinky_tip = hand_landmarks.landmark[20]
                
                # 1. Cursor Movement: Index finger tracking
                # Ensure the movement is mapped within the specific padded rectangle
                x3 = int(index_tip.x * cam_width)
                y3 = int(index_tip.y * cam_height)
                
                # We check the rest of the fingers to see if we are in moving mode vs scrolling
                index_up = index_tip.y < hand_landmarks.landmark[6].y
                middle_up = middle_tip.y < hand_landmarks.landmark[10].y
                ring_down = ring_tip.y > hand_landmarks.landmark[14].y
                pinky_down = pinky_tip.y > hand_landmarks.landmark[18].y

                # Mouse Movement Mode: Only index finger is up
                if index_up and not middle_up and ring_down and pinky_down:
                    # Convert coordinates to screen size
                    x_mapped = int(np.interp(x3, (frame_r, cam_width - frame_r), (0, screen_width)))
                    y_mapped = int(np.interp(y3, (frame_r, cam_height - frame_r), (0, screen_height)))
                    
                    # Apply low pass filter for smoothing
                    cloc_x = ploc_x + (x_mapped - ploc_x) / smooth_factor
                    cloc_y = ploc_y + (y_mapped - ploc_y) / smooth_factor
                    
                    # Move mouse safely
                    try:
                        pyautogui.moveTo(cloc_x, cloc_y)
                    except pyautogui.FailSafeException:
                        pass
                        
                    ploc_x, ploc_y = cloc_x, cloc_y
                    cv2.circle(img, (x3, y3), 15, (255, 0, 0), cv2.FILLED)
                
                # 2. Left Click Mode: Pinch Thumb and Index Finger together
                dist_left_click = calculate_distance(thumb_tip, index_tip)
                if dist_left_click < 0.05: # Distance threshold
                    cv2.circle(img, (x3, y3), 15, (0, 255, 0), cv2.FILLED)
                    if not left_clicked:
                        pyautogui.click()
                        left_clicked = True
                else:
                    left_clicked = False
                    
                # 3. Right Click Mode: Pinch Index and Middle Finger together
                dist_right_click = calculate_distance(index_tip, middle_tip)
                # Ensure not left clicking at the same time
                if dist_right_click < 0.05 and dist_left_click > 0.08:
                    x4 = int(middle_tip.x * cam_width)
                    y4 = int(middle_tip.y * cam_height)
                    cx, cy = (x3 + x4) // 2, (y3 + y4) // 2
                    cv2.circle(img, (cx, cy), 15, (0, 0, 255), cv2.FILLED)
                    if not right_clicked:
                        pyautogui.rightClick()
                        right_clicked = True
                else:
                    right_clicked = False
                    
                # 4. Scroll Mode: Index and Middle fingers up and apart, moving vertically
                if index_up and middle_up and ring_down and pinky_down and dist_right_click > 0.05:
                    cv2.circle(img, (x3, y3), 15, (255, 255, 0), cv2.FILLED)
                    x4 = int(middle_tip.x * cam_width)
                    y4 = int(middle_tip.y * cam_height)
                    cv2.circle(img, (x4, y4), 15, (255, 255, 0), cv2.FILLED)
                    
                    # Current middle point of both fingers
                    curr_y = (y3 + y4) // 2
                    
                    if prev_y != 0:
                        diff_y = prev_y - curr_y
                        if abs(diff_y) > 5: # Threshold for scroll sensitivity
                            # diff_y > 0 means fingers moved UP -> scroll DOWN (macOS natural scrolling)
                            pyautogui.scroll(int(diff_y * 1.5)) # Adjust scroll speed scaling
                            
                    prev_y = curr_y
                else:
                    prev_y = 0


        # Display FPS
        c_time = time.time()
        fps = 1 / (c_time - p_time) if p_time else 0
        p_time = c_time
        cv2.putText(img, f'FPS: {int(fps)}', (20, 50), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 0), 3)
        
        # Display window
        cv2.imshow("AI Gesture Cursor Tracker", img)
        
        # Press 'q' or 'ESC' to exit
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q') or key == 27:
            break

except KeyboardInterrupt:
    print("User interrupted.")

finally:
    cap.release()
    cv2.destroyAllWindows()
    print("Cleaned up resources.")
