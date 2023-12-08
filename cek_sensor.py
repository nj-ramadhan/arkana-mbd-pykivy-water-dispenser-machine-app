from gpiozero import Button
from gpiozero import DigitalInputDevice

in_sensor_proximity_bawah = DigitalInputDevice(25, pull_up=False) #pull_up=false mean pull_down
in_sensor_proximity_atas = DigitalInputDevice(22, pull_up=False)
in_sensor_flow = DigitalInputDevice(19, pull_up=False)
in_machine_ready = DigitalInputDevice(27, pull_up=False)

def proximityBawahDown():
    print("proximity bawah is down")

def proximityBawahUp():
    print("proximity bawah is up")

def proximityAtasDown():
    print("proximity Atas is down")

def proximityAtasUp():
    print("proximity Atas is up")

def flowDown():
    print("flow is down")

def flowUp():
    print("flow is up")


in_sensor_flow.when_activated = flowUp
in_sensor_flow.when_deactivated = flowDown
in_sensor_proximity_bawah.when_activated = proximityBawahUp
in_sensor_proximity_bawah.when_deactivated = proximityBawahDown
in_sensor_proximity_atas.when_activated = proximityAtasUp
in_sensor_proximity_atas.when_deactivated = proximityAtasDown

while True :
    pass