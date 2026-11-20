# Peta kod `comp_template.html`

Enjin ialah satu fail HTML dengan `<canvas 1080×1920>`. `render(t)` melukis bingkai pada saat `t` secara deterministik (rawak guna `rng(seed)`), jadi bingkai yang sama sentiasa sama. `render.js` memanggil `render(i/30)` untuk setiap bingkai.

## Zon skrin (selamat untuk UI TikTok)
- 98–160: jenama kecil (logo + "MISI PENJELAJAH CILIK")
- 182–244: cip level (warna ikut level)
- 280–370: tajuk babak (Baloo 2 800, 82–96px)
- 440–1395: zon gambar (`ZT`,`ZB`, lebar maks `ZW=1000`)
- 1430–1514: kapsyen pil
- 1580: dulang 9 lencana (`SLOT_Y`); 1648: bar XP

## Apa yang diubah untuk program baru

1. **`NAMES`**: senarai nama fail gambar (tanpa `.jpg`) dalam `ph/` dan `bg/`.
2. **`LEVELS`**: satu objek per level/sub-misi:
   ```js
   {chip:'LEVEL 3 · THE TOP', stamp:'SUB-MISI', title:'Dunia Jurassic', col:CORAL,
    photos:[...], z:[1,0,...],          // z: 1 zum masuk, 0 zum keluar (selang-seli)
    caps:['kapsyen per gambar', ...],
    badge:['🦖','Penjelajah Dinosaur'],
    boss:true?  calm:true?               // boss: cop merah + meter ketinggian; calm: tempo/muzik lembut
    collage:[5 nama]? collage3:[3 nama]? }
   ```
   Jumlah lencana dulang ialah 9 (`tray()` dan `slotX()` andaikan 9). Ubah jika bilangan level berbeza.
3. **`BUS`**: babak bas 2D sebelum level ke-`li`: `{dest, sub, tod:0 pagi|1 siang|2 petang|3 malam, city:1, deco:'🦖'}`. Menara The TOP dilukis oleh `komtar()`. Gantikan dengan mercu tanda lain atau buang `city`.
4. **`buildTimeline()`**: urutan babak (intro, level, map `m:0/1/2`, bus, done, end, thanks) dan tempoh. `SLIDE=2.5` saat per gambar, `STAMP`, `AWARD`.
5. **Peta 3D**: `LL` (lat/long tempat), `COAST`/`ISLAND` (poligon pantai kasar), `ROUTES[m]` (titik laluan), tajuk peta dalam `drawMap` (`const T=[...]`), km sebenar `[95,32,88][m]`, label pin & ikon. Kamera per peta dalam blok `if(m===0)...`. `CAM.s` ialah px per km dan `tilt` sudut condong.
6. **Teks**: `drawIntro` (nama sekolah, tajuk, baris tarikh), `drawDone` (`lines` papan skor), `drawEnd` (doa, slogan), `drawThanks` (kredit, tarikh). Gambar latar mozek ada dalam `pics`.
7. **Warna**: `NAVY, TEAL, GOLD, CORAL, GREEN`. Selaraskan dengan warna baju/logo sekolah.

## Muzik (`music.py`)
- Baca `timeline.json` (dihasilkan `render.js`). Mod per bar ditentukan `mode_at(t)`: `intro`, `main`, `boss`, `calm` (peta/level dengan "Masjid" dalam tajuk, ubah ikut program), `night`, `outro`.
- Progresi C–G–Am–F, 120 BPM, melodi glockenspiel `MEL` 8 bar. SFX per cue: `shimmer, ding, whoosh, pop, click, horn, stamp, boss, badge, fanfare, engine_<d>`.
- Untuk mood sentimental: kurangkan dram, guna `calm` sepanjang, tempo lebih perlahan (ubah `BEAT/BAR`).

## Semakan pantas
- `node render.js stills 1.8,4.2,...` kemudian `montage` dan baca imej untuk semak tindihan teks, label terpotong di tepi, dan skala peta.
- Masalah lazim yang pernah dibaiki: label pin terkeluar skrin (clamp x), tiang papan tanda melintasi bas (pendekkan), lencana bertindih dulang (pudarkan dulang semasa anugerah), peta terlalu jauh (naikkan `CAM.s`).
