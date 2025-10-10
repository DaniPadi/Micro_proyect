from machine import Pin, I2C, WDT, ADC
from ssd1306 import SSD1306_I2C
import time

# --- Watchdog Timer ---
wdt = WDT(timeout=5000)  # Reinicia si pasan más de 5s sin alimentarse

# --- Variables globales ---
movement_event = False
emergency_event = False

# --- Inicialización de pantalla OLED ---
i2c = I2C(0, scl=Pin(22), sda=Pin(21))
oled = SSD1306_I2C(128, 64, i2c)

# --- Sensor LDR (luz ambiente) ---
# Conectar así:
# 3.3V --- [LDR] ---◄--- GPIO 35 --- [10kΩ] --- GND
ldr = ADC(Pin(35))              
ldr.atten(ADC.ATTN_11DB)        # Mide hasta 3.3 V
ldr.width(ADC.WIDTH_12BIT)      # Resolución 0–4095

# --- Funciones de interrupción ---
def movement_break(pin):
    global movement_event
    movement_event = True
    print("Movimiento detectado")

def emergency_break(pin):
    global emergency_event
    emergency_event = True
    print("Emergencia activada")

# --- Configuración de sensores ---
sensor_PIR = Pin(12, Pin.IN)
sensor_PIR.irq(trigger=Pin.IRQ_RISING, handler=movement_break)

panic_button = Pin(18, Pin.IN, Pin.PULL_UP)
panic_button.irq(trigger=Pin.IRQ_FALLING, handler=emergency_break)

# --- Función para actualizar la pantalla ---
def update_display(message1, message2=""):
    oled.fill(0)
    oled.text("Sistema Seguridad", 0, 0)
    oled.text("----------------", 0, 10)
    oled.text(message1, 0, 30)
    if message2:
        oled.text(message2, 0, 45)
    oled.show()

# --- Programa principal ---
def main():
    global movement_event, emergency_event

    while True:
        wdt.feed()  # Alimenta el Watchdog

        # Leer el valor de luz ambiente
        luz = ldr.read()
        print("Valor ADC:", luz)  # Para calibración en el monitor serial

        # Clasificar nivel de luz
        # (ajustado para divisor con LDR al positivo y resistencia a GND)
        if luz > 3000:
            estado_luz = "Luz intensa"
        elif luz > 1500:
            estado_luz = "Luz media"
        else:
            estado_luz = "Oscuridad"

        # --- Manejo de eventos ---
        if movement_event:
            print("Ejecutando accion: movimiento")
            update_display("Movimiento detectado", estado_luz)
            movement_event = False
            time.sleep_ms(1500)

        elif emergency_event:
            print("Ejecutando accion: emergencia")
            update_display("!! EMERGENCIA !!", "Boton activado")
            emergency_event = False
            time.sleep_ms(2000)

        else:
            # Si no hay eventos, muestra la luz ambiente
            update_display("Esperando eventos...", estado_luz)

        time.sleep_ms(300)

# --- Inicio del programa ---
if __name__ == "__main__":
    main()
