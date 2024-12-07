import cv2
import pytesseract
import pandas as pd
from tkinter import Tk, Label, Button, filedialog, Text
from PIL import Image, ImageTk
from fuzzywuzzy import process
from pytesseract import Output

# Konfigurasi tesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Fungsi untuk memuat dataset
def load_dataset(file_path):
    data = pd.read_csv(file_path)
    return data

# Preprocessing gambar
def preprocess_image(image):
    # Konversi ke skala abu-abu
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # Adaptive thresholding untuk penyesuaian kontras
    binary = cv2.adaptiveThreshold(
        gray, 
        maxValue=255, 
        adaptiveMethod=cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
        thresholdType=cv2.THRESH_BINARY, 
        blockSize=11,  # Ukuran blok piksel untuk menghitung threshold
        C=2            # Konstanta yang dikurangkan dari rata-rata
    )
    return binary

# Fungsi OCR menggunakan image_to_data
def ocr_core(img):
    data = pytesseract.image_to_data(img, lang='eng', config='--psm 6 --oem 1', output_type=Output.DICT)
    result_text = ""
    
    # Hanya ambil teks dengan confidence > 60
    for i in range(len(data['text'])):
        if int(data['conf'][i]) > 60:
            result_text += f"{data['text'][i]} "
    return result_text.strip()

# Fungsi untuk mencari buku
def search_book(text, dataset):
    book_titles = dataset["title"].tolist()
    result = process.extractOne(text, book_titles)
    if result:
        matched_title = result[0]
        similarity = result[1]
        if similarity > 80:  # Ambang batas kecocokan tinggi
            book_info = dataset[dataset["title"] == matched_title].iloc[0]
            return {
                "title": book_info["title"],
                "author": book_info["authors"],
                "description": book_info["description"],
            }
        elif similarity > 50:  # Ambang batas kecocokan rendah untuk saran
            return {"suggestion": matched_title}
    return None  # Tidak ada kecocokan

# Fungsi untuk memilih file
def select_file():
    global img, tk_img, img_label
    file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.bmp;*.avif")])
    if file_path:
        img = cv2.imread(file_path)
        if img is None:
            result_label.config(text="Gambar tidak valid!")
        else:
            # Tampilkan gambar di GUI
            img_preprocessed = preprocess_image(img)
            img_rgb = cv2.cvtColor(img_preprocessed, cv2.COLOR_GRAY2RGB)  # Kompatibilitas dengan PIL
            img_pil = Image.fromarray(img_rgb)
            img_pil = img_pil.resize((300, 300), Image.Resampling.LANCZOS)
            tk_img = ImageTk.PhotoImage(img_pil)
            img_label.config(image=tk_img)
            img_label.image = tk_img
            result_label.config(text="Gambar berhasil dimuat, klik 'Proses OCR'.")

# Fungsi untuk menjalankan OCR dan pencarian buku
def process_ocr():
    if img is not None:
        text = ocr_core(img)
        result = search_book(text, dataset)
        result_text.delete("1.0", "end")
        if result:
            if "title" in result:
                result_text.insert(
                    "1.0",
                    f"Hasil OCR: {text}\n\n"
                    f"Buku ditemukan:\n"
                    f"Judul: {result['title']}\n"
                    f"Penulis: {result['author']}\n"
                    f"Deskripsi: {result['description']}",
                )
            elif "suggestion" in result:
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
root.geometry("600x600")

# Memuat dataset
dataset_path = "datas.csv"  # Ganti dengan path ke file dataset Anda
dataset = load_dataset(dataset_path)

# Elemen GUI
Label(root, text="OCR Pencari Buku", font=("Helvetica", 16)).pack(pady=10)
Button(root, text="Pilih Gambar", command=select_file, width=20).pack(pady=10)
img_label = Label(root)
img_label.pack(pady=10)
Button(root, text="Proses OCR", command=process_ocr, width=20).pack(pady=10)
result_label = Label(root, text="", font=("Helvetica", 12))
result_label.pack(pady=10)
result_text = Text(root, height=10, width=70)
result_text.pack(pady=10)

# Jalankan GUI
img = None
root.mainloop()
