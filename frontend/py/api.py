import json
from js import window, Object
from pyodide.ffi import to_js

_initial_used=set()

async def api(path, method='GET', data=None):
    if method=='GET' and path in ('events','library') and path not in _initial_used:
        _initial_used.add(path)
        try:
            cached=json.loads(str(await window.sttInitialData(path)))
            if cached['ok']: return json.loads(cached['data'])
        except Exception: pass
    options={'method':method}
    if data is not None: options.update(headers={'Content-Type':'application/json'},body=json.dumps(data))
    response=await window.fetch('/api/'+path,to_js(options,dict_converter=Object.fromEntries))
    if response.status==204: return None
    try: result=json.loads(str(await response.text()))
    except Exception: raise RuntimeError(f'Server tidak merespons dengan benar ({response.status}).')
    if not response.ok: raise RuntimeError(result.get('error','Permintaan gagal.'))
    return result
