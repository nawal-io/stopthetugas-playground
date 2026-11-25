import os
from pathlib import Path
from flask import Flask, g, jsonify, request, send_from_directory, abort, redirect
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
from werkzeug.exceptions import HTTPException
from dotenv import load_dotenv
from .models import Base
from .storage import Storage
ROOT=Path(__file__).resolve().parents[1]

def init_schema(engine):
    Base.metadata.create_all(engine)
    # Additive upgrade for databases created by the previous release.
    with engine.begin() as conn:
        if 'ends_at' not in {c['name'] for c in inspect(conn).get_columns('events')}:
            conn.execute(text('ALTER TABLE events ADD COLUMN ends_at VARCHAR(32)'))

def create_app(config=None):
    load_dotenv(ROOT/'.env')
    app=Flask(__name__,static_folder=None)
    production=bool(os.getenv('VERCEL'))
    app.config.update(DATABASE_URL=os.getenv('DATABASE_URL') or '',STORAGE_BACKEND=os.getenv('STORAGE_BACKEND','local'),MEDIA_ROOT=ROOT/'media',MAX_CONTENT_LENGTH=4*1024*1024+65536,MAX_FORM_MEMORY_SIZE=512*1024)
    if config: app.config.update(config)
    url=app.config['DATABASE_URL']
    if production and (not url or app.config['STORAGE_BACKEND']!='supabase'): raise RuntimeError('Vercel requires PostgreSQL and Supabase Storage.')
    if not url: url='sqlite:///'+str(ROOT/'db.sqlite3')
    if url.startswith(('postgres://','postgresql://')): url='postgresql+psycopg://'+url.split('://',1)[1]
    if production and not url.startswith('postgresql+psycopg://'): raise RuntimeError('Production requires PostgreSQL.')
    engine=create_engine(url, pool_pre_ping=True, **({'poolclass':NullPool} if not url.startswith('sqlite') else {}))
    factory=sessionmaker(bind=engine,expire_on_commit=False)
    app.extensions['engine']=engine
    if not production: init_schema(engine)
    mode=app.config['STORAGE_BACKEND']; sup_url=os.getenv('SUPABASE_URL',''); key=os.getenv('SUPABASE_SERVICE_ROLE_KEY','')
    if mode not in ('local','supabase') or (mode=='supabase' and not (sup_url and key)): raise RuntimeError('Storage configuration incomplete.')
    app.extensions['storage']=Storage(mode,app.config['MEDIA_ROOT'],sup_url,key,os.getenv('SUPABASE_STORAGE_BUCKET','materials'))
    @app.before_request
    def setup():
        if request.path.startswith('/api/'):
            if request.method in ('POST','PATCH','DELETE') and request.headers.get('Sec-Fetch-Site')=='cross-site': abort(403,'Permintaan lintas situs ditolak.')
            g.db=factory()
    @app.teardown_request
    def close(error):
        db=g.pop('db',None)
        if db: db.close()
    @app.after_request
    def headers(r):
        r.headers['X-Content-Type-Options']='nosniff'
        if request.path.startswith('/api/'): r.headers['Cache-Control']='no-store'
        return r
    @app.errorhandler(HTTPException)
    def http_error(e): return jsonify(error='Request upload melebihi batas server. PDF maksimal 4 MB dan metadata harus singkat.' if e.code==413 else e.description),e.code
    @app.errorhandler(Exception)
    def error(e):
        app.logger.exception('Request failed'); return jsonify(error='Server mengalami masalah. Coba lagi.'),500
    @app.get('/api/health')
    def health():
        g.db.execute(text('SELECT 1')); return jsonify(status='ok',storage=mode)
    from .calendar_bp import bp as calendar
    from .reminders_bp import bp as reminders
    from .library_bp import bp as library
    for bp in (calendar,reminders,library): app.register_blueprint(bp)
    @app.get('/')
    def home(): return send_from_directory(ROOT/'frontend','index.html')
    @app.get('/<any(kalender,jadwal,tugas,perpustakaan):page>')
    def page(page): return redirect('/#'+page)
    @app.get('/py/<path:name>')
    def browser_python(name): return send_from_directory(ROOT/'frontend'/'py',name,mimetype='text/plain' if name.endswith('.py') else ('application/javascript' if name.endswith('.js') else 'application/json'))
    @app.cli.command('init-db')
    def init_db(): init_schema(engine); print('Database ready.')
    return app
