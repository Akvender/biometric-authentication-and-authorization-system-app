__all__ = ["face_recognition"]

import cv2
import os
from deepface import DeepFace


def face_recognition(img1, img2):
    try:
        cv2.imwrite('temp_img1.jpg', img1)
        cv2.imwrite('temp_img2.jpg', img2)
        result = DeepFace.verify('temp_img1.jpg', 'temp_img2.jpg')
        os.remove('temp_img1.jpg')
        os.remove('temp_img2.jpg')
        return result

    except:
        os.remove('temp_img1.jpg')
        os.remove('temp_img2.jpg')
        return False
