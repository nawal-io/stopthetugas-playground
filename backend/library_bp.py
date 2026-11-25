from flask import Blueprint, request, jsonify, g, current_app, abort, send_file
from sqlalchemy import select
from werkzeug.utils import secure_filename
from uuid import uuid4
from io import BytesIO
from .models import Material
from requests import RequestException
bp=Blueprint('library',__name__,url_prefix='/api/library')
COURSES=['Basis Data','Jaringan Komputer','Pemrograman','Sistem Operasi','Rekayasa Perangkat Lunak','Lainnya']
LIMIT=4*1024*1024

@bp.get('')
def listing():
    return jsonify(materials=[m.as_dict() for m in g.db.scalars(select(Material).order_by(Material.id.desc()))],courses=COURSES)

@bp.post('')
def upload():
    fields={k:request.form.get(k,'').strip() for k in ('title','creator','course')}
    if not fields['title'] or len(fields['title'])>200 or not fields['creator'] or len(fields['creator'])>120 or fields['course'] not in COURSES: abort(400,'Judul, creator dan mata kuliah wajib valid.')
    f=request.files.get('file')
    if not f or not f.filename.lower().endswith('.pdf'): abort(400,'Hanya file PDF yang diterima.')
    data=f.stream.read(LIMIT+1)
    if len(data)>LIMIT: abort(400,'Ukuran PDF maksimal 4 MB.')
    if not data.startswith(b'%PDF-'): abort(400,'Isi file bukan PDF yang valid.')
    key=uuid4().hex+'.pdf'; storage=current_app.extensions['storage']
    try: storage.put(key,data)
    except (OSError,RequestException):
        current_app.logger.exception('PDF storage upload failed')
        abort(503,'Penyimpanan PDF tidak tersedia. Coba lagi atau hubungi pengelola.')
    m=Material(**fields,key=key,filename=secure_filename(f.filename)[:250] or 'materi.pdf',size=len(data))
    try:
        g.db.add(m); g.db.commit()
    except Exception:
        g.db.rollback()
        try: storage.delete(key)
        except Exception: current_app.logger.exception('Storage cleanup failed')
        raise
    return jsonify(m.as_dict()),201

def material(id):
    m=g.db.get(Material,id)
    if not m: abort(404,'Materi tidak ditemukan.')
    return m

def serve(id,attachment):
    m=material(id)
    try: data=current_app.extensions['storage'].get(m.key)
    except FileNotFoundError: abort(404,'File tidak ditemukan.')
    response=send_file(BytesIO(data),mimetype='application/pdf',as_attachment=attachment,download_name=m.filename,max_age=0)
    response.headers['X-Frame-Options']='SAMEORIGIN'
    return response

@bp.get('/preview/<int:id>')
def preview(id): return serve(id,False)
@bp.get('/download/<int:id>')
def download(id): return serve(id,True)
@bp.delete('/<int:id>')
def delete(id):
    m=material(id); key=m.key
    g.db.delete(m); g.db.commit()
    try: current_app.extensions['storage'].delete(key)
    except Exception: current_app.logger.exception('Orphan storage object: %s',key)
    return '',204
