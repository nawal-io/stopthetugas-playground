from js import document, window
from pyodide.ffi import create_proxy
from html import escape
from datetime import datetime, timezone, timedelta
import asyncio
WIB=timezone(timedelta(hours=7))
proxies=[]
def el(id): return document.getElementById(id)
def safe(s): return escape(str(s),quote=True)
def dt(s): return datetime.fromisoformat(s).astimezone(WIB)
def now(): return datetime.now(WIB)
def stamp(s):
    d=dt(s); months='Jan Feb Mar Apr Mei Jun Jul Agu Sep Okt Nov Des'.split()
    return f'{d.day} {months[d.month-1]} {d.year}, {d:%H:%M} WIB'
def hours(e):
    start=dt(e['starts_at']); end=dt(e['ends_at']) if e.get('ends_at') else None
    if end is None: return start.strftime('%H:%M')
    return start.strftime('%H:%M')+' – '+end.strftime('%H:%M' if end.date()==start.date() else '%d/%m %H:%M')
def event_stamp(e):
    return stamp(e['starts_at']).rsplit(', ',1)[0]+', '+hours(e)+' WIB'
def show(id): el(id).showModal()
def close(id): el(id).close()
def notice(msg='', error=False):
    box=el('notice'); box.textContent=str(msg); box.hidden=not bool(msg)
    box.className='mb-4 rounded-lg border px-4 py-3 text-sm '+('bg-rose-50 text-rose-800 border-rose-200 dark:bg-rose-950 dark:text-rose-200 dark:border-rose-900' if error else 'bg-emerald-50 text-emerald-800 border-emerald-200 dark:bg-emerald-950 dark:text-emerald-200 dark:border-emerald-900')
def bind_target(target,event,fn):
    def handler(e):
        try:
            if event=='submit': e.preventDefault()
            result=fn(e)
            if asyncio.iscoroutine(result):
                async def run():
                    try: await result
                    except Exception as exc: notice(exc,True)
                asyncio.ensure_future(run())
        except Exception as exc: notice(exc,True)
    p=create_proxy(handler); proxies.append(p); target.addEventListener(event,p)
def ready():
    el('runtime-status').hidden=True; el('content').hidden=False
    for item in document.querySelectorAll('[data-ready]'): item.disabled=False

def bind(id,event,fn): bind_target(el(id),event,fn)
