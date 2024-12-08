import time
import aiohttp
from googletrans import Translator

translator = Translator()  # Создаём объект Translator один раз

async def check_status_servers():
    """Проверка состояния серверов Fortnite через Fortnite Status API"""
    url = "https://fortnitestatus.statuspage.io/api/v2/status.json"  # API URL для получения состояния серверов
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    new_status = await get_json(response)
                    local_time = get_time()
                    if new_status != "err":
                        return f"""Состояние серверов Fortnite на 
{local_time[-1]} год, {local_time[2]} {local_time[1]}, {local_time[3]}:
{new_status}"""
                    else:
                        return "При получении данных произошла ошибка. Попробуйте пожалуйста позже."
                else:
                    return f"Ошибка при получении статуса серверов: {response.status}"
    except Exception as e:
        return f"Ошибка при получении статуса серверов: {str(e)}"

async def get_json(response):
    """Получение JSON из ответа и перевод состояния"""
    try:
        response_json = await response.json()
        status_description = response_json.get("status", {}).get("description", "Ошибка получения данных")
        # Переводим статус на русский язык
        new_status = translator.translate(status_description, src='en', dest='ru').text
        return new_status
    except Exception as e:
        return "err"

def get_time():
    """Получаем текущее время в формате 'день недели, месяц день, год'"""
    seconds = time.time()
    local_time = time.ctime(seconds).split()
    
    weekdays = {
        "Mon": "понедельник",
        "Tue": "вторник",
        "Wed": "среда",
        "Thu": "четверг",
        "Fri": "пятница",
        "Sat": "суббота",
        "Sun": "воскресенье",
    }

    months = {
        "Jan": "январь",
        "Feb": "февраль",
        "Mar": "март",
        "Apr": "апрель",
        "May": "май",
        "Jun": "июнь",
        "Jul": "июль",
        "Aug": "август",
        "Sep": "сентябрь",
        "Oct": "октябрь",
        "Nov": "ноябрь",
        "Dec": "декабрь",
    }

    # Используем словари для перевода дней недели и месяцев
    local_time[0] = weekdays.get(local_time[0], local_time[0])
    local_time[1] = months.get(local_time[1], local_time[1])

    return local_time
