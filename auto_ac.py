import time
import random
import datetime
import tkinter as tk
from DHT22 import DHT22
from pnhLCD1602 import LCD1602

# Khởi tạo cảm biến và màn hình LCD
sensor = DHT22(pin=4)
lcd = LCD1602()

# Biến điều khiển
auto_mode = False
aircon_on = False
humidifier_on = False
set_temp = 25
set_humidity = 50
schedule_time = None
duration_hours = None 
duration_start = None

def toggle_auto_mode():
    global auto_mode
    auto_mode = not auto_mode
    update_ui()

def toggle_aircon():
    global aircon_on
    aircon_on = not aircon_on
    update_ui()

def toggle_humidifier():
    global humidifier_on
    humidifier_on = not humidifier_on
    update_ui()

def set_temperature(temp):
    global set_temp
    set_temp = temp
    update_ui()

def set_humidity_level(humidity):
    global set_humidity
    set_humidity = humidity
    update_ui()

def set_schedule():
    global schedule_time
    schedule_time = schedule_entry.get()  #
    print(f"🕒 Đã đặt hẹn giờ! Điều hòa sẽ BẬT vào {schedule_time} và chạy trong 2 phút.")
    update_ui()


def set_duration():
    global duration_hours, duration_start
    if aircon_on or humidifier_on:  
        try:
            duration_hours = int(duration_entry.get()) 
            duration_start = datetime.datetime.now()
            print(f"⏳ Đã đặt thời gian chạy {duration_hours} phút. Điều hòa sẽ tự tắt sau {duration_hours} phút.")
            update_ui()
        except ValueError:
            print("⚠️ Lỗi: Hãy nhập số phút hợp lệ!")


def update_display(temp, humidity):
    lcd.clear()
    if aircon_on and humidifier_on:
        lcd.write_string(f"T:{set_temp}C Env:{temp:.1f}C")
        lcd.set_cursor(1, 0)
        lcd.write_string(f"H:{set_humidity}% Env:{humidity:.1f}%")
    elif aircon_on and not humidifier_on:
        lcd.set_cursor(0, 0)
        lcd.write_string(f"T:{set_temp}C Env:{temp:.1f}C")
        lcd.set_cursor(1, 0)
        lcd.write_string(f"H:OFF Env:{humidity:.1f}%")
    elif not aircon_on and humidifier_on :
        lcd.set_cursor(0, 0)
        lcd.write_string(f"T:OFF Env:{temp:.1f}C")
        lcd.set_cursor(1, 0)
        lcd.write_string(f"H:{set_humidity}% Env:{humidity:.1f}%")
    elif not aircon_on and not humidifier_on  :
        lcd.set_cursor(0, 0)
        lcd.write_string(f"T:OFF Env:{temp:.1f}C")
        lcd.set_cursor(1, 0)
        lcd.write_string(f"H:OFF Env:{humidity:.1f}%")

def control_aircon(temp):
    global aircon_on
    if auto_mode:
        if temp > 27 or temp < 18:
            aircon_on = True
        elif temp == set_temp:
            aircon_on = False
        update_ui()

def control_humidifier(humidity):
    global humidifier_on
    if auto_mode:
        if humidity < 40 or humidity > 60:
            humidifier_on = True
        elif humidity == set_humidity:
            humidifier_on = False
        update_ui()

schedule_activated = False 

def check_schedule():
    global aircon_on, humidifier_on, duration_start, schedule_activated
    now = datetime.datetime.now().strftime("%H:%M")

    if schedule_time and now == schedule_time and not aircon_on and not schedule_activated:
        aircon_on = True
        humidifier_on = True
        duration_start = datetime.datetime.now()
        schedule_activated = True  
        print(f"🕒 Hẹn giờ kích hoạt! Điều hòa và máy phun sương đã BẬT vào {now}. Tự động tắt sau 2 phút.")
        update_ui()

    if duration_start:
        elapsed = (datetime.datetime.now() - duration_start).total_seconds() / 60
        if elapsed >= 2:  # Sau 2 phút thì tắt (tiện cho việc test)
            aircon_on = False
            humidifier_on = False
            duration_start = None
            schedule_activated = False 
            print(f"⏳ Đã hết 2 phút! Điều hòa và máy phun sương đã TẮT.")
            update_ui()

