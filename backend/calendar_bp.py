from flask import Blueprint, request, jsonify, g, abort
from sqlalchemy import select
from datetime import datetime, timezone
from .models import Event
bp = Blueprint('calendar', __name__, url_prefix='/api/events')

def clean(data):
    if not isinstance(data,dict): abort(400, 'Data harus berupa objek JSON.')
    result = {}
    for field, limit in [('name',200),('creator',120),('description',2000)]:
        value = data.get(field, '')
        if not isinstance(value,str) or len(value.strip())>limit or (field!='description' and not value.strip()): abort(400, f'Isi {field} dengan benar (maksimal {limit} karakter).')
        result[field]=value.strip()
    if data.get('kind') not in ('task','class'): abort(400,'Tipe entri tidak valid.')
    result['kind']=data['kind']
    try:
        dt=datetime.fromisoformat(data['starts_at'])
        if dt.tzinfo is None: raise ValueError()
        result['starts_at']=dt.astimezone(timezone.utc).isoformat(timespec='seconds')
    except (ValueError,TypeError,KeyError,OverflowError): abort(400,'Tanggal dan waktu dengan zona waktu wajib diisi.')
    end = data.get('ends_at')
    result['ends_at'] = None
    if end not in (None, ''):
        try:
            finish = datetime.fromisoformat(end)
            if finish.tzinfo is None: raise ValueError()
            if finish < dt: abort(400, 'Waktu selesai tidak boleh lebih awal dari waktu mulai.')
            result['ends_at'] = finish.astimezone(timezone.utc).isoformat(timespec='seconds')
        except (ValueError, TypeError, OverflowError): abort(400, 'Waktu selesai tidak valid.')
    if result['kind'] == 'class' and result['ends_at'] is None:
        abort(400, 'Waktu selesai kuliah wajib diisi.')
    return result

@bp.get('')
def list_events():
    return jsonify([e.as_dict() for e in g.db.scalars(select(Event).order_by(Event.starts_at,Event.id))])

@bp.post('')
def create():
    e=Event(**clean(request.get_json(silent=True)))
    g.db.add(e); g.db.commit()
    return jsonify(e.as_dict()),201

@bp.route('/<int:id>', methods=['PATCH','DELETE'])
def change(id):
    e=g.db.get(Event,id)
    if not e: abort(404,'Entri tidak ditemukan.')
    if request.method=='DELETE':
        g.db.delete(e); g.db.commit(); return '',204
    data=request.get_json(silent=True)
    if not isinstance(data,dict): abort(400,'Data tidak valid.')
    merged = {**e.as_dict(), **data}
    # Existing classes without an end remain editable after adding one.
    for k,v in clean(merged).items(): setattr(e,k,v)
    g.db.commit(); return jsonify(e.as_dict())
