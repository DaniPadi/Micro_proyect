from machine import Pin, I2C, ADC
from ssd1306 import SSD1306_I2C
import time, random
import onewire, ds18x20


# --- Configuración del sistema ---
system_configuration = {
    'temperatura_limite': 33.0,
    'modo_operacion': 'automatico',
    'alarma_sonora': True,
    'tiempo_ciclo': 1500,
    'dispositivos': {
        'led_rojo': { 'pin': 2, 'estado': False},
        'led_verde': { 'pin': 5, 'estado': False},
        'buzzer': { 'pin': 13, 'estado': False}
    },
    'sensores': {
        'temperatura': {'pin': 15, 'calibracion': 0.0},
        'potenciometro': {'pin': 34}
    }
}

ds_pin = Pin(system_configuration['sensores']['temperatura']['pin'])
ow = onewire.OneWire(ds_pin)
ds = ds18x20.DS18X20(ow)
roms = ds.scan()

# --- Configuración de periféricos ---
def configure_system(system_configuration):
    devices = {}
    periphericals = {'leds': {}, 'buzzers': {}, 'sensors': {}, 'potenciometers':{}}
    type_periphericals = {'led': 'leds', 'buzzer': 'buzzers', 'sensor': 'sensors', 'potenciometro': 'potenciometers'}

    devices.update(system_configuration['dispositivos'])
    devices.update(system_configuration['sensores'])

    for name, config in devices.items():
        prefix = name.split('_', 1)[0]
        group = type_periphericals.get(prefix)
        if group:
            periphericals[group][name] = config
    
    return periphericals

# --- Inicializar periféricos ---
def initializate_periphericals(periphericals):
    leds = {}
    buzzers = {}
    sensors = {}
    peripherical = {}
    for name, config in periphericals['leds'].items():
        led = Pin(config['pin'], Pin.OUT)
        led.value(config['estado'])
        leds[name] = led

    for name, config in periphericals['buzzers'].items():
        buzzer = Pin(config['pin'], Pin.OUT)
        buzzer.value(config['estado'])
        buzzers[name] = buzzer
    
    pot_config = periphericals['potenciometers'].get('potenciometro')
    if pot_config:
        pot = ADC(Pin(pot_config['pin']))
        pot.atten(ADC.ATTN_11DB)
        pot.width(ADC.WIDTH_10BIT)
        sensors['potenciometer'] = pot

    peripherical.update(leds)
    peripherical.update(buzzers)
    peripherical.update(sensors)

    print(peripherical)


    i2c = I2C(0, scl=Pin(22), sda=Pin(21), freq=400000)
    oled = SSD1306_I2C(128, 64, i2c)

    return oled, peripherical

log_events = []

def record_event(kind, description):
    event = {
        'timestamp': time.localtime(),
        'kind': kind,
        'description': description
    }
    log_events.append(event)
    return event 

# --- Mostrar en OLED el último evento ---
def show_status(oled, temp, last_event, mode):
    oled.fill(0)
    oled.text("Sistema Control", 0, 0)
    oled.text("Modo: {}".format(mode[:7]), 0, 12)
    oled.text("Temp: {:.2f} C".format(temp), 0, 28)

    # Mostrar descripción del último evento
    if last_event:
        oled.text(last_event['kind'], 0, 44)
        oled.text(last_event['description'][:16], 0, 56)
    oled.show()

# --- Lectura de temperatura simulada ---
def read_temperature():
    if not roms:
        print("Sensor DS18B20 no detectado")
        return 0.0  # valor de respaldo
    ds.convert_temp()
    time.sleep_ms(750)
    temp = ds.read_temp(roms[0])
    return temp

# --- Programa principal ---
def main():
    periphericals = configure_system(system_configuration)
    oled, HPeriphericals = initializate_periphericals(periphericals)
    last_event = None
    estado_anterior = None

    pot = HPeriphericals['potenciometer']

    while True:
        temp = read_temperature()
        valor_pot = pot.read()
        print(valor_pot)
        if valor_pot < 512:
            system_configuration['modo_operacion'] = "manual"
        else:
            system_configuration['modo_operacion'] = "automatico"

        # Verificar condición y generar evento si hay cambio de estado
        if system_configuration['modo_operacion'] == "automatico":
            if temp > system_configuration['temperatura_limite']:
                HPeriphericals['buzzer'].value(1)
                time.sleep_ms(150)
                HPeriphericals['buzzer'].value(0)
                if estado_anterior != "ALERTA":
                    HPeriphericals['led_rojo'].value(1)
                    HPeriphericals['led_verde'].value(0)
                    last_event = record_event("ALERTA", "Temp alta: {:.1f}C".format(temp))
                    estado_anterior = "ALERTA"
            else:
                if estado_anterior != "NORMAL":
                    HPeriphericals['led_rojo'].value(0)
                    HPeriphericals['led_verde'].value(1)
                    last_event = record_event("OK", "Temp norm: {:.1f}C".format(temp))
                    estado_anterior = "NORMAL"

        # Mostrar estado actual en OLED
        show_status(oled, temp, last_event, system_configuration['modo_operacion'])
        time.sleep_ms(system_configuration["tiempo_ciclo"])

if __name__ == "__main__":
    main()