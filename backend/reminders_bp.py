from flask import Blueprint, jsonify
from datetime import datetime
from zoneinfo import ZoneInfo
bp=Blueprint('reminders',__name__,url_prefix='/api/reminders')
@bp.get('/clock')
def clock():
    return jsonify(now=datetime.now(ZoneInfo('Asia/Jakarta')).isoformat(), timezone='Asia/Jakarta')
