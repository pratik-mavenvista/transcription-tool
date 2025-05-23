from app import create_app, db
from app.models import User, Transcription, MoM # Import your models

app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Transcription': Transcription, 'MoM': MoM}

if __name__ == '__main__':
    with app.app_context():
        db.create_all() # Creates database tables from models, if they don't exist
    app.run(debug=True)
