# SKINSOLVER-Somethinc-Serum

## 1. Pengenalan Singkat  

**SKINSOLVER** adalah chatbot Discord berbasis **Python** yang dibangun dengan pendekatan **rule-based (regex)** dan mekanisme *reflection* kata ganti. Bot ini membantu pengguna menemukan **serum Somethinc** sesuai tipe kulit dan fokus perawatan — seperti *kulit kusam*, *jerawat*, hingga *anti-aging*.

Dengan interaksi berbasis pola kata kunci, pengguna cukup menjawab pertanyaan sederhana, lalu bot akan memberikan rekomendasi produk yang relevan.

Proyek ini menjadi contoh praktis implementasi **chatbot rule-based sederhana** dengan integrasi **Discord API** untuk edukasi dan panduan kecantikan. 

---

## 2. Cara Setup & Run

Ikuti langkah-langkah berikut untuk menjalankan bot di perangkat Anda:  

* **Buat Discord Bot & Dapatkan Token**
   - Buka [Discord Developer Portal](https://discord.com/developers/applications)
   - Klik **New Application** → beri nama → buat **Bot**
   - Salin **Bot Token** dari tab *Bot*. Token ini yang dipakai di kode Python Anda (DISCORD_TOKEN=...)
     
* **Clone repository**  
   ```bash
   git clone https://github.com/username/skinsolver-bot.git
   cd skinsolver-bot
   ```

* **Buat virtual environment**
    ```bash
   python -m venv venv
   source venv/bin/activate   # Linux/Mac
   venv\Scripts\activate      # Windows

   ```
* **Install requirements**
    ```bash
    pip install -r requirements.txt
    ```

* **Tambahkan Discord Token**  
  Salin `.env.template` menjadi `.env` lalu isi `DISCORD_TOKEN=your_discord_token_here` (ganti dengan token Discord Anda)

* **Jalankan bot**
  ```bash
   python bot.py
   ```
---

  ## 3. Demo
  <img width="1740" height="1336" alt="Image" src="https://github.com/user-attachments/assets/1e592ad5-2966-4f16-9551-d389adb9a6c2" />
  Klik di sini untuk lihat video demo
  <a href="https://github.com/user-attachments/assets/46f73b63-1992-412e-9943-ef52f18f212d">
    SKINSOLVER-Somethinc-Serum
  </a>
   
---

  ## 4. Alasan Pembuatan Bot

  Bot ini dibuat karena banyak pengguna skincare, khususnya pemula, sering kebingungan memilih produk yang sesuai dengan masalah kulit mereka.
Dengan adanya SKINSOLVER, pengguna dapat mendapatkan rekomendasi cepat dan informatif langsung dari Discord server, tanpa harus membaca ulasan panjang atau mencari info secara manual.
Selain itu, bot ini juga menjadi sarana pembelajaran kami dalam mengembangkan chatbot interaktif berbasis Python dan Discord API.

---

## 5. Sumber

Sumber utama yang digunakan dalam bot ini adalah **decision tree rekomendasi serum resmi dari Skintific**.  
Decision tree tersebut dipilih karena:  

- Memberikan panduan terstruktur dalam pemilihan produk sesuai **tipe kulit** dan **masalah utama kulit**.  
- Memastikan rekomendasi bot tetap **konsisten dengan standar brand resmi**, bukan opini pribadi.  
- Membantu pengguna dalam **proses pengambilan keputusan yang cepat dan mudah**, tanpa harus membaca deskripsi produk satu per satu.  
- Menjadi dasar logika sederhana yang dapat diimplementasikan ke dalam bot Discord dengan format percabangan (if-else atau mapping).  

Berikut visualisasi decision tree dari Skintific yang menjadi rujukan:  

![Image](https://github.com/user-attachments/assets/6b78cd60-136b-410c-b00d-baa3da1179bf)  
![Image](https://github.com/user-attachments/assets/95ff9492-0df4-4835-879c-cd5526a4312e)  
![Image](https://github.com/user-attachments/assets/ea276b86-867a-4d60-b6c6-185c3a4af28d)  

Selain itu, tutorial dari video youtube [How to Build a Discord Bot With Python - Full Tutorial 2025+](https://youtu.be/YD_N6Ffoojw?si=UddLO1FfyahCuh8v) digunakan sebagai acuan pengintegrasi bot dalam discord.

---

## 6. Team
- Satama Safika (22/492880/TK/53955)
- Danella Zefanya Siahaan (22/492877/TK/53953)
