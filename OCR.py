import cv2
import pytesseract
from tkinter import Tk, Label, Button, filedialog, Text
from PIL import Image, ImageTk, ImageOps

# konfigurasi tesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# fungsi OCR
def ocr_core(img):
    text = pytesseract.image_to_string(img, lang='eng', config='--psm 6 --oem 1')
    return text

# preprocessing gambar
def preprocess_image(image):
    # Konversi ke skala abu-abu
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # Thresholding untuk binerisasi
    binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
    # Menghapus noise
    denoised = cv2.medianBlur(binary, 3)
    return denoised

# fungsi untuk memilih file
def select_file():
    global img, tk_img, img_label
    file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.bmp")])
    if file_path:
        # Membaca gambar
        img = cv2.imread(file_path)
        if img is None:
            result_label.config(text="Gambar tidak valid!")
        else:
            # Tampilkan gambar di GUI
            img = preprocess_image(img)
            img_rgb = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)  # Untuk kompatibilitas PIL
            img_pil = Image.fromarray(img_rgb)
            img_pil = img_pil.resize((300, 300), Image.Resampling.LANCZOS)  # Resize gambar
            tk_img = ImageTk.PhotoImage(img_pil)
            img_label.config(image=tk_img)
            img_label.image = tk_img
            result_label.config(text="Gambar berhasil dimuat, klik 'Proses OCR'.")

# fungsi untuk menjalankan OCR
def process_ocr():
    if img is not None:
        text = ocr_core(img)
        result_text.delete("1.0", "end")  # Hapus teks sebelumnya
        result_text.insert("1.0", text)  # Tampilkan hasil OCR
        result_label.config(text="OCR selesai!")
    else:
        result_label.config(text="Pilih gambar terlebih dahulu.")

# GUI menggunakan Tkinter
root = Tk()
root.title("OCR GUI")
root.geometry("600x600")

# Elemen GUI
Label(root, text="OCR dengan Python", font=("Helvetica", 16)).pack(pady=10)

# Tombol untuk memilih file
Button(root, text="Pilih Gambar", command=select_file, width=20).pack(pady=10)

# Label untuk menampilkan gambar
img_label = Label(root)
img_label.pack(pady=10)

# Tombol untuk memproses OCR
Button(root, text="Proses OCR", command=process_ocr, width=20).pack(pady=10)

# Label hasil
result_label = Label(root, text="", font=("Helvetica", 12))
result_label.pack(pady=10)

# Textbox untuk hasil OCR
result_text = Text(root, height=10, width=70)
result_text.pack(pady=10)

# Jalankan GUI
img = None  # Variabel global untuk gambar
root.mainloop()
