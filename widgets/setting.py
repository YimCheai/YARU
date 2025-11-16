import tkinter as tk
from tkinter import messagebox, ttk
import requests
import json
import os
from datetime import datetime, timedelta

API_KEY = "3cddf97d69024b8587578689b3ab2812"
CONFIG_PATH = "widgets/config.json"
os.makedirs("widgets", exist_ok=True)

EDU_OFFICE_MAP = {
    "서울특별시교육청": "B10", "부산광역시교육청": "C10", "대구광역시교육청": "D10",
    "인천광역시교육청": "E10", "광주광역시교육청": "F10", "대전광역시교육청": "G10",
    "울산광역시교육청": "H10", "세종특별자치시교육청": "I10", "경기도교육청": "J10",
    "강원도교육청": "K10", "충청북도교육청": "M10", "충청남도교육청": "N10",
    "전라북도교육청": "P10", "전라남도교육청": "Q10", "경상북도교육청": "R10",
    "경상남도교육청": "S10", "제주특별자치도교육청": "T10"
}

ALLERGY_MAP = {
    "1": "난류", "2": "우유", "3": "메밀", "4": "땅콩", "5": "대두", "6": "밀",
    "7": "고등어", "8": "게", "9": "새우", "10": "돼지고기", "11": "복숭아",
    "12": "토마토", "13": "아황산류", "14": "호두", "15": "닭고기", "16": "쇠고기",
    "17": "오징어", "18": "조개류", "19": "잣"
}


def load_config():
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {
        "move_subjects": [],
        "allergies": [],
        "alarm_before_lunch": 10,
        "alarm_before_class": 5
    }


def save_config(config):
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=4)


def get_today_subjects(config):
    """오늘 시간표에서 과목 목록 가져오기"""
    if "school_code" not in config:
        return []

    edu_code = config.get("edu_office_code")
    school_code = config.get("school_code")
    grade = config.get("grade", 1)
    class_num = config.get("class", 1)

    today_date = datetime.today()
    if today_date.weekday() == 5:
        today_date += timedelta(days=2)
    elif today_date.weekday() == 6:
        today_date += timedelta(days=1)

    today = today_date.strftime("%Y%m%d")

    url = f"https://open.neis.go.kr/hub/hisTimetable?KEY={API_KEY}&Type=json&ATPT_OFCDC_SC_CODE={edu_code}&SD_SCHUL_CODE={school_code}&GRADE={grade}&CLASS_NM={class_num}&SEM=2&ALL_TI_YN=N&TI_FROM_YMD={today}&TI_TO_YMD={today}"

    try:
        data = requests.get(url).json()
        if "hisTimetable" in data:
            time_table = data["hisTimetable"][1]["row"]
            subjects = [lesson.get("ITRT_CNTNT", "") for lesson in time_table]
            return list(set(subjects))  # 중복 제거
    except:
        pass
    return []


