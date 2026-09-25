import os

from flask import Flask
from flask_login import LoginManager

from models import db, User


app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "emp-development-secret")
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///emp.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


def create_admin():
    admin = User.query.filter_by(role="Admin").first()

    if not admin:
        admin = User(
            name="Administrator",
            email="admin@emp.local",
            role="Admin",
            is_active=True,
            is_approved=True
        )
        admin.set_password("admin123")
        db.session.add(admin)
        db.session.commit()


with app.app_context():
    db.create_all()
    create_admin()


if __name__ == "__main__":
    app.run(debug=True)