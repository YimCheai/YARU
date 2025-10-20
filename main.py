import tkinter as tk
from PIL import Image, ImageTk
import subprocess  # 다른 파이썬 파일 실행용

root = tk.Tk()
root.title("YARU 위젯")
root.geometry("700x400")
root.configure(bg="#1E2144")
root.resizable(False, False)

canvas = tk.Canvas(root, width=700, height=400, bg="#1E2144", highlightthickness=0)
canvas.pack()

# 토끼
image = Image.open("images/yaruRabbit.png")
orig_width, orig_height = image.size
max_width = 150
ratio = max_width / orig_width
new_width = int(orig_width * ratio)
new_height = int(orig_height * ratio)
image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
img = ImageTk.PhotoImage(image)
canvas.create_image(70, 30, anchor="nw", image=img)

# 🟦 둥근 사각형 함수
def create_rounded_rectangle(x1, y1, x2, y2, radius=25, **kwargs):
    points = [
        x1 + radius, y1,
        x2 - radius, y1,
        x2, y1,
        x2, y1 + radius,
        x2, y2 - radius,
        x2, y2,
        x2 - radius, y2,
        x1 + radius, y2,
        x1, y2,
        x1, y2 - radius,
        x1, y1 + radius,
        x1, y1
    ]
    return canvas.create_polygon(points, smooth=True, **kwargs)

rect_y1 = 270
rect_y2 = 385
create_rounded_rectangle(50, rect_y1, 650, rect_y2, radius=35, fill="#2E2E5C", outline="")


canvas.create_text(250, 100, text="학교를 등록하고", fill="white", font=("Pretendard SemiBold", 18), anchor="nw")
canvas.create_text(250, 130, text="시간표와 급식 정보를 확인하세요!", fill="white", font=("Pretendard SemiBold", 18), anchor="nw")

menu_icons = ["images/calender.png", "images/meal.png", "images/setting.png"]
menu_texts = ["시간표", "급식", "설정"]
menu_images = []

rect_width = 600
num_icons = len(menu_icons)
icon_size = 60
gap = rect_width / (num_icons + 1)
y_icon = rect_y1 + 20

def open_timetable():
    # widgets/timetable_widget.py 실행
    subprocess.Popen(["python", "widgets/timetable_widget.py"])

for i, icon_path in enumerate(menu_icons):
    icon_img = Image.open(icon_path)
    icon_img = icon_img.resize((icon_size, icon_size), Image.Resampling.LANCZOS)
    icon_tk = ImageTk.PhotoImage(icon_img)
    menu_images.append(icon_tk)

    x_pos = 50 + gap * (i + 1) - icon_size / 2
    image_id = canvas.create_image(x_pos, y_icon, anchor="nw", image=icon_tk)
    canvas.create_text(x_pos + icon_size / 2, y_icon + icon_size + 5, text=menu_texts[i],
                       fill="#A0AAC3", font=("Pretendard-Regular", 12), anchor="n")

    # 시간표 아이콘 클릭 이벤트만 바인딩
    if menu_texts[i] == "시간표":
        canvas.tag_bind(image_id, "<Button-1>", lambda e: open_timetable())

root.mainloop()
