from flask import Blueprint, render_template, request, current_app, session, redirect, url_for
from sql_provider import SQLProvider
from db_context_manager import DBContextManager
from db_work import select_dict, insert, select_result
from access import login_required, group_required
import os
from datetime import datetime, date

blueprint_order = Blueprint('bp_order', __name__, template_folder='templates')

provider = SQLProvider(os.path.join(os.path.dirname(__file__), 'sql'))


@blueprint_order.route('/', methods=['GET', 'POST'])
@login_required
@group_required
def order_index():
    db_config = current_app.config['dbconfig']
    current_date = datetime.today().strftime('%Y-%m-%d')
    if request.method == 'GET':
        sql = provider.get('all_items.sql')
        items = select_dict(db_config, sql)
        basket_items = session.get('basket', {})
        return render_template('basket_order_list.html', items=items, date_today=str(current_date), basket=basket_items, order_price=sum([int(basket_items[key]['b_price']) for key in basket_items]) )
    else:
        b_id = request.form['b_id']
        info = request.form['info']
        delete = request.form['del']
        if info == "True":
            items, schema_1, result, schema_2 = inform(b_id)
            return render_template('billboard_info.html', items=items, schema_1=schema_1, schema_2=schema_2, result=result)
        elif delete == "True":
            basket_items = session.get('basket', {})
            del basket_items[b_id]
            session['basket']=basket_items
            session.permanent = True
            return redirect(url_for('bp_order.order_index'))
        else:
            period = request.form['period']
            if period:
                int(period)
            else:
                period = int(1)
            start = request.form['start']
            if start:
                    print(start)
            else:
                    start = current_date
            start_ = datetime.strptime(start, '%Y-%m-%d').date()
            sql_1 = provider.get('check_schedule.sql', b_id=b_id, today=str(current_date))
            dates = select_result(db_config, sql_1)
            sql_2 = provider.get('find_end.sql', start=start, period=period)
            end = select_result(db_config, sql_2)
            end_ = datetime.strptime(end[0][0], '%Y-%m-%d').date()

           # print(start_, type(start_))
           # print(end_, type(end_))
            flag =False
            for dati in dates:
                #print(dati[0])
                #print(dati[1])
                if (dati[0] <= start_ and dati[1] >= start_) or (dati[0] <= end_ and dati[1] >= end_) :
                    flag = True
            if flag == True:
                sql = provider.get('all_items.sql')
                items = select_dict(db_config, sql)
                basket_items = session.get('basket', {})
                return render_template('basket_order_list.html', items=items, date_today=str(current_date), basket=basket_items, order_price=sum([int(basket_items[key]['b_price']) for key in basket_items]), flag=flag)
            else:
                sql = provider.get('all_items.sql')
                items = select_dict(db_config, sql)  # каждый раз снова лезем в БД

                add_to_basket(b_id, period, start, items)  # {'b_id' : {'b_address' : < >, 'b_price' : < >, 'amount' : < >}}


                return redirect(url_for('bp_order.order_index'))


def add_to_basket(b_id: str, period, start, items: dict):
    item_description = [item for item in items if str(item['b_id']) == str(b_id)]
    item_description = item_description[0]
    curr_basket = session.get('basket', {})

    if b_id in curr_basket:
        curr_basket[b_id]['b_price'] = int(period) * int(item_description['b_price'])
        curr_basket[b_id]['period'] = period
        curr_basket[b_id]['start'] = start
    else:
        curr_basket[b_id] = {
            'b_address': item_description['b_address'],
            'b_price': int(period) * int(item_description['b_price']),
            'period': period,
            'start': start
        }
        session['basket'] = curr_basket
        session.permanent = True
    return True


@blueprint_order.route('/order', methods=['GET', 'POST'])
@login_required
@group_required
def save_order():
    user_id = session.get('user_id')
    if session.get('basket', {}):
        current_basket = session.get('basket', {})
        order_id = save_order_with_list(current_app.config['dbconfig'], user_id, current_basket)
        if order_id:
            session.pop('basket')
            return render_template('order_created.html', order_id=order_id)
        else:
            return 'Что-то пошло не так'
    else:
        return redirect(url_for('bp_order.order_index'))


def inform(b_id):
    current_date = datetime.today().strftime('%Y-%m-%d')
    db_config = current_app.config['dbconfig']
    sql_1 = provider.get('find_info.sql', b_id=b_id)
    items = select_result(db_config, sql_1)
    schema_1=(("ID:", "Адрес расположения:", "Цена за месяц аренды:", "Размер (МхМ):", "Качество:", "Дата установки:", "Фамилия владельца:", "Кантактный телефон:"),)
    sql_2 = provider.get('check_schedule.sql', b_id=b_id, today=str(current_date))
    result = select_result(db_config, sql_2)
    schema_2=("Начало", "Конец")
    return items, schema_1, result, schema_2



@blueprint_order.route('/clear')
@login_required
@group_required
def clear_basket():
    if 'basket' in session:
        session.pop('basket')
    return redirect(url_for('bp_order.order_index'))


def save_order_with_list(dbconfig: dict, user_id: int, current_basket: dict):
    with DBContextManager(dbconfig) as cursor:
        if cursor is None:
            raise ValueError('Курсор не создан')
        current_date = datetime.today().strftime('%Y-%m-%d')
        _sql1 = provider.get('insert_order.sql', t_id=user_id, order_date=current_date, order_price=sum([int(current_basket[key]['b_price']) for key in current_basket]))
        result1 = cursor.execute(_sql1)
        if result1 == 1:  # 1 - кол-во созданных строк
            _sql2 = provider.get('select_order_id.sql', user_id=user_id)
            cursor.execute(_sql2)
            order_id = cursor.fetchall()[0][0]
            if order_id:
                for key in current_basket:
                    b_price = current_basket[key]['b_price']
                    start = current_basket[key]['start']
                    period = current_basket[key]['period']
                    _sql3 = provider.get('insert_order_list.sql', start=start, period=period, order_id=order_id, b_id=key,  b_price=b_price)
                    _sql4 = provider.get('insert_schedule.sql', s_start=start, period=period, b_id=key)
                    cursor.execute(_sql3)
                    cursor.execute(_sql4)
                return order_id