def school_settings_window():
    config = load_config()

    root = tk.Tk()
    root.title("학교 설정")
    root.geometry("600x750")
    root.configure(bg="#1E2144")

    # 탭 생성
    notebook = ttk.Notebook(root)
    notebook.pack(fill="both", expand=True, padx=10, pady=10)

    # ==================== 탭1: 학교 정보 ====================
    tab1 = tk.Frame(notebook, bg="#1E2144")
    notebook.add(tab1, text="학교 정보")

    def search_school():
        school_name = entry_school_name.get()
        edu_code = EDU_OFFICE_MAP[combo_edu.get()]
        if not school_name:
            messagebox.showwarning("경고", "학교명을 입력해주세요")
            return
        url = f"https://open.neis.go.kr/hub/schoolInfo?KEY={API_KEY}&Type=json&ATPT_OFCDC_SC_CODE={edu_code}&SCHUL_NM={school_name}"
        try:
            data = requests.get(url).json()
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
        if not school_listbox.curselection():
            return
        selection = school_listbox.get(school_listbox.curselection())
        name, code = selection.rsplit("(", 1)
        entry_school_code.delete(0, tk.END)
        entry_school_code.insert(0, code.replace(")", ""))

    def save_school_settings():
        school_code = entry_school_code.get()
        grade = entry_grade.get()
        class_num = entry_class.get()
        edu_code = EDU_OFFICE_MAP[combo_edu.get()]

        if not (school_code and grade and class_num):
            messagebox.showwarning("경고", "모든 항목을 입력해주세요")
            return

        config["edu_office_code"] = edu_code
        config["school_code"] = school_code
        config["grade"] = int(grade)
        config["class"] = int(class_num)
        save_config(config)
        messagebox.showinfo("완료", "학교 정보가 저장되었습니다")

    tk.Label(tab1, text="교육청:", bg="#1E2144", fg="white", font=("Pretendard SemiBold", 12)).place(x=30, y=20)
    combo_edu = ttk.Combobox(tab1, values=list(EDU_OFFICE_MAP.keys()), font=("Pretendard", 12))
    combo_edu.current(0)
    combo_edu.place(x=150, y=20, width=380)

    tk.Label(tab1, text="학교명:", bg="#1E2144", fg="white", font=("Pretendard SemiBold", 12)).place(x=30, y=60)
    entry_school_name = tk.Entry(tab1, font=("Pretendard", 12))
    entry_school_name.place(x=150, y=60, width=280)
    tk.Button(tab1, text="검색", command=search_school, bg="#2E2E5C", fg="white", font=("Pretendard SemiBold", 12)).place(
        x=450, y=60, width=80)

    school_listbox = tk.Listbox(tab1, font=("Pretendard", 12))
    school_listbox.place(x=30, y=100, width=500, height=150)
    school_listbox.bind("<<ListboxSelect>>", select_school)

    tk.Label(tab1, text="학교 코드:", bg="#1E2144", fg="white", font=("Pretendard SemiBold", 12)).place(x=30, y=270)
    entry_school_code = tk.Entry(tab1, font=("Pretendard", 12))
    entry_school_code.place(x=150, y=270, width=200)

    tk.Label(tab1, text="학년:", bg="#1E2144", fg="white", font=("Pretendard SemiBold", 12)).place(x=30, y=310)
    entry_grade = tk.Entry(tab1, font=("Pretendard", 12))
    entry_grade.place(x=150, y=310, width=200)

    tk.Label(tab1, text="반:", bg="#1E2144", fg="white", font=("Pretendard SemiBold", 12)).place(x=30, y=350)
    entry_class = tk.Entry(tab1, font=("Pretendard", 12))
    entry_class.place(x=150, y=350, width=200)

    tk.Button(tab1, text="저장", command=save_school_settings, bg="#FFD700", fg="black",
              font=("Pretendard SemiBold", 14)).place(x=220, y=400, width=120, height=40)

    # 기존 설정 불러오기
    if "school_code" in config:
        entry_school_code.insert(0, config["school_code"])
        entry_grade.insert(0, config.get("grade", ""))
        entry_class.insert(0, config.get("class", ""))

    # ==================== 탭2: 이동수업 ====================
    tab2 = tk.Frame(notebook, bg="#1E2144")
    notebook.add(tab2, text="이동수업")

    tk.Label(tab2, text="이동수업 과목 관리", bg="#1E2144", fg="white", font=("Pretendard SemiBold", 16)).pack(pady=20)

    frame_move = tk.Frame(tab2, bg="#1E2144")
    frame_move.pack(pady=10)

    tk.Label(frame_move, text="과목 검색:", bg="#1E2144", fg="white", font=("Pretendard", 12)).grid(row=0, column=0,
                                                                                                padx=10)
    entry_subject_search = tk.Entry(frame_move, font=("Pretendard", 12), width=20)
    entry_subject_search.grid(row=0, column=1, padx=10)

    # 검색 결과 리스트박스
    search_listbox = tk.Listbox(tab2, font=("Pretendard", 11), height=6)
    search_listbox.pack(pady=5, padx=30, fill="x")

    def search_subjects():
        keyword = entry_subject_search.get().strip()
        search_listbox.delete(0, tk.END)

        if not keyword:
            messagebox.showwarning("경고", "검색어를 입력하세요")
            return

        subjects = get_today_subjects(config)
        if not subjects:
            messagebox.showinfo("알림", "학교 정보를 먼저 저장하거나\n오늘 시간표가 없습니다")
            return

        # 키워드로 필터링
        filtered = [s for s in subjects if keyword.lower() in s.lower()]

        if filtered:
            for subj in filtered:
                search_listbox.insert(tk.END, subj)
        else:
            messagebox.showinfo("검색 결과", "일치하는 과목이 없습니다")

    tk.Button(frame_move, text="검색", command=search_subjects, bg="#2E2E5C", fg="white",
              font=("Pretendard SemiBold", 12)).grid(row=0, column=2, padx=5)

    tk.Label(tab2, text="━━━━━━━━━━━━━━━━━━", bg="#1E2144", fg="#555", font=("Pretendard", 10)).pack(pady=5)
    tk.Label(tab2, text="등록된 이동수업 과목", bg="#1E2144", fg="white", font=("Pretendard SemiBold", 14)).pack(pady=5)

    listbox_subjects = tk.Listbox(tab2, font=("Pretendard", 12), height=8)
    listbox_subjects.pack(pady=10, padx=30, fill="both", expand=True)

    def refresh_subject_list():
        listbox_subjects.delete(0, tk.END)
        for subj in config.get("move_subjects", []):
            listbox_subjects.insert(tk.END, subj)

    def add_subject_from_search():
        if not search_listbox.curselection():
            messagebox.showwarning("경고", "검색 결과에서 과목을 선택하세요")
            return
        subject = search_listbox.get(search_listbox.curselection())

        if "move_subjects" not in config:
            config["move_subjects"] = []
        if subject in config["move_subjects"]:
            messagebox.showinfo("알림", "이미 등록된 과목입니다")
            return
        config["move_subjects"].append(subject)
        save_config(config)
        refresh_subject_list()
        messagebox.showinfo("완료", f"'{subject}' 추가됨")

    def delete_subject():
        if not listbox_subjects.curselection():
            messagebox.showwarning("경고", "삭제할 과목을 선택하세요")
            return
        subject = listbox_subjects.get(listbox_subjects.curselection())
        config["move_subjects"].remove(subject)
        save_config(config)
        refresh_subject_list()
        messagebox.showinfo("완료", f"'{subject}' 삭제됨")

    btn_frame = tk.Frame(tab2, bg="#1E2144")
    btn_frame.pack(pady=10)
    tk.Button(btn_frame, text="선택한 과목 추가", command=add_subject_from_search, bg="#4CAF50", fg="white",
              font=("Pretendard SemiBold", 12)).pack(side="left", padx=5)
    tk.Button(btn_frame, text="선택 삭제", command=delete_subject, bg="#FF6B6B", fg="white",
              font=("Pretendard SemiBold", 12)).pack(side="left", padx=5)

    refresh_subject_list()

    # ==================== 탭3: 알레르기 ====================
    tab3 = tk.Frame(notebook, bg="#1E2144")
    notebook.add(tab3, text="알레르기")

    tk.Label(tab3, text="알레르기 항목 관리", bg="#1E2144", fg="white", font=("Pretendard SemiBold", 16)).pack(pady=20)

    frame_allergy = tk.Frame(tab3, bg="#1E2144")
    frame_allergy.pack(pady=10)

    tk.Label(frame_allergy, text="알레르기:", bg="#1E2144", fg="white", font=("Pretendard", 12)).grid(row=0, column=0,
                                                                                                  padx=10)
    combo_allergy = ttk.Combobox(frame_allergy, values=list(ALLERGY_MAP.values()), font=("Pretendard", 12), width=20)
    combo_allergy.grid(row=0, column=1, padx=10)

    listbox_allergies = tk.Listbox(tab3, font=("Pretendard", 12), height=15)
    listbox_allergies.pack(pady=10, padx=30, fill="both", expand=True)

    def refresh_allergy_list():
        listbox_allergies.delete(0, tk.END)
        for allergy in config.get("allergies", []):
            listbox_allergies.insert(tk.END, allergy)

    def add_allergy():
        allergy = combo_allergy.get().strip()
        if not allergy:
            messagebox.showwarning("경고", "알레르기를 선택하세요")
            return
        if "allergies" not in config:
            config["allergies"] = []
        if allergy in config["allergies"]:
            messagebox.showinfo("알림", "이미 등록된 알레르기입니다")
            return
        config["allergies"].append(allergy)
        save_config(config)
        refresh_allergy_list()
        messagebox.showinfo("완료", f"'{allergy}' 추가됨")

    def delete_allergy():
        if not listbox_allergies.curselection():
            messagebox.showwarning("경고", "삭제할 알레르기를 선택하세요")
            return
        allergy = listbox_allergies.get(listbox_allergies.curselection())
        config["allergies"].remove(allergy)
        save_config(config)
        refresh_allergy_list()
        messagebox.showinfo("완료", f"'{allergy}' 삭제됨")

    tk.Button(frame_allergy, text="추가", command=add_allergy, bg="#2E2E5C", fg="white",
              font=("Pretendard SemiBold", 12)).grid(row=0, column=2, padx=5)
    tk.Button(tab3, text="선택 삭제", command=delete_allergy, bg="#FF6B6B", fg="white",
              font=("Pretendard SemiBold", 12)).pack(pady=10)

    refresh_allergy_list()

    # ==================== 탭4: 알람 시간 ====================
    tab4 = tk.Frame(notebook, bg="#1E2144")
    notebook.add(tab4, text="알람 설정")

    tk.Label(tab4, text="알람 시간 설정", bg="#1E2144", fg="white", font=("Pretendard SemiBold", 16)).pack(pady=30)

    frame_alarm = tk.Frame(tab4, bg="#1E2144")
    frame_alarm.pack(pady=20)

    tk.Label(frame_alarm, text="점심시간 전 알람 (분):", bg="#1E2144", fg="white", font=("Pretendard", 12)).grid(row=0,
                                                                                                         column=0,
                                                                                                         pady=10,
                                                                                                         padx=10,
                                                                                                         sticky="w")
    entry_lunch_alarm = tk.Entry(frame_alarm, font=("Pretendard", 12), width=10)
    entry_lunch_alarm.grid(row=0, column=1, pady=10)
    entry_lunch_alarm.insert(0, str(config.get("alarm_before_lunch", 10)))

    tk.Label(frame_alarm, text="수업 전 알람 (분):", bg="#1E2144", fg="white", font=("Pretendard", 12)).grid(row=1, column=0,
                                                                                                       pady=10, padx=10,
                                                                                                       sticky="w")
    entry_class_alarm = tk.Entry(frame_alarm, font=("Pretendard", 12), width=10)
    entry_class_alarm.grid(row=1, column=1, pady=10)
    entry_class_alarm.insert(0, str(config.get("alarm_before_class", 5)))

    def save_alarm_settings():
        try:
            lunch_min = int(entry_lunch_alarm.get())
            class_min = int(entry_class_alarm.get())
            if lunch_min < 1 or class_min < 1:
                raise ValueError
            config["alarm_before_lunch"] = lunch_min
            config["alarm_before_class"] = class_min
            save_config(config)
            messagebox.showinfo("완료", "알람 시간이 저장되었습니다")
        except ValueError:
            messagebox.showerror("오류", "올바른 숫자를 입력하세요 (1 이상)")

    tk.Button(tab4, text="저장", command=save_alarm_settings, bg="#FFD700", fg="black", font=("Pretendard SemiBold", 14),
              width=15).pack(pady=30)

    root.mainloop()


if __name__ == "__main__":
    school_settings_window()