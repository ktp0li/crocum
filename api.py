#!flask/bin/python
from flask import Flask
from flask.views import MethodView
from libterraform import TerraformCommand
from threading import Thread

app = Flask(__name__)


@app.route('/')
def index():
    return "puk"


class UserAPI(MethodView):
    def __init__(self):
        self.dir = '/home/user/lab/terraform'
        self.cli = TerraformCommand(self.dir)

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
        user_id = str(1)
        if self.cli.workspace('new', user_id).retcode in [0, 2]:
            self.thread = Thread(target=(lambda userid: self.cli.apply(
                var={'user-id': userid})), args=(user_id), daemon=True)
            self.thread.start()
            return 'Lab is creating...', 202
        else:
            return 'Lab is exist', 409

    # destroy lab
    def delete(self, user_id):
        if self.cli.workspace('select', str(user_id)).retcode in [0, 2]:
            self.thread = Thread(target=(lambda userid: self.cli.destroy(
                var={'user-id': userid})), args=(str(user_id)), daemon=True)
            self.thread.start()
            return 'Lab is destroying...', 202
        else:
            return 'Lab is not exist', 409


user_view = UserAPI.as_view('user_api')
app.add_url_rule('/api/lab1', defaults={'user_id': None},
                 view_func=user_view, methods=['GET', ])
app.add_url_rule('/api/lab1', view_func=user_view, methods=['POST', ])
app.add_url_rule('/api/lab1/<int:user_id>', view_func=user_view,
                 methods=['GET', 'DELETE', ])
# @app.route('/api/labs', methods=['GET'])
# def list_labs():
#     pass
#
#
# @app.route('/api/lab1/<int:user_id>', methods=['POST'])
# def deploy_lab():
#     pass
#
#
# @app.route('/api/lab1/<int:user_id>', methods=['DELETE'])
# def destroy_lab():
#     pass
#
#
# @app.route('/api/lab1', methods=['GET'])
# def list_users():
#     pass
#
#
# @app.route('/api/lab1/<int:user_id>', methods=['GET'])
# def lab_status():
#     pass
#
#
# @app.route('/api/lab1/check', methods=['GET'])
# def check_lab():
#     pass


if __name__ == '__main__':
    app.run(debug=True)
