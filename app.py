from config import db, app, login_manager
from models import Users
import views

@login_manager.user_loader
def load_user(id):
    return Users.query.get(id)


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run()
