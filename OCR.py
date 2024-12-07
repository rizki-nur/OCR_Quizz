import cv2
import pytesseract
import pandas as pd
from tkinter import Tk, Label, Button, filedialog, Text
from PIL import Image, ImageTk, ImageOps
from fuzzywuzzy import process

# Konfigurasi tesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Fungsi OCR
def ocr_core(img):
    text = pytesseract.image_to_string(img, lang='eng', config='--psm 6 --oem 1')
    return text

# Preprocessing gambar
def preprocess_image(image):
    # Konversi ke skala abu-abu
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # Menghapus noise
    denoised = cv2.medianBlur(gray, 3)
    # Thresholding untuk binerisasi
    binary = cv2.threshold(denoised, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
    return binary

# Memuat dataset
def load_dataset(file_path):
    data = pd.read_csv(file_path)
    return data

# Fungsi untuk mencari buku
def search_book(text, dataset):
    # Ambil daftar judul buku untuk proses pencocokan
    book_titles = dataset["title"].tolist()
    # Cari judul dengan kemiripan tertinggi
    result = process.extractOne(text, book_titles)
    
    if result:
        matched_title = result[0]
        similarity = result[1]
        if similarity > 80:  # Ambang batas kecocokan tinggi
            # Ambil baris dari dataset berdasarkan judul yang cocok
            book_info = dataset[dataset["title"] == matched_title].iloc[0]
            return {
                "title": book_info["title"],
                "author": book_info["authors"],
                "description": book_info["description"],
            }
        elif similarity > 50:  # Ambang batas kecocokan rendah untuk saran
            return {"suggestion": matched_title}
    
    return None  # Jika tidak ada kecocokan

# Fungsi untuk memilih file
def select_file():
    global img, tk_img, img_label
    file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.bmp;*.avif")])
    if file_path:
        # Membaca gambar
        img = cv2.imread(file_path)
        if img is None:
            result_label.config(text="Gambar tidak valid!")
        else:
            # Tampilkan gambar di GUI
            img = preprocess_image(img)
            img_rgb = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)  # untuk kompatibilitas PIL
            img_pil = Image.fromarray(img_rgb)
            img_pil = img_pil.resize((300, 300), Image.Resampling.LANCZOS)  # resize gambar
            tk_img = ImageTk.PhotoImage(img_pil)
            img_label.config(image=tk_img)
            img_label.image = tk_img
            result_label.config(text="Gambar berhasil dimuat, klik 'Proses OCR'.")

# Fungsi untuk menjalankan OCR dan pencarian buku
def process_ocr():
    if img is not None:
        text = ocr_core(img)
        result = search_book(text, dataset)  # Gunakan dataset lengkap
        result_text.delete("1.0", "end")  # Hapus teks sebelumnya
        
        if result:
            if "title" in result:  # Buku ditemukan
                result_text.insert(
                    "1.0",
                    f"Hasil OCR: {text}\n\n"
                    f"Buku ditemukan:\n"
                    f"Judul: {result['title']}\n"
                    f"Penulis: {result['author']}\n"
                    f"Deskripsi: {result['description']}",
                )
            elif "suggestion" in result:  # Buku tidak ditemukan tetapi ada saran
                result_text.insert(
                    "1.0",
                    f"Hasil OCR: {text}\n\n"
                    f"Buku tidak ditemukan.\n"
                    f"Mungkin yang Anda maksud adalah: {result['suggestion']}",
                )
        else:
            result_text.insert("1.0", f"Hasil OCR: {text}\n\nBuku tidak ditemukan.")
        
        result_label.config(text="OCR selesai!")
    else:
        result_label.config(text="Pilih gambar terlebih dahulu.")

# GUI menggunakan Tkinter
root = Tk()
root.title("OCR Pencari Buku")
root.geometry("600x700")

# Memuat dataset
dataset_path = "datas.csv"  # Ganti dengan path ke file dataset Anda
dataset = load_dataset(dataset_path)

# Elemen GUI
Label(root, text="OCR Pencari Buku", font=("Helvetica", 16)).pack(pady=10)

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