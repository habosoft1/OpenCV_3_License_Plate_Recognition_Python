import kivy
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.app import App
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.widget import Widget
from kivy.graphics.texture import Texture
from kivy.clock import Clock

from helperClasses import MyVideoCapture
import helperFunctions
from ProcessPlate import checkFrame


class MainWindow(Screen):
    started = False
    frame_update = 50  # ms
    vid = MyVideoCapture(0)
    update_event = None

    def callback_start_stop(self):
        self.started = not self.started
        if self.update_event is None:
            self.update_event = Clock.schedule_interval(
                self.update, self.frame_update/1000)
        if self.started:
            self.update_event()
        else:
            self.update_event.cancel()

    def update(self, elapsed_time):
        ret, frame = self.vid.get_frame()
        if ret:
            image_frame, plate = checkFrame(frame)
            self.image_main.texture = helperFunctions.get_texture(
                frame=image_frame)
            if plate:
                print(plate)
                self.plaka_label.text = plate.strChars
            else:
                self.plaka_label.text = ""

            self.image_main.x = self.image_main.parent.width*.5 - self.image_main.width*.5


class DataWindow(Screen):
    pass


class WindowManager(ScreenManager):
    pass


kv = Builder.load_file("main_ui.kv")


class PlakaApp(App):
    def build(self):
        return kv


if __name__ == '__main__':
    PlakaApp().run()