def check_duration():
    global aircon_on, humidifier_on, duration_hours, duration_start
    if duration_hours and duration_start:
        elapsed = (datetime.datetime.now() - duration_start).total_seconds() / 60 
        if elapsed >= duration_hours:
            aircon_on = False
            humidifier_on = False
            duration_hours = None
            duration_start = None
            print(f"⏳ Hết thời gian cài đặt! Điều hòa và máy phun sương đã TẮT.")
            update_ui()

def update_ui():
    auto_btn.config(text=f"Auto Mode: {'ON' if auto_mode else 'OFF'}")
    ac_btn.config(text=f"AC: {'ON' if aircon_on else 'OFF'}")
    humidifier_btn.config(text=f"Humidifier: {'ON' if humidifier_on else 'OFF'}")
    temp_label.config(text=f"Nhiệt độ cài đặt: {set_temp}°C")
    humidity_label.config(text=f"Độ ẩm cài đặt: {set_humidity}%")
    schedule_label.config(text=f"Hẹn giờ: {schedule_time if schedule_time else '---'}")
    duration_label.config(text=f"Chạy trong: {duration_hours if duration_hours else '---'} giờ")

def main_loop():
    temp, humidity = random.uniform(15, 30), random.uniform(30, 70)
    update_display(temp, humidity)
    control_aircon(temp)
    control_humidifier(humidity)
    check_schedule()
    check_duration()
    root.after(1000, main_loop)

# Giao diện Tkinter
root = tk.Tk()
root.title("Điều hòa thông minh")

# Auto Mode
auto_btn = tk.Button(root, text="Auto Mode: OFF", command=toggle_auto_mode)
auto_btn.pack()

# Bật/tắt điều hòa
ac_btn = tk.Button(root, text="AC: OFF", command=toggle_aircon)
ac_btn.pack()

# Bật/tắt phun sương
humidifier_btn = tk.Button(root, text="Humidifier: OFF", command=toggle_humidifier)
humidifier_btn.pack()

temp_label = tk.Label(root, text=f"Nhiệt độ cài đặt: {set_temp}°C")
temp_label.pack()

# Tăng/Giảm nhiệt độ
temp_frame = tk.Frame(root)
temp_frame.pack()

temp_up = tk.Button(temp_frame, text="+", command=lambda: set_temperature(set_temp + 1))
temp_up.grid(row=0, column=0)

temp_down = tk.Button(temp_frame, text="-", command=lambda: set_temperature(set_temp - 1))
temp_down.grid(row=0, column=1)

humidity_label = tk.Label(root, text=f"Độ ẩm cài đặt: {set_humidity}%")
humidity_label.pack()

# Tăng/Giảm độ ẩm
humi_frame = tk.Frame(root)
humi_frame.pack()

humi_up = tk.Button(humi_frame, text="+", command=lambda: set_humidity_level(set_humidity + 5))
humi_up.grid(row=0, column=0)
humi_down = tk.Button(humi_frame, text="-", command=lambda: set_humidity_level(set_humidity - 5))
humi_down.grid(row=0, column=1)


# Hẹn giờ bật/tắt
schedule_label = tk.Label(root, text="Hẹn giờ: ---")
schedule_label.pack()
schedule_entry = tk.Entry(root)
schedule_entry.pack()
schedule_btn = tk.Button(root, text="Đặt giờ", command=set_schedule)
schedule_btn.pack()

# Hẹn giờ chạy X giờ
duration_label = tk.Label(root, text="Chạy trong: --- giờ")
duration_label.pack()
duration_entry = tk.Entry(root)
duration_entry.pack()
duration_btn = tk.Button(root, text="Đặt thời gian chạy", command=set_duration)
duration_btn.pack()

# Chạy chương trình
main_loop()
root.mainloop()
