import os  # работа с объектами операционной системы

from flask import Blueprint, render_template, request, current_app, redirect, url_for

from access import group_required, login_required
from db_work import select, select_result
from sql_provider import SQLProvider
from db_work import call_proc



blueprint_report = Blueprint('bp_report', __name__, template_folder='templates')  # создание blueprint'а

provider = SQLProvider(os.path.join(os.path.dirname(__file__), 'sql'))  # создание словаря для текущего blueprint'а

@blueprint_report.route('/', methods=['GET', 'POST'])
@login_required
@group_required
def variants():
    if request.method == 'GET':
        return render_template('select_report.html', report_list=current_app.config['report_list'])
    else:
        rep_id = request.form.get('rep_id')
        if request.form.get('create_rep'):
            url_rep = current_app.config['report_url'][rep_id]['create_rep']
        else:
            url_rep = current_app.config['report_url'][rep_id]['view_rep']
        return redirect(url_for(url_rep))


@blueprint_report.route('create/month_paymant', methods=['GET', 'POST'])
@login_required
@group_required
def create_pm():
    month = (
    "Январь", "Февраль", "Март", "Апрель", "Май", "Июнь", "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь")
    if request.method == 'GET':
        return render_template('pay_per_month.html', var="Создание", month=month)
    else:
        input_month = request.form.get('input_month')
        input_year = request.form.get('input_year')
        input_month =int(input_month)+1
        if input_month and input_year:
            _sql = provider.get('check_date.sql', input_month=input_month, input_year=input_year)
            check, schema = select(current_app.config['db_config'], _sql)
            if int(check[0][0]) >= 1:
                return render_template('pay_per_month.html', message="Отчет за этот месяц уже существует", var="Создание", month=month)
            call_proc(current_app.config['db_config'], 'pay_month', input_month, input_year)
            return render_template('pay_per_month.html', message="Отчет создан", var="Создание", month=month)
        else:
            return render_template('pay_per_month.html', message="Повторите ввод", var="Создание", month=month)


@blueprint_report.route('create/count_bills', methods=['GET', 'POST'])
@login_required
@group_required
def create_rb():
    _sql = provider.get('get_bills.sql')
    bills = select_result(current_app.config['db_config'], _sql)
    if request.method == 'GET':
        _sql = provider.get('get_bills.sql')
        bills = select_result(current_app.config['db_config'], _sql)
        return render_template('reserved_billboards.html', var="Создание", billboards=bills)
    else:
        input_ = request.form.get('input')
        input_year = request.form.get('input_year')
        if input_ and input_year:
            _sql = provider.get('check_id.sql', input=input_, input_year=input_year  )
            check, schema = select(current_app.config['db_config'], _sql)
            if int(check[0][0]) >= 1:
                return render_template('reserved_billboards.html', message="Отчет о данном биллборде уже существует", var="Создание", billboards=bills)
            call_proc(current_app.config['db_config'], 'res_bill', input_, input_year)
            return render_template('reserved_billboards.html', message="Отчет создан", var="Создание", billboards=bills)
        else:
            return render_template('reserved_billboards.html', message="Повторите ввод", var="Создание", billboards=bills)

@blueprint_report.route('view/month_paymant', methods=['GET', 'POST'])
@login_required
@group_required
def view_pm():
    month = ("Январь", "Февраль", "Март", "Апрель", "Май", "Июнь", "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь")
    if request.method == 'GET':
        return render_template('pay_per_month.html', var="Просмотр", month=month)
    else:
        input_month = request.form.get('input_month')
        input_year = request.form.get('input_year')
        input_month = int(input_month) + 1
        if input_month and input_year:
            _sql = provider.get('check_date.sql',  input_month=input_month, input_year=input_year)
            check, schema = select(current_app.config['db_config'], _sql)
            if int(check[0][0]) == 1:
                _sql = provider.get('pm_pull.sql',  input_month=input_month, input_year=input_year)
                result, schema = select(current_app.config['db_config'], _sql)
                return render_template('result_set.html', result=result,
                                           message=f"Отчет о прибыли за {input_month}-й месяц {input_year} год", input_1="Месяц", input_2="Год", input_3="Прибыль")
            else:
                return render_template('pay_per_month.html', message="Отчета за этот месяц еще не существует", var="Просмотр", month=month)
        else:
            return render_template('pay_per_month.html', message="Повторите ввод", var="Просмотр", month=month)


@blueprint_report.route('view/count_bills', methods=['GET', 'POST'])
@login_required
@group_required
def view_rb():
    _sql = provider.get('get_bills.sql')
    bills = select_result(current_app.config['db_config'], _sql)
    if request.method == 'GET':
        return render_template('reserved_billboards.html', var="Просмотр", billboards=bills)
    else:
        input_ = request.form.get('input')
        input_year = request.form.get('input_year')
        if input_ and input_year:
            _sql = provider.get('check_id.sql', input=input_, input_year=input_year)
            check, schema = select(current_app.config['db_config'], _sql)
            if int(check[0][0]) == 1:
                _sql = provider.get('rb_pull.sql', input=input_, input_year=input_year)
                result, schema = select(current_app.config['db_config'], _sql)
                return render_template('result_set.html', result=result,
                               message=f"Отчет количестве заказов биллборда с ID {input_} за 2020 год", input_1="ID биллборда", input_2="Год", input_3="Количество заказов")
            return render_template('reserved_billboards.html', message="Отчет об этом биллборде еще не содан", var="Просмотр", billboards=bills)
        else:
            return render_template('reserved_billboards.html', message="Повторите ввод", var="Просмотр", billboards=bills)





