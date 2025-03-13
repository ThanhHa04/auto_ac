import time
import threading
from EmulatorGUI import GPIO
from DHT22 import DHT22
from pnhLCD1602 import LCD1602

def Main():
    try:
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)

        BTN_AUTO = 17
        BTN_SELECT = 27
        BTN_UP = 6
        BTN_DOWN = 5
        BTN_BACK = 19
        BTN_OK = 16
        BTN_ON = 12
        LED_Temp = 23
        LED_Humid = 24
        LED_auto_mode = 18

        GPIO.setup(LED_Temp, GPIO.OUT)
        GPIO.setup(LED_Humid, GPIO.OUT)
        GPIO.setup(LED_auto_mode, GPIO.OUT)
        GPIO.output(LED_Temp, GPIO.LOW)
        GPIO.output(LED_Humid, GPIO.LOW)
        GPIO.output(LED_auto_mode, GPIO.LOW)

        gpioPin = [BTN_AUTO, BTN_SELECT, BTN_UP, BTN_DOWN, BTN_BACK, BTN_OK, BTN_ON]
        Choices = ["Nhiệt độ", "Độ ẩm"]
        ledPin = [LED_Temp, LED_Humid, LED_auto_mode]
        
        lcd = LCD1602()
        dht_sensor = DHT22(pin=4)

        global current_selection, measuring, in_selection_mode, set_temp, set_humid, temperature_on, humidifier_on
        current_selection = 0
        measuring = True
        set_temp = 25
        set_humid = 50
        in_selection_mode = False
        temperature_on = False
        humidifier_on = False

        for pin in gpioPin:
            GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

        def move_selection():
            """Chuyển lựa chọn giữa Nhiệt độ và Độ ẩm khi nhấn nút."""
            global current_selection            
            current_selection = (current_selection + 1) % len(Choices)
            display_current_selection()  

        def start_measure():
            """Đo nhiệt độ, độ ẩm và hiển thị trên LCD."""
            global measuring
            while measuring:
                temp, humid = dht_sensor.read()
                if temp is not None and humid is not None:
                    lcd.clear()
                    lcd.write_string(f"Temp:{'ON' if temperature_on else 'OFF'} T:{temp:.1f}C")
                    lcd.set_cursor(1, 0)
                    lcd.write_string(f"Humid:{'ON' if humidifier_on else 'OFF'} H:{humid:.1f}%")
                update_leds()
                time.sleep(2)

        def update_leds():
            """Cập nhật trạng thái đèn LED"""
            GPIO.output(LED_auto_mode, GPIO.HIGH if measuring else GPIO.LOW)
            GPIO.output(LED_Temp, GPIO.HIGH if temperature_on else GPIO.LOW)
            GPIO.output(LED_Humid, GPIO.HIGH if humidifier_on else GPIO.LOW)

        def display_current_selection():
            """Hiển thị chế độ lựa chọn hiện tại."""
            lcd.clear()
            lcd.set_cursor(0, 0)
            lcd.write_string("CHON THIET LAP:")
            lcd.set_cursor(1, 0)
            lcd.write_string(f"> {Choices[current_selection]}")

        def confirm_selection(lcd):
            global in_selection_mode, temperature_on, humidifier_on, measuring, set_temp, set_humid  
            lcd.clear()

            if current_selection == 0:
                update_leds()
                lcd.write_string(f"TEMP: {'ON' if temperature_on else 'OFF'}")
                lcd.set_cursor(1, 0)
                lcd.write_string(f"T: {set_temp}C")
                
                # Điều chỉnh nhiệt độ 
                while in_selection_mode:
                    if GPIO.input(BTN_UP) == GPIO.LOW:
                        time.sleep(0.1)
                        set_temp += 1
                        lcd.clear()
                        lcd.write_string(f"TEMP:{'ON' if temperature_on else 'OFF'}")
                        lcd.set_cursor(1, 0)
                        lcd.write_string(f"T: {set_temp}C")

                    if GPIO.input(BTN_DOWN) == GPIO.LOW:
                        time.sleep(0.1)
                        set_temp -= 1
                        lcd.clear()
                        lcd.write_string(f"TEMP:{'ON' if temperature_on else 'OFF'}")
                        lcd.set_cursor(1, 0)
                        lcd.write_string(f"T: {set_temp}C")

                    if GPIO.input(BTN_ON) == GPIO.LOW:
                        temperature_on = not temperature_on 
                        time.sleep(0.1)
                        lcd.clear()
                        lcd.write_string(f"TEMP:{'ON' if temperature_on else 'OFF'}")
                        lcd.set_cursor(1, 0)
                        lcd.write_string(f"T: {set_temp}C") 

                    if GPIO.input(BTN_BACK) == GPIO.LOW: 
                        time.sleep(0.1)
                        back_to_measure()
                        return

            elif current_selection == 1:  # Chọn "Độ ẩm"  
                update_leds()
                lcd.write_string(f"HUMID: {'ON' if humidifier_on else 'OFF'}")
                lcd.set_cursor(1, 0)
                lcd.write_string(f"H: {set_humid}%")

                # Điều chỉnh độ ẩm
                while in_selection_mode:
                    if GPIO.input(BTN_UP) == GPIO.LOW:
                        time.sleep(0.1)
                        set_humid += 5
                        lcd.clear()
                        lcd.write_string(f"HUM:{'ON' if humidifier_on else 'OFF'}")
                        lcd.set_cursor(1, 0)
                        lcd.write_string(f"H: {set_humid}%")

                    if GPIO.input(BTN_DOWN) == GPIO.LOW:
                        time.sleep(0.1)
                        set_humid -= 5
                        lcd.clear()
                        lcd.write_string(f"HUM:{'ON' if humidifier_on else 'OFF'}")
                        lcd.set_cursor(1, 0)
                        lcd.write_string(f"H: {set_humid}%")

                    if GPIO.input(BTN_ON) == GPIO.LOW:
                        humidifier_on = not humidifier_on
                        time.sleep(0.1)
                        lcd.clear()
                        lcd.write_string(f"HUM:{'ON' if humidifier_on else 'OFF'}")
                        lcd.set_cursor(1, 0)
                        lcd.write_string(f"H: {set_humid}%")

                    if GPIO.input(BTN_BACK) == GPIO.LOW: 
                        time.sleep(0.1)
                        back_to_measure()
                        return

            time.sleep(2)

        def back_to_measure():
            """Nhấn BACK để thoát chế độ chọn và quay lại đo lường"""
            global in_selection_mode, measuring
            in_selection_mode = False
            measuring = True
            update_leds()
            threading.Thread(target=start_measure, daemon=True).start()

        # Chạy đo nhiệt độ ngay khi khởi động
        measure_thread = threading.Thread(target=start_measure, daemon=True)
        measure_thread.start()

        while True:
            if GPIO.input(BTN_SELECT) == GPIO.LOW:  # Nhấn chọn
                time.sleep(0.1)
                if GPIO.input(BTN_SELECT) == GPIO.LOW:
                    in_selection_mode = True
                    measuring = False  # Dừng đo khi vào chọn thiết lập
                    display_current_selection()
                    time.sleep(0.3)  # Thời gian chờ để tránh nhấn quá nhanh

            if in_selection_mode and GPIO.input(BTN_UP) == GPIO.LOW:  # Chuyển lựa chọn
                time.sleep(0.1)
                if GPIO.input(BTN_UP) == GPIO.LOW:
                    move_selection()
                    time.sleep(0.3)

            if in_selection_mode and GPIO.input(BTN_OK) == GPIO.LOW:  # Xác nhận
                time.sleep(0.1)
                if GPIO.input(BTN_OK) == GPIO.LOW:
                    confirm_selection(lcd)  # Truyền lcd vào đây
                    time.sleep(0.3)

            if in_selection_mode and GPIO.input(BTN_BACK) == GPIO.LOW:  # Nhấn BACK để thoát
                time.sleep(0.1)
                if GPIO.input(BTN_BACK) == GPIO.LOW:
                    back_to_measure()  # Quay lại chế độ đo
                    time.sleep(0.3)  # Thời gian chờ sau khi thoát

            time.sleep(0.05)  # Thêm thời gian nhỏ để vòng lặp hoạt động mượt mà hơn

    except KeyboardInterrupt:
        GPIO.cleanup()
        print("Chương trình kết thúc.")

if __name__ == "__main__":
    Main()
