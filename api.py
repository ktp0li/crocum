#!flask/bin/python
from flask import Flask, request
from flask.views import MethodView
from libterraform import TerraformCommand
from threading import Thread
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = ""
db = SQLAlchemy(app)
dir = '/home/user/lab/terraform'


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    email = db.Column(db.String, unique=True, nullable=False)


def api_creation(lab_name):
    class Lab(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        user_id = db.Column(db.Integer, unique=True, nullable=False)
        state = db.Column(db.String)

    class LabAPI(MethodView):
        def __init__(self):
            self.dir = f'{dir}/{lab_name}'
            self.cli = TerraformCommand(self.dir)

        # func for ferraform apply/destroy
        def change_lab(self, action, userid):
            self.cli.workspace('select', userid)
            option = {'var': f'user-id={userid}', 'auto-approve': ...}
            self.cli.run(action, option)
            self.cli.workspace('select', 'default')

        def create_user(self, username, email):
            user = User(username=username, email=email)
            db.session.add(user)
            db.session.commit()
            return user.id

# list users or lab status
        def get(self, user_id):
            if user_id is None:
                stdout = self.cli.workspace('list').value
                return stdout.split('\n')
            else:
                self.cli.workspace('select', str(user_id))
                return self.cli.state('list').value

        # deploy lab
        def post(self):
            data = request.get_json()
            user_id = str(self.create_user(data['username'], data['email']))
            if self.cli.workspace('new', user_id).retcode in (0, 2):
                self.thread = Thread(target=self.change_lab,
                                     args=('apply', user_id), daemon=True)
                self.thread.start()
                return {'status': 202,
                        'message': f'{lab_name} is creating...'}, 202
            else:
                return {'status': 409,
                        'message': f'{lab_name} already exist'}, 409

        # destroy lab
        def delete(self, user_id):
            if self.cli.workspace('select', str(user_id)).retcode in [0, 2]:
                self.thread = Thread(
                        target=self.change_lab,
                        args=('destroy', str(user_id)), daemon=True)
                self.thread.start()
                return {'status': 202,
                        'message': f'{lab_name} is destroying...'}, 202
            else:
                return {'status': 404,
                        'message': f'{lab_name} not found'}, 404

    lab_view = LabAPI.as_view('lab_api')
    app.add_url_rule(f'/api/{lab_name}', defaults={'user_id': None},
                     view_func=lab_view, methods=['GET', ])
    app.add_url_rule(f'/api/{lab_name}', view_func=lab_view,
                     methods=['POST', ])
    app.add_url_rule(f'/api/{lab_name}/<int:user_id>', view_func=lab_view,
                     methods=['GET', 'DELETE', ])


class UserAPI(MethodView):
    def get(self, user_id):
        if user_id is None:
            users = User.query.all()
            return {'users': [{'id': user.id,
                               'username': user.username,
                               'email': user.email} for user in users]}
        else:
            user = db.session.get(User, user_id)
            if user is None:
                return {'status': 404, 'message': 'User not found'}
            else:
                return {'user': {'id': user.id,
                                 'username': user.username,
                                 'email': user.email}}

    def post(self):
        data = request.get_json()
        user = User(username=data['username'], email=data['email'])
        db.session.add(user)
        db.session.commit()
        return {'id': user.id, 'username': user.username, 'email': user.email}

    def delete(self, user_id):
        user = db.session.get(User, user_id)
        if user is None:
            return {'status': 404, 'message': 'User not found'}
        else:
            db.session.delete(user)
            db.session.commit()
            return {'status:': 200, 'message': 'User succesfully deleted'}


user_view = UserAPI.as_view('user_api')
app.add_url_rule('/api/user/', view_func=user_view, methods=['GET', ],
                 defaults={'user_id': None})
app.add_url_rule('/api/user/<int:user_id>', view_func=user_view,
                 methods=['GET', ])
app.add_url_rule('/api/user/', view_func=user_view, methods=['POST', ])
app.add_url_rule('/api/user/<int:user_id>',
                 view_func=user_view, methods=['DELETE', ])

# @app.route('/api/lab1/check', methods=['GET'])
# def check_lab():
#     pass


with app.app_context():
    db.create_all()


if __name__ == '__main__':
    api_creation('lab1')
    app.run(debug=True)
    db.init_app(app)
