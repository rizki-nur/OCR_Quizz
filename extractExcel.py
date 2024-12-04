import pandas as pd
#C:\Project\OCR Python\Books.xlsx
# Ganti dengan path file Anda
BookLibrary = "data.csv"

# Jika file CSV
try:
    # Abaikan baris yang bermasalah
    data = pd.read_csv(BookLibrary) #, on_bad_lines='skip'
    print("Data berhasil dimuat!")
    print(data.head())  # Menampilkan 5 baris pertama
except Exception as e:
    print(f"Error saat membaca file: {e}")
