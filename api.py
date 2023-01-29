#!flask/bin/python
from flask import Flask, request
from flask.views import MethodView
from libterraform import TerraformCommand
from threading import Thread
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = ""
db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    email = db.Column(db.String, unique=True, nullable=False)


class Lab(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, unique=True, nullable=False)
    state = db.Column(db.String)


app.before_first_request(db.create_all)


def api_creation(lab_name):
    class LabAPI(MethodView):
        def __init__(self):
            self.dir = f'{os.getcwd()}/terraform/{lab_name}'
            self.cli = TerraformCommand(self.dir)

        # func for ferraform apply/destroy
        def change_lab(self, action, labid):
            self.cli.workspace('add', str(labid))
            self.cli.workspace('select', str(labid))
            #lab = db.session.get(Lab, labid)
            option = {'var': f'user-id={labid}', 'auto-approve': ...}
            print(self.cli.run(cmd=action, options=option))
            #db.session.add(lab)
            #db.session.commit()
            self.cli.workspace('select', 'default')

        def create_lab_in_db(self, user_id):
            if (db.session.get(User, user_id)) is not None:
                lab = Lab(user_id=user_id, state='')
                db.session.add(lab)
                db.session.commit()
                print(lab.id)
                return lab.id
            else:
                return None

        # list users or lab status
        def get(self, user_id):
            if user_id is None:
                labs = Lab.query.all()
                return {'status': 200, 'message': {'labs':
                                                   [{'id': lab.id,
                                                     'user_id': lab.user_id,
                                                     'state': lab.state}
                                                    for lab in labs]}}
            else:
                self.cli.workspace('select', str(user_id))
                return self.cli.state('list').value

        # deploy lab
        def post(self, user_id):
            if (lab_id := self.create_lab_in_db(user_id)) is not None:
                self.thread = Thread(
                      target=self.change_lab,
                      args=('apply', lab_id), daemon=True)
                self.thread.start()
                return {'status': 202,
                        'message': {'id': lab_id}}, 202
            else:
                return {'status': 404, 'message': "User not found"}

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
    app.add_url_rule(f'/api/{lab_name}/<int:user_id>', view_func=lab_view,
                     methods=['GET', 'DELETE', 'POST', ])


class UserAPI(MethodView):
    def get(self, user_id):
        if user_id is None:
            users = User.query.all()
            return {'status': 200, 'message': {'users':
                                               [{'id': user.id,
                                                 'username': user.username,
                                                 'email': user.email}
                                                for user in users]}}
        else:
            if (user := db.session.get(User, user_id)) is None:
                return {'status': 404, 'message': 'User not found'}
            else:
                return {'status': 200, 'message': {'user':
                                                   {'id': user.id,
                                                    'username': user.username,
                                                    'email': user.email}}}

    def post(self):
        data = request.get_json()
        user = User(username=data['username'], email=data['email'])
        db.session.add(user)
        db.session.commit()
        return {'status': 200, 'message':
                {'user': {'id': user.id,
                          'username': user.username,
                          'email': user.email}}}

    def put(self, user_id):
        if (user := db.session.get(User, user_id)) is None:
            return {'status': 404, 'message': 'User not found'}
        else:
            data = request.get_json()
            if (email := data.get('email')) is not None:
                user.email = email
            if (username := data.get('username')) is not None:
                user.username = username
            db.session.add(user)
            db.session.commit()
            return {'status': 200, 'message': {'user':
                                               {'id': user.id,
                                                'username': user.username,
                                                'email': user.email}}}

    def delete(self, user_id):
        if (user := db.session.get(User, user_id)) is None:
            return {'status': 404, 'message': 'User not found'}
        else:
            db.session.delete(user)
            db.session.commit()
            return {'status:': 200, 'message': 'User succesfully deleted'}


user_view = UserAPI.as_view('user_api')
app.add_url_rule('/api/user/', view_func=user_view, methods=['GET', ],
                 defaults={'user_id': None})
app.add_url_rule('/api/user/', view_func=user_view, methods=['POST', ])
app.add_url_rule('/api/user/<int:user_id>',
                 view_func=user_view, methods=['DELETE', 'GET', 'PUT'])

# @app.route('/api/lab1/check', methods=['GET'])
# def check_lab():
#     pass


if __name__ == '__main__':
    api_creation('lab1')
    app.run(debug=True)
