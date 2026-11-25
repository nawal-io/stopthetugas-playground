from ui_helpers import *
from api import api
import calendar

events=[]; anchor=now().date(); mode='month'; editing=None


def cards(items):
    return ''.join(f'''<article class="rounded-lg border p-3 break-words {'border-amber-200 bg-amber-50 dark:border-amber-900 dark:bg-amber-950' if e['kind']=='task' else 'border-indigo-200 dark:border-indigo-900 bg-indigo-50 dark:bg-indigo-950'}"><span class="text-xs font-semibold {'text-amber-800 dark:text-amber-300' if e['kind']=='task' else 'text-indigo-800 dark:text-indigo-300'}">{'Tugas' if e['kind']=='task' else 'Ruang Kuliah'} · {hours(e)}</span><h3 class="mt-1 text-sm font-semibold">{safe(e['name'])}</h3><p class="mt-1 text-xs text-slate-600 dark:text-slate-300">{safe(e['description'])}</p><p class="mt-1 text-xs text-slate-500 dark:text-slate-400">Oleh: {safe(e['creator'])}</p><div class="mt-2 flex flex-wrap gap-2"><button data-edit="{e['id']}" class="rounded-md border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-900 px-2 py-1 text-xs font-medium">Edit</button><button data-delete="{e['id']}" class="rounded-md border border-rose-200 bg-white dark:bg-slate-900 px-2 py-1 text-xs font-medium text-rose-700 dark:text-rose-300">Hapus</button></div></article>''' for e in items)

MONTHS='Januari Februari Maret April Mei Juni Juli Agustus September Oktober November Desember'.split()
selected_day=None

def render_reminders():
    from reminders import render as render_dashboard
    render_dashboard(events)

def render():
    for kind,page in [('task','tugas'),('class','jadwal')]:
        subset=[e for e in events if e['kind']==kind]
        el(page+'-grid').innerHTML=''.join(f'<section class="space-y-2"><p class="text-xs text-slate-500 dark:text-slate-400">{event_stamp(e)}</p>{cards([e])}</section>' for e in subset) or '<p class="text-sm text-slate-500 dark:text-slate-400">Belum ada entri.</p>'
    first=anchor-timedelta(days=anchor.weekday()) if mode=='week' else anchor.replace(day=1)-timedelta(days=anchor.replace(day=1).weekday())
    count=7 if mode=='week' else 7*len(calendar.Calendar().monthdatescalendar(anchor.year,anchor.month))
    el('range').textContent=f'{MONTHS[anchor.month-1]} {anchor.year}' if mode!='week' else f'{first.day} {MONTHS[first.month-1]} – {(first+timedelta(days=6)).day} {MONTHS[(first+timedelta(days=6)).month-1]} {(first+timedelta(days=6)).year}'
    for b in el('view-mode').querySelectorAll('button'):
        active=str(b.dataset.mode)==mode
        for cls in ('bg-indigo-600','text-white'): b.classList.toggle(cls,active)
        b.setAttribute('aria-pressed',str(active).lower())
    if mode=='agenda':
        subset=[e for e in events if dt(e['starts_at']).date().month==anchor.month and dt(e['starts_at']).date().year==anchor.year]
        el('calendar-grid').innerHTML='<div class="p-4 space-y-3">'+(''.join(f'<div><p class="text-xs mb-2 text-slate-500">{event_stamp(e)}</p>{cards([e])}</div>' for e in subset) or '<p class="text-sm text-slate-500">Tidak ada agenda bulan ini.</p>')+'</div>'
        render_reminders(); return
    days=[]
    for i in range(count):
        d=first+timedelta(days=i); today=d==now().date(); items=[e for e in events if dt(e['starts_at']).date()==d]
        mark='bg-indigo-600 text-white' if today else ('text-slate-400' if d.month!=anchor.month and mode=='month' else '')
        pills=''.join(f'<span class="block truncate rounded px-1.5 py-1 text-xs font-medium {"bg-amber-100 text-amber-900 dark:bg-amber-950 dark:text-amber-300" if e["kind"]=="task" else "bg-indigo-100 text-indigo-900 dark:bg-indigo-950 dark:text-indigo-300"}">{hours(e)} {safe(e["name"])}</span>' for e in items[:3])
        extra=f'<span class="text-xs text-slate-500">+{len(items)-3} lainnya</span>' if len(items)>3 else ''
        days.append(f'<button type="button" data-day="{d.isoformat()}" class="min-w-0 min-h-[110px] text-left self-stretch flex flex-col gap-1 border-r border-b border-slate-200 dark:border-slate-800 p-2 hover:bg-slate-50 dark:hover:bg-slate-800"><span class="inline-flex items-center justify-center rounded-full w-7 h-7 text-xs font-semibold {mark}">{d.day}</span><span class="w-full space-y-1">{pills}{extra}</span></button>')
    heads=''.join(f'<div class="text-center py-3 text-xs font-semibold text-slate-500 dark:text-slate-400 border-b border-slate-200 dark:border-slate-800">{d}</div>' for d in ['Sen','Sel','Rab','Kam','Jum','Sab','Min'])
    el('calendar-grid').innerHTML='<div class="grid grid-cols-7 min-w-[770px]">'+heads+''.join(days)+'</div>'
    render_reminders()

