import cv2
from kivy.graphics.texture import Texture


def get_texture(frame, format='rgb'):
    buf1 = cv2.flip(frame, 0)
    buf = buf1.tostring()

    size = (frame.shape[1], frame.shape[0])

    texture = Texture.create(size=size, colorfmt=format)
    texture.blit_buffer(buf, colorfmt=format, bufferfmt='ubyte')
    return texture
