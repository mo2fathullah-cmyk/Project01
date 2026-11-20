---
name: video-montaj-lawatan
description: Hasilkan video montaj premium (gaya penyiaran Astro / Media Prima) untuk lawatan sekolah, rombongan, program atau perjalanan kanak-kanak daripada gambar-gambar rawak pengguna, lengkap dengan pembukaan logo, peta laluan 3D, animasi bas 2D antara lokasi, konsep "level permainan" dengan lencana dan bar XP, muzik latar asal bebas hak cipta, serta versi TikTok 9:16 dan WhatsApp. Gunakan skill ini setiap kali pengguna mahu video montaj, video kenangan, video penutup program, video TikTok/Reels lawatan sambil belajar, rombongan sekolah, PASTI, tadika atau program kanak-kanak, atau menghantar gambar mengikut lokasi dan meminta video "masterpiece", walaupun mereka tidak menyebut perkataan "montaj".
---

# Video Montaj Lawatan ("Misi Penjelajah Cilik")

Skill ini merakam cara kerja yang menghasilkan video montaj lawatan SRAZ ke The TOP Penang (18.11.2026) dan montaj Jelajah Cilik PASTI Al-Huda (17.11.2026). Pengguna (seorang waris/ibu bapa dan staf UniMAP) menulis dalam Bahasa Melayu santai; balas dalam bahasa yang sama.

Hasil akhirnya ialah video MP4 1080×1920 yang dirender sendiri (canvas HTML + Playwright + ffmpeg), bukan sekadar papan cerita.

## 1. Aliran kerja dengan pengguna

Pengguna suka dirunding dulu, bukan terus dijana. Ikut urutan ini:

1. **Fahamkan brief.** Baca tentatif/poster program (biasanya gambar). Kenal pasti sekolah, tarikh, lokasi, masa.
2. **Tanya ~5 soalan sebelum mula**, contohnya video rujukan, format (TikTok 9:16?), muzik/mood, panjang, angka peserta & kredit. Kalau pengguna kata "kau cadangkan", buat pilihan sendiri dan nyatakan.
3. **Terima gambar senyap-senyap.** Pengguna hantar gambar berkelompok dan akan kata **"selesai"**. Selepas setiap kelompok:
   - Buang gambar yang sama/hampir sama (pose sama, sudut sama), simpan yang paling jelas/paling ramai wajah. Versi **menegak** lebih baik untuk TikTok.
   - Agak sendiri lokasi setiap gambar (pengguna kata "kau agak la") dan senaraikan dalam jadual: Babak | Gambar.
   - Nyatakan gambar yang dibuang & sebabnya, gambar kabur yang perlu keputusan, dan babak yang masih kosong.
   - Salin gambar ke repo dengan nama berawalan mengikut urutan cerita (`01_bas_...`, `06c_jurassic_...`) supaya susunan jelas.
4. **Cadang 3 konsep papan cerita**, setiap satu dengan idea, logo pembuka, peta 3D, aliran, "kelainan" dan muzik. Beri cadangan pilihan.
5. **Papan cerita visual** untuk konsep yang dipilih: halaman Artifact dengan bingkai 9:16 gambar sebenar per babak, garis masa, lencana dan senarai "perlu disahkan".
6. **Produksi video penuh** (bahagian 3). Tunjuk pratonton bingkai kepada diri sendiri (helaian kontak) dan baiki sebelum render penuh.
7. **Hantar** versi WhatsApp (render inline) + versi TikTok + kulit (attach), dan senarai semakan ringkas.

Pengguna kerap menambah fakta/gambar/teks di tengah render. Kumpul perubahan, hentikan render (`pkill -f "render.js full"`), kemas kini, jana semula muzik jika garis masa berubah, dan render semula. Galakkan pengguna memberi semua pembetulan teks sekaligus.

## 2. Citarasa pengguna (dipelajari daripada pembetulan sebenar)

Ini datang daripada aduan sebenar. Hormati semuanya kerana pengguna akan perasan:

- **Tahap "wow" penyiaran**: premium, sinematik, tertib, "orang terkedu". Elak rupa amatur: pakai kad gambar berbingkai putih + bayang, latar kabur gambar sama, light leak, bokeh, grain halus, vignette.
- **Gerakan perlahan**: zum masuk/keluar perlahan (≈1.0→1.1 sepanjang slaid), bukan close-up laju. Setiap gambar ≥2.5 s. "Video laju tak match muzik" ialah aduan utama.
- **Semua gambar yang diberi mesti dipakai** (kecuali pendua/kabur yang disahkan). Gambar mesti besar dan **tidak dilindung teks**.
- **Tajuk babak kekal kelihatan** di zon atas, tidak ditindih gambar. Teks kapsyen dalam pil gelap di bawah kad.
- **Isi ruang**: tiada ruang kosong besar. Gambar lebar dipan perlahan, kolaj untuk kumpulan gambar makan.
- **Teks penutup/terima kasih kekal ≥4 s** supaya sempat dibaca.
- **Kredit**: tanya. Untuk SRAZ: "Terima kasih kepada para guru yang terlibat · Ikhlas daripada **para waris**". Jangan tulis "seorang waris" kerana video mewakili semua.
- **Fakta sebenar** menambah nilai (cth. "Rainbow Skywalk tingkat 68", "16 tarikan dalam satu menara", nama tarikan sebenar). Guna fakta yang pengguna beri, jangan reka.
- **Masa perjalanan sebenar** pada peta (cth. "Bertolak 8.45 malam · tiba ± 10.00 malam") dan suasana ikut waktu: siang → senja → malam berbintang.
- **Sentuhan Islamik** sesuai: doa ilmu رَبِّ زِدْنِي عِلْمًا, slogan sekolah, "praktikal solat jamak Maghrib & Isyak".
- Wajah kanak-kanak boleh ditunjuk jelas (pengguna sahkan), tiada pengaburan.

