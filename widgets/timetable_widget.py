import tkinter as tk
from PIL import Image, ImageTk
import requests
from datetime import datetime
import json
import os

API_KEY = "3cddf97d69024b8587578689b3ab2812"
TYPE = "json"
SEMESTER = 2

# ------------------ config.json 불러오기 ------------------
CONFIG_PATH = "widgets/config.json"
if not os.path.exists(CONFIG_PATH):
    raise FileNotFoundError("config.json이 존재하지 않습니다. 학교 설정을 먼저 완료하세요.")

with open(CONFIG_PATH, "r", encoding="utf-8") as f:
    config = json.load(f)

EDU_OFFICE_CODE = config.get("edu_office_code", "B10")  # 기본값 서울
SCHOOL_CODE = config.get("school_code")
GRADE = config.get("grade", 1)
CLASS = config.get("class", 1)

today = datetime.today().strftime("%Y%m%d")

# ------------------ NEIS API 요청 ------------------
url = (
    f"https://open.neis.go.kr/hub/hisTimetable?"
    f"KEY={API_KEY}&Type={TYPE}"
    f"&ATPT_OFCDC_SC_CODE={EDU_OFFICE_CODE}"
    f"&SD_SCHUL_CODE={SCHOOL_CODE}"
    f"&GRADE={GRADE}&CLASS_NM={CLASS}"
    f"&SEM={SEMESTER}"
    f"&ALL_TI_YN=N"
    f"&TI_FROM_YMD={today}&TI_TO_YMD={today}"
)

response = requests.get(url)
data = response.json()

time_table = []
if "hisTimetable" in data:
    try:
        time_table = data["hisTimetable"][1]["row"]
    except (KeyError, IndexError):
        time_table = []

# ------------------ 이동수업 과목 ------------------
MOVE_SUBJECTS = [
    "수학Ⅱ",
    "* 네트워크 소프트웨어 개발 방법 수립",
    "* 네트워크 프로그래밍 구현",
    "통합과학",
    "프로그래밍(PYTHON)"
]

# ------------------ Tkinter 창 ------------------
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

# ------------------ 제목 ------------------
canvas.create_text(
    canvas_width / 2,
    start_y,
    text="오늘 시간표",
    fill="white",
    font=("Pretendard SemiBold", 22),
    anchor="n"
)

# ------------------ 시간표 표시 ------------------
if time_table:
    for idx, lesson in enumerate(time_table):
        period = lesson.get("PERIO", "")
        subject = lesson.get("ITRT_CNTNT", "")

        if any(move.replace(" ", "") in subject.replace(" ", "") for move in MOVE_SUBJECTS):
            move_text = " (이동수업)"
            color = "#FFD700"
        else:
            move_text = ""
            color = "white"

        canvas.create_text(
            canvas_width / 2,
            start_y + 70 + idx * line_height,
            text=f"{period}교시: {subject}{move_text}",
            fill=color,
            font=("Pretendard SemiBold", 18),
            anchor="n"
        )
else:
    canvas.create_text(
        canvas_width / 2,
        start_y + 70,
        text="오늘 수업이 없어요",
        fill="white",
        font=("Pretendard SemiBold", 18),
        anchor="n"
    )

root.mainloop()
