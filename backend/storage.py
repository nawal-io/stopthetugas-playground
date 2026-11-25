from pathlib import Path
from urllib.parse import quote
import requests

class Storage:
    def __init__(self, mode, path, url='', key='', bucket='materials'):
        self.mode=mode; self.path=Path(path); self.url=url.rstrip('/')+'/storage/v1/object/'+quote(bucket,safe='')+'/'; self.headers={'Authorization':'Bearer '+key,'apikey':key}
        if mode=='local': self.path.mkdir(parents=True,exist_ok=True)
    def put(self,key,data):
        if self.mode=='local': (self.path/key).write_bytes(data); return
        r=requests.post(self.url+key,data=data,headers={**self.headers,'Content-Type':'application/pdf','x-upsert':'false'},timeout=25); r.raise_for_status()
    def get(self,key):
        if self.mode=='local': return (self.path/key).read_bytes()
        r=requests.get(self.url.replace('/object/','/object/authenticated/')+key,headers=self.headers,timeout=25); r.raise_for_status(); return r.content
    def delete(self,key):
        if self.mode=='local': (self.path/key).unlink(missing_ok=True); return
        r=requests.delete(self.url.rstrip('/'),json={'prefixes':[key]},headers=self.headers,timeout=25)
        if r.status_code!=404: r.raise_for_status()
