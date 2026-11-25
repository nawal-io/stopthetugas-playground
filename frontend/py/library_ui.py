from ui_helpers import *
from api import api
import json
from js import DataTransfer
materials=[]; courses=[]; selected=''; chosen=None

def render():
    el('tabs').innerHTML=''.join(f'<button data-course="{safe(c)}" class="whitespace-nowrap rounded-full border px-3 py-2 text-xs font-semibold {"bg-indigo-600 text-white border-indigo-600" if c==selected else "bg-white dark:bg-slate-900 text-slate-600 dark:text-slate-300 border-slate-200 dark:border-slate-800"}">{safe(c or "Semua File")} · {sum(not c or m["course"]==c for m in materials)}</button>' for c in ['']+courses)
    q=str(el('search').value).strip().lower(); items=[m for m in materials if (not selected or m['course']==selected) and q in ' '.join(m[k] for k in ('title','creator','course')).lower()]
    el('material-count').textContent=str(len(items))+' materi'
    el('materials').innerHTML=''.join(f'''<article class="flex flex-col rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 p-5 min-w-0"><div class="flex items-start gap-2"><span class="rounded-md bg-rose-50 px-2 py-1 text-xs font-bold text-rose-700 dark:text-rose-300">PDF</span><span class="flex-1 text-xs text-slate-500 dark:text-slate-400 break-words">{safe(m['course'])}</span><button data-delete="{m['id']}" aria-label="Hapus materi" class="rounded-md p-2 text-slate-500 dark:text-slate-400 hover:bg-rose-50 hover:text-rose-700"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"><path d="M3 6h18M9 6V3h6v3M6 6l1 15h10l1-15M10 10v7M14 10v7"/></svg></button></div><h3 class="mt-4 font-semibold text-slate-900 dark:text-slate-100 break-words">{safe(m['title'])}</h3><p class="mt-2 text-sm text-slate-600 dark:text-slate-300 break-words">Oleh: {safe(m['creator'])}</p><p class="mt-1 text-xs font-medium text-slate-500 dark:text-slate-400 tabular-nums">{stamp(m['created_at'])} · {m['size']/1024:.0f} KB</p><div class="mt-auto pt-5 grid grid-cols-2 gap-2"><button data-preview="{m['id']}" class="rounded-lg border border-slate-300 dark:border-slate-700 px-3 py-2 text-sm font-medium hover:bg-slate-50 dark:hover:bg-slate-800">Preview</button><a href="/api/library/download/{m['id']}" class="rounded-lg bg-indigo-600 px-3 py-2 text-center text-sm font-medium text-white hover:bg-indigo-700">Unduh</a></div></article>''' for m in items) or '<div class="col-span-full rounded-xl border border-dashed border-slate-300 dark:border-slate-700 p-10 text-center text-sm text-slate-500 dark:text-slate-400">Belum ada materi yang cocok.</div>'

async def refresh():
    global materials,courses
    result=await api('library'); materials=result['materials']; courses=result['courses']; el('course').innerHTML='<option value="">Pilih mata kuliah</option>'+''.join(f'<option>{safe(c)}</option>' for c in courses); render()

def pick(file):
    global chosen
    chosen=None; el('file-info').textContent='Tarik PDF atau klik untuk memilih'; el('upload-submit').disabled=True
    if not file: return
    if not str(file.name).lower().endswith('.pdf') or file.size>4*1024*1024 or file.size<5:
        el('file-info').textContent='Pilih PDF yang valid, maksimal 4 MB.'; return
    chosen=file; el('file-info').textContent=f'{file.name} · {file.size/1024:.1f} KB'; el('upload-submit').disabled=False

def drop(e):
    e.preventDefault()
    file=e.dataTransfer.files.item(0)
    if file:
        transfer=DataTransfer.new(); transfer.items.add(file); el('file').files=transfer.files
    pick(el('file').files.item(0))
def drag(e): e.preventDefault()
def open_upload(e):
    el('upload-form').reset(); el('upload-error').textContent=''; pick(None); show('upload-modal')
async def submit(e):
    e.preventDefault()
    pick(el('file').files.item(0))
    if chosen is None:
        el('upload-error').textContent='Pilih PDF yang valid, maksimal 4 MB.'; return
    button=el('upload-submit'); button.disabled=True; el('upload-error').textContent=''
    try:
        result=json.loads(str(await window.uploadPdfForm('upload-form')))
        if not result['ok']:
            try: msg=json.loads(result['data']).get('error')
            except Exception: msg=None
            raise RuntimeError(msg or f"Upload gagal (HTTP {result['status']}).")
        close('upload-modal'); notice('PDF berhasil diunggah.'); await refresh()
    except Exception as exc: el('upload-error').textContent=str(exc)
    finally: button.disabled=chosen is None

def filter_tab(e):
    global selected
    t=e.target.closest('button[data-course]')
    if t: selected=str(t.dataset.course); render()
async def action(e):
    t=e.target.closest('button[data-preview],button[data-delete]')
    if not t: return
    if t.hasAttribute('data-preview'):
        id=int(t.dataset.preview); el('pdf-frame').src=f'/api/library/preview/{id}'; el('preview-download').href=f'/api/library/download/{id}'; show('preview-modal')
    elif window.confirm('Hapus PDF ini untuk semua pengguna?'):
        await api('library/'+str(t.dataset.delete),'DELETE'); await refresh(); notice('Materi dihapus.')
def clear_preview(e): el('pdf-frame').src='about:blank'
def setup():
    bind('add-pdf','click',open_upload); bind('cancel-upload','click',lambda e:close('upload-modal')); bind('file','change',lambda e:pick(e.target.files.item(0))); bind('dropzone','dragover',drag); bind('dropzone','drop',drop); bind('upload-form','submit',submit); bind('search','input',lambda e:render()); bind('tabs','click',filter_tab); bind('materials','click',action); bind('close-preview','click',lambda e:close('preview-modal')); bind('preview-modal','close',clear_preview)
