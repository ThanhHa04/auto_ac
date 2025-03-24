import time
import threading
from EmulatorGUI import GPIO
from DHT22 import DHT22
from pnhLCD1602 import LCD1602


def Main():
    try:
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)

        BTN_SELECT = 27
        BTN_UP = 6
        BTN_DOWN = 5
        BTN_BACK = 19
        BTN_OK = 16
        BTN_AC= 7
        BTN_HM = 8
        BTN_AUTOMODE = 12
        RELAY_TEMP = 20
        RELAY_HUMID = 21
        LED_Temp = 23
        LED_Humid = 24
        LED_auto_mode = 18

        GPIO.setup(RELAY_TEMP, GPIO.OUT)
        GPIO.setup(RELAY_HUMID, GPIO.OUT)
        GPIO.setup(LED_Temp, GPIO.OUT)
        GPIO.setup(LED_Humid, GPIO.OUT)
        GPIO.setup(LED_auto_mode, GPIO.OUT)

        GPIO.output(LED_Temp, GPIO.LOW)
        GPIO.output(LED_Humid, GPIO.LOW)
        GPIO.output(LED_auto_mode, GPIO.LOW)
        GPIO.output(RELAY_TEMP, GPIO.LOW)
        GPIO.output(RELAY_HUMID, GPIO.LOW)

        gpioPin = [ BTN_SELECT, BTN_UP, BTN_DOWN, BTN_BACK, BTN_OK, BTN_AUTOMODE,BTN_AC,BTN_HM]
        Choices = ["Nhiệt độ", "Độ ẩm", "Lập Lịch", "Hẹn giờ"]
        ledPin = [LED_Temp, LED_Humid, LED_auto_mode]
        
        lcd = LCD1602()
        dht_sensor = DHT22(pin=4)

        global current_selection, measuring, in_selection_mode, set_temp, set_humid, temperature_on, humidifier_on, auto_mode, timer_time, schedule_time
        current_selection = 0
        measuring = True
        set_temp = 25
        set_humid = 50
        in_selection_mode = False
        temperature_on = False
        humidifier_on = False
        auto_mode = False
        schedule_time = (7, 0, 10, 0)
        timer_time = 30

        for pin in gpioPin:
            GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

        def move_selection():
            global current_selection            
            current_selection = (current_selection + 1) % len(Choices)
            display_current_selection()  

        def start():
            global measuring, auto_mode, temperature_on, humidifier_on, set_temp, set_humid
            while measuring:
                temp, humid = dht_sensor.read()
                if temp is not None and humid is not None:
                    lcd.clear()
                    lcd.write_string(f"T:{str(set_temp) + 'C' if temperature_on else 'OFF'} Env:{temp:.1f}C")
                    lcd.set_cursor(1, 0)
                    lcd.write_string(f"H:{str(set_humid) + '%' if humidifier_on else 'OFF'} Env:{humid:.1f}%")
                    if auto_mode:
                        if temp < 16 or temp > 28:
                            temperature_on = True
                        elif auto_mode and temp == set_temp:
                            temperature_on = False
                        update_leds()

                        if humid < 40 :
                            humidifier_on = True
                        elif auto_mode and humid > set_humid:
                            humidifier_on = False
                        update_leds()

                if GPIO.input(BTN_AUTOMODE) == GPIO.LOW:
                    auto_mode = not auto_mode
                    print(f"Chế độ tự động đang {'BẬT!' if auto_mode else 'TẮT!'}")
                    update_leds()
                    time.sleep(0.1)

                time.sleep(0.2)

        def update_leds():
            GPIO.output(LED_auto_mode, GPIO.HIGH if auto_mode else GPIO.LOW)
            GPIO.output(LED_Temp, GPIO.HIGH if temperature_on else GPIO.LOW)
            GPIO.output(LED_Humid, GPIO.HIGH if humidifier_on else GPIO.LOW)
        
        def adjust_temperature():
            global set_temp, temperature_on
            lcd.clear()
            lcd.write_string(f"TEMP: {'ON' if temperature_on else 'OFF'}")
            lcd.set_cursor(1, 0)
            lcd.write_string(f"T: {set_temp}C")

            while in_selection_mode:
                if GPIO.input(BTN_UP) == GPIO.LOW:
                    time.sleep(0.1)
                    set_temp += 1
                    lcd.clear()
                    lcd.write_string(f"TEMP: {'ON' if temperature_on else 'OFF'}")
                    lcd.set_cursor(1, 0)
                    lcd.write_string(f"T: {set_temp}C")

                if GPIO.input(BTN_DOWN) == GPIO.LOW:
                    time.sleep(0.1)
                    set_temp -= 1
                    lcd.clear()
                    lcd.write_string(f"TEMP: {'ON' if temperature_on else 'OFF'}")
                    lcd.set_cursor(1, 0)
                    lcd.write_string(f"T: {set_temp}C")

                if GPIO.input(BTN_AC) == GPIO.LOW:
                    temperature_on = not temperature_on
                    update_leds()
                    time.sleep(0.1)
                    print("Máy lạnh đang bật!" if temperature_on else "Máy lạnh đang tắt!")
                    lcd.clear()
                    lcd.write_string(f"TEMP: {'ON' if temperature_on else 'OFF'}")
                    lcd.set_cursor(1, 0)
                    lcd.write_string(f"T: {set_temp}C")

                if GPIO.input(BTN_BACK) == GPIO.LOW:
                    time.sleep(0.1)
                    back_to_start()
                    return

        def adjust_humidity():
            global set_humid, humidifier_on
            lcd.clear()
            lcd.write_string(f"HUMID: {'ON' if humidifier_on else 'OFF'}")
            lcd.set_cursor(1, 0)
            lcd.write_string(f"H: {set_humid}%")

            while in_selection_mode:
                if GPIO.input(BTN_UP) == GPIO.LOW:
                    time.sleep(0.1)
                    set_humid += 5
                    lcd.clear()
                    lcd.write_string(f"HUMID: {'ON' if humidifier_on else 'OFF'}")
                    lcd.set_cursor(1, 0)
                    lcd.write_string(f"H: {set_humid}%")

                if GPIO.input(BTN_DOWN) == GPIO.LOW:
                    time.sleep(0.1)
                    set_humid -= 5
                    lcd.clear()
                    lcd.write_string(f"HUMID: {'ON' if humidifier_on else 'OFF'}")
                    lcd.set_cursor(1, 0)
                    lcd.write_string(f"H: {set_humid}%")

                if GPIO.input(BUTTON_HM) == GPIO.LOW:
                    humidifier_on = not humidifier_on
                    update_leds()
                    time.sleep(0.1)
                    print("Máy phun sương đang bật!" if humidifier_on else "Máy phun sương đang tắt!")
                    lcd.clear()
                    lcd.write_string(f"HUMID: {'ON' if humidifier_on else 'OFF'}")
                    lcd.set_cursor(1, 0)
                    lcd.write_string(f"H: {set_humid}%")

                if GPIO.input(BTN_BACK) == GPIO.LOW:
                    time.sleep(0.1)
                    back_to_start()
                    return

        def set_schedule_time(lcd):
            global schedule_time, auto_mode  
            is_start_time = True 
            lcd.clear()
            lcd.set_cursor(0, 0)
            lcd.write_string(f"Bắt đầu: {schedule_time[0]}:{schedule_time[1]:02d}")
            lcd.set_cursor(1, 0)
            lcd.write_string(f"Kết thúc: {schedule_time[2]}:{schedule_time[3]:02d}")

            while in_selection_mode:
                if GPIO.input(BTN_UP) == GPIO.LOW: 
                    time.sleep(0.1)
                    if is_start_time:  
                        schedule_time = (schedule_time[0], schedule_time[1] + 30, schedule_time[2], schedule_time[3])
                        if schedule_time[1] >= 60:  
                            schedule_time = (schedule_time[0] + 1, 0, schedule_time[2], schedule_time[3])
                    else: 
                        schedule_time = (schedule_time[0], schedule_time[1], schedule_time[2], schedule_time[3] + 30)
                        if schedule_time[3] >= 60: 
                            schedule_time = (schedule_time[0], schedule_time[1], schedule_time[2] + 1, 0)
                
                    lcd.clear()
                    lcd.set_cursor(0, 0)
                    lcd.write_string(f"Bắt đầu: {schedule_time[0]}:{schedule_time[1]:02d}")
                    lcd.set_cursor(1, 0)
                    lcd.write_string(f"Kết thúc: {schedule_time[2]}:{schedule_time[3]:02d}")

                if GPIO.input(BTN_DOWN) == GPIO.LOW:  # Giảm thời gian
                    time.sleep(0.1)
                    if is_start_time:  
                        schedule_time = (schedule_time[0], schedule_time[1] - 30, schedule_time[2], schedule_time[3])
                        if schedule_time[1] < 0:  
                            schedule_time = (schedule_time[0] - 1, 30, schedule_time[2], schedule_time[3])
                    else:  
                        schedule_time = (schedule_time[0], schedule_time[1], schedule_time[2], schedule_time[3] - 30)
                        if schedule_time[3] < 0: 
                            schedule_time = (schedule_time[0], schedule_time[1], schedule_time[2] - 1, 30)
                    
                    lcd.clear()
                    lcd.set_cursor(0, 0)
                    lcd.write_string(f"Bắt đầu: {schedule_time[0]}:{schedule_time[1]:02d}")
                    lcd.set_cursor(1, 0)
                    lcd.write_string(f"Kết thúc: {schedule_time[2]}:{schedule_time[3]:02d}")

                if GPIO.input(BTN_AUTOMODE) == GPIO.LOW:  
                    time.sleep(0.1)
                    if auto_mode:
                        auto_mode == False
                    lcd.clear()
                    if is_start_time:
                        lcd.write_string(f"Bắt đầu: {schedule_time[0]}:{schedule_time[1]:02d}")
                    else:
                        lcd.write_string(f"Kết thúc: {schedule_time[2]}:{schedule_time[3]:02d}")

                if GPIO.input(BTN_BACK) == GPIO.LOW: 
                    start_hour = schedule_time[0]
                    start_minute = schedule_time[1]
                    end_hour = schedule_time[2]
                    end_minute = schedule_time[3]
                    print(f"Điều hòa sẽ bật lúc {start_hour} giờ {start_minute} phút")
                    print(f"Điều hòa sẽ tắt lúc {end_hour} giờ {end_minute} phút")
                    if auto_mode:
                        auto_mode = False
                    time.sleep(0.1)
                    back_to_start()
                    return

        def set_timer_time(lcd):
            global timer_time, auto_mode  
            hours = timer_time // 60 
            minutes = timer_time % 60 
            lcd.write_string(f"Hẹn giờ: {hours}h {minutes}p")

            while in_selection_mode:
                if GPIO.input(BTN_UP) == GPIO.LOW:  
                    time.sleep(0.1)
                    timer_time += 30 
                    hours = timer_time // 60  
                    minutes = timer_time % 60  
                    lcd.clear()
                    lcd.write_string(f"Hẹn giờ: {hours}h {minutes}p")

                if GPIO.input(BTN_DOWN) == GPIO.LOW:  
                    time.sleep(0.1)
                    if timer_time > 30: 
                        timer_time -= 30
                        hours = timer_time // 60 
                        minutes = timer_time % 60  
                        lcd.clear()
                        lcd.write_string(f"Hẹn giờ: {hours}h {minutes}p")
                    else:
                        lcd.clear()
                        lcd.write_string(f"Hẹn giờ: 0h 0p") 

                if GPIO.input(BTN_BACK) == GPIO.LOW:  
                    print(f"Điều hòa sẽ tắt trong {hours} giờ {minutes} phút")
                    if auto_mode:
                        auto_mode = False
                    time.sleep(0.1)
                    back_to_start()
                    return

        def display_current_selection():
            lcd.clear()
            lcd.set_cursor(0, 0)
            lcd.write_string("Chọn thiết lập:")
            lcd.set_cursor(1, 0)
            lcd.write_string(f"> {Choices[current_selection]}")

        def confirm_selection(lcd):
            global in_selection_mode, temperature_on, humidifier_on, measuring, set_temp, set_humid  
            lcd.clear()

            if current_selection == 0:
                adjust_temperature() 

            elif current_selection == 1:
                adjust_humidity() 
            
            elif current_selection == 2: 
                set_schedule_time(lcd)

            elif current_selection == 3: 
                set_timer_time(lcd)
            
            time.sleep(2)

        def back_to_start():
            global in_selection_mode, measuring
            in_selection_mode = False
            measuring = True
            update_leds()
            threading.Thread(target=start, daemon=True).start()
            
        # Chạy đo nhiệt độ ngay khi khởi động
        measure_thread = threading.Thread(target=start, daemon=True)
        measure_thread.start()

        while True:
            if GPIO.input(BTN_SELECT) == GPIO.LOW: 
                time.sleep(0.1)
                if GPIO.input(BTN_SELECT) == GPIO.LOW:
                    in_selection_mode = True
                    measuring = False  
                    display_current_selection()
                    time.sleep(0.3) 

            if in_selection_mode and GPIO.input(BTN_UP) == GPIO.LOW:  
                time.sleep(0.1)
                if GPIO.input(BTN_UP) == GPIO.LOW:
                    move_selection()
                    time.sleep(0.3)

            if in_selection_mode and GPIO.input(BTN_OK) == GPIO.LOW:  
                time.sleep(0.1)
                if GPIO.input(BTN_OK) == GPIO.LOW:
                    confirm_selection(lcd) 
                    time.sleep(0.3)

            if in_selection_mode and GPIO.input(BTN_BACK) == GPIO.LOW:  
                time.sleep(0.1)
                if GPIO.input(BTN_BACK) == GPIO.LOW:
                    back_to_start() 
                    time.sleep(0.1)  

            if not auto_mode and GPIO.input(BTN_AC) == GPIO.LOW:
                time.sleep(0.1)
                if GPIO.input(BTN_AC) == GPIO.LOW:
                    temperature_on = not temperature_on
                    GPIO.output(RELAY_TEMP, GPIO.HIGH if temperature_on else GPIO.LOW)
                    GPIO.output(LED_Temp, GPIO.HIGH if temperature_on else GPIO.LOW)
                    print("Điều hòa:", "BẬT" if temperature_on else "TẮT")
                    time.sleep(0.3)

            if not auto_mode and GPIO.input(BTN_HM) == GPIO.LOW:
                time.sleep(0.1)
                if GPIO.input(BTN_HM) == GPIO.LOW:
                    humidifier_on = not humidifier_on
                    GPIO.output(RELAY_HUMID, GPIO.HIGH if humidifier_on else GPIO.LOW)
                    GPIO.output(LED_Humid, GPIO.HIGH if humidifier_on else GPIO.LOW)
                    print("Phun sương:", "BẬT" if humidifier_on else "TẮT")
                    time.sleep(0.3)

            time.sleep(0.05)

    except KeyboardInterrupt:
        GPIO.cleanup()
        print("Chương trình kết thúc.")

if __name__ == "__main__":
    Main()