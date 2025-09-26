from machine import Pin, I2C
from ssd1306 import SSD1306_I2C
import time

system_configuration = {
    'dispositivos': {
        'led_rojo': { 'pin': 2, 'estado': False},
        'led_verde': { 'pin': 4, 'estado': False}
    }
}

def configure_system(system_configuration):
    leds = {}
    devices= system_configuration['dispositivos']
    
    for name, config in devices.items():
        led = Pin(config['pin'], Pin.OUT)
        led.value(config['estado'])
        leds[name] = led
    
    i2c = I2C (0, scl=Pin(22), sda=Pin(21), freq=400000)
    
    oled = SSD1306_I2C(128, 64, i2c)

    return oled, leds

def main():
    oled, leds = configure_system(system_configuration)
    while True:
        oled.fill(0)
        oled.text("Hello ESP32!", 0, 0)
        oled.text("OLED working!", 0, 54)
        oled.show()
        for led in leds.values():
            led.value(1)
            time.sleep_ms(100)
            led.value(0)
            time.sleep_ms(100)

        
if __name__ == "__main__":
    main()
    
