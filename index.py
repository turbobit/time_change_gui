import tkinter as tk
import sys
import ctypes
from tkinter import messagebox
import os
import ntplib
from datetime import datetime
import logging

# 로그 설정
logging.basicConfig(filename='log.txt', level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

# NTP 서버에서 현재 시간을 가져오는 함수
def get_ntp_time():
    global last_known_time  # 마지막으로 알려진 시간을 전역 변수로 사용
    try:
        client = ntplib.NTPClient()
        response = client.request('kr.pool.ntp.org', version=3)
        # 응답에서 타임스탬프를 읽고 datetime 형식으로 변환
        current_time = datetime.fromtimestamp(response.tx_time)
        last_known_time = current_time  # 마지막으로 알려진 시간 업데이트
        return current_time
    except Exception as e:
        logging.error(f"NTP 서버에서 시간을 가져오는 중 오류 발생: {e}")
        try:
            os.system('w32tm /resync')  # 윈도우 자동 시간 업데이트 명령어
            current_time = datetime.now()  # 현재 시간을 가져옴
            last_known_time = current_time  # 마지막으로 알려진 시간 업데이트
            return current_time
        except Exception as e:
            logging.error(f"윈도우 시간 동기화 중 오류 발생: {e}")
            return last_known_time  # 마지막으로 알려진 시간 반환

# 시간을 2017년 11월 20일로 변경하는 함수
def change_time():
    global update_current_time
    original_time = get_ntp_time()
    if original_time is None:
        messagebox.showerror("오류", "NTP 서버로부터 시간을 가져올 수 없습니다.")
        return

    try:
        # 2017년 11월 20일로 시간을 변경합니다.
        new_date = "2017-11-20"
        new_time = "12:00:00"
        os.system(f'date {new_date}')
        os.system(f'time {new_time}')
        logging.info("시스템 시간이 2017년 11월 20일 12:00:00로 변경되었습니다.")
        # messagebox.showinfo("성공", "시스템 시간이 2017년 11월 20일로 변경되었습니다.")
        update_current_time()
    except Exception as e:
        logging.error(f"시간 변경 중 오류 발생: {e}")
        messagebox.showerror("오류", "시스템 시간을 변경하는 중 오류가 발생했습니다.")

# 현재 시간을 복원하는 함수
def restore_time():
    global update_current_time
    current_time = get_ntp_time()
    if current_time is None:
        messagebox.showerror("오류", "NTP 서버로부터 현재 시간을 가져올 수 없습니다.")
        return

    try:
        # 현재 시간을 사용자에게 먼저 표시합니다.
        current_time_str = current_time.strftime("%Y-%m-%d %H:%M")
        logging.info(f"현재 시간은: {current_time_str} 입니다.")

        # 현재 시간을 시스템에 설정합니다.
        restore_date = current_time.strftime("%Y-%m-%d")
        restore_time = current_time.strftime("%H:%M:%S")
        os.system(f'date {restore_date}')
        os.system(f'time {restore_time}')
        
        logging.info(f"시스템 시간이 현재 시간으로 복원되었습니다. {current_time_str}")
        # messagebox.showinfo("현재 시간", f"시스템 시간이 현재 시간으로 {current_time_str} 복원되었습니다.")
        update_current_time()
    except Exception as e:
        logging.error(f"시간 복원 중 오류 발생: {e}")
        messagebox.showerror("오류", "시스템 시간을 복원하는 중 오류가 발생했습니다.")

# GUI 생성
def check_admin():
    try:
        is_admin = ctypes.windll.shell32.IsUserAnAdmin()
    except:
        is_admin = False
    if not is_admin:
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, __file__, None, 1)
        sys.exit()

check_admin()

root = tk.Tk()
root.geometry('400x200')

# 현재 시간을 표시하는 레이블
current_time_label = tk.Label(root, text="현재 시간을 불러오는 중...", font=('Helvetica', 12))
current_time_label.pack(pady=10)

def update_current_time():
    system_time = datetime.now()
    system_time_str = system_time.strftime("%Y-%m-%d %H:%M:%S")
    current_time_label.config(text=f"시스템 시간: {system_time_str}")
    # 1분마다 시간 업데이트
    root.after(1000, update_current_time)

# 처음 실행 시 시간 업데이트
update_current_time()
root.geometry('400x200')
root.title("시간 변경 및 원복 프로그램")


restore_button = tk.Button(root, text="인터넷시간으로맞추기", command=restore_time, bg='lightgreen', fg='black', font=('Helvetica', 14, 'bold'), width=25, height=2)
restore_button.pack(pady=15)

change_button = tk.Button(root, text="변경", command=change_time, bg='lightblue', fg='black', font=('Helvetica', 14, 'bold'), width=25, height=1)
change_button.pack(pady=15)

root.mainloop()
