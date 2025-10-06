from machine import Pin
import time

def configure_system():
#-----Configuración de los leds-----
    red_led = Pin(2, Pin.OUT)
    yellow_led = Pin(4, Pin.OUT)
    green_led = Pin(5, Pin.OUT)
    leds = [red_led, yellow_led, green_led]
#------Configuración de los botones-----
    emergency_button = Pin(18, Pin.IN, Pin.PULL_UP)
    reset_button = Pin(19, Pin.IN, Pin.PULL_UP)
    
    modes = ["normal_mode", "emergency_mode"]
    
    return leds, emergency_button, reset_button, modes


def normal_cycle(leds, state, start):
    turnOff_leds(leds)
    states = [
        (leds[0], 2000),
        (leds[1], 2000),
        (leds[2], 2000)
    ]
    
    turnOff_leds(leds)
    
    led, duration = states[state]
    led.value(1)
    
    now = time.ticks_ms()
    
    if time.ticks_diff(time.ticks_ms(), start) > duration:
        state = (state + 1) % len(states)
        start = time.ticks_ms()
        
    return state, start


def emergency_mode(leds, state, start):
    turnOff_leds(leds)
    
    red = leds[0]
    states = [
        (red, 500, 1),  # encendido
        (red, 500, 0)   # apagado
    ]

    led, duration, value = states[state]
    led.value(value)

    now = time.ticks_ms()
    if time.ticks_diff(now, start) > duration:
        state = (state + 1) % len(states)
        start = now

    return state, start


def turnOff_leds(leds):
 for led in leds:
  led.value(0)
  
  
def read_button(button):
    current_button_value = button.value()
    
    return current_button_value


def main():
    leds, reset_button, emergency_button, modes = configure_system()
    current_mode = 0
    estado_anterior_boton = 1
    
    start = time.ticks_ms()
    emergency_state = 0
    trafficLight_status = 0
    print("El modo actual es ", modes[current_mode])
    
    while True:
        time.sleep_ms(200) # Anti-rebote (debounce)
        
        if estado_anterior_boton == 1 and read_button(emergency_button) == 0:
            current_mode = 0
            print("El modo actual es ", modes[current_mode])
            
        elif estado_anterior_boton ==1 and read_button(reset_button) == 0:
            current_mode = 1
            print("El modo actual es ", modes[current_mode])
        
        if current_mode == 0:
            trafficLight_status, start = normal_cycle(leds, trafficLight_status, start)
        elif current_mode == 1:
            emergency_state, start = emergency_mode(leds, emergency_state, start)
        

if __name__ == "__main__":
    main()