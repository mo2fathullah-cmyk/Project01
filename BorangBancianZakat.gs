/**
 * BORANG BANCIAN PENERIMA ZAKAT
 * ------------------------------------------------------------
 * Skrip ini mencipta Google Form + Google Sheet respons secara automatik,
 * dan menukar semua jawapan kepada HURUF BESAR sebaik sahaja dihantar.
 *
 * CARA GUNA:
 * 1. Buka https://script.google.com  >  "Projek baharu"
 * 2. Padam kod sedia ada, tampal SEMUA kod ini, tekan Simpan.
 * 3. Pilih fungsi "ciptaBorangZakat" di bar atas, tekan "Jalankan".
 * 4. Benarkan akses (Semak kebenaran > pilih akaun > Lanjutan > Pergi ke projek).
 * 5. Buka "Log pelaksanaan" untuk dapatkan pautan borang & spreadsheet.
 * Jalankan SEKALI sahaja (setiap kali dijalankan, borang baru akan dicipta).
 */

function ciptaBorangZakat() {
  var form = FormApp.create('BORANG BANCIAN PENERIMA ZAKAT');
  form.setDescription(
    'Sila isi semua maklumat dengan lengkap dan benar.\n' +
    'Semua jawapan akan disimpan dalam HURUF BESAR secara automatik.\n' +
    'Maklumat anda adalah SULIT dan hanya digunakan untuk tujuan bancian zakat.'
  );
  form.setProgressBar(true);
  form.setAllowResponseEdits(false);
  form.setConfirmationMessage(
    'TERIMA KASIH. Maklumat anda telah berjaya direkodkan.'
  );

  // ---------------- BAHAGIAN A ----------------
  form.addSectionHeaderItem().setTitle('BAHAGIAN A: MAKLUMAT PEMOHON');

  teks_(form, 'NAMA PENUH (SEPERTI DALAM KAD PENGENALAN)', '', null, null);

  teks_(form, 'NO. KAD PENGENALAN',
    'Contoh: 800101-09-1234',
    '^\\d{6}-\\d{2}-\\d{4}$',
    'Sila ikut format 800101-09-1234 (dengan tanda -)');

  teks_(form, 'NO. TELEFON',
    'Contoh: 012-3456789',
    '^0\\d{1,2}-\\d{7,8}$',
    'Sila ikut format 012-3456789 (dengan tanda -)');

  form.addParagraphTextItem()
    .setTitle('ALAMAT RUMAH')
    .setHelpText('Alamat penuh termasuk poskod dan negeri')
    .setRequired(true);

  // ---------------- BAHAGIAN B ----------------
  form.addPageBreakItem().setTitle('BAHAGIAN B: MAKLUMAT TANGGUNGAN');

  var regexBilangan = '^\\d{1,2}$';
  var mesejBilangan = 'Sila isi nombor sahaja (contoh: 0, 1, 2)';
  teks_(form, 'BILANGAN ANAK YANG MASIH BERSEKOLAH', 'Isi 0 jika tiada', regexBilangan, mesejBilangan);
  teks_(form, 'BILANGAN ANAK YANG BEKERJA', 'Isi 0 jika tiada', regexBilangan, mesejBilangan);
  teks_(form, 'BILANGAN TANGGUNGAN SELAIN ANAK', 'Contoh: ibu bapa, adik-beradik. Isi 0 jika tiada', regexBilangan, mesejBilangan);

  // ---------------- BAHAGIAN C ----------------
  form.addPageBreakItem().setTitle('BAHAGIAN C: MAKLUMAT PENDAPATAN');

  var regexRM = '^(\\d+(\\.\\d{1,2})?|[Tt][Ii][Dd][Aa][Kk] [Bb][Ee][Rr][Kk][Ee][Nn][Aa][Aa][Nn])$';
  var mesejRM = 'Isi nombor sahaja tanpa RM dan koma (contoh: 1500), atau tulis TIDAK BERKENAAN';

  teks_(form, 'PENDAPATAN BULANAN SUAMI (RM)',
    'Contoh: 1500. Tulis TIDAK BERKENAAN jika tiada.', regexRM, mesejRM);

  teks_(form, 'PENDAPATAN BULANAN ISTERI (RM)',
    'Contoh: 1200. JIKA TIADA, TULIS: TIDAK BERKENAAN', regexRM, mesejRM);

  form.addGridItem()
    .setTitle('ADAKAH ANDA MENERIMA BANTUAN / PENDAPATAN BERIKUT?')
    .setHelpText('Sila tandakan YA atau TIDAK bagi setiap satu')
    .setRows(['PERKESO (SOCSO)', 'JABATAN KEBAJIKAN MASYARAKAT (JKM)', 'ZAKAT'])
    .setColumns(['YA', 'TIDAK'])
    .setRequired(true);

  // ---------------- BAHAGIAN D ----------------
  form.addPageBreakItem().setTitle('BAHAGIAN D: AKUAN PEMOHON');

  form.addCheckboxItem()
    .setTitle('AKUAN')
    .setChoiceValues([
      'SAYA MENGESAHKAN BAHAWA SEMUA MAKLUMAT YANG DIBERIKAN ADALAH BENAR, ' +
      'DAN JIKA SAYA BERDUSTA, IA ADALAH SATU DOSA ATAS DIRI SAYA.'
    ])
    .setRequired(true);

  // ---------------- SPREADSHEET RESPONS + HURUF BESAR ----------------
  var ss = SpreadsheetApp.create('RESPONS - BORANG BANCIAN PENERIMA ZAKAT');
  form.setDestination(FormApp.DestinationType.SPREADSHEET, ss.getId());
  ScriptApp.newTrigger('hurufBesar').forSpreadsheet(ss).onFormSubmit().create();

  Logger.log('PAUTAN BORANG (edarkan kepada responden): ' + form.getPublishedUrl());
  Logger.log('PAUTAN EDIT BORANG: ' + form.getEditUrl());
  Logger.log('SPREADSHEET RESPONS: ' + ss.getUrl());
}

/** Tukar setiap jawapan yang baru dihantar kepada HURUF BESAR. */
function hurufBesar(e) {
  var range = e.range;
  var baris = range.getValues()[0].map(function (v) {
    return typeof v === 'string' ? v.toUpperCase() : v;
  });
  range.setValues([baris]);
}

function teks_(form, tajuk, bantuan, regex, mesej) {
  var item = form.addTextItem().setTitle(tajuk).setRequired(true);
  if (bantuan) item.setHelpText(bantuan);
  if (regex) {
    item.setValidation(
      FormApp.createTextValidation()
        .requireTextMatchesPattern(regex)
        .setHelpText(mesej)
        .build()
    );
  }
  return item;
}
