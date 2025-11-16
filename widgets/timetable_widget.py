import tkinter as tk
from tkinter import messagebox
import requests
import json
import os
from datetime import datetime, timedelta
import threading
import winsound
import time

API_KEY = "3cddf97d69024b8587578689b3ab2812"
CONFIG_PATH = "widgets/config.json"
SEMESTER = 2
TYPE = "json"


def timetable_window():
    if not os.path.exists(CONFIG_PATH):
        messagebox.showwarning("경고", "학교 설정을 먼저 완료하세요")
        from setting import school_settings_window
        school_settings_window()
        return

    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        config = json.load(f)

    edu_code = config.get("edu_office_code")
    school_code = config.get("school_code")
    grade = config.get("grade", 1)
    class_num = config.get("class", 1)

    # 설정에서 이동수업 과목 불러오기
    MOVE_SUBJECTS = config.get("move_subjects", [])

    # 알람 시간 설정 불러오기
    alarm_before_lunch = config.get("alarm_before_lunch", 10)
    alarm_before_class = config.get("alarm_before_class", 5)

    today_date = datetime.today()
    if today_date.weekday() == 5:
        today_date += timedelta(days=2)
    elif today_date.weekday() == 6:
        today_date += timedelta(days=1)

    today = today_date.strftime("%Y%m%d")
    display_date = today_date.strftime("%Y년 %m월 %d일")

    url = f"https://open.neis.go.kr/hub/hisTimetable?KEY={API_KEY}&Type={TYPE}&ATPT_OFCDC_SC_CODE={edu_code}&SD_SCHUL_CODE={school_code}&GRADE={grade}&CLASS_NM={class_num}&SEM={SEMESTER}&ALL_TI_YN=N&TI_FROM_YMD={today}&TI_TO_YMD={today}"

    try:
        data = requests.get(url).json()
    except Exception as e:
        messagebox.showerror("오류", f"시간표 API 요청 실패: {e}")
        return

    time_table = []
    if "hisTimetable" in data:
        try:
            time_table = data["hisTimetable"][1]["row"]
        except (KeyError, IndexError):
            time_table = []

    root = tk.Tk()
    root.title("오늘 시간표")
    root.geometry("750x650")
    root.configure(bg="#1E2144")
    root.resizable(False, False)

    canvas = tk.Canvas(root, width=750, height=650, bg="#1E2144", highlightthickness=0)
    canvas.pack()

    canvas_width = 750
    start_y = 30
    line_height = 35

    canvas.create_text(canvas_width / 2, start_y, text="오늘 시간표", fill="white", font=("Pretendard SemiBold", 22),
                       anchor="n")
    canvas.create_text(canvas_width / 2, start_y + 40, text=display_date, fill="white",
                       font=("Pretendard SemiBold", 18), anchor="n")

    # 이동수업 과목 저장 (알람용)
    move_class_periods = []

    if time_table:
        for idx, lesson in enumerate(time_table):
            period = lesson.get("PERIO", "")
            subject = lesson.get("ITRT_CNTNT", "")

            # 이동수업 체크
            is_move = any(move.replace(" ", "") in subject.replace(" ", "") for move in MOVE_SUBJECTS)

            if is_move:
                move_text = " (이동수업)"
                color = "#FFD700"
                move_class_periods.append(int(period))
            else:
                move_text = ""
                color = "white"

            canvas.create_text(canvas_width / 2, start_y + 150 + idx * line_height,
                               text=f"{period}교시: {subject}{move_text}",
                               fill=color, font=("Pretendard SemiBold", 18), anchor="n")
    else:
        canvas.create_text(canvas_width / 2, start_y + 150, text="오늘 수업이 없어요",
                           fill="white", font=("Pretendard SemiBold", 18), anchor="n")

    CLASS_START_TIMES = {1: "08:30", 2: "09:30", 3: "10:30", 4: "11:30", 5: "13:20", 6: "14:20", 7: "15:20"}
    LUNCH_PERIODS = [1, 5]
    alarm_running = False

    def show_alarm_popup(msg):
        nonlocal alarm_running
        alarm_running = True
        popup = tk.Toplevel()
        popup.title("알람!")
        popup.geometry("350x150")
        popup.configure(bg="#1E2144")
        tk.Label(popup, text=msg, fg="red", bg="#1E2144", font=("Pretendard SemiBold", 14)).pack(pady=20)

        def stop_alarm():
            nonlocal alarm_running
            alarm_running = False
            popup.destroy()

        tk.Button(popup, text="확인", command=stop_alarm, font=("Pretendard SemiBold", 12), bg="#FFD700").pack()

        def beep_sound():
            nonlocal alarm_running
            while alarm_running:
                winsound.Beep(1200, 500)
                time.sleep(0.2)
                winsound.Beep(1000, 500)
                time.sleep(0.2)

        threading.Thread(target=beep_sound, daemon=True).start()

    def check_alarms():
        triggered = set()
        while True:
            now = datetime.now().strftime("%H:%M")
            for period, start in CLASS_START_TIMES.items():
                # 점심시간 전 알람
                if period in LUNCH_PERIODS:
                    alarm_time = (datetime.strptime(start, "%H:%M") - timedelta(minutes=alarm_before_lunch)).strftime(
                        "%H:%M")
                    msg = f"{period}교시 수업시간 {alarm_before_lunch}분 전입니다!"
                # 일반 수업 알람
                else:
                    alarm_time = (datetime.strptime(start, "%H:%M") - timedelta(minutes=alarm_before_class)).strftime(
                        "%H:%M")
                    msg = f"{period}교시 수업시간 {alarm_before_class}분 전입니다!"

                if now == alarm_time and period not in triggered:
                    triggered.add(period)
                    threading.Thread(target=show_alarm_popup, args=(msg,), daemon=True).start()

                # 이동수업 알람 (수업 시작 10분 전)
                if period in move_class_periods:
                    move_alarm_time = (datetime.strptime(start, "%H:%M") - timedelta(minutes=10)).strftime("%H:%M")
                    move_key = f"move_{period}"
                    if now == move_alarm_time and move_key not in triggered:
                        triggered.add(move_key)
                        move_msg = f"🚨 {period}교시 이동수업 10분 전!\n교실 이동 준비하세요!"
                        threading.Thread(target=show_alarm_popup, args=(move_msg,), daemon=True).start()

            time.sleep(30)

    threading.Thread(target=check_alarms, daemon=True).start()
    root.mainloop()


if __name__ == "__main__":
    timetable_window()