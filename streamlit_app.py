"""
Дашборд ТСН «Солнечный»
Читает данные напрямую с Яндекс.Диска по публичной ссылке.
"""

import streamlit as st
import pandas as pd
from datetime import datetime, date
import requests
from urllib.parse import urlencode
import io

# ===== НАСТРОЙКИ =====
# Вставьте сюда публичную ссылку на ваш файл с Яндекс.Диска
YANDEX_DISK_PUBLIC_LINK = "ВАША_ПУБЛИЧНАЯ_ССЫЛКА_СЮДА"

st.set_page_config(
    page_title="Дашборд ТСН «Солнечный»",
    page_icon="🏠",
    layout="wide",
)

# ===== ЗАГРУЗКА ДАННЫХ С ЯНДЕКС.ДИСКА =====
@st.cache_data(ttl=60)
def load_data_from_yadisk(public_link):
    try:
        base_url = 'https://cloud-api.yandex.net/v1/disk/public/resources/download?'
        final_url = base_url + urlencode(dict(public_key=public_link))
        response = requests.get(final_url)
        
        if response.status_code != 200:
            st.error(f"Ошибка Яндекс.Диска: {response.status_code}")
            return None, None, None, None
            
        download_url = response.json()['href']
        download_response = requests.get(download_url)
        
        if download_response.status_code != 200:
            st.error(f"Ошибка скачивания: {download_response.status_code}")
            return None, None, None, None

        excel_file = io.BytesIO(download_response.content)
        
        tasks = pd.read_excel(excel_file, sheet_name="Задачи")
        eval_list = pd.read_excel(excel_file, sheet_name="Оценочный_лист")
        mail = pd.read_excel(excel_file, sheet_name="Переписка")
        fin = pd.read_excel(excel_file, sheet_name="Финансы")
        
        return tasks, eval_list, mail, fin

    except Exception as e:
        st.error(f"Ошибка при загрузке данных: {e}")
        return None, None, None, None

tasks, eval_list, mail, fin = load_data_from_yadisk(YANDEX_DISK_PUBLIC_LINK)

# ===== ОТОБРАЖЕНИЕ =====
if tasks is not None:
    st.title("🏠 Дашборд ТСН «Солнечный»")
    st.caption(f"Дата обновления: {datetime.now().strftime('%d.%m.%Y %H:%M')}")

    # Блок «Задачи»
    st.header("📋 Задачи")
    tasks["Срок"] = pd.to_datetime(tasks["Срок"], errors="coerce").dt.date
    today = date.today()
    total_tasks = len(tasks)
    overdue = len(tasks[(tasks["Статус"] != "Готово") & (tasks["Срок"] < today)])
    today_tasks = len(tasks[tasks["Срок"] == today])
    in_progress = len(tasks[tasks["Статус"] == "В работе"])
    done = len(tasks[tasks["Статус"] == "Готово"])
    
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Всего задач", total_tasks)
    col2.metric("Просрочено", overdue, delta_color="inverse")
    col3.metric("На сегодня", today_tasks)
    col4.metric("В работе", in_progress)
    col5.metric("Готово", done)
    
    def highlight_status(row):
        if row["Статус"] == "Готово":
            return ["background-color: #C6EFCE"] * len(row)
        elif row["Статус"] == "В работе":
            return ["background-color: #FFEB9C"] * len(row)
        elif row["Статус"] == "Не начато":
            return ["background-color: #D9D9D9"] * len(row)
        return [""] * len(row)
    
    st.dataframe(tasks.style.apply(highlight_status, axis=1), use_container_width=True)
    
    # Блок «Подготовка к зиме»
    st.header("❄️ Подготовка к зиме")
    total_docs = len(eval_list)
    done_docs = len(eval_list[eval_list["Наличие (Да/Нет)"] == "Да"])
    progress = done_docs / total_docs if total_docs > 0 else 0
    col1, col2 = st.columns([1, 3])
    col1.metric("Собрано документов", f"{done_docs} из {total_docs}")
    col2.progress(progress, text=f"Готовность: {progress:.0%}")
    st.dataframe(eval_list, use_container_width=True)
    
    # Блок «Переписка»
    st.header("✉️ Переписка")
    col1, col2 = st.columns(2)
    col1.metric("Входящих всего", len(mail))
    pending = len(mail[mail["Исх. №"].isna() | (mail["Исх. №"] == "")])
    col2.metric("Ожидают ответа", pending)
    st.dataframe(mail, use_container_width=True)
    
    # Блок «Финансы»
    st.header("💰 Финансы")
    fin["Сумма"] = pd.to_numeric(fin["Сумма"], errors="coerce").fillna(0)
    income = fin[fin["Тип (приход/расход)"] == "Приход"]["Сумма"].sum()
    expense = fin[fin["Тип (приход/расход)"] == "Расход"]["Сумма"].sum()
    debt = fin[fin["Тип (приход/расход)"] == "Задолженность"]["Сумма"].sum()
    col1, col2, col3 = st.columns(3)
    col1.metric("Приход", f"{income:,.0f} ₽".replace(",", " "))
    col2.metric("Расход", f"{expense:,.0f} ₽".replace(",", " "))
    col3.metric("Задолженность", f"{debt:,.0f} ₽".replace(",", " "))
    st.dataframe(fin, use_container_width=True)
else:
    st.warning("Данные не загружены. Проверьте ссылку на Яндекс.Диск.")
