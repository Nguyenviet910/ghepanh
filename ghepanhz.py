import os
from tkinter import Tk, Label, Button, filedialog, messagebox, Text, END, Scrollbar, RIGHT, Y
from tkinter import ttk
from PIL import Image

# ----------------- Chọn thư mục/file -----------------
def select_input_folder():
    folder = filedialog.askdirectory()
    if folder:
        global input_folder
        input_folder = folder
        lbl_input.config(text=f"Ảnh gốc: {folder}")

def select_output_folder():
    folder = filedialog.askdirectory()
    if folder:
        global output_folder
        output_folder = folder
        lbl_output.config(text=f"Xuất ảnh: {folder}")

def select_frame_file():
    file = filedialog.askopenfilename(filetypes=[
        ("Ảnh", "*.jpg *.jpeg *.png *.webp *.bmp *.gif"),
        ("Tất cả file", "*.*")
    ])
    if file:
        global frame_path
        frame_path = file
        lbl_frame.config(text=f"Khung: {file}")

# ----------------- Xử lý ảnh -----------------
def crop_center_resize(img, target_size):
    """Crop chính giữa giữ tỉ lệ rồi resize"""
    target_w, target_h = target_size
    w, h = img.size
    ratio_target = target_w / target_h
    ratio_img = w / h

    if ratio_img > ratio_target:  # ảnh rộng hơn
        new_w = int(h * ratio_target)
        offset = (w - new_w) // 2
        img = img.crop((offset, 0, offset + new_w, h))
    else:  # ảnh cao hơn
        new_h = int(w / ratio_target)
        offset = (h - new_h) // 2
        img = img.crop((0, offset, w, offset + new_h))

    return img.resize(target_size)

def batch_add_frame():
    try:
        if not input_folder or not output_folder or not frame_path:
            messagebox.showerror("Lỗi", "Vui lòng chọn đầy đủ ảnh gốc, thư mục xuất và khung!")
            return

        # Load frame
        frame = Image.open(frame_path).convert("RGBA")
        if frame.size != (1080, 1920):
            frame = frame.resize((1080, 1920))

        # Lọc tất cả định dạng ảnh
        supported_formats = (".jpg", ".jpeg", ".png", ".webp", ".bmp", ".gif")
        files = [f for f in os.listdir(input_folder) if f.lower().endswith(supported_formats)]
        total = len(files)
        if total == 0:
            messagebox.showwarning("Không có ảnh", "Thư mục không có ảnh hợp lệ.")
            return

        # Cấu hình progress bar và log
        progress_bar["maximum"] = total
        progress_bar["value"] = 0
        log_box.delete(1.0, END)

        for i, file_name in enumerate(files, start=1):
            img_path = os.path.join(input_folder, file_name)
            img = Image.open(img_path).convert("RGBA")
            img = crop_center_resize(img, (1080, 1080))

            # Ghép ảnh
            result = frame.copy()
            x = 0
            y = (1920 - 1080) // 2
            result.paste(img, (x, y), img)  # giữ alpha

            # Lưu ảnh
            base_name, ext = os.path.splitext(file_name)
            output_file = os.path.join(output_folder, f"{base_name}.jpg")
            result.convert("RGB").save(output_file, "JPEG", quality=95)

            # Update progress bar và log
            progress_bar["value"] = i
            app.update_idletasks()
            log_box.insert(END, f"✅ {i}/{total}: {file_name} đã ghép xong\n")
            log_box.see(END)

        messagebox.showinfo("Thành công", f"Đã xử lý {total} ảnh thành công!")

    except Exception as e:
        messagebox.showerror("Lỗi", str(e))

# ----------------- GUI -----------------
app = Tk()
app.title("Phần mềm ghép ảnh hàng loạt")
app.geometry("700x600")

input_folder = ""
output_folder = ""
frame_path = ""

# Chọn thư mục ảnh gốc
Label(app, text="Chọn thư mục ảnh gốc:").pack(pady=5)
Button(app, text="Chọn thư mục ảnh gốc", command=select_input_folder).pack()
lbl_input = Label(app, text="Chưa chọn")
lbl_input.pack()

# Chọn khung ảnh (mọi định dạng)
Label(app, text="1080x1920):").pack(pady=5)
Button(app, text="Chọn khung", command=select_frame_file).pack()
lbl_frame = Label(app, text="Chưa chọn")
lbl_frame.pack()

# Chọn thư mục xuất
Label(app, text="Chọn thư mục xuất ảnh:").pack(pady=5)
Button(app, text="Chọn thư mục xuất", command=select_output_folder).pack()
lbl_output = Label(app, text="Chưa chọn")
lbl_output.pack()

# Nút ghép ảnh
Button(app, text="🚀 Ghép ảnh", command=batch_add_frame, bg="green", fg="white", padx=20, pady=10).pack(pady=10)

# Progress bar
progress_bar = ttk.Progressbar(app, length=600, mode="determinate")
progress_bar.pack(pady=10)

# Log
Label(app, text="Log xử lý:").pack()
scrollbar = Scrollbar(app)
scrollbar.pack(side=RIGHT, fill=Y)
log_box = Text(app, height=15, width=85, yscrollcommand=scrollbar.set)
log_box.pack(pady=5)
scrollbar.config(command=log_box.yview)

app.mainloop()
