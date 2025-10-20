import tkinter as tk
import requests
from datetime import datetime
import json
import os

API_KEY = "3cddf97d69024b8587578689b3ab2812"
TYPE = "json"

# config.json 불러오기
CONFIG_PATH = "widgets/config.json"
if not os.path.exists(CONFIG_PATH):
    raise FileNotFoundError("config.json이 존재하지 않습니다. 먼저 학교 설정을 완료하세요.")

with open(CONFIG_PATH, "r", encoding="utf-8") as f:
    config = json.load(f)

SCHOOL_CODE = config["school_code"]

today = datetime.today().strftime("%Y%m%d")

url = (
    f"https://open.neis.go.kr/hub/mealServiceDietInfo?"
    f"KEY={API_KEY}&Type={TYPE}"
    f"&ATPT_OFCDC_SC_CODE=B10"
    f"&SD_SCHUL_CODE={SCHOOL_CODE}"
    f"&MLSV_YMD={today}"
)

response = requests.get(url)
data = response.json()

meal_list = []
if "mealServiceDietInfo" in data:
    meal_rows = data["mealServiceDietInfo"][1]["row"]
    for item in meal_rows:
        dishes = item.get("DDISH_NM", "").replace("<br/>", "\n")
        meal_list.append({
            "name": item.get('MMEAL_SC_NM'),
            "dishes": dishes
        })

# ------------------ Tkinter 창 ------------------
root = tk.Tk()
root.title("오늘 급식")
root.geometry("1200x500")  # 세로도 조금 늘림
root.configure(bg="#1E2144")
root.resizable(False, False)

canvas = tk.Canvas(root, width=1200, height=500, bg="#1E2144", highlightthickness=0)
canvas.pack()

canvas_width = 1200
title_y = 30
start_y = 100  # 제목과 첫 끼 사이 간격 넉넉히
meal_width = canvas_width // 3  # 3끼를 균등 배치

# 제목
canvas.create_text(
    canvas_width / 2,
    title_y,
    text="오늘 급식",
    fill="white",
    font=("Pretendard SemiBold", 26),
    anchor="n"
)

# 3끼 표시
if meal_list:
    for i, meal in enumerate(meal_list):
        x_pos = meal_width * i + meal_width // 2
        canvas.create_text(
            x_pos,
            start_y,
            text=meal["name"],
            fill="#FFD700",
            font=("Pretendard SemiBold", 22),
            anchor="n"
        )
        canvas.create_text(
            x_pos,
            start_y + 50,  # 끼니 이름과 메뉴 사이 간격
            text=meal["dishes"],
            fill="white",
            font=("Pretendard SemiBold", 16),
            anchor="n",
            justify="center"
        )
else:
    canvas.create_text(
        canvas_width / 2,
        start_y,
        text="오늘 급식이 없어요",
        fill="white",
        font=("Pretendard SemiBold", 18),
        anchor="n"
    )

root.mainloop()
