import time
import random
import datetime
from EmulatorGUI import GPIO
from DHT22 import DHT22
from pnhLCD1602 import LCD1602

sensor = DHT22(pin=4)
lcd = LCD1602()

# Khai báo các chân GPIO
BTN_AUTO = 17
BTN_SELECT = 27
BTN_UP = 6
BTN_DOWN = 5
BTN_BACK = 19
LED_Temp = 23
LED_Humid = 24

# Thiết lập GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

GPIO.setup(LED_Temp, GPIO.OUT)
GPIO.output(LED_Temp, GPIO.LOW)
GPIO.setup(LED_Humid, GPIO.OUT)
GPIO.output(LED_Humid, GPIO.LOW)

# Cấu hình nút nhấn
for pin in [BTN_AUTO, BTN_SELECT, BTN_UP, BTN_DOWN, BTN_BACK]:
    GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Biến trạng thái
auto_mode = False
temperature_on = False
humidifier_on = False
set_temp = 25
set_humid = 50
selected_mode = "NONE"

def toggle_auto_mode(channel):
    global auto_mode
    if isinstance(channel, _tkinter.Tcl_Obj):  
        channel = int(channel.get())     
    if not GPIO.input(channel):  # Sửa lỗi ở đây
        auto_mode = not auto_mode
        print(f"Chế độ tự động {'bật' if auto_mode else 'tắt'}.")

selection = "TEMPERATURE"
def toggle_selection(channel):
    global selection
    if isinstance(channel, _tkinter.Tcl_Obj):  
        channel = int(channel.get())
    if not GPIO.input(channel):
        selection = "HUMID" if selection == "TEMPERATURE" else "TEMPERATURE"
        temp, humid = sensor.read()
        update_display(temp, humid)

def adjust_value(channel, increase=True):
    global set_temp, set_humid, selected_mode
    if isinstance(channel, _tkinter.Tcl_Obj):  
        channel = int(channel.get())
    if not GPIO.input(channel):
        if selected_mode == "TEMP":
            set_temp += 1 if increase else -1
            print(f"Set Temperature: {set_temp}°C")
        elif selected_mode == "HUMID":
            set_humid += 5 if increase else -5
            print(f"Set Humid: {set_humid}%")
        temp, humid = sensor.read()
        update_display(temp, humid)

def handle_back(channel):
    global selected_mode
    if isinstance(channel, _tkinter.Tcl_Obj):  
        channel = int(channel.get())
    if not GPIO.input(channel): 
        selected_mode = "NONE"
        print("Returning to main screen")

# Đăng ký sự kiện ngắt
GPIO.add_event_detect(BTN_AUTO, GPIO.FALLING, callback=toggle_auto_mode, bouncetime=300)
GPIO.add_event_detect(BTN_SELECT, GPIO.FALLING, callback=toggle_selection, bouncetime=300)
GPIO.add_event_detect(BTN_UP, GPIO.FALLING, callback=lambda ch: adjust_value(ch, True), bouncetime=200)
GPIO.add_event_detect(BTN_DOWN, GPIO.FALLING, callback=lambda ch: adjust_value(ch, False), bouncetime=200)
GPIO.add_event_detect(BTN_BACK, GPIO.FALLING, callback=handle_back, bouncetime=300)

def update_display(temp, humid):
    global temperature_on, humidifier_on

    if auto_mode and (temp > 28 or temp < 16): 
        temperature_on = True
    elif auto_mode and humid == set_temp:
        temperature_on = False

    if auto_mode and (humid > 60 or humid < 40):
        humidifier_on = True
    elif auto_mode and (humid == set_humid):
        humidifier_on = False

    GPIO.output(LED_Temp, temperature_on)
    GPIO.output(LED_Humid, humidifier_on)

    lcd.clear()
    lcd.write_string(f"Tem:{'ON' if temperature_on else 'OFF'} Env:{temp:.1f}C")
    lcd.set_cursor(1, 0)
    lcd.write_string(f"Hum:{'ON' if humidifier_on else 'OFF'} Env:{humid:.1f}%")

# Vòng lặp chính
def main_loop():
    try:
        while True:
            temp, humid = sensor.read()
            update_display(temp, humid)
            time.sleep(3)
    except KeyboardInterrupt:
        GPIO.cleanup()
        print("Chương trình kết thúc.")

if __name__ == "__main__":
    main_loop()
