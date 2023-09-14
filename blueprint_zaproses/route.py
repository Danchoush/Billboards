import os  # работа с объектами операционной системы

from flask import Blueprint, request, render_template, current_app  # глобальная переменная с конфигом app

from access import group_required, login_required
from db_work import select, select_result
from sql_provider import SQLProvider
import numbers




blueprint_zaproses = Blueprint('bp_zaproses', __name__, template_folder='templates')  # создание blueprint'а

provider = SQLProvider(os.path.join(os.path.dirname(__file__), 'sql'))  # создание словаря для текущего blueprint'а


@blueprint_zaproses.route('queries', methods=['GET'])
@group_required
def queries():
    if request.method == 'GET':
        return render_template('select_zapros.html')


@blueprint_zaproses.route('/month_search', methods=['GET', 'POST'])
@group_required
def month_search():
    fake_schema = ["ID", "Имя", "Тел.", "Адрес", "Сфера деятельности", "Дата заключения договора"]
    month = ("Январь", "Февраль", "Март", "Апрель", "Май", "Июнь", "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь")
    if request.method == 'GET':
        return render_template('month_search.html', month=month)
    else:
        input_month = int(request.form.get('input_month'))+1
        input_year = int(request.form.get('input_year'))
        if input_month and input_year :
            _sql = provider.get('zapr_1.sql', input_month=input_month, input_year=input_year)
            result, schema = select(current_app.config['dbconfig'],_sql)
            if result == ():
                return render_template('month_search.html', mes="Данных не найдено", month=month)
            else:
                return render_template('db_result.html', schema=fake_schema, result=result, message=f"Сведения об арендаторах, заключивших договор в месяце {month[input_month-1]}.")
        else:
            return render_template('month_search.html', mes="Попробуй снова", month=month)

@blueprint_zaproses.route('/phone_search', methods=['GET', 'POST'])
@group_required
def phone_search():
    fake_schema = ["ID", "Имя", "Тел.", "Адрес", "Сфера деятельности", "Дата заключения договора"]
    if request.method == 'GET':
        return render_template('phone_search.html')
    else:
        input_ = str(request.form.get('input'))

        if input_ :
            _sql = provider.get('zapr_2.sql', input_phone = input_)
            result, schema = select(current_app.config['dbconfig'],_sql)
            if result == ():
                return render_template('phone_search.html', mes="Данных не найдено")
            else:
                return render_template('db_result.html', schema=fake_schema, result=result, message=f"Сведения об арендаторе")
        else:
            return render_template('phone_search.html', mes="Попробуй снова")

@blueprint_zaproses.route('/sum_per_one', methods=['GET', 'POST'])
@group_required
def sum_per_one():
    _sql = provider.get('search_names.sql')
    names= select_result(current_app.config['dbconfig'], _sql)
    print(names)
    fake_schema = ["Стоимость заказа","ID"]
    if request.method == 'GET':
        return render_template('form_1.html', names=names)
    else:
        input_ = request.form.get('input')
        if input_ :
            _sql = provider.get('zapr_3.sql', input_name=input_)
            result, schema = select(current_app.config['dbconfig'],_sql)
            if result == ():
                return render_template('form_1.html', mes="Данных не найдено", names=names)
            else:
                return render_template('db_result.html', schema=fake_schema, result=result, message=f"Суммарная стоимость заказа:")
        else:
            return render_template('form_1.html',mes="Попробуй снова", names=names)