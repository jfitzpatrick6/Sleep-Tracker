from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required, current_user
from . import db
from .models import SleepEntry
from datetime import date, timedelta
import json

bp = Blueprint('main', __name__)

def get_sleep_data(period='14', target=8.0):
    if not current_user.is_authenticated:
        return 0.0, 0.0, [], 14

    # Get all entries for the user, sorted by date
    all_entries = SleepEntry.query.filter_by(user_id=current_user.id)\
        .order_by(SleepEntry.sleep_date).all()

    # Calculate lifetime debt (all time)
    lifetime_debt = sum((target - e.hours_slept) for e in all_entries)

    # Determine cutoff date based on selected period
    today = date.today()
    if period == '7':
        days = 7
        cutoff = today - timedelta(days=6)
        period_label = '7 days'
    elif period == '14':
        days = 14
        cutoff = today - timedelta(days=13)
        period_label = '14 days'
    elif period == '30':
        days = 30
        cutoff = today - timedelta(days=29)
        period_label = '30 days'
    elif period == '90':
        days = 90
        cutoff = today - timedelta(days=89)
        period_label = '90 days'
    elif period == 'ytd':
        cutoff = date(today.year, 1, 1)
        period_label = 'Year to Date'
    else:  # 'all'
        cutoff = date(2000, 1, 1)  # far in the past
        period_label = 'All Time'

    # Filter entries for the selected period
    recent_entries = [e for e in all_entries if e.sleep_date >= cutoff]

    # Calculate debt only for the visible period
    period_debt = sum((target - e.hours_slept) for e in recent_entries)

    # Build history for the chart (running debt within this period)
    history = []
    running_debt = 0.0

    for entry in recent_entries:
        daily_deficit = target - entry.hours_slept
        running_debt += daily_deficit
        history.append({
            'date': entry.sleep_date.strftime('%b %d'),
            'hours': round(entry.hours_slept, 1),
            'debt': round(running_debt, 1)
        })

    # For All Time or YTD we don't fill missing dates (too many gaps possible)
    if period not in ['ytd', 'all'] and len(history) < days:
        # Simple fill for short periods only
        pass

    return round(lifetime_debt, 1), round(period_debt, 1), history, period_label


@bp.route('/')
@login_required
def index():
    period = request.args.get('period', '14')
    allowed = ['7', '14', '30', '90', 'ytd', 'all']
    if period not in allowed:
        period = '14'

    lifetime_debt, period_debt, history, period_label = get_sleep_data(period)

    recent = SleepEntry.query.filter_by(user_id=current_user.id)\
        .order_by(SleepEntry.sleep_date.desc()).limit(10).all()

    return render_template('index.html',
                           lifetime_debt=lifetime_debt,
                           period_debt=period_debt,
                           history=json.dumps(history),
                           period=period,
                           period_label=period_label,
                           username=current_user.username,
                           recent=recent)


# Keep your existing /add and /delete routes unchanged
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
        except Exception:
            pass
    
    return render_template('add_entry.html', today=today)


@bp.route('/delete/<int:entry_id>')
@login_required
def delete_entry(entry_id):
    entry = SleepEntry.query.filter_by(id=entry_id, user_id=current_user.id).first_or_404()
    db.session.delete(entry)
    db.session.commit()
    return redirect(url_for('main.index'))


@bp.route('/settings')
@login_required
def settings():
    return render_template('settings.html')