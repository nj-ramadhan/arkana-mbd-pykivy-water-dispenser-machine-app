import numpy as np
import kivy
import sys
import os
from kivymd.app import MDApp
from kivymd.toast import toast
from kivymd.uix.datatables import MDDataTable
from kivy.lang import Builder
from kivy.core.window import Window
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.card import MDCard
from kivy.clock import Clock
from kivy.config import Config
from kivy.metrics import dp
from datetime import datetime
from pathlib import Path
from kivy.properties import ObjectProperty
from kivy.properties import StringProperty
import minimalmodbus
import time
import qrcode


qr = qrcode.QRCode(
    version=1,
    error_correction=qrcode.constants.ERROR_CORRECT_L,
    box_size=10,
    border=4,
)

colors = {
    "Blue": {
        "200": "#A3D8DD",
        "500": "#A3D8DD",
        "700": "#A3D8DD",
    },

    "BlueGray": {
        "200": "#09343C",
        "500": "#09343C",
        "700": "#09343C",
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

valve_cold = False
valve_normal = False
pump_main = False
pump_cold = False
pump_normal = False
linear_motor = False
stepper_open_close = False


from gpiozero import Button
from gpiozero import RotaryEncoder
from gpiozero import DigitalInputDevice
from gpiozero import Motor
from gpiozero import DigitalOutputDevice

if(not DEBUG):
    in_sensor_proximity = Button(17)
    in_sensor_flow = DigitalInputDevice(19)
    in_limit_opened = Button(27)
    in_limit_closed = Button(22)

    out_valve_cold = DigitalOutputDevice(20)
    out_valve_normal = DigitalOutputDevice(26)
    out_pump_main = DigitalOutputDevice(21)
    out_pump_cold = DigitalOutputDevice(5)
    out_pump_normal = DigitalOutputDevice(6)
    out_stepper_enable = DigitalOutputDevice(23)
    out_stepper_direction = DigitalOutputDevice(24)
    out_stepper_pulse = DigitalOutputDevice(12)
    out_motor_linear = Motor(16, 25)

BAUDRATE = 19200
BYTESIZES = 8
STOPBITS = 1
TIMEOUT = 0.5
PARITY = minimalmodbus.serial.PARITY_EVEN
MODE = minimalmodbus.MODE_RTU

pulsePerLiter = 450
pulsePerMiliLiter = 450/1000

cold = False
product = 0
pulse = 0
levelMainTank = 0
levelNormalTank = 0
levelColdTank = 0

if (not DEBUG):
    mainTank = minimalmodbus.Instrument('dev/ttyUSB0', 1)
    mainTank.serial.baudrate = BAUDRATE
    mainTank.serial.bytesize = BYTESIZES
    mainTank.serial.parity = PARITY
    mainTank.serial.stopbits = STOPBITS
    mainTank.serial.timeout = 0.5
    mainTank.mode = MODE
    mainTank.clear_buffers_before_each_transaction = True

    coldTank = minimalmodbus.Instrument('dev/ttyUSB0', 2)
    coldTank.serial.baudrate = BAUDRATE
    coldTank.serial.bytesize = BYTESIZES
    coldTank.serial.parity = PARITY
    coldTank.serial.stopbits = STOPBITS
    coldTank.serial.timeout = 0.5
    coldTank.mode = MODE
    coldTank.clear_buffers_before_each_transaction = True

    normalTank = minimalmodbus.Instrument('dev/ttyUSB0', 3)
    normalTank.serial.baudrate = BAUDRATE
    normalTank.serial.bytesize = BYTESIZES
    normalTank.serial.parity = PARITY
    normalTank.serial.stopbits = STOPBITS
    normalTank.serial.timeout = 0.5
    normalTank.mode = MODE
    normalTank.clear_buffers_before_each_transaction = True

# in_sensor_flow.when_activated(lambda : measure)

def measure():
    global pulse
    pulse +=1

def levelCheck(levelMainTank, levelColdTank, levelNormalTank):
    if(levelMainTank >=500.0):
      #send request to server
        print('request for refill')
    
    if(levelColdTank >=50.0):            
        pumpColdAct(1)
        
    if(levelNormalTank >=50.0):
        pumpNormalAct(1)

    if(levelColdTank <=20.0):
        pumpColdAct(0)
        
    if(levelNormalTank <=20.0):
        pumpColdAct(0)

def valveColdAct(exec : bool):
    global valve1IO
    if (exec):
        if(not DEBUG):
            valve1IO.on()
        print('valve 1 on')
    else :
        if(not DEBUG):
            valve1IO.off()
        print('valve 1 off')

def valveNormalAct(exec : bool):
    global valve2IO
    if (exec):
        if(not DEBUG):
            valve2IO.on()
        print('valve 2 on')
    else :
        if(not DEBUG):
            valve2IO.off()
        print('valve 2 off')

def pumpMainAct(exec : bool):
    global out_pump_main
    if (exec):
        if(not DEBUG):
            out_pump_main.on()
        print('pump main on')
    else :
        if(not DEBUG):
            out_pump_main.off()
        print('pump main off')

def pumpColdAct(exec : bool):
    global out_pump_cold
    if (exec):
        if(not DEBUG):
            out_pump_cold.on()
        print('pump cold on')
    else :
        if(not DEBUG):
            out_pump_cold.off()
        print('pump cold off')

def pumpNormalAct(exec : bool):
    global out_pump_normal
    if (exec):
        if(not DEBUG):
            out_pump_normal.on()
        print('pump normal on')
    else :
        if(not DEBUG):
            out_pump_normal.off()
        print('pump normal off')

def stepperAct(exec : str):
    global out_stepper_enable, out_stepper_direction ,out_stepper_pulse, in_limit_opened, in_limit_closed
    
    if(not DEBUG):
        out_stepper_enable.on()
    
    if (exec == 'open'):
        if(not DEBUG):
            out_stepper_direction.on()
            while not in_limit_opened.value:
                out_stepper_pulse.value = 0.5
            
            out_stepper_pulse.value = 0
    else:
        if(not DEBUG):
            out_stepper_direction.off()
            while not in_limit_closed.value:
                out_stepper_pulse.value = 0.5
            
            out_stepper_pulse.value = 0

def linearMotorAct(exec : str):
    global out_motor_linear
    
    if (exec == 'up'):
        if(not DEBUG):
            out_motor_linear.forward()
    else:
        if(not DEBUG):
            out_motor_linear.backward()
    
    if(not DEBUG):
        out_motor_linear.stop()

    

class ScreenSplash(MDBoxLayout):
    screen_manager = ObjectProperty(None)
    app_window = ObjectProperty(None)
    
    def __init__(self, **kwargs):
        super(ScreenSplash, self).__init__(**kwargs)
        Clock.schedule_interval(self.update_progress_bar, .01)
        Clock.schedule_interval(self.regular_check, .1)

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

    def regular_check(self, *args):
        global levelColdTank, levelMainTank, levelNormalTank

        # program for reading sensor end control system algorithm
        if(not DEBUG):
            levelMainTank = mainTank.read_register(5,0,3,False)
            levelColdTank = coldTank.read_register(5,0,3,False)
            levelNormalTank = normalTank.read_register(5,0,3,False)
        
            levelCheck(
                levelColdTank=levelColdTank,
                levelNormalTank=levelNormalTank,
                levelMainTank= levelNormalTank
            )
        # pass

class ScreenChooseProduct(MDBoxLayout):
    screen_manager = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(ScreenChooseProduct, self).__init__(**kwargs)
        Clock.schedule_interval(self.regular_check, .1)

    def cold_mode(self, value):
        global cold
        cold = value

    def choose_payment(self, value):
        global product
        self.screen_manager.current = 'screen_choose_payment'
        print(value)
        product = value
        print(type(product))

    def screen_info(self):
        self.screen_manager.current = 'screen_info'

    def regular_check(self, *args):
        global levelColdTank, levelMainTank, levelNormalTank, cold

        # program for reading sensor end control system algorithm
        if(not DEBUG):
            levelMainTank = mainTank.read_register(5,0,3,False)
            levelColdTank = coldTank.read_register(5,0,3,False)
            levelNormalTank = normalTank.read_register(5,0,3,False)

            levelCheck(
                levelColdTank=levelColdTank,
                levelNormalTank=levelNormalTank,
                levelMainTank= levelNormalTank
            )

        # program for displaying IO condition
        if (cold):
            self.ids.bt_cold.md_bg_color = "#3C9999"
            self.ids.bt_normal.md_bg_color = "#09343C"
        else:
            self.ids.bt_cold.md_bg_color = "#09343C"
            self.ids.bt_normal.md_bg_color = "#3C9999"       

class ScreenChoosePayment(MDBoxLayout):
    screen_manager = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(ScreenChoosePayment, self).__init__(**kwargs)

    def pay(self, method):
        global qr

        print(method)
        try:
            if(method=="GOPAY"):
                time.sleep(0.1)
                qr.add_data("insert data here, it is gopay now")
                qr.make(fit=True)

                img = qr.make_image(back_color=(255, 255, 255), fill_color=(55, 95, 100))
                img.save("qr_payment.png")

                self.screen_manager.current = 'screen_qr_payment'
                print("payment gopay")
                toast("successfully pay with GOPAY")

            elif(method=="ShopeePay"):
                time.sleep(0.1)
                qr.add_data("insert data here, it is ShopeePay now")
                qr.make(fit=True)

                img = qr.make_image(back_color=(255, 255, 255), fill_color=(55, 95, 100))
                img.save("qr_payment.png")

                self.screen_manager.current = 'screen_qr_payment'
                print("payment ovo")
                toast("successfully pay with ShopeePay")

            elif(method=="QRIS"):
                time.sleep(0.1)
                qr.add_data("insert data here, it is QRIS now")
                qr.make(fit=True)

                img = qr.make_image(back_color=(255, 255, 255), fill_color=(55, 95, 100))
                img.save("qr_payment.png")

                self.screen_manager.current = 'screen_qr_payment'
                print("payment qris")
                toast("successfully pay with QRIS")
        except:
            print("payment error")

    def screen_choose_product(self):
        self.screen_manager.current = 'screen_choose_product'

class ScreenOperate(MDBoxLayout):
    screen_manager = ObjectProperty(None)

    def __init__(self, **kwargs):       
        super(ScreenOperate, self).__init__(**kwargs)

    def move_up(self):
        linearMotorAct('up')
        print("move up")
        toast("moving tumbler base up")

    def move_down(self):
        linearMotorAct('down')
        print("move down")
        toast("moving tumbler base down")

    def fill_start(self):
        global pulse, product, pulsePerMiliLiter

        if(not DEBUG):
            stepperAct('open')
        pulse = 0

        while pulse <= pulsePerMiliLiter*product:
            if (cold):
              if(not DEBUG):
                pumpColdAct(1)
            else:
              if(not DEBUG):
                pumpNormalAct(1)
        
        if(not DEBUG):
            pumpColdAct(0)
            pumpNormalAct(0)
            stepperAct('close')

        print(cold)
        print("fill start")
        toast("water filling is started")

    def fill_stop(self):
        if(not DEBUG):
            pumpColdAct(0)
            pumpNormalAct(0)

        print("fill stop")
        toast("thank you for decreasing plastic bottle trash by buying our product")
        self.screen_manager.current = 'screen_choose_product'

class ScreenQRPayment(MDBoxLayout):
    screen_manager = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(ScreenQRPayment, self).__init__(**kwargs)
        Clock.schedule_interval(self.regular_check, 1)
        
    def regular_check(self, *args):
        self.ids.image_qr_payment.source = 'qr_payment.png'
        self.ids.image_qr_payment.reload()
        # pass

    def cancel(self):
        self.screen_manager.current = 'screen_choose_product'

    def dummy_success(self):
        self.screen_manager.current = 'screen_operate' 

class ScreenInfo(MDBoxLayout):
    screen_manager = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(ScreenInfo, self).__init__(**kwargs)

    def screen_choose_product(self):
        self.screen_manager.current = 'screen_choose_product'

    def screen_maintenance(self):
        self.screen_manager.current = 'screen_maintenance'      
 

class ScreenMaintenance(MDBoxLayout):
    screen_manager = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(ScreenMaintenance, self).__init__(**kwargs)
        Clock.schedule_interval(self.regular_check, .1)

    def act_valve_cold(self):
        global valve_cold

        if (valve_cold):
            valve_cold = False 
            valveColdAct(False)
        else:
            valve_cold = True 
            valveColdAct(True)

    def act_valve_normal(self):
        global valve_normal
        if (valve_normal):
            valve_normal = False 
            valveNormalAct(False)
        else:
            valve_normal = True 
            valveNormalAct(True)

    def act_pump_main(self):
        global pump_main

        if (pump_main):
            pumpMainAct(True)
            pump_main = False
        else:
            pumpMainAct(False)
            pump_main = True

    def act_pump_cold(self):
        global pump_cold

        if (pump_cold):
            pumpColdAct(True)
            pump_cold = False
        else:
            pumpColdAct(False)
            pump_cold = True

    def act_pump_normal(self):
        global pump_normal

        if (pump_normal):
            pumpNormalAct(True)
            pump_normal = False
        else:
            pumpNormalAct(False)
            pump_normal = True

    def act_open(self):
        global stepper_open_close, in_limit_opened

        # stepper_open_close is boolean, if stepper_open_close on it can change GPIO condition to move open or close
        # if (stepper_open_close):
        #     stepperAct('open')
        #     stepper_open_close = False
        # else:
        #     stepperAct('close')
        #     stepper_open_close = True
        # if not lsOpen
        try:
            if (not in_limit_opened) :
                stepperAct('open')
                stepper_open_close = False
        except:
            toast("error")



    def act_close(self):
        global stepper_open_close, in_limit_closed

        # stepper_open_close is boolean, if stepper_open_close on it can change GPIO condition to move open or close
        # if (stepper_open_close):
        #     stepperAct('open')
        #     stepper_open_close = False
        # else:
        #     stepperAct('close')
        #     stepper_open_close = True

        try:
            if (not in_limit_closed) :
                stepperAct('close')
                stepper_open_close = True
        except:
            toast("error")

    def act_up(self):
        global linear_motor

        linearMotorAct('up')

        # linear_motor is boolean, if linear motor on it can change GPIO condition to move up or down
        # if (linear_motor):
        #     pass

    def act_down(self):
        global linear_motor

        linearMotorAct('down')

        # if (linear_motor):
        #     pass

    def exit(self):
        self.screen_manager.current = 'screen_choose_product'

    def regular_check(self, *args):
        global levelColdTank, levelMainTank, levelNormalTank

        self.ids.lb_level_main.text = str(levelMainTank)
        self.ids.lb_level_cold.text = str(levelColdTank)
        self.ids.lb_level_normal.text = str(levelNormalTank)

        if (not DEBUG):
            levelMainTank = mainTank.read_register(5,0,3,False)
            levelColdTank = coldTank.read_register(5,0,3,False)
            levelNormalTank = normalTank.read_register(5,0,3,False)

            levelCheck(
                levelColdTank=levelColdTank,
                levelNormalTank=levelNormalTank,
                levelMainTank= levelNormalTank
            )

        # program for displaying IO condition        
        if (valve_cold):
            self.ids.bt_valve_cold.md_bg_color = "#3C9999"
        else:
            self.ids.bt_valve_cold.md_bg_color = "#09343C"

        if (valve_normal):
            self.ids.bt_valve_normal.md_bg_color = "#3C9999"
        else:
            self.ids.bt_valve_normal.md_bg_color = "#09343C"

        if (pump_main):
            self.ids.bt_pump_main.md_bg_color = "#3C9999"
        else:
            self.ids.bt_pump_main.md_bg_color = "#09343C"

        if (pump_cold):
            self.ids.bt_pump_cold.md_bg_color = "#3C9999"
        else:
            self.ids.bt_pump_cold.md_bg_color = "#09343C"

        if (pump_normal):
            self.ids.bt_pump_normal.md_bg_color = "#3C9999"
        else:
            self.ids.bt_pump_normal.md_bg_color = "#09343C"

        if (stepper_open_close):
            self.ids.bt_open.md_bg_color = "#3C9999"
            self.ids.bt_close.md_bg_color = "#3C9999"
        else:
            self.ids.bt_open.md_bg_color = "#09343C"
            self.ids.bt_close.md_bg_color = "#09343C"

class WaterDispenserMachineApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def build(self):
        self.theme_cls.colors = colors
        self.theme_cls.primary_palette = "BlueGray"
        self.theme_cls.accent_palette = "Blue"
        self.icon = 'asset/Icon_Logo.png'
        # Window.fullscreen = 'auto'
        # Window.borderless = True
        Window.size = 1080, 640
        # Window.allow_screensaver = True

        screen = Builder.load_file('main.kv')

        return screen


if __name__ == '__main__':
    WaterDispenserMachineApp().run()