## 3. Enjin produksi

Fail dalam skill ini:

| Fail | Guna |
|---|---|
| `scripts/prep_assets.sh` | gred gambar, latar kabur, logo bulat 720px, muat turun font Baloo 2 / Nunito / Amiri |
| `assets/comp_template.html` | enjin animasi canvas 1080×1920 (contoh lengkap SRAZ). Salin sebagai `comp.html` dan ubah data |
| `scripts/render.js` | Playwright: `stills t1,t2,..` untuk semakan, `full out.mp4 30` untuk render penuh; tulis `timeline.json` |
| `scripts/music.py` | muzik asal (ukulele, glockenspiel, bass, dram ringan, pad) + SFX ikut `timeline.json` (numpy sahaja) |
| `scripts/finish.sh` | mux, loudnorm −14 LUFS, versi TikTok & WhatsApp, kulit, helaian QC |
| `references/engine.md` | peta kod `comp_template.html`: apa yang perlu diubah untuk program baru |

Langkah:

```bash
W=<scratchpad>/video; mkdir -p $W && cp assets/comp_template.html $W/comp.html && cp scripts/{render.js,music.py} $W/
bash scripts/prep_assets.sh <folder_gambar> <logo.jpg> $W
# edit $W/comp.html mengikut references/engine.md
cd $W && (python3 -m http.server 8765 --bind 127.0.0.1 >/dev/null 2>&1 &)
node render.js stills 2,5,9,20,40,60     # semak; buat helaian dengan `montage stills/t*.jpg -tile 5x2 -geometry 324x576+6+6 m.jpg` dan Read
node render.js full video_noaudio.mp4 30 # ~12 fps render, jalankan di latar belakang
python3 music.py                         # selepas timeline.json terkini
bash scripts/finish.sh $W <folder_output> <NamaVideo>
```

Nota teknikal penting:
- **Mesti guna pelayan http tempatan.** Gambar dari `file://` mencemari canvas dan `toDataURL` gagal.
- Render penuh ≈ 6–7 minit untuk 2.5 minit video. Jalankan di latar belakang dan beri update ringkas.
- Fail MP4 tidak di-commit (`.gitignore *.mp4`). Commit gambar, papan cerita dan sumber produksi sahaja.
- Logo 240px akan nampak lembut bila dibesarkan. Minta fail logo resolusi tinggi jika ada.
- Muzik disintesis sendiri, jadi bebas hak cipta. Kau tidak boleh mendengarnya, jadi semak tahap bunyi sahaja dan **beritahu pengguna untuk dengar dulu**. Mereka boleh tukar muzik dalam TikTok.
- Jangan guna `rm` dengan glob relatif selepas `cd`, kerana semakan keselamatan akan menolaknya. Guna folder baharu atau laluan mutlak.

## 4. Struktur cerita lalai (konsep "Misi")

Pembukaan logo (≈6 s: titik cahaya → logo + kilauan emas → "MISI PENJELAJAH CILIK" → butang MULA ▶) → Level 1 (naik bas) → **peta 3D** bandar asal ➜ destinasi → Level 2 (tiba) → **bas 2D** dengan papan tanda hijau JKR "SETERUSNYA ➜ <tarikan>" antara setiap tarikan → Level/Sub-misi per tarikan (cop "LEVEL n" / "SUB-MISI" → slaid → **lencana baru** terbang ke dulang) → Level Bos (tarikan paling hebat, dengan meter/angka khas) → peta senja ke persinggahan → level persinggahan (tempo lembut) → peta malam pulang + "Selamat pulang! 🏠" → **MISI SELESAI!** (gambar kumpulan, papan skor, konfeti, XP 100%) → kad doa ilmu + "LEVEL SETERUSNYA ▶" → kad terima kasih → pudar hitam.

Konsep lain (buku skrap/diari, "Dari Bumi ke Langit", sentimental emas petang dengan piano) boleh dibina dengan enjin yang sama dengan menukar `LEVELS`, gaya HUD dan mod muzik.
