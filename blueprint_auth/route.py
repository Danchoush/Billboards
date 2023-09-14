import os
from typing import Optional, Dict
from flask import Blueprint, request, render_template, current_app, session, redirect, url_for
from db_work import select_dict
from sql_provider import SQLProvider

blueprint_auth = Blueprint('bp_auth', __name__, template_folder='templates')
provider = SQLProvider(os.path.join(os.path.dirname(__file__), 'sql'))

@blueprint_auth.route('/', methods=['GET', 'POST'])
def start_auth():
    if request.method == 'GET':
        return render_template('input_login.html', message='')
    else:
        login = request.form.get('login')
        password = request.form.get('password')
        if login:
            user_info = define_user(login, password)
            if user_info:
                user_dict = user_info[0]
                session['user_id'] = user_dict['user_id']  # формирование сессии
                session['user_group'] = user_dict['user_group']
                if session['user_group'] == None:
                    session['user_group'] = "external"
                session.permanent = True  # зафиксировать занесение данных в сессию
                return redirect(url_for('query_2'))  # передача управления обратно в app.py
            else:
                return render_template('input_login.html', message='Пользователь не найден')
        return render_template('input_login.html', message='Повторите ввод')


def define_user(login: str, password: str) -> Optional[Dict]:
    sql_internal = provider.get('internal_user.sql', login=login, password=password)  # формирование запросов
    sql_external = provider.get('external_user.sql', login=login, password=password)

    user_info = None

    for sql_search in [sql_internal, sql_external]:
        user_info = select_dict(current_app.config['db_config'], sql_search)  # осуществление запросов в разные таблицы
        if user_info:
            break
    return user_info