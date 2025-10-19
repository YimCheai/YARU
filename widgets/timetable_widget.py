import tkinter as tk
from PIL import Image, ImageTk
import requests
from datetime import datetime

# ------------------ NEIS API 설정 ------------------
API_KEY = "3cddf97d69024b8587578689b3ab2812"
EDU_OFFICE_CODE = "J10"      # 서울git add .
교육청
SCHOOL_CODE = "7530174"      # 미림마이스터고
GRADE = 2
CLASS = 1
TYPE = "json"

today = datetime.today().strftime("%Y%m%d")
url = f"https://open.neis.go.kr/hub/hisTimetable?KEY={API_KEY}&Type={TYPE}&ATPT_OFCDC_SC_CODE={EDU_OFFICE_CODE}&SD_SCHUL_CODE={SCHOOL_CODE}&GRADE={GRADE}&CLASS_NM={CLASS}&ALL_TI_YN=N&TI_FROM_YMD={today}&TI_TO_YMD={today}"

response = requests.get(url)
data = response.json()

# 오늘 시간표 데이터 추출
time_table = []
if "hisTimetable" in data:
    time_table = data.get("hisTimetable", [])
    if time_table:
        time_table = time_table[1]["row"]  # 실제 수업 데이터

# ------------------ Tkinter 창 ------------------
root = tk.Tk()
root.title("오늘 시간표")
root.geometry("400x300")
root.configure(bg="#1E2144")
root.resizable(False, False)

canvas = tk.Canvas(root, width=400, height=300, bg="#1E2144", highlightthickness=0)
canvas.pack()

# ------------------ 오늘 시간표 표시 ------------------
start_x = 20
start_y = 20
line_height = 25

canvas.create_text(start_x, start_y, text="오늘 시간표", fill="white", font=("Pretendard SemiBold", 16), anchor="nw")

if time_table:
    for idx, lesson in enumerate(time_table):
        period = lesson.get("PERIO", "")
        subject = lesson.get("ITRT_CNTNT", "")
        canvas.create_text(start_x, start_y + 30 + idx*line_height, text=f"{period}교시: {subject}", fill="white", font=("Pretendard SemiBold", 14), anchor="nw")
else:
    canvas.create_text(start_x, start_y + 50, text="오늘 수업이 없어요", fill="white", font=("Pretendard SemiBold", 14), anchor="nw")

root.mainloop()
