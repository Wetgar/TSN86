"""
Дашборд ТСН «Солнечный»
Данные читаются с Яндекс.Диска по публичной ссылке.
Дизайн: кастомный CSS, шрифт Inter, тёмная боковая панель.
"""

import streamlit as st
import pandas as pd
from datetime import datetime, date
import requests
from urllib.parse import urlencode
import io

# ===== НАСТРОЙКИ =====
YANDEX_DISK_PUBLIC_LINK = "https://disk.yandex.ru/i/FHAn8Ecc0Q5u0w"

st.set_page_config(
    page_title="Дашборд ТСН «Солнечный»",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ===== КАСТОМНЫЙ CSS =====
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    .stApp {
        background: #F5F7FA;
    }

    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2rem;
        max-width: 1400px;
    }

    h1 { font-size: 28px; font-weight: 700; color: #1F4E79; margin-bottom: 0.5rem; }
    h2 { font-size: 20px; font-weight: 600; color: #2E75B6; margin-top: 1.5rem; margin-bottom: 1rem; }
    h3 { font-size: 16px; font-weight: 600; color: #34495E; }

    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1F4E79 0%, #16395B 100%);
    }
    section[data-testid="stSidebar"] * {
        color: #FFFFFF !important;
    }
    section[data-testid="stSidebar"] .stRadio label {
        padding: 8px 12px;
        border-radius: 8px;
        transition: background 0.2s;
    }
    section[data-testid="stSidebar"] .stRadio label:hover {
        background: rgba(255,255,255,0.1);
    }

    .main-header {
        background: linear-gradient(135deg, #1F4E79 0%, #2E75B6 100%);
        padding: 22px 28px;
        border-radius: 14px;
        color: white;
        margin-bottom: 22px;
        box-shadow: 0 4px 16px rgba(31, 78, 121, 0.25);
    }
    .main-header h1 {
        color: white;
        margin: 0;
        font-size: 26px;
        font-weight: 700;
    }
    .main-header p {
        margin: 6px 0 0 0;
        opacity: 0.9;
        font-size: 13px;
    }

    .metric-card {
        background: white;
        padding: 18px 20px;
        border-radius: 12px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.06);
        border-left: 4px solid #2E75B6;
        margin-bottom: 12px;
        transition: transform 0.15s, box-shadow 0.15s;
    }
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 16px rgba(0,0,0,0.1);
    }
    .metric-card.red { border-left-color: #E74C3C; }
    .metric-card.yellow { border-left-color: #F39C12; }
    .metric-card.green { border-left-color: #27AE60; }
    .metric-card.blue { border-left-color: #3498DB; }
    .metric-card.purple { border-left-color: #9B59B6; }

    .metric-label {
        font-size: 11px;
        color: #7F8C8D;
        text-transform: uppercase;
        letter-spacing: 0.8px;
        font-weight: 600;
        margin-bottom: 6px;
    }
    .metric-value {
        font-size: 28px;
        font-weight: 700;
        color: #2C3E50;
        line-height: 1.1;
    }

    .section-header {
        font-size: 20px;
        font-weight: 700;
        color: #1F4E79;
        margin: 25px 0 15px 0;
        padding-bottom: 8px;
        border-bottom: 2px solid #E1E8ED;
    }

    .stDataFrame {
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 2px 10px rgba(0,0,0,0.06);
    }

    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #27AE60, #2ECC71);
        border-radius: 10px;
    }

    .stButton > button {
        border-radius: 10px;
        font-weight: 600;
        background: #2E75B6;
        color: white;
        border: none;
        padding: 8px 18px;
        transition: background 0.2s;
    }
    .stButton > button:hover {
        background: #1F4E79;
    }

    footer { visibility: hidden; }
    #MainMenu { visibility: hidden; }
</style>
""", unsafe_allow_html=True)


# ===== ЗАГРУЗКА ДАННЫХ =====
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


# ===== БОКОВАЯ ПАНЕЛЬ =====
with st.sidebar:
    st.markdown("## 🏠 ТСН «Солнечный»")
    st.markdown("---")
    page = st.radio(
        "Навигация",
        ["📊 Обзор", "📋 Задачи", "❄️ Подготовка", "✉️ Переписка", "💰 Финансы"],
        label_visibility="collapsed",
    )
    st.markdown("---")
    if st.button("🔄 Обновить данные"):
        st.cache_data.clear()
        st.rerun()
    st.markdown("---")
    st.caption(f"Обновлено:\n{datetime.now().strftime('%d.%m.%Y %H:%M')}")


# ===== ЗАГРУЗКА =====
tasks, eval_list, mail, fin = load_data_from_yadisk(YANDEX_DISK_PUBLIC_LINK)


# ===== ОТОБРАЖЕНИЕ =====
if tasks is not None:
    st.markdown("""
    <div class="main-header">
        <h1>🏠 Дашборд ТСН «Солнечный»</h1>
        <p>Управление домом: п. Солнечный, ул. Спортивная, д. 11/1</p>
    </div>
    """, unsafe_allow_html=True)

    # ===== ОБЗОР =====
    if page == "📊 Обзор":
        st.markdown('<div class="section-header">📊 Общая картина</div>', unsafe_allow_html=True)

        tasks["Срок"] = pd.to_datetime(tasks["Срок"], errors="coerce").dt.date
        today = date.today()
        total_tasks = len(tasks)
        overdue = len(tasks[(tasks["Статус"] != "Готово") & (tasks["Срок"] < today)])

        total_docs = len(eval_list)
        done_docs = len(eval_list[eval_list["Наличие (Да/Нет)"] == "Да"])
        progress = done_docs / total_docs if total_docs > 0 else 0

        fin["Сумма"] = pd.to_numeric(fin["Сумма"], errors="coerce").fillna(0)
        fin_income = fin[fin["Тип (приход/расход)"] == "Приход"]["Сумма"].sum()
        fin_expense = fin[fin["Тип (приход/расход)"] == "Расход"]["Сумма"].sum()

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(f'<div class="metric-card blue"><div class="metric-label">Всего задач</div><div class="metric-value">{total_tasks}</div></div>', unsafe_allow_html=True)
        with col2:
            st.markdown(f'<div class="metric-card red"><div class="metric-label">Просрочено</div><div class="metric-value">{overdue}</div></div>', unsafe_allow_html=True)
        with col3:
            st.markdown(f'<div class="metric-card green"><div class="metric-label">Готовность к зиме</div><div class="metric-value">{progress:.0%}</div></div>', unsafe_allow_html=True)
        with col4:
            st.markdown(f'<div class="metric-card purple"><div class="metric-label">Приход / Расход</div><div class="metric-value">{fin_income/1000:.0f}к / {fin_expense/1000:.0f}к</div></div>', unsafe_allow_html=True)

        st.markdown('<div class="section-header">❄️ Подготовка к зиме</div>', unsafe_allow_html=True)
        st.progress(progress, text=f"Собрано {done_docs} из {total_docs} документов")

    # ===== ЗАДАЧИ =====
    elif page == "📋 Задачи":
        st.markdown('<div class="section-header">📋 Задачи</div>', unsafe_allow_html=True)

        tasks["Срок"] = pd.to_datetime(tasks["Срок"], errors="coerce").dt.date
        today = date.today()
        total_tasks = len(tasks)
        overdue = len(tasks[(tasks["Статус"] != "Готово") & (tasks["Срок"] < today)])
        today_tasks = len(tasks[tasks["Срок"] == today])
        in_progress = len(tasks[tasks["Статус"] == "В работе"])
        done = len(tasks[tasks["Статус"] == "Готово"])

        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            st.markdown(f'<div class="metric-card blue"><div class="metric-label">Всего</div><div class="metric-value">{total_tasks}</div></div>', unsafe_allow_html=True)
        with col2:
            st.markdown(f'<div class="metric-card red"><div class="metric-label">Просрочено</div><div class="metric-value">{overdue}</div></div>', unsafe_allow_html=True)
        with col3:
            st.markdown(f'<div class="metric-card yellow"><div class="metric-label">На сегодня</div><div class="metric-value">{today_tasks}</div></div>', unsafe_allow_html=True)
        with col4:
            st.markdown(f'<div class="metric-card blue"><div class="metric-label">В работе</div><div class="metric-value">{in_progress}</div></div>', unsafe_allow_html=True)
        with col5:
            st.markdown(f'<div class="metric-card green"><div class="metric-label">Готово</div><div class="metric-value">{done}</div></div>', unsafe_allow_html=True)

        def highlight_status(row):
            if row["Статус"] == "Готово":
                return ["background-color: #C6EFCE"] * len(row)
            elif row["Статус"] == "В работе":
                return ["background-color: #FFEB9C"] * len(row)
            elif row["Статус"] == "Не начато":
                return ["background-color: #D9D9D9"] * len(row)
            return [""] * len(row)

        st.dataframe(tasks.style.apply(highlight_status, axis=1), use_container_width=True, height=500)

    # ===== ПОДГОТОВКА =====
    elif page == "❄️ Подготовка":
        st.markdown('<div class="section-header">❄️ Подготовка к зиме</div>', unsafe_allow_html=True)

        total_docs = len(eval_list)
        done_docs = len(eval_list[eval_list["Наличие (Да/Нет)"] == "Да"])
        progress = done_docs / total_docs if total_docs > 0 else 0

        col1, col2 = st.columns([1, 3])
        with col1:
            st.markdown(f'<div class="metric-card green"><div class="metric-label">Собрано</div><div class="metric-value">{done_docs} / {total_docs}</div></div>', unsafe_allow_html=True)
        with col2:
            st.markdown("**Готовность к отопительному периоду**")
            st.progress(progress, text=f"{progress:.0%}")

        st.dataframe(eval_list, use_container_width=True, height=500)

    # ===== ПЕРЕПИСКА =====
    elif page == "✉️ Переписка":
        st.markdown('<div class="section-header">✉️ Переписка</div>', unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f'<div class="metric-card purple"><div class="metric-label">Входящих всего</div><div class="metric-value">{len(mail)}</div></div>', unsafe_allow_html=True)
        with col2:
            pending = len(mail[mail["Исх. №"].isna() | (mail["Исх. №"] == "")])
            st.markdown(f'<div class="metric-card yellow"><div class="metric-label">Ожидают ответа</div><div class="metric-value">{pending}</div></div>', unsafe_allow_html=True)

        st.dataframe(mail, use_container_width=True, height=500)

    # ===== ФИНАНСЫ =====
    elif page == "💰 Финансы":
        st.markdown('<div class="section-header">💰 Финансы</div>', unsafe_allow_html=True)

        fin["Сумма"] = pd.to_numeric(fin["Сумма"], errors="coerce").fillna(0)
        income = fin[fin["Тип (приход/расход)"] == "Приход"]["Сумма"].sum()
        expense = fin[fin["Тип (приход/расход)"] == "Расход"]["Сумма"].sum()
        debt = fin[fin["Тип (приход/расход)"] == "Задолженность"]["Сумма"].sum()

        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f'<div class="metric-card green"><div class="metric-label">Приход</div><div class="metric-value">{income:,.0f} ₽</div></div>'.replace(",", " "), unsafe_allow_html=True)
        with col2:
            st.markdown(f'<div class="metric-card red"><div class="metric-label">Расход</div><div class="metric-value">{expense:,.0f} ₽</div></div>'.replace(",", " "), unsafe_allow_html=True)
        with col3:
            st.markdown(f'<div class="metric-card yellow"><div class="metric-label">Задолженность</div><div class="metric-value">{debt:,.0f} ₽</div></div>'.replace(",", " "), unsafe_allow_html=True)

        st.dataframe(fin, use_container_width=True, height=400)

else:
    st.warning("Данные не загружены. Проверьте ссылку на Яндекс.Диск.")
