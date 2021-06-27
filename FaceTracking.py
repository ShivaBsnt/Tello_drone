import cv2
import numpy as np
from djitellopy import tello
import time


me = tello.Tello()

me.connect()

print(me.get_battery())
me.streamon()
me.takeoff()
time.sleep(2.2)
me.send_rc_control(0, 0, 25, 0)

w, h = 360, 240
fb_range = [6200, 6800]
pid = [0.4, 0.4, 0]
p_error = 0


def find_face(img):
    # getting haarcascade xml file for face recognition
    face_cascade = cv2.CascadeClassifier("Resources/haarcascade_frontalface_default.xml")
    # converting image to gray to make it easier to detect face
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(img_gray, 1.1, 6)
    face_list = []
    face_list_area = []

    for (x, y, w, h) in faces:
        cv2.rectangle(img, (x, y), (x+w, y+h), (0, 0, 255), 1)
        cx = x + w // 2
        cy = y + h // 2
        area = w * h
        cv2.circle(img, (cx, cy), 2, (0, 255, 0), cv2.FILLED)
        face_list.append([cx, cy])
        face_list_area.append(area)
    if len(face_list_area) != 0:
        i = face_list_area.index(max(face_list_area))
        return img, [face_list[i], face_list_area[i]]
    else:
        return img, [[0, 0], 0]


def face_track(info, w, pid, p_error):
    area = info[1]
    x, y = info[0]
    fb = 0
    error = x - w//2
    speed = pid[0]*error + pid[1] * (error-p_error)
    speed = int(np.clip(speed, -100, 100))
    if area > fb_range[1] > area:
        fb = 0
    if area > fb_range[1]:
        fb = -20
    elif area < fb_range[0] and area != 0:
        fb = 20
    if x == 0:
        speed = 0
        error = 0
    me.send_rc_control(0, fb, 0, speed)
    print("speed :", speed, "fb :", fb, )
    return error


# cap = cv2.VideoCapture(0)
while True:
    try:
        # _, img = cap.read()
        img = me.get_frame_read()
        my_frame = img.frame
        img = cv2.resize(my_frame, (w, h))
        img, info = find_face(img)
        p_error = face_track(info, w, pid, p_error)
        print("Center", info[0], "Area", info[1])
        cv2.imshow("Image", img)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            cv2.destroyAllWindows()
            me.send_rc_control(0, 0, 0, 0)
            me.land()

            break
    except Exception as e:
        print(str(e))
