import streamlit as st
import requests

st.set_page_config(page_title="Конвертер Валют", page_icon="💱")

st.title("Конвертер Валют")
st.write("Узнайте актуальный курс валют в реальном времени.")

@st.cache_data
def get_currencies():
    try:
        response = requests.get("https://api.frankfurter.app/currencies")
        if response.status_code == 200:
            return response.json()
        else:
            return {}
    except Exception as e:
        st.error(f"Ошибка получения списка валют: {e}")
        return {}

def get_rate(from_currency, to_currency, amount):
    try:
        url = f"https://api.frankfurter.app/latest?amount={amount}&from={from_currency}&to={to_currency}"
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            rate = data['rates'][to_currency]
            return rate
        else:
            return None
    except Exception as e:
        st.error(f"Ошибка получения курса: {e}")
        return None


currencies = get_currencies()

if currencies:
    currency_codes = list(currencies.keys())
    
    
    col1, col2 = st.columns(2)
    with col1:
        from_currency = st.selectbox(
            "Из валюты (1 ед.):",
            currency_codes,
            index=currency_codes.index("RUB") if "RUB" in currency_codes else 0
        )

    with col2:
        to_currency = st.selectbox(
            "В валюту:",
            currency_codes,
            index=currency_codes.index("USD") if "USD" in currency_codes else 1
        )

    st.divider()

    if st.button("Рассчитать курс"):
        if from_currency == to_currency:
            st.warning("Выберите разные валюты для конвертации.")
        else:
            with st.spinner('Загрузка данных...'):
                rate = get_rate(from_currency, to_currency, 1)
                
                if rate:
                    st.success("Курс получен успешно!")
                    
                    st.markdown(f"""
                    ### Результат:
                    **1 {from_currency}** = **{rate:.4f} {to_currency}**
                    """)
                    
                    inverse_rate = 1 / rate
                    st.caption(f"(Обратный курс: 1 {to_currency} ≈ {inverse_rate:.4f} {from_currency})")
                else:
                    st.error("Не удалось получить курс. Проверьте соединение с интернетом.")
else:
    st.error("Не удалось загрузить список валют. Возможно, сервис временно недоступен.")

st.markdown("---")
st.caption("Данные предоставлены сервисом Frankfurter API")