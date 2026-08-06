# ✈️ Aviation Crosswind Early Warning System (ACEWS) Prototype

> **Purwarupa Sistem Peringatan Dini Angin Silang (Crosswind) Aviasi Berbasis Logic Control, Data Pipeline, dan Antarmuka HMI Visualisasi Radar 2D.**

---

## 📌 Latar Belakang & Konteks Proyek

Proyek ini dikembangkan secara **Mandiri (Independent Project)** sebagai bagian dari program **Magang / Praktik Kerja Lapangan di BMKG Batam (Stasiun Meteorologi Hang Nadim Batam)**.

> [!IMPORTANT]
> **Pernyataan Data Dummy (Mock Data)**:
> Seluruh data parameter cuaca (seperti *Wind Speed*, *Wind Direction*, dan *Runway Heading*) yang digunakan dalam purwarupa ini adalah **DATA SIMULASI / TIRUAN (DUMMY DATA)** yang dibangkitkan khusus untuk pengujian logika alur data, evaluasi ambang batas bahaya, dan demonstrasi antarmuka HMI visual.

---

## 💡 Masalah & Solusi (Problem & Solution)

### Tantangan Meteorologi Aviasi
Angin silang (*crosswind*) dengan kecepatan tinggi merupakan salah satu faktor risiko paling kritis dalam dunia penerbangan. Dorongan gaya lateral akibat angin silang dapat mengganggu stabilitas aerodinamik pesawat pada fase yang paling krusial, yaitu **Pendaratan (*Landing*)** dan **Lepas Landas (*Take-off*)**.

### Solusi ACEWS
**ACEWS (Aviation Crosswind Early Warning System)** dirancang sebagai purwarupa solusi otomatisasi pemantauan angin silang. Sistem ini mengolah trigonometri komponen vektor angin secara *real-time* terhadap orientasi landasan pacu (*Runway Heading*), lalu memberikan kalkulasi presisi komponen *Crosswind* dan *Headwind/Tailwind* beserta status peringatan dini berjenjang (*Early Warning Status*) pada antarmuka *Control Room HMI*.

$$\text{Relative Angle } (\theta) = \text{Wind\_Dir} - \text{Runway\_Head}$$

$$\text{Crosswind Component} = |\text{Wind\_Speed} \times \sin(\theta)|$$

$$\text{Headwind Component} = \text{Wind\_Speed} \times \cos(\theta)$$

---

## 🏗️ Arsitektur Sistem (3-Tier Architecture)

```
  +-----------------------+      +-----------------------+      +-------------------------------+
  |   LOGIKA KONTROL PLC  | ---> | DATA PIPELINE BROKER  | ---> |     HMI CONTROL ROOM DASHBOARD|
  |  (OpenPLC / Ladder)   |      |      (Node-RED)       |      |   (Python Flask & Canvas 2D)  |
  +-----------------------+      +-----------------------+      +-------------------------------+
```

1. **Tier 1: Logic Control (OpenPLC / PLC Diagram Ladder)**
   - Mengolah variabel masukan analog/digital meteorologi.
   - Menggunakan operasi matematika desimal (`INT_TO_REAL`, `SUB`, `SIN`, `MUL`, `ABS`) untuk menentukan besaran komponen crosswind dan mengaktifkan output alarm logika dasar.
2. **Tier 2: Integration & Data Broker (Node-RED)**
   - Menghubungkan alur data telemetry JSON secara periodik dari sensor/simulasi ke backend server melalui protokol REST API HTTP POST (`/update-data`).
3. **Tier 3: HMI Control Room (Python Flask & Canvas 2D Tactical Visualizer)**
   - Menyediakan backend server Flask yang memproses telemetri dan antarmuka web taktis berbasis *Aero Dark Glassmorphic Theme*.
   - Menampilkan proyeksi kompas radar 2D landasan pacu yang berputar dinamis berikut panah vektor angin dan kartu indikator telemetri.

---

## 🚀 Fitur-Fitur Utama Dashboard HMI

- 🎯 **Visualisator Radar 2D Landasan Pacu (Runway Visualizer)**:
  - Landasan pacu 2D interaktif (lengkap dengan marka *piano keys*, *centerline*, dan nomor penanda runway e.g. RWY 09/27) yang berputar secara otomatis sesuai sudut *Runway Heading*.
  - Panah vektor arah angin utama (*Wind Vector Arrow*) yang menunjuk dari asal bertiupnya angin.
  - Panah komponen *Crosswind* lateral (menunjukkan arah dorongan angin dari Kanan/Kiri landasan).
