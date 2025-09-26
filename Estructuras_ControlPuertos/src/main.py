from machine import Pin, I2C
from ssd1306 import SSD1306_I2C
import time

system_configuration = {
    'temperatura_limite': 25.0,
    'modo_operacion': 'automatico',
    'alarma_sonora': True,
    'tiempo_ciclo': 3000,
    'dispositivos': {
        'led_rojo': { 'pin': 2, 'estado': False},
        'led_verde': { 'pin': 4, 'estado': False},
        'buzzer': { 'pin': 5, 'estado': False}
    },
    'sensores': {
        'temperatura': {'pin': 15, 'calibracion': 0.0}
    }
}

def configure_system(system_configuration):
    devices = {}

    periphericals = {
        'leds': {},
        'buzzers': {},
        'sensors': {}
    }

    type_periphericals = {
        'led': 'leds',
        'buzzer': 'buzzers',
        'sensores': 'sensors'
    }

    devices.update(system_configuration['dispositivos'])
    devices.update(system_configuration['sensores'])

    for name, config in devices.items():
        prefix = name.split('_', 1)[0]
        group = type_periphericals.get(prefix)
        if group:
            periphericals[group][name] = config
        
    return periphericals

def initializate_periphericals(periphericals):
    leds = {}
    for name, config in periphericals['leds'].items():
        led = Pin(config['pin'], Pin.OUT)
        led.value(config['estado'])
        leds[name] = led
    
    i2c = I2C (0, scl=Pin(22), sda=Pin(21), freq=400000)
    
    oled = SSD1306_I2C(128, 64, i2c)

    return oled, leds

def main():
    periphericals = configure_system(system_configuration)
    oled, leds = initializate_periphericals(periphericals)

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
    
