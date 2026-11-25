from ui_helpers import *
import calendar_ui, library_ui

PAGES=('dashboard','kalender','jadwal','tugas','perpustakaan')

def drawer(opened=False):
    el('sidebar').classList.toggle('-translate-x-full',not opened)
    el('drawer-overlay').hidden=not opened
    el('mobile-menu').setAttribute('aria-expanded',str(opened).lower())

def route(e=None):
    page=str(window.location.hash).lstrip('#')
    if page not in PAGES: page='dashboard'; window.history.replaceState(None,'','#dashboard')
    for name in PAGES: el('view-'+name).hidden=name!=page
    for link in document.querySelectorAll('nav a'):
        active=str(link.getAttribute('href'))=='#'+page
        for cls in ('bg-indigo-50','text-indigo-700','dark:bg-indigo-950','dark:text-indigo-300'): link.classList.toggle(cls,active)
        if active: link.setAttribute('aria-current','page')
        else: link.removeAttribute('aria-current')
    document.title=({'jadwal':'Jadwal Kuliah'}.get(page,page.title()))+' · Stop the Tugas'
    drawer(); window.scrollTo(0,0)

def theme(e=None):
    dark=document.documentElement.classList.contains('dark')
    if e is not None:
        dark=not dark; document.documentElement.classList.toggle('dark',dark)
        try: window.localStorage.setItem('stt-theme','dark' if dark else 'light')
        except Exception: pass
    for icon in document.querySelectorAll('[data-theme-icon]'): icon.textContent='☀' if dark else '☾'

async def main():
    window.sttTakeover()
    bind_target(window,'hashchange',route)
    bind('mobile-menu','click',lambda e:drawer(el('drawer-overlay').hidden))
    bind('drawer-overlay','click',lambda e:drawer())
    bind_target(document,'keydown',lambda e:drawer() if e.key=='Escape' else None)
    for button in document.querySelectorAll('[data-theme]'): bind_target(button,'click',theme)
    theme(); route()
    calendar_ui.setup(); library_ui.setup()
    async def load(fn):
        try: await fn()
        except Exception as exc: notice(exc,True)
    await asyncio.gather(load(calendar_ui.refresh),load(library_ui.refresh))
    ready()
    async def loop():
        count=0
        while True:
            await asyncio.sleep(15); count+=1
            if count%4==0: await load(calendar_ui.refresh)
            else: calendar_ui.render_reminders()
    asyncio.ensure_future(loop())
async def boot():
    try: await main()
    except Exception as exc:
        el('runtime-status').textContent='Kontrol Python gagal dimuat. Muat ulang halaman.'
        notice(exc,True)
asyncio.ensure_future(boot())
