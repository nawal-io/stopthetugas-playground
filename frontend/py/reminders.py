from ui_helpers import *
from api import api
import math

def reminder(e):
    t=dt(e['starts_at']); n=now(); days=(t.date()-n.date()).days
    if t<n: return None
    if e['kind']=='task' and 0<=days<=7:
        return (f'H-{0 if days==0 else 1 if days==1 else 3 if days<=3 else 7}',f'{days} hari lagi' if days else 'Deadline hari ini')
    if e['kind']=='class' and days==1: return ('H-1','Kuliah besok')
    if e['kind']=='class' and days==0: return ('H-menit',f'Mulai dalam {math.ceil((t-n).total_seconds()/60)} menit')
    return None

def render(events):
    n=now(); week=n.date()-timedelta(days=n.weekday()); end=week+timedelta(days=7)
    upcoming=[(e,reminder(e)) for e in events if reminder(e)]
    el('reminders').innerHTML=''.join(f'''<article class="rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 p-4"><span class="rounded-md px-2 py-1 text-xs font-semibold {'bg-amber-100 text-amber-800 dark:bg-amber-950 dark:text-amber-300' if e['kind']=='task' else 'bg-indigo-100 text-indigo-800 dark:bg-indigo-950 dark:text-indigo-300'}">{r[0]}</span><h3 class="mt-3 font-semibold break-words">{safe(e['name'])}</h3><p class="mt-1 text-sm text-slate-600 dark:text-slate-300">{r[1]}</p><p class="mt-2 text-xs text-slate-500 dark:text-slate-400 tabular-nums">{event_stamp(e)}</p></article>''' for e,r in upcoming) or '<p class="text-sm text-slate-500 dark:text-slate-400">Tidak ada pengingat mendatang.</p>'
    thisweek=[e for e in events if week<=dt(e['starts_at']).date()<end]
    for kind,id in [('task','task-count'),('class','class-count')]: el(id).textContent=str(sum(e['kind']==kind for e in thisweek))
    el('week-list').innerHTML=''.join(f'<div class="flex flex-wrap justify-between gap-2 border-b border-slate-100 dark:border-slate-800 py-3"><span class="font-medium break-words">{safe(e["name"])}</span><span class="text-xs text-slate-500 dark:text-slate-400">{event_stamp(e)}</span></div>' for e in thisweek) or '<p class="py-4 text-sm text-slate-500 dark:text-slate-400">Belum ada agenda minggu ini.</p>'

