from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from . import db
from .models import SleepEntry
from datetime import date, timedelta
import json

bp = Blueprint('main', __name__)

def get_sleep_debt_and_history(target=8.0):
    entries = SleepEntry.query.order_by(SleepEntry.sleep_date).all()
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
def index():
    target = 8.0  # you can make this dynamic later
    current_debt, history = get_sleep_debt_and_history(target)
    recent = SleepEntry.query.order_by(SleepEntry.sleep_date.desc()).limit(10).all()
    return render_template('index.html',
                           current_debt=current_debt,
                           recent=recent,
                           history=json.dumps(history),
                           target=target)

@bp.route('/add', methods=['GET', 'POST'])
def add_entry():
    from datetime import date
    today = date.today().isoformat()
    
    if request.method == 'POST':
        try:
            sleep_date = date.fromisoformat(request.form['sleep_date'])
            hours = int(request.form.get('hours', 0))
            minutes = int(request.form.get('minutes', 0))
            
            # Convert hours + minutes to decimal hours
            total_hours = hours + (minutes / 60.0)
            
            notes = request.form.get('notes', '').strip()
            
            # Update if exists, otherwise create new
            existing = SleepEntry.query.filter_by(sleep_date=sleep_date).first()
            if existing:
                existing.hours_slept = total_hours
                existing.notes = notes
            else:
                entry = SleepEntry(sleep_date=sleep_date, hours_slept=total_hours, notes=notes)
                db.session.add(entry)
                
            db.session.commit()
            return redirect(url_for('main.index'))
        except (ValueError, TypeError):
            # You can add flash messages later for better error feedback
            pass
    
    return render_template('add_entry.html', today=today)

@bp.route('/settings', methods=['GET', 'POST'])
def settings():
    # For now just shows target (easy to expand to DB-stored settings later)
    if request.method == 'POST':
        # In a real app you'd save target to a Settings table
        return redirect(url_for('main.index'))
    return render_template('settings.html')

@bp.route('/delete/<int:entry_id>')
def delete_entry(entry_id):
    entry = SleepEntry.query.get_or_404(entry_id)
    db.session.delete(entry)
    db.session.commit()
    return redirect(url_for('main.index'))