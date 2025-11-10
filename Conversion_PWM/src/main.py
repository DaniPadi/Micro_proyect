# ============================================================
# UNIVERSIDAD POPULAR DEL CESAR
# PROGRAMA DE INGENIERÍA ELECTRÓNICA
# ASIGNATURA: MICROCONTROLADORES
# PRODUCTO DE APRENDIZAJE:
# Sistema de Monitoreo Analógico con Control PWM y PID
# ============================================================

from machine import ADC, PWM, Pin
import time

# ============================================================
# CONFIGURACIÓN DE ENTRADAS ANALÓGICAS (ADC)
# ============================================================

# Sensor de humedad del suelo (GPIO36)
adc_humedad = ADC(Pin(33))
adc_humedad.atten(ADC.ATTN_11DB)  # Rango 0 - 3.3V

# Sensor de gas MQ-2 (GPIO39)
adc_gas = ADC(Pin(32))
adc_gas.atten(ADC.ATTN_11DB)

# (Opcional) Potenciómetro de referencia (GPIO34)
# adc_ref = ADC(Pin(34))
# adc_ref.atten(ADC.ATTN_11DB)

# ============================================================
# CONFIGURACIÓN DE SALIDAS PWM (ACTUADORES)
# ============================================================

# Ventilador DC (GPIO23)
pwm_ventilador = PWM(Pin(23), freq=1000, duty=0)

# Servomotor (GPIO22)
pwm_servo = PWM(Pin(22), freq=50, duty=77)   # 1.5ms = posición neutra

# LED indicador (GPIO21)
pwm_led = PWM(Pin(21), freq=5000, duty=0)

# (Opcional) Elemento calefactor (GPIO25)
# pwm_calefactor = PWM(Pin(25), freq=1000, duty=0)


# ============================================================
# CLASE PRINCIPAL: CONTROLADOR ANALÓGICO
# ============================================================

class ControladorAnalogico:
    def __init__(self):
        # Punto de consigna (Set Point)
        self.set_point_humedad = 50.0  # Humedad objetivo (%)

        # Variables PID
        self.error_anterior = 0.0
        self.integral = 0.0

        # Constantes PID (ajustables)
        self.kp = 2.0
        self.ki = 0.1
        self.kd = 0.5

    # ------------------------------------------------------------
    def leer_sensores(self):
        """Lectura y conversión de los sensores analógicos"""
        lectura_hum = adc_humedad.read()
        humedad = (lectura_hum / 4095) * 100   # Escala a porcentaje

        lectura_gas = adc_gas.read()
        gas_ppm = (lectura_gas / 4095) * 1000  # Escala a ppm aproximado

        return humedad, gas_ppm

    # ------------------------------------------------------------
    def control_pid_humedad(self, humedad_actual):
        """Control PID para mantener la humedad en el punto objetivo"""
        error = self.set_point_humedad - humedad_actual
        self.integral += error
        derivada = error - self.error_anterior

        salida = (self.kp * error) + (self.ki * self.integral) + (self.kd * derivada)

        # Limitar salida (0% - 100%)
        salida = min(0, max(100, salida))

        # Convertir a duty cycle (0 - 1023)
        duty_ventilador = int((salida / 100) * 1023)
        pwm_ventilador.duty(duty_ventilador)

        # Guardar error actual
        self.error_anterior = error

        return salida

    # ------------------------------------------------------------
    def control_calidad_aire(self, gas_ppm):
        """Control por umbrales de calidad del aire"""
        if gas_ppm > 500:  # Nivel crítico
            pwm_ventilador.duty(1023)
            pwm_servo.duty(128)  # Gira el servo a posición de ventilación máxima
            pwm_led.duty(1023)   # LED máximo (alerta)
        elif gas_ppm > 200:  # Nivel advertencia
            pwm_ventilador.duty(512)
            pwm_led.duty(512)
            pwm_servo.duty(100)
        else:  # Nivel normal
            pwm_led.duty(256)
            pwm_servo.duty(77)  # Posición neutra

# ============================================================
# BUCLE PRINCIPAL (MAIN LOOP)
# ============================================================

control = ControladorAnalogico()

print("=== Sistema de Monitoreo Analógico Iniciado ===")
print("Leyendo sensores y aplicando control PID...\n")

while True:
    humedad, gas_ppm = control.leer_sensores()
    salida_pid = control.control_pid_humedad(humedad)
    control.control_calidad_aire(gas_ppm)

    print("Humedad: {:.2f}% | Gas: {:.2f} ppm | PID salida: {:.2f}%".format(
        humedad, gas_ppm, salida_pid))

    time.sleep(1)
