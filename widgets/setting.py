import tkinter as tk
from tkinter import messagebox, ttk
import requests
import json
import os

API_KEY = "3cddf97d69024b8587578689b3ab2812"

# 교육청 이름 → 코드 매핑
EDU_OFFICE_MAP = {
    "서울특별시교육청": "B10",
    "부산광역시교육청": "D10",
    "대구광역시교육청": "E10",
    "인천광역시교육청": "C10",
    "광주광역시교육청": "F10",
    "대전광역시교육청": "G10",
    "울산광역시교육청": "H10",
    "세종특별자치시교육청": "I10",
    "경기도교육청": "J10",
    "강원도교육청": "K10",
    "충청북도교육청": "M10",
    "충청남도교육청": "N10",
    "전라북도교육청": "O10",
    "전라남도교육청": "P10",
    "경상북도교육청": "Q10",
    "경상남도교육청": "R10",
    "제주특별자치도교육청": "S10"
}

def search_school():
    school_name = entry_school_name.get()
    edu_office_code = EDU_OFFICE_MAP[combo_edu.get()]
    if not school_name:
        messagebox.showwarning("경고", "학교명을 입력해주세요")
        return

    url = (
        f"https://open.neis.go.kr/hub/schoolInfo?"
        f"KEY={API_KEY}&Type=json&ATPT_OFCDC_SC_CODE={edu_office_code}&SCHUL_NM={school_name}"
    )
    try:
        response = requests.get(url)
        data = response.json()
    except Exception as e:
        messagebox.showerror("오류", f"API 요청 실패: {e}")
        return

    school_listbox.delete(0, tk.END)

    if "schoolInfo" in data:
        rows = data["schoolInfo"][1]["row"]
        for row in rows:
            name = row["SCHUL_NM"]
            code = row["SD_SCHUL_CODE"]
            school_listbox.insert(tk.END, f"{name} ({code})")
    else:
        messagebox.showinfo("결과 없음", "검색 결과가 없습니다")

def select_school(event):
    selection = school_listbox.get(school_listbox.curselection())
    name, code = selection.rsplit("(", 1)
    entry_school_code.delete(0, tk.END)
    entry_school_code.insert(0, code.replace(")", ""))

def save_settings():
    school_code = entry_school_code.get()
    grade = entry_grade.get()
    class_num = entry_class.get()

    if not (school_code and grade and class_num):
        messagebox.showwarning("경고", "모든 항목을 입력해주세요")
        return

    config = {
        "school_code": school_code,
        "grade": int(grade),
        "class": int(class_num)
    }

    os.makedirs("widgets", exist_ok=True)
    with open("widgets/config.json", "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=4)

    messagebox.showinfo("완료", "설정이 저장되었습니다")
    root.destroy()  # 설정 창 닫기 → 메인 화면으로 돌아감

# ------------------ Tkinter 창 ------------------
root = tk.Tk()
root.title("학교 설정")
root.geometry("500x500")
root.configure(bg="#1E2144")

# 교육청 선택
tk.Label(root, text="교육청:", bg="#1E2144", fg="white", font=("Pretendard SemiBold", 12)).place(x=30, y=20)
combo_edu = ttk.Combobox(root, values=list(EDU_OFFICE_MAP.keys()), font=("Pretendard", 12))
combo_edu.current(0)
combo_edu.place(x=150, y=20, width=300)

# 학교명 입력
tk.Label(root, text="학교명:", bg="#1E2144", fg="white", font=("Pretendard SemiBold", 12)).place(x=30, y=60)
entry_school_name = tk.Entry(root, font=("Pretendard", 12))
entry_school_name.place(x=150, y=60, width=200)

btn_search = tk.Button(root, text="검색", command=search_school, bg="#2E2E5C", fg="white", font=("Pretendard SemiBold", 12))
btn_search.place(x=370, y=60, width=80)

# 학교 검색 결과 리스트박스
school_listbox = tk.Listbox(root, font=("Pretendard", 12))
school_listbox.place(x=30, y=100, width=420, height=150)
school_listbox.bind("<<ListboxSelect>>", select_school)

# 선택된 학교 코드
tk.Label(root, text="학교 코드:", bg="#1E2144", fg="white", font=("Pretendard SemiBold", 12)).place(x=30, y=270)
entry_school_code = tk.Entry(root, font=("Pretendard", 12))
entry_school_code.place(x=150, y=270, width=200)

# 학년, 반 입력
tk.Label(root, text="학년:", bg="#1E2144", fg="white", font=("Pretendard SemiBold", 12)).place(x=30, y=310)
entry_grade = tk.Entry(root, font=("Pretendard", 12))
entry_grade.place(x=150, y=310, width=200)

tk.Label(root, text="반:", bg="#1E2144", fg="white", font=("Pretendard SemiBold", 12)).place(x=30, y=350)
entry_class = tk.Entry(root, font=("Pretendard", 12))
entry_class.place(x=150, y=350, width=200)

btn_save = tk.Button(root, text="저장", command=save_settings, bg="#FFD700", fg="black", font=("Pretendard SemiBold", 14))
btn_save.place(x=180, y=400, width=120, height=40)

root.mainloop()
