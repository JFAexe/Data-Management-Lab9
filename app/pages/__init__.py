from .main import page_main
from .procedures import page_procedures
from .requests import page_requests
from .tables import page_tables
from .views import page_views

PAGES = {
    'Главная': page_main,
    'Таблицы': page_tables,
    'Запросы': page_requests,
    'Процедуры': page_procedures,
    'Представления': page_views
}
