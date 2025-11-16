import tkinter as tk
import requests
from datetime import datetime, timedelta
import json
import os
import re

API_KEY = "3cddf97d69024b8587578689b3ab2812"
TYPE = "json"
CONFIG_PATH = "widgets/config.json"

# 알레르기 매핑
ALLERGY_MAP = {
    "1": "난류", "2": "우유", "3": "메밀", "4": "땅콩", "5": "대두", "6": "밀",
    "7": "고등어", "8": "게", "9": "새우", "10": "돼지고기", "11": "복숭아",
    "12": "토마토", "13": "아황산류", "14": "호두", "15": "닭고기", "16": "쇠고기",
    "17": "오징어", "18": "조개류", "19": "잣"
}

# config.json 불러오기
if not os.path.exists(CONFIG_PATH):
    raise FileNotFoundError("config.json이 존재하지 않습니다. 먼저 학교 설정을 완료하세요.")

with open(CONFIG_PATH, "r", encoding="utf-8") as f:
    config = json.load(f)

EDU_OFFICE_CODE = config.get("edu_office_code", "B10")
SCHOOL_CODE = config["school_code"]

# 사용자가 등록한 알레르기
USER_ALLERGIES = config.get("allergies", [])

# 오늘 날짜
today_date = datetime.today()
if today_date.weekday() == 5:
    today_date += timedelta(days=2)
elif today_date.weekday() == 6:
    today_date += timedelta(days=1)

today = today_date.strftime("%Y%m%d")
display_date = today_date.strftime("%Y년 %m월 %d일")

# 급식 API 요청
url = (
    f"https://open.neis.go.kr/hub/mealServiceDietInfo?"
    f"KEY={API_KEY}&Type={TYPE}"
    f"&ATPT_OFCDC_SC_CODE={EDU_OFFICE_CODE}"
    f"&SD_SCHUL_CODE={SCHOOL_CODE}"
    f"&MLSV_YMD={today}"
)

response = requests.get(url)
data = response.json()
meal_list = []

# 급식 데이터 파싱
if "mealServiceDietInfo" in data:
    try:
        meal_rows = data["mealServiceDietInfo"][1]["row"]
        for item in meal_rows:
            dishes_raw = item.get("DDISH_NM", "").replace("<br/>", "\n")

            dish_lines = dishes_raw.split("\n")
            user_allergy_warnings = []
            clean_dishes = []

            for dish in dish_lines:
                allerg_match = re.search(r'\(([\d.,]+)\)', dish)
                if allerg_match:
                    allerg_nums = allerg_match.group(1)
                    user_allergies_in_dish = []

                    for num in allerg_nums.split('.'):
                        num = num.strip()
                        if num in ALLERGY_MAP:
                            allergy_name = ALLERGY_MAP[num]

                            # 사용자 알레르기 체크
                            if allergy_name in USER_ALLERGIES:
                                user_allergies_in_dish.append(allergy_name)

                    clean_dish = re.sub(r'\([\d.,]+\)', '', dish).strip()
                    clean_dishes.append(clean_dish)

                    # 사용자 알레르기가 있는 경우만 저장
                    if user_allergies_in_dish:
                        allergy_str = ", ".join(user_allergies_in_dish)
                        user_allergy_warnings.append(f"{clean_dish}: {allergy_str}")
                else:
                    clean_dishes.append(dish.strip())

            meal_list.append({
                "name": item.get('MMEAL_SC_NM'),
                "dishes": "\n".join(clean_dishes),
                "user_warnings": user_allergy_warnings
            })
    except (KeyError, IndexError):
        meal_list = []

# Tkinter GUI
root = tk.Tk()
root.title("오늘 급식")
root.geometry("1400x800")
root.configure(bg="#1E2144")
root.resizable(False, False)

canvas = tk.Canvas(root, width=1400, height=800, bg="#1E2144", highlightthickness=0)
canvas.pack()

canvas_width = 1400
title_y = 40
date_y = 85
start_y = 150
meal_width = canvas_width // 3
line_height = 24

# 제목
canvas.create_text(
    canvas_width / 2,
    title_y,
    text="오늘 급식",
    fill="white",
    font=("Pretendard SemiBold", 28),
    anchor="n"
)

# 날짜 표시
canvas.create_text(
    canvas_width / 2,
    date_y,
    text=display_date,
    fill="white",
    font=("Pretendard SemiBold", 16),
    anchor="n"
)

# 3끼 표시
if meal_list:
    for i, meal in enumerate(meal_list):
        x_pos = meal_width * i + meal_width // 2

        # 끼니 이름
        canvas.create_text(
            x_pos,
            start_y,
            text=meal["name"],
            fill="#FFD700",
            font=("Pretendard SemiBold", 24),
            anchor="n"
        )

        # 메뉴
        canvas.create_text(
            x_pos,
            start_y + 55,
            text=meal["dishes"],
            fill="white",
            font=("Pretendard SemiBold", 17),
            anchor="n",
            justify="center"
        )

        num_lines = meal["dishes"].count("\n") + 1

        # 사용자 알레르기 경고만 표시
        if meal["user_warnings"]:
            warning_y = start_y + 55 + num_lines * line_height + 30

            canvas.create_text(
                x_pos,
                warning_y,
                text="🚨 알레르기 주의!",
                fill="#FF3333",
                font=("Pretendard ExtraBold", 18),
                anchor="n"
            )

            # 메뉴: 알레르기 형식으로 표시
            warning_text = "\n".join(meal["user_warnings"])
            canvas.create_text(
                x_pos,
                warning_y + 35,
                text=warning_text,
                fill="#FF6666",
                font=("Pretendard SemiBold", 15),
                anchor="n",
                justify="center"
            )
else:
    canvas.create_text(
        canvas_width / 2,
        start_y,
        text="오늘 급식이 없어요",
        fill="white",
        font=("Pretendard SemiBold", 20),
        anchor="n"
    )

root.mainloop()