def open_day(d):
    global selected_day
    selected_day=d
    el('day-title').textContent=f'{d.day} {MONTHS[d.month-1]} {d.year}'
    el('day-events').innerHTML=cards([e for e in events if dt(e['starts_at']).date()==d]) or '<p class="text-sm text-slate-500">Belum ada agenda pada tanggal ini.</p>'
    show('day-modal')

async def refresh():
    global events
    events=await api('events'); render()

def open_form(e=None, day=None, kind=None):
    global editing
    el('event-error').textContent=''; editing=e['id'] if e else None; el('event-form').reset(); el('form-title').textContent='Edit agenda' if e else 'Tambah agenda'
    el('kind').value=e['kind'] if e else (kind or 'class')
    for k in ('name','description','creator'): el(k).value=e[k] if e else ''
    el('starts_at').value=dt(e['starts_at']).strftime('%Y-%m-%dT%H:%M') if e else ((day.isoformat()+'T08:00') if day else now().strftime('%Y-%m-%dT%H:%M'))
    el('ends_at').value=dt(e['ends_at']).strftime('%Y-%m-%dT%H:%M') if e and e.get('ends_at') else ''
    sync_time_fields()
    show('event-modal')

def sync_time_fields(e=None):
    task=str(el('kind').value)=='task'
    el('start-label').textContent='Tenggat (WIB)' if task else 'Waktu mulai (WIB)'
    el('end-label').textContent='Waktu selesai (opsional, WIB)' if task else 'Waktu selesai (WIB)'
    el('ends_at').required=not task
    el('ends_at').min=el('starts_at').value
    if not task and not str(el('ends_at').value) and str(el('starts_at').value):
        el('ends_at').value=(datetime.fromisoformat(str(el('starts_at').value))+timedelta(hours=1)).strftime('%Y-%m-%dT%H:%M')
async def submit(e):
    e.preventDefault(); button=el('save-event'); button.disabled=True
    try:
        data={k:str(el(k).value) for k in ('kind','name','description','creator','starts_at')}; data['starts_at']+='+07:00'
        end=str(el('ends_at').value)
        data['ends_at']=end+'+07:00' if end else None
        if end and dt(data['ends_at'])<dt(data['starts_at']): raise ValueError('Waktu selesai tidak boleh lebih awal dari waktu mulai.')
        await api(f'events/{editing}' if editing else 'events','PATCH' if editing else 'POST',data); close('event-modal'); await refresh(); notice('Agenda tersimpan.')
    except Exception as exc: el('event-error').textContent=str(exc)
    finally: button.disabled=False

async def action(e):
    target=e.target.closest('button[data-edit],button[data-delete],button[data-day]')
    if not target: return
    if target.hasAttribute('data-day'): open_day(datetime.fromisoformat(str(target.dataset.day)).date()); return
    if el('day-modal').open: close('day-modal')
    if target.hasAttribute('data-edit'): open_form(next(x for x in events if x['id']==int(target.dataset.edit)))
    elif window.confirm('Hapus agenda ini untuk semua pengguna?'):
        await api('events/'+str(target.dataset.delete),'DELETE'); await refresh(); notice('Agenda dihapus.')

def move(n):
    global anchor
    if mode=='week': anchor+=timedelta(days=n*7)
    else:
        m=anchor.year*12+anchor.month-1+n; anchor=anchor.replace(year=m//12,month=m%12+1,day=1)
    render()
def change_mode(e):
    global mode
    target=e.target.closest('button[data-mode]')
    if target: mode=str(target.dataset.mode); render()
def today(e):
    global anchor
    anchor=now().date(); render()
def setup():
    bind('add-event','click',lambda e:open_form())
    bind('add-jadwal','click',lambda e:open_form(kind='class'))
    bind('add-tugas','click',lambda e:open_form(kind='task'))
    bind('cancel-event','click',lambda e:close('event-modal'))
    bind('event-form','submit',submit)
    bind('kind','change',sync_time_fields); bind('starts_at','change',sync_time_fields)
    for id in ('calendar-grid','jadwal-grid','tugas-grid','day-events'): bind(id,'click',action)
    bind('prev','click',lambda e:move(-1)); bind('next','click',lambda e:move(1)); bind('today','click',today); bind('view-mode','click',change_mode)
    bind('close-day','click',lambda e:close('day-modal'))
    def add_day(e):
        close('day-modal'); open_form(day=selected_day)
    bind('add-day','click',add_day)
