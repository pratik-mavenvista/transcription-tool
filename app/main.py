from flask import Blueprint, render_template, request, jsonify, flash
from flask_login import current_user, login_required
from app import db
from app.models import Transcription, MoM # Make sure MoM model is imported
from app.forms import MoMForm # Import MoMForm
from app.utils import generate_basic_summary # Import the summarizer

bp = Blueprint('main', __name__)

@bp.route('/')
@bp.route('/index')
def index():
    # This is a placeholder. You might want to pass some data to the template.
    return render_template('index.html', title='Home')

@bp.route('/transcribe')
@login_required # Protect this route
def transcribe():
    return render_template('transcribe.html', title='Live Transcription')

@bp.route('/save_transcription', methods=['POST'])
@login_required
def save_transcription():
    data = request.get_json()
    if not data or 'transcription' not in data:
        return jsonify({'status': 'error', 'message': 'No transcription data provided'}), 400

    text = data['transcription']
    if not text.strip():
        return jsonify({'status': 'error', 'message': 'Transcription is empty'}), 400

    try:
        new_transcription = Transcription(body=text, user_id=current_user.id)
        db.session.add(new_transcription)
        db.session.commit()
        flash('Transcription saved successfully!', 'success')
        return jsonify({'status': 'success', 'message': 'Transcription saved'})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error saving transcription: {e}")
        return jsonify({'status': 'error', 'message': 'Failed to save transcription due to a server error'}), 500

@bp.route('/dashboard')
@login_required
def dashboard():
    page = request.args.get('page', 1, type=int)
    # Query transcriptions for the current user, ordered by timestamp descending
    user_transcriptions = Transcription.query.filter_by(user_id=current_user.id)\
                                          .order_by(Transcription.timestamp.desc())\
                                          .paginate(page=page, per_page=5) # Paginate for better display
    return render_template('dashboard.html', title='Dashboard', transcriptions=user_transcriptions)

@bp.route('/transcription/<int:transcription_id>/mom', methods=['GET', 'POST'])
@login_required
def manage_mom(transcription_id):
    transcription = Transcription.query.get_or_404(transcription_id)
    if transcription.user_id != current_user.id:
        flash('You are not authorized to access this transcription or MoM.', 'danger')
        return redirect(url_for('main.dashboard'))

    mom = transcription.mom # Access the MoM via the backref
    form = MoMForm()

    if form.validate_on_submit():
        if mom: # Existing MoM, update it
            mom.summary = form.summary.data
            db.session.commit()
            flash('Minutes of Meeting updated successfully!', 'success')
        else: # New MoM, create it
            new_mom = MoM(summary=form.summary.data, 
                          transcription_id=transcription.id, 
                          user_id=current_user.id)
            db.session.add(new_mom)
            db.session.commit()
            flash('Minutes of Meeting created successfully!', 'success')
        return redirect(url_for('main.dashboard')) # Or redirect to view the MoM itself

    if mom: # If MoM exists, pre-fill form with its summary
        form.summary.data = mom.summary
    elif request.method == 'GET': # For new MoM, pre-fill with basic summary on GET
        form.summary.data = generate_basic_summary(transcription.body)
        
    return render_template('manage_mom.html', 
                           title='Manage Minutes of Meeting', 
                           form=form, 
                           transcription=transcription,
                           mom=mom)
