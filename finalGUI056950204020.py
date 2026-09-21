import csv
import tkinter as tk
from tkinter import messagebox, ttk


def save_to_csv():
    # ดึงชื่อไฟล์จากช่องกรอก
    filename = filename_entry.get().strip()
    if not filename:
        messagebox.showwarning("แจ้งเตือน", "กรุณาระบุชื่อไฟล์ก่อนบันทึก")
        return

    # ตรวจสอบว่าชื่อไฟล์มีนามสกุล .csv หรือยัง
    if not filename.endswith(".csv"):
        filename += ".csv"

    # รวบรวมข้อมูลจากช่องกรอกทั้ง 5 รายการ
    data = []
    for i, row in enumerate(rows):
        name = row["name"].get().strip()
        bedtime = row["bedtime"].get().strip()
        wake_time = row["wake_time"].get().strip()

        # ถ้ามีการกรอกข้อมูลในแถวนั้นๆ
        if name or bedtime or wake_time:
            # ตรวจสอบว่ากรอกครบทุกช่องในแถวดังกล่าวหรือไม่
            if not (name and bedtime and wake_time):
                messagebox.showwarning(
                    "ข้อมูลไม่ครบถ้วน",
                    f"กรุณากรอกข้อมูลรายการที่ {i+1} ให้ครบทุกช่อง",
                )
                return
            data.append([name, bedtime, wake_time])

    # ตรวจสอบว่ามีข้อมูลอย่างน้อย 1 รายการหรือไม่
    if not data:
        messagebox.showwarning("แจ้งเตือน", "กรุณากรอกข้อมูลอย่างน้อย 1 รายการ")
        return

    # บันทึกลงไฟล์ CSV
    try:
        with open(filename, mode="w", newline="", encoding="utf-8-sig") as file:
            writer = csv.writer(file)
            # เขียน Header 3 คอลัมน์
            writer.writerow(["ชื่อ", "เวลาเข้านอน", "เวลาตื่น"])
            # เขียนข้อมูล
            writer.writerows(data)

        messagebox.showinfo(
            "สำเร็จ",
            f"บันทึกข้อมูลจำนวน {len(data)} รายการลงในไฟล์ '{filename}' เรียบร้อยแล้ว!",
        )
    except Exception as e:
        messagebox.showerror("ผิดพลาด", f"ไม่สามารถบันทึกไฟล์ได้: {e}")


# สร้างหน้าต่างหลัก
root = tk.Tk()
root.title("โปรแกรมบันทึกข้อมูลการนอนของนักศึกษา")
root.geometry("520x400")
root.resizable(False, False)

# ส่วนกำหนดชื่อไฟล์
frame_file = ttk.Frame(root, padding=10)
frame_file.pack(fill="x")

ttk.Label(frame_file, text="ชื่อไฟล์:").pack(side="left", padx=5)
filename_entry = ttk.Entry(frame_file, width=25)
filename_entry.insert(0, "sleep.csv")  # กำหนดค่าเริ่มต้นเป็น sleep.csv
filename_entry.pack(side="left", padx=5)

# ส่วนตารางกรอกข้อมูล 5 รายการ
frame_inputs = ttk.LabelFrame(
    root, text=" กรอกข้อมูลนักศึกษา (5 รายการ) ", padding=10
)
frame_inputs.pack(fill="both", expand=True, padx=10, pady=5)

# สร้าง Header สำหรับตาราง
headers = ["รายการที่", "ชื่อ", "เวลาเข้านอน", "เวลาตื่น"]
for col_idx, header in enumerate(headers):
    ttk.Label(frame_inputs, text=header, font=("Tahoma", 9, "bold")).grid(
        row=0, column=col_idx, padx=5, pady=5, sticky="w"
    )

# สร้างช่องกรอกข้อมูล 5 แถว
rows = []
for i in range(5):
    # ลำดับรายการ
    ttk.Label(frame_inputs, text=f"{i+1}.").grid(
        row=i + 1, column=0, padx=5, pady=3
    )

    # ช่องกรอกชื่อ
    name_ent = ttk.Entry(frame_inputs, width=20)
    name_ent.grid(row=i + 1, column=1, padx=5, pady=3)

    # ช่องกรอกเวลาเข้านอน
    bed_ent = ttk.Entry(frame_inputs, width=15)
    bed_ent.grid(row=i + 1, column=2, padx=5, pady=3)

    # ช่องกรอกเวลาตื่นนอน
    wake_ent = ttk.Entry(frame_inputs, width=15)
    wake_ent.grid(row=i + 1, column=3, padx=5, pady=3)

    rows.append({"name": name_ent, "bedtime": bed_ent, "wake_time": wake_ent})

# ปุ่มบันทึกข้อมูล
frame_button = ttk.Frame(root, padding=10)
frame_button.pack(fill="x")

btn_save = ttk.Button(frame_button, text="บันทึกข้อมูลลง CSV", command=save_to_csv)
btn_save.pack(side="right", padx=5)

# เริ่มการทำงานของ GUI
root.mainloop()