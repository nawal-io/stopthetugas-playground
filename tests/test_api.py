import unittest, tempfile, io
from pathlib import Path
from backend import create_app

class ApiTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(); p=Path(self.tmp.name)
        self.app=create_app({'TESTING':True,'DATABASE_URL':'sqlite:///'+str(p/'test.sqlite3'),'STORAGE_BACKEND':'local','MEDIA_ROOT':p/'media'})
        self.c=self.app.test_client()
    def tearDown(self):
        self.app.extensions['engine'].dispose(); self.tmp.cleanup()
    def test_pages(self):
        for path in ('/','/py/main.py','/py/config.json','/api/health'):
            self.assertEqual(self.c.get(path).status_code,200,path)
        for page in ('kalender','jadwal','tugas','perpustakaan'):
            r=self.c.get('/'+page); self.assertEqual(r.status_code,302); self.assertEqual(r.headers['Location'],'/#'+page)
        self.assertIn('text/plain',self.c.get('/py/main.py').content_type)
    def test_calendar(self):
        data=dict(kind='task',name='ERD',creator='Tim C',starts_at='2026-11-28T09:00:00+07:00')
        r=self.c.post('/api/events',json=data); self.assertEqual(r.status_code,201); id=r.json['id']; self.assertIn('02:00:00+00:00',r.json['starts_at'])
        self.assertEqual(self.c.patch(f'/api/events/{id}',json={'name':'Revisi'}).json['name'],'Revisi')
        self.assertEqual(len(self.c.get('/api/events').json),1)
        self.assertEqual(self.c.delete(f'/api/events/{id}').status_code,204)
        self.assertEqual(self.c.post('/api/events',json={}).status_code,400)
    def upload(self,data,name='a.pdf'):
        return self.c.post('/api/library',data={'title':'ERD','creator':'Tim D','course':'Basis Data','file':(io.BytesIO(data),name)})
    def test_library(self):
        r=self.upload(b'%PDF-1.4\n%%EOF'); self.assertEqual(r.status_code,201); id=r.json['id']
        for action,disposition in [('preview','inline'),('download','attachment')]:
            response=self.c.get(f'/api/library/{action}/{id}'); self.assertEqual(response.mimetype,'application/pdf'); self.assertTrue(response.headers['Content-Disposition'].startswith(disposition))
        self.assertEqual(self.c.patch(f'/api/library/{id}',json={}).status_code,405)
        self.assertEqual(self.c.delete(f'/api/library/{id}').status_code,204)
        self.assertEqual(self.c.get(f'/api/library/preview/{id}').status_code,404)
    def test_invalid(self):
        for data,name in [(b'fake','a.pdf'),(b'%PDF-','a.docx'),(b'%PDF-'+b'x'*(4*1024*1024),'a.pdf')]: self.assertEqual(self.upload(data,name).status_code,400)
    def test_max_size(self):
        data=b'%PDF-'+b'x'*(4*1024*1024-5); r=self.upload(data); self.assertEqual(r.status_code,201); self.assertEqual(r.json['size'],len(data))

    def test_medium_pdf_upload_regression(self):
        for size in (65536, 377242, 1024*1024):
            with self.subTest(size=size):
                r=self.upload(b"%PDF-"+b"x"*(size-5))
                self.assertEqual(r.status_code,201,r.get_data(as_text=True))
                self.assertEqual(r.json["size"],size)

    def test_event_range(self):
        data=dict(kind='class',name='Basis Data',creator='Tim C',starts_at='2026-11-25T08:00:00+07:00',ends_at='2026-11-25T10:30:00+07:00')
        r=self.c.post('/api/events',json=data)
        self.assertEqual(r.status_code,201,r.get_data(as_text=True))
        self.assertEqual(r.json['ends_at'],'2026-11-25T03:30:00+00:00')
        id=r.json['id']
        self.assertEqual(self.c.patch(f'/api/events/{id}',json={'ends_at':'2026-11-25T07:00:00+07:00'}).status_code,400)
        self.assertEqual(self.c.patch(f'/api/events/{id}',json={'ends_at':'2026-11-25T11:00:00+07:00'}).status_code,200)
        self.assertEqual(self.c.post('/api/events',json={**data,'ends_at':None}).status_code,400)
        self.assertEqual(self.c.post('/api/events',json={**data,'kind':'task','ends_at':None}).status_code,201)
