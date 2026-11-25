# Stop the Tugas — PyScript + Flask
Fresh installation; no Django, Jinja, JWT or login. Python 3.12 recommended. Public collaboration means anyone can edit/delete shared data; do not upload private or copyrighted material without permission. Creator is self-declared.

## Local (Windows CMD)
```
py -3.12 -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
python -m unittest discover -s tests -v
python run.py
```
Open http://127.0.0.1:5000 and http://127.0.0.1:5000/api/health. Linux/macOS: `python3 -m venv .venv`, `source .venv/bin/activate`, `cp .env.example .env`. SQLite tables are created automatically locally. Internet is required for Tailwind, Google Fonts and PyScript runtime; first load can take more than 1–2 seconds. Use desktop Chrome/Edge/Firefox for native PDF viewer. No Node build.

## Production (one Vercel project)
1. Create Supabase project, private Storage bucket `materials`, limit 4 MiB, MIME application/pdf. Get database connection string (session pooler for IPv4; SSL required), project URL and service role key. Never expose key to browser/GitHub.
2. Set Vercel root directory to repository root (not api/backend/frontend), framework Flask, Python 3.12. Entry `api/index.py` exports app. `vercel.json` includes frontend in function bundle. Flask serves HTML and Python source via explicit routes on same origin. Do not add blanket rewrites unless deployment logs indicate a routing issue.
3. Set production environment variables: DATABASE_URL=postgresql://...?...sslmode=require (use correct query separator); STORAGE_BACKEND=supabase; SUPABASE_URL=https://PROJECT.supabase.co; SUPABASE_SERVICE_ROLE_KEY=...; SUPABASE_STORAGE_BUCKET=materials. No CORS needed. Vercel must not use SQLite or local media.
4. Initialize tables once before first deploy: in local shell temporarily set DATABASE_URL to production connection string and STORAGE_BACKEND=local, run `python -m flask --app api.index init-db`; reset env to local afterward. SQLAlchemy create_all is for fresh schema only; use Alembic for future schema changes.
5. For an empty repository: `git init`, `git add .`, `git commit -m "PyScript Flask baseline"`, `git branch -M main`, `git remote add origin https://github.com/constellation-a2/stop-the-tugas.git`, `git push -u origin main`. For existing repository clone and use separate branch/PR, do not force push. Import repo in Vercel and deploy once.
6. Verify `/api/health`, all five pages, create/edit/delete event, upload/preview/download/delete PDF including exact 4 MiB file, filter/search, countdown, persistence after redeploy. Vercel's standard payload limit is 4.5 MB; app limits request to 4 MiB + 64 KiB and PDF to 4 MiB. Test real deployment. If browser lacks inline viewer, use download.

## Team ownership
B: backend/reminders_bp.py and frontend/py/reminders.py. C: backend/calendar_bp.py, frontend/py/calendar_ui.py, kalender/jadwal/tugas.html. D: backend/library_bp.py, storage.py, frontend/py/library_ui.py, perpustakaan.html. Shared models and app factory require coordinated PR. Dates entered WIB (+07:00), persisted UTC; reminder tiers H-7 (4–7 days), H-3 (2–3), H-1 (1), H-0 (today); upcoming classes today show minute countdown. Calendar entries are one-off, not recurring. Reminder is in-app only.

## Limitations and testing
Syntax/static checks only in authoring environment if dependencies unavailable; run tests locally. Supabase/Vercel and PyScript browser runtime need live testing. File header validation is not antivirus or complete PDF parsing. Public mutation is intentionally anonymous; add abuse controls, backup and moderation before broad release. Storage deletion errors are logged for orphan cleanup. CDN styling requires connectivity. License not selected; agree with team before publishing as open source.

## SPA update
Only index.html is loaded. Menu uses #dashboard, #kalender, #jadwal, #tugas, #perpustakaan; legacy page paths redirect to hashes. All five views share one PyScript runtime and event cache. No additional PyScript packages. First cold boot depends on network, device and CDN; a sub-two-second boot is not guaranteed. Browser back/forward works through hashchange. Theme is saved to localStorage. On small screens the sidebar is a drawer and calendar scrolls horizontally. Month and week grids open date detail; agenda mode lists the selected month.

Upload now uses a native JavaScript FormData(form) bridge, after Python validates the actual file input. Drop uses DataTransfer to populate that input. All multipart fields have names. Submit default is prevented synchronously, before asynchronous Python work. Backend API and schema remain compatible; keep your existing db.sqlite3, media/ and .env when updating (back up first). Replace frontend folder entirely to remove obsolete HTML files. No database migration required.

Browser acceptance: open DevTools Network (Preserve log); navigate between all five hashes and confirm no additional document/PyScript runtime requests. Test back/forward, theme after reload, drawer on mobile, date detail and prefilled date, invalid PDF, upload via picker and drop, preview/download and deletion. Cold start timing and actual browser/CDN behavior must be measured locally.

### Upload hotfix
Raised multipart parser memory limit from 64 KiB to 512 KiB to avoid rejecting valid PDF uploads during multipart decoding. Actual file limit remains 4 MiB. Regression tests cover 64 KiB, approximately 368.4 KiB, 1 MiB and 4 MiB.

## V3: Rentang waktu dan startup non-blocking

- `ends_at` menyimpan waktu selesai dalam ISO UTC. Kuliah baru wajib memiliki waktu selesai; tugas boleh kosong (waktu mulai adalah tenggat). Rentang lintas tengah malam didukung dan ditampilkan bersama tanggal selesai; kalender mengelompokkan event berdasarkan tanggal mulai.
- Upgrade SQLite otomatis menambahkan kolom nullable tanpa menghapus data. Agenda lama tetap tampil dengan jam mulai saja; edit untuk melengkapi jam selesai. Backup `db.sqlite3`, `.env`, dan `media/` sebelum update. PostgreSQL produksi lama: backup dan jalankan `python -m flask --app api.index init-db` dengan DATABASE_URL produksi sebelum deploy.
- Initial render HTML + `frontend/py/initial.js` membaca data langsung dari API dan mengaktifkan navigasi, tema, dan drawer sebelum Python siap. Python mengambil alih kontrol CRUD, filter, dan preview. Tidak ada overlay blocking. Pyodide tetap dipakai dengan nol package tambahan agar kompatibel dengan datetime, calendar, asyncio, dan FFI; MicroPython bukan pengganti drop-in. Target 0,3 detik belum diukur dan tidak dijamin. CDN tetap dibutuhkan.
- Setelah ekstrak, di PowerShell masuk ke folder yang berisi `run.py`: `cd stt-pyscript` (jika masih berada di folder luar). `python -m venv .venv`; `.\.venv\Scripts\python.exe -m pip install -r requirements.txt`; `Copy-Item .env.example .env` (hanya instalasi baru); `.\.venv\Scripts\python.exe run.py`.
- Tes: `.\.venv\Scripts\python.exe -m unittest discover -s tests -v`. Uji juga render sebelum Python siap, navigasi hash, dark mode, kalender dan upload PDF 368 KB di browser.