- 📊 **Kartu Telemetri Real-Time**:
  - Kecepatan Angin (knots & km/jam).
  - Arah Angin (°M & Kardinal N/E/S/W).
  - Runway Heading (°M & Designator Runway).
  - Komponen Crosswind (knots & label dorongan Kanan/Kiri).
  - Komponen Headwind/Tailwind (knots & status Headwind/Tailwind).
- 🚨 **Sistem Alert Bahaya Berjenjang (Multi-Threshold Alarm)**:
  - 🟢 **SAFE**: Crosswind < 10.0 knots *(Landasan aman untuk operasional)*
  - 🟡 **CAUTION**: Crosswind 10.0 - 14.9 knots *(Crosswind moderat, tingkatkan kewaspadaan)*
  - 🟠 **WARNING**: Crosswind 15.0 - 19.9 knots *(Crosswind tinggi, peringatan dini)*
  - 🔴 **CRITICAL**: Crosswind ≥ 20.0 knots *(BAHAYA: Melebihi batas aman pendaratan!)*
- ⚡ **Modul Simulasi Otomatis (Auto-Simulation Engine)**:
  - Memiliki tombol toggle `▶ JALANKAN SIMULASI OTOMATIS` untuk menguji animasi visualizer tanpa server eksternal.
  - Menyediakan 4 Skenario Cuaca Dinamis: *Normal*, *Crosswind Moderat*, *Badai & Gust Ekstrem*, dan *Rotasi Sudut 360°*.
- 🌐 **Netlify Standalone Deployment Ready**:
  - Menyediakan versi 100% client-side HTML mandiri di folder `netlify_deploy/` untuk langsung di-upload ke Netlify Drop.

---

## 📁 Struktur Repositori

```
hmi_aviation/
│
├── README.md                           # Dokumentasi resmi proyek
├── requirements.txt                    # Dependensi Python Flask
├── .gitignore                          # Filter pengabaian Git
│
├── hmi_aviation/                       # Modul Backend Flask & Template HMI Local
│   ├── app.py                          # Server Flask dengan Kalkulasi Vektor Otomatis
│   ├── index_netlify.html              # Salinan HMI Standalone Netlify
│   └── templates/
│       └── index.html                  # Template HMI Dashboard Control Room
│
├── netlify_deploy/                     # Folder Siap Upload ke Netlify (Drag & Drop)
│   └── index.html                      # Single-File Interactive HMI Dashboard
│
└── plc_openplc/                        # berkas logika PLC & OpenPLC Project
    ├── plc.xml                         # Diagram Ladder & Blok Fungsi OpenPLC
    └── project.json                    # Konfigurasi Proyek OpenPLC
```

---

## 🛠️ Cara Menjalankan Proyek

### Opsional A: Menjalankan Server Local Python Flask
1. Clone repositori ini:
   ```bash
   git clone https://github.com/USERNAME/ACEWS-Prototype.git
   cd ACEWS-Prototype
   ```
2. Pastikan Python sudah terinstal, lalu pasang dependensi:
   ```bash
   pip install -r requirements.txt
   ```
3. Jalankan server Flask:
   ```bash
   cd hmi_aviation
   python app.py
   ```
4. Buka peramban dan akses: **`http://127.0.0.1:5000`**

---

### Opsional B: Deploy Langsung ke Netlify (Tanpa Installation)
1. Kunjungi **[app.netlify.com/drop](https://app.netlify.com/drop)**.
2. Drag & drop folder **`netlify_deploy`** ke halaman tersebut.
3. Website HMI ACEWS langsung aktif secara publik dengan fitur simulasi cuaca otomatis!

---

## 🎓 Pengakuan & Ucapan Terima Kasih

Proyek purwarupa ini diselesaikan sebagai bagian dari kegiatan **Magang / Praktik Kerja Lapangan di BMKG Batam (Stasiun Meteorologi Hang Nadim Batam)**. Ucapan terima kasih disampaikan kepada seluruh pembimbing dan teknisi di BMKG Batam atas dorongan dan ilmu yang diberikan selama masa magang.

---
*Dikembangkan oleh peserta magang BMKG Batam - Fikri Rizkia Prisyabil • 2026*
