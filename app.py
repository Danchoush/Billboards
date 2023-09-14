from flask import Flask, request, render_template, json, session, redirect, url_for
from blueprint_zaproses.route import blueprint_zaproses
from blueprint_auth.route import blueprint_auth
from blueprint_report.route import blueprint_report
from blueprint_order.route import blueprint_order

from db_work import select

app = Flask(__name__)
app.secret_key = 'SuperKey'

app.register_blueprint(blueprint_zaproses, url_prefix='/zaproses')  # регистрация blue-print'а
app.register_blueprint(blueprint_auth, url_prefix='/blueprint_auth')
app.register_blueprint(blueprint_report, url_prefix='/reports')
app.register_blueprint(blueprint_order, url_prefix='/orders')


with open('data_files/dbconfig.json', 'r') as f:
     db_config = json.load(f)
app.config['dbconfig'] = db_config
with open('data_files/access.json', 'r') as file:
    access_config = json.load(file)
    app.config['access_config'] = access_config
app.config['db_config'] = json.load(open('data_files/dbconfig.json'))
with open('data_files/report_list.json', 'r', encoding='utf-8') as file:
    report_list = json.load(file)
    app.config['report_list'] = report_list
with open('data_files/report_url.json', 'r', encoding='utf-8') as file:
    report_url = json.load(file)
    app.config['report_url'] = report_url



@app.route('/', methods=['GET', 'POST'])
def query():
    if 'user_id' in session:
        if session.get('user_group', "external") == "external":
            return render_template('external_user_menu.html')
        else:
            return render_template('internal_user_menu.html', user_group=session.get('user_group'))
    else:
        return render_template('start_request.html')

@app.route('/menu', methods=['GET', 'POST'])
def query_2():
    return render_template('start_request.html')

@app.route('/exit')
def goodbye():
    session.clear()
    return render_template('goodbye.html')


#@app.route('/greeting/')
#@app.route('/greeting/<name>')
# def greeting_handler(name: str = None) -> str:
#     if name is None:
#         return 'Hello unknown'
#     return f'Hello, {name}'  # -> "Hello, ivan" == "Hello, " + "ivan" == " ".join(["Hello, ", name])


# @app.route('/products', methods=['GET'])
# def get_all_products():
#     sql = """
#     select
#         prod_id,
#         prod_name,
#         prod_price
#     from supermarket
#     """
#     all_rows, schema = select(db_config, sql)
#     return str(all_rows)


# @app.route('/', methods=['GET', 'POST'])
# def query():
#     return render_template('start_request.html')

@app.route('/form', methods=['GET', 'POST'])
def form_handler():
    if request.method == 'GET':
        return render_template('form.html')
    else:
        login = request.form.get('login')
        password = request.form.get('password')
        return f'Login: {login}, password: {password}'


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5001)
