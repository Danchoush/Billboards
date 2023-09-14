from functools import wraps
from flask import session, render_template, request, current_app


# Декоратор проверяющий факт авторизации пользователя в сессии
def login_required(func):
    @wraps(func)  # стандартный декоратор flask
    def wrapper(*args, **kwargs):
        if 'user_id' in session:
            return func(*args, *kwargs)  # запуск функции
        return render_template('refuse.html')
    return wrapper


# Сверка запроса пользователя с его правами в конфиге
def group_validation(config: dict) -> bool:
    endpoint_func = request.endpoint  # это "blueprint.имя_обработчика" --- конкретный элемент blueprint'а
    endpoint_app = request.endpoint.split('.')[0]  # это "blueprint" --- весь blueprint
    if 'user_group' in session:
        user_group = session['user_group']
        if user_group in config and endpoint_app in config[user_group]:
            return True
        if user_group in config and endpoint_func in config[user_group]:
            return True
    return False


# Декоратор проверки доступа к функции f для текущего пользователя в сессии (доступ задается в отдельном конфиге)
def group_required(f):
    @wraps(f)  # стандартный декоратор flask
    def wrapper(*args, **kwargs):
        config = current_app.config['access_config']  # todo
        if group_validation(config):
            return f(*args, **kwargs)
        return render_template('refuse.html')
    return wrapper

def external_validation(config):
    endpoint_app = request.endpoint.split('.')[0]
    user_id = session.get('user_id')
    user_group = session.get('user_group')
    if user_id and user_group is None:
        if endpoint_app in config['external']:
            return True
    return False


def external_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        config = current_app.config['access_config']
        if external_validation(config):
            return f(*args, **kwargs)
        return render_template('external_user_menu.html')
    return wrapper