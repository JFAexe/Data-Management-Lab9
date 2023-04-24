import datetime

import streamlit as st
from pypika import Order

from .queries import QUERY_COMAPRE_OPERATORS, format_query


def blank():
    st.write(' ')


def display_sql(query):
    if st.session_state.sql:
        st.code(query)


def warning():
    st.write('#### Не рекомендуется использовать данный функционал')
    return not st.checkbox('Я знаю что делаю')


def display_query(db, query):
    result = db.run_query(query)
    if len(result) > 0:
        st.json(result[0])
    else:
        st.write('Недостаточно данных')


def display_query_formated(db, query, field, ff):
    result = db.run_query(query)[0]
    if result.get(field):
        result[field] = ff(result.get(field))
    if len(result) > 0:
        st.json(result)
    else:
        st.write('Недостаточно данных')


def non_empty_button(db, query, label):
    if len(query.get_sql()) > 1:
        query = format_query(query)
        display_sql(query)

        if st.button(label):
            db.run_query_uncached(query, fetch=False)


def non_empty_dataframe(db, query):
    if len(query.get_sql()) > 1:
        query = format_query(query)
        display_sql(query)

        st.dataframe(
            data=db.run_query_uncached(query),
            use_container_width=True
        )


def populate_elements(query, conditions, elements):
    for element in conditions:
        element = elements.get(element)
        if element is None:
            continue
        query = element[0](query=query, **element[1])

    return query


def append_elements(options, elements):
    values = []
    for option in options:
        option = elements.get(option)
        if option is None:
            continue
        values.append((option[0], option[1](**option[2])))

    return values


def default_or_value(cond, default, element, args):
    return default if not cond else element(**args)


def bool_compare_box(query, label, compared):
    return query.where(compared == st.checkbox(label))


def bool_update_box(label):
    right, middle, left = st.columns(
        spec=[1, 2, 3],
        gap='medium'
    )

    with right:
        st.write(label)

    with middle:
        select = st.radio(
            label='Значение ' + label,
            label_visibility='collapsed',
            options=['Задать', 'DEFAULT'],
            horizontal=True
        )

    with left:
        must_default = select == 'DEFAULT'

        value = st.checkbox(
            label='Новый ' + label,
            label_visibility='collapsed',
            disabled=must_default
        )

        value = value if not must_default else select

    return value


def number_compare_box(query, label, compared):
    left, right = st.columns([1, 2], gap='medium')

    with left:
        number = st.number_input(
            label=label,
            value=1,
            min_value=1,
            step=1
        )

    with right:
        operation = st.radio(
            label='Операция для ' + label,
            options=QUERY_COMAPRE_OPERATORS.keys(),
            horizontal=True
        )

    return query.where(
        QUERY_COMAPRE_OPERATORS.get(operation)(compared, number)
    )


def number_update_box(label):
    right, middle, left = st.columns(
        spec=[1, 2, 3],
        gap='medium'
    )

    with right:
        st.write(label)

    with middle:
        select = st.radio(
            label='Значение ' + label,
            label_visibility='collapsed',
            options=['Задать', 'DEFAULT'],
            horizontal=True
        )

    with left:
        must_default = select == 'DEFAULT'

        value = st.number_input(
            label='Новый ' + label,
            label_visibility='collapsed',
            min_value=1,
            value=1,
            step=1,
            disabled=must_default
        )

        value = value if not must_default else select

    return value


def number_select_update_box(label, options):
    right, middle, left = st.columns(
        spec=[1, 2, 3],
        gap='medium'
    )

    with right:
        st.write(label)

    with middle:
        select = st.radio(
            label='Значение ' + label,
            label_visibility='collapsed',
            options=['Выбрать', 'Задать'],
            horizontal=True
        )

    with left:
        if select == 'Выбрать':
            value = st.selectbox(
                label='Новый ' + label,
                label_visibility='collapsed',
                options=options
            )
        else:
            value = st.number_input(
                label='Новый ' + label,
                label_visibility='collapsed',
                min_value=1,
                value=1,
                step=1
            )

    return value


def text_compare_box(query, label, compared, options=None, uid=False):
    left, right = st.columns([2, 3], gap='medium')

    disabled = options is None
    value = None

    with left:
        mode = st.checkbox(
            label=label + ' по паттерну',
            value=disabled,
            disabled=disabled or uid
        )

    with right:
        if mode or disabled:
            value = st.text_input(
                label=label,
                label_visibility='collapsed',
                value='%'
            )

            value = compared.like(value)
        else:
            value = st.selectbox(
                label=label,
                label_visibility='collapsed',
                options=options
            )

            value = compared == value

    return query.where(value)


def uuid_select_box(label, options, selected, options_):
    right, middle, left = st.columns(
        spec=[1, 2, 3],
        gap='medium'
    )

    with right:
        st.write(label)

    with middle:
        select = st.radio(
            label='Значение ' + label,
            label_visibility='collapsed',
            options=options,
            index=options.index(selected),
            horizontal=True
        )

    with left:
        for i in range(len(options)):
            if select == options[i]:
                value = st.selectbox(
                    label=options[i] + label,
                    label_visibility='collapsed',
                    options=options_[i]
                )

    return value, select


def date_time_box(label, disabled=False):
    left, right = st.columns(2, gap='medium')

    with left:
        date = st.date_input(
            label='Дата ' + label,
            disabled=disabled
        )

    with right:
        time = st.time_input(
            label='Время ' + label,
            step=datetime.timedelta(seconds=300),
            disabled=disabled
        )

        time.isoformat(timespec='seconds')

    return datetime.datetime.combine(date, time)


def date_time_compare_box(query, label, compared):
    left_date, right_date = st.columns([1, 2], gap='medium')

    with left_date:
        date = st.date_input('Дата ' + label)

    with right_date:
        operation_date = st.radio(
            label='Операция для ' + label,
            options=QUERY_COMAPRE_OPERATORS.keys(),
            horizontal=True
        )

    left_time, right_time = st.columns([1, 2], gap='medium')

    with left_time:
        compare_time = st.checkbox('Время ' + label)

    with right_time:
        if compare_time:
            time = st.time_input(
                label='Время ' + label,
                label_visibility='collapsed',
                step=datetime.timedelta(seconds=300)
            )

            time.isoformat(timespec='seconds')

    if compare_time:
        date = datetime.datetime.combine(date, time)

    return query.where(
        QUERY_COMAPRE_OPERATORS.get(operation_date)(compared, date)
    )


def date_time_update_box(label):
    date_option = st.radio(
        label='Дата ' + label,
        options=['Установить', 'Убрать'],
        horizontal=True,
        label_visibility='collapsed'
    )

    date = date_time_box(label, date_option == 'Убрать')

    if date_option == 'Убрать':
        date = None

    return date


def groupby_box(query, fields):
    groupby = st.multiselect(
        label='Группировка по',
        options=fields,
        default=None,
        label_visibility='collapsed'
    )

    if len(groupby) > 0:
        query = query.groupby(*groupby)

    return query


def orderby_box(query, fields):
    orderby = st.multiselect(
        label='Порядок по',
        options=fields,
        default=None,
        label_visibility='collapsed'
    )

    order = st.radio(
        label='Порядок',
        options=['ASC', 'DESC'],
        horizontal=True,
        label_visibility='collapsed'
    )

    if len(orderby) > 0:
        order = Order.desc if order == 'DESC' else Order.asc
        query = query.orderby(
            *orderby,
            order=order
        )

    return query


def limitby_box(query):
    limitby = st.number_input(
        label='Число',
        value=1,
        min_value=1,
        step=1
    )

    return query.limit(limitby)
