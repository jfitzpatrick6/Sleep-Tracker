from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from flask_login import login_required, current_user
from . import db
from .models import SleepEntry
from datetime import date, timedelta
import json

bp = Blueprint('main', __name__)

def get_sleep_debt_and_history(target=8.0):
    if not current_user.is_authenticated:
        return 0.0, []
    
    entries = SleepEntry.query.filter_by(user_id=current_user.id)\
        .order_by(SleepEntry.sleep_date).all()
    
    debt = 0.0
    history = []
    for entry in entries:
        daily_deficit = target - entry.hours_slept
        debt += daily_deficit
        history.append({
            'date': entry.sleep_date.isoformat(),
            'hours': round(entry.hours_slept, 2),
            'debt': round(debt, 2)
        })
    return round(debt, 2), history

@bp.route('/')
@login_required
def index():
    target = 8.0
    current_debt, history = get_sleep_debt_and_history(target)
    recent = SleepEntry.query.filter_by(user_id=current_user.id)\
        .order_by(SleepEntry.sleep_date.desc()).limit(10).all()
    
    return render_template('index.html',
                           current_debt=current_debt,
                           recent=recent,
                           history=json.dumps(history),
                           target=target,
                           username=current_user.username)

@bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_entry():
    from datetime import date
    today = date.today().isoformat()
    
    if request.method == 'POST':
        try:
            sleep_date = date.fromisoformat(request.form['sleep_date'])
            hours = int(request.form.get('hours', 0))
            minutes = int(request.form.get('minutes', 0))
            total_hours = hours + (minutes / 60.0)
            notes = request.form.get('notes', '').strip()
            
            existing = SleepEntry.query.filter_by(
                user_id=current_user.id, 
                sleep_date=sleep_date
            ).first()
            
            if existing:
                existing.hours_slept = total_hours
                existing.notes = notes
            else:
                entry = SleepEntry(
                    user_id=current_user.id,
                    sleep_date=sleep_date,
                    hours_slept=total_hours,
                    notes=notes
                )
                db.session.add(entry)
            
            db.session.commit()
            return redirect(url_for('main.index'))
        except (ValueError, TypeError):
            pass
    
    return render_template('add_entry.html', today=today)

@bp.route('/delete/<int:entry_id>')
@login_required
def delete_entry(entry_id):
    entry = SleepEntry.query.filter_by(id=entry_id, user_id=current_user.id).first_or_404()
    db.session.delete(entry)
    db.session.commit()
    return redirect(url_for('main.index'))

# Optional: Settings (still static for now)
@bp.route('/settings')
@login_required
def settings():
    return render_template('settings.html')