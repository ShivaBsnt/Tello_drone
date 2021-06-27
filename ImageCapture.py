from djitellopy import tello

import cv2

me = tello.Tello()

me.connect()

print(me.get_battery())

me.streamon()

while True:
    try:
        img = me.get_frame_read()
        my_frame = img.frame
        img = cv2.resize(my_frame, (360, 240))
        cv2.imshow("Image", my_frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            cv2.destroyAllWindows()
            break
    except Exception as e:
        print(str(e))
