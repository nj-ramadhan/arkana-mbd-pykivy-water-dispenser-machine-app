import numpy as np
import kivy
import sys
import os
from kivymd.app import MDApp
from kivymd.toast import toast
from kivymd.uix.datatables import MDDataTable
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivymd.uix.filemanager import MDFileManager
from kivy.clock import Clock
from kivy.config import Config
from kivy.metrics import dp
from datetime import datetime
from pathlib import Path
from kivy.properties import ObjectProperty
from kivy.properties import StringProperty
import time

colors = {
    "Red": {
        "A200": "#EE2222",
        "A500": "#EE2222",
        "A700": "#EE2222",
    },

    "Blue": {
        "200": "#3D969E",
        "500": "#3D969E",
        "700": "#3D969E",
    },

    "Light": {
        "StatusBar": "E0E0E0",
        "AppBar": "#202020",
        "Background": "#EEEEEE",
        "CardsDialogs": "#FFFFFF",
        "FlatButtonDown": "#CCCCCC",
    },

    "Dark": {
        "StatusBar": "101010",
        "AppBar": "#E0E0E0",
        "Background": "#111111",
        "CardsDialogs": "#000000",
        "FlatButtonDown": "#333333",
    },
}

DEBUG = True

class ScreenSplash(BoxLayout):
    screen_manager = ObjectProperty(None)
    screen_choose_product = ObjectProperty(None)
    app_window = ObjectProperty(None)
    
    def __init__(self, **kwargs):
        super(ScreenSplash, self).__init__(**kwargs)
        Clock.schedule_interval(self.update_progress_bar, .01)

    def update_progress_bar(self, *args):
        if (self.ids.progress_bar.value + 1) < 100:
            raw_value = self.ids.progress_bar_label.text.split('[')[-1]
            value = raw_value[:-2]
            value = eval(value.strip())
            new_value = value + 1
            self.ids.progress_bar.value = new_value
            self.ids.progress_bar_label.text = 'Loading.. [{:} %]'.format(new_value)
        else:
            self.ids.progress_bar.value = 100
            self.ids.progress_bar_label.text = 'Loading.. [{:} %]'.format(100)
            time.sleep(0.5)
            self.screen_manager.current = 'screen_choose_product'
            return False

class ScreenChooseProduct(BoxLayout):
    screen_manager = ObjectProperty(None)
    screen_choose_payment = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(ScreenChooseProduct, self).__init__(**kwargs)

    def choose_payment(self, value):
        self.screen_manager.current = 'screen_choose_payment'
        print(value)

    def screen_info(self):
        self.screen_manager.current = 'screen_info'
        
class ScreenChoosePayment(BoxLayout):
    screen_manager = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(ScreenChoosePayment, self).__init__(**kwargs)

    def pay(self, method):
        print(method)
        try:
            if(method=="GOPAY"):
                print("payment gopay")
            elif(method=="OVO"):
                print("payment ovo")
            elif(method=="DIRECT"):
                print("payment direct")
        except:
            print("payment error")
        

class ScreenOperateManual(BoxLayout):
    screen_manager = ObjectProperty(None)

    def __init__(self, **kwargs):      
        super(ScreenOperateManual, self).__init__(**kwargs)

class ScreenOperateAuto(BoxLayout):
    screen_manager = ObjectProperty(None)

    def __init__(self, **kwargs):       
        super(ScreenOperateAuto, self).__init__(**kwargs)

class ScreenInfo(BoxLayout):
    screen_manager = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(ScreenInfo, self).__init__(**kwargs)

    def screen_choose_product(self):
        self.screen_manager.current = 'screen_choose_product'
        

class WaterDispenserMachineApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def build(self):
        self.theme_cls.colors = colors
        self.theme_cls.primary_palette = "Blue"
        self.icon = 'asset/logo.ico'
        Window.fullscreen = 'auto'
        Window.borderless = True
        # Window.size = 1366, 768
        Window.allow_screensaver = True

        screen = Builder.load_file('main.kv')

        return screen


if __name__ == '__main__':
    WaterDispenserMachineApp().run()