import math
from datetime import datetime, timedelta

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import yfinance as yf


st.set_page_config(
    page_title="내일 주가 예상",
    page_icon="🔮",
    layout="wide",
)


# =========================================================
# 종목 설정
# =========================================================
STOCKS = {
    "SK하이닉스": {"ticker": "000660.KS", "currency": "KRW", "market": "한국"},
    "삼성전자": {"ticker": "005930.KS", "currency": "KRW", "market": "한국"},
    "카카오": {"ticker": "035720.KS", "currency": "KRW", "market": "한국"},
    "NAVER": {"ticker": "035420.KS", "currency": "KRW", "market": "한국"},
    "현대차": {"ticker": "005380.KS", "currency": "KRW", "market": "한국"},
    "엔비디아": {"ticker": "NVDA", "currency": "USD", "market": "미국"},
    "AMD": {"ticker": "AMD", "currency": "USD", "market": "미국"},
    "브로드컴": {"ticker": "AVGO", "currency": "USD", "market": "미국"},
    "팔란티어": {"ticker": "PLTR", "currency": "USD", "market": "미국"},
    "애플": {"ticker": "AAPL", "currency": "USD", "market": "미국"},
    "마이크로소프트": {"ticker": "MSFT", "currency": "USD", "market": "미국"},
    "테슬라": {"ticker": "TSLA", "currency": "USD", "market": "미국"},
    "마이크론": {"ticker": "MU", "currency": "USD", "market": "미국"},
    "TSMC": {"ticker": "TSM", "currency": "USD", "market": "미국"},
    "ASML": {"ticker": "ASML", "currency": "USD", "market": "미국"},
    "슈퍼마이크로컴퓨터": {"ticker": "SMCI", "currency": "USD", "market": "미국"},
    "반에크 반도체 ETF": {"ticker": "SMH", "currency": "USD", "market": "미국"},
    "S&P 500": {"ticker": "^GSPC", "currency": "USD", "market": "지수"},
    "나스닥 종합": {"ticker": "^IXIC", "currency": "USD", "market": "지수"},
    "코스피": {"ticker": "^KS11", "currency": "KRW", "market": "지수"},
}

LOOKBACK_OPTIONS = {
    "3개월": "3mo",
    "6개월": "6mo",
    "1년": "1y",
    "2년": "2y",
}


# =========================================================
# 스타일
# =========================================================
st.markdown(
    """
    <style>
    .main-title {
        font-size: 2.25rem;
        font-weight: 850;
        margin-bottom: 0.15rem;
    }

    .subtitle {
        color: #777777;
        margin-bottom: 1.35rem;
    }

    .forecast-card {
        border: 1px solid rgba(128, 128, 128, 0.25);
        border-radius: 15px;
        padding: 18px;
        min-height: 175px;
        background-color: rgba(128, 128, 128, 0.04);
        margin-bottom: 14px;
    }

    .forecast-name {
        font-size: 1.05rem;
        font-weight: 800;
    }

    .forecast-ticker {
        color: #888888;
        font-size: 0.78rem;
        margin-bottom: 12px;
    }

    .forecast-price {
        font-size: 1.45rem;
        font-weight: 850;
        margin-bottom: 5px;
    }

    .forecast-label {
        font-size: 0.78rem;
        color: #777777;
        margin-top: 7px;
    }

    .analysis-box {
        border-left: 5px solid #777777;
        padding: 13px 16px;
        border-radius: 8px;
        background-color: rgba(128, 128, 128, 0.07);
        margin: 10px 0 15px 0;
    }

    div[data-testid="stMetric"] {
        border: 1px solid rgba(128, 128, 128, 0.22);
        border-radius: 13px;
        padding: 12px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# 공통 함수
# =========================================================
def safe_float(value, default=None):
    try:
        if value is None or pd.isna(value):
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def format_price(value, currency):
    value = safe_float(value)

    if value is None:
        return "-"

    if currency == "KRW":
        return f"₩{value:,.0f}"

    return f"${value:,.2f}"


def normalize_data(data):
    if data is None or data.empty:
        return pd.DataFrame()

    result = data.copy()

    if isinstance(result.columns, pd.MultiIndex):
        result.columns = result.columns.get_level_values(0)

    result = result.loc[:, ~result.columns.duplicated()]

    if "Close" not in result.columns:
        return pd.DataFrame()

    result = result.dropna(subset=["Close"], how="all")

    if result.empty:
        return pd.DataFrame()

    result.index = pd.to_datetime(result.index)

    try:
        result.index = result.index.tz_localize(None)
    except (TypeError, AttributeError):
        pass

    return result.sort_index()


# =========================================================
# Yahoo 데이터 조회
# =========================================================
@st.cache_data(ttl=1800, show_spinner=False)
def download_stock_data(ticker, period="1y"):
    error_messages = []

    try:
        data = yf.download(
            tickers=ticker,
            period=period,
            interval="1d",
            auto_adjust=False,
            actions=False,
            progress=False,
            threads=False,
            timeout=30,
            multi_level_index=False,
        )

        data = normalize_data(data)

        if not data.empty:
            return data, ""

        error_messages.append("yf.download에서 빈 데이터가 반환되었습니다.")

    except Exception as error:
        error_messages.append(
            f"yf.download: {type(error).__name__}: {error}"
        )

    try:
        data = yf.Ticker(ticker).history(
            period=period,
            interval="1d",
            auto_adjust=False,
            actions=False,
            timeout=30,
        )

        data = normalize_data(data)

        if not data.empty:
            return data, ""

        error_messages.append("Ticker.history에서 빈 데이터가 반환되었습니다.")

    except Exception as error:
        error_messages.append(
            f"Ticker.history: {type(error).__name__}: {error}"
        )

    return pd.DataFrame(), "\n".join(error_messages)


# =========================================================
# 기술지표
# =========================================================
def calculate_indicators(data):
    result = data.copy()
    close = result["Close"]

    result["RETURN"] = close.pct_change()
    result["MA5"] = close.rolling(5).mean()
    result["MA20"] = close.rolling(20).mean()
    result["MA60"] = close.rolling(60).mean()

    result["EMA12"] = close.ewm(span=12, adjust=False).mean()
    result["EMA26"] = close.ewm(span=26, adjust=False).mean()
    result["MACD"] = result["EMA12"] - result["EMA26"]
    result["MACD_SIGNAL"] = result["MACD"].ewm(
        span=9,
        adjust=False,
    ).mean()

    change = close.diff()
    gain = change.clip(lower=0)
    loss = -change.clip(upper=0)

    average_gain = gain.ewm(
        alpha=1 / 14,
        adjust=False,
        min_periods=14,
    ).mean()

    average_loss = loss.ewm(
        alpha=1 / 14,
        adjust=False,
        min_periods=14,
    ).mean()

    relative_strength = (
        average_gain
        / average_loss.replace(0, float("nan"))
    )

    result["RSI"] = (
        100 - 100 / (1 + relative_strength)
    )

    result["VOLATILITY20"] = (
        result["RETURN"].rolling(20).std()
    )

    return result


# =========================================================
# 다음 거래일 날짜
# 단순 주말 제외 방식
# =========================================================
def get_next_business_day(last_date):
    next_date = pd.Timestamp(last_date) + timedelta(days=1)

    while next_date.weekday() >= 5:
        next_date += timedelta(days=1)

    return next_date


# =========================================================
# 내일 예상 계산
# =========================================================
def calculate_tomorrow_forecast(data):
    """
    최근 모멘텀과 변동성을 이용한 단순 통계 모델입니다.

    예상수익률 구성:
    - 최근 5일 평균수익률: 30%
    - 최근 20일 평균수익률: 20%
    - 5일 이동평균 기울기: 15%
    - 20일 이동평균 기울기: 10%
    - MACD 신호: 15%
    - RSI 조정: 10%

    과도한 예측을 막기 위해 예상수익률을
    최근 일간 변동성의 일정 범위로 제한합니다.
    """
    indicators = calculate_indicators(data)
    valid_close = indicators["Close"].dropna()

    if len(valid_close) < 65:
        return None

    latest = indicators.iloc[-1]
    previous = indicators.iloc[-2]

    current_price = safe_float(latest["Close"])
    previous_price = safe_float(previous["Close"])

    returns = indicators["RETURN"].dropna()

    mean_return_5 = safe_float(
        returns.tail(5).mean(),
        0,
    )

    mean_return_20 = safe_float(
        returns.tail(20).mean(),
        0,
    )

    ma5_now = safe_float(latest["MA5"])
    ma5_previous = safe_float(previous["MA5"])
    ma20_now = safe_float(latest["MA20"])
    ma20_previous = safe_float(previous["MA20"])

    ma5_slope = 0
    ma20_slope = 0

    if ma5_now is not None and ma5_previous not in (None, 0):
        ma5_slope = ma5_now / ma5_previous - 1

    if ma20_now is not None and ma20_previous not in (None, 0):
        ma20_slope = ma20_now / ma20_previous - 1

    macd = safe_float(latest["MACD"], 0)
    macd_signal = safe_float(latest["MACD_SIGNAL"], 0)

    macd_component = 0

    if current_price not in (None, 0):
        macd_component = (
            macd - macd_signal
        ) / current_price

    rsi = safe_float(latest["RSI"], 50)

    # RSI가 과매수면 하향, 과매도면 상향 조정
    if rsi >= 70:
        rsi_component = -0.003
    elif rsi >= 60:
        rsi_component = -0.001
    elif rsi <= 30:
        rsi_component = 0.003
    elif rsi <= 40:
        rsi_component = 0.001
    else:
        rsi_component = 0

    raw_expected_return = (
        mean_return_5 * 0.30
        + mean_return_20 * 0.20
        + ma5_slope * 0.15
        + ma20_slope * 0.10
        + macd_component * 0.15
        + rsi_component * 0.10
    )

    daily_volatility = safe_float(
        returns.tail(20).std(),
        0,
    )

    # 예측치가 비현실적으로 커지지 않도록 제한
    maximum_expected_move = max(
        daily_volatility * 0.80,
        0.003,
    )

    expected_return = max(
        -maximum_expected_move,
        min(maximum_expected_move, raw_expected_return),
    )

    expected_price = current_price * (
        1 + expected_return
    )

    # 예상 범위는 최근 20일 변동성의 약 1배
    lower_return = expected_return - daily_volatility
    upper_return = expected_return + daily_volatility

    lower_price = max(
        0,
        current_price * (1 + lower_return),
    )

    upper_price = current_price * (
        1 + upper_return
    )

    positive_probability = 50

    if daily_volatility > 0:
        normalized_signal = (
            expected_return / daily_volatility
        )

        positive_probability = (
            50 + normalized_signal * 25
        )

    positive_probability = max(
        20,
        min(80, positive_probability),
    )

    if expected_return > 0.002:
        direction = "상승 우세"
        direction_color = "#e53935"
        arrow = "▲"
    elif expected_return < -0.002:
        direction = "하락 우세"
        direction_color = "#1565c0"
        arrow = "▼"
    else:
        direction = "보합 예상"
        direction_color = "#777777"
        arrow = "―"

    signal_strength = abs(
        positive_probability - 50
    ) * 2

    if signal_strength >= 45:
        confidence = "보통"
    elif signal_strength >= 25:
        confidence = "낮음"
    else:
        confidence = "매우 낮음"

    latest_date = indicators.index[-1]
    next_date = get_next_business_day(
        latest_date
    )

    price_change = (
        current_price - previous_price
        if previous_price is not None
        else None
    )

    daily_change_percent = (
        (current_price / previous_price - 1) * 100
        if previous_price not in (None, 0)
        else None
    )

    return {
        "current_price": current_price,
        "previous_price": previous_price,
        "price_change": price_change,
        "daily_change_percent": daily_change_percent,
        "expected_price": expected_price,
        "expected_return": expected_return * 100,
        "lower_price": lower_price,
        "upper_price": upper_price,
        "positive_probability": positive_probability,
        "negative_probability": 100 - positive_probability,
        "direction": direction,
        "direction_color": direction_color,
        "arrow": arrow,
        "confidence": confidence,
        "rsi": rsi,
        "daily_volatility": daily_volatility * 100,
        "mean_return_5": mean_return_5 * 100,
        "mean_return_20": mean_return_20 * 100,
        "ma5_slope": ma5_slope * 100,
        "ma20_slope": ma20_slope * 100,
        "macd": macd,
        "macd_signal": macd_signal,
        "latest_date": latest_date,
        "next_date": next_date,
    }


# =========================================================
# 차트 함수
# =========================================================
def create_forecast_chart(
    data,
    forecast,
    stock_name,
):
    recent = data.tail(60).copy()

    figure = go.Figure()

    figure.add_trace(
        go.Scatter(
            x=recent.index,
            y=recent["Close"],
            mode="lines",
            name="종가",
            line=dict(width=2),
        )
    )

    last_date = recent.index[-1]
    current_price = forecast["current_price"]
    next_date = forecast["next_date"]

    figure.add_trace(
        go.Scatter(
            x=[last_date, next_date],
            y=[
                current_price,
                forecast["expected_price"],
            ],
            mode="lines+markers",
            name="내일 기준 예상",
            line=dict(
                width=3,
                dash="dash",
            ),
            marker=dict(size=10),
        )
    )

    figure.add_trace(
        go.Scatter(
            x=[next_date],
            y=[forecast["upper_price"]],
            mode="markers",
            name="예상 상단",
            marker=dict(
                symbol="triangle-up",
                size=12,
            ),
        )
    )

    figure.add_trace(
        go.Scatter(
            x=[next_date],
            y=[forecast["lower_price"]],
            mode="markers",
            name="예상 하단",
            marker=dict(
                symbol="triangle-down",
                size=12,
            ),
        )
    )

    figure.add_trace(
        go.Scatter(
            x=[
                last_date,
                next_date,
                next_date,
                last_date,
            ],
            y=[
                current_price,
                forecast["upper_price"],
                forecast["lower_price"],
                current_price,
            ],
            fill="toself",
            fillcolor="rgba(128,128,128,0.15)",
            line=dict(
                color="rgba(128,128,128,0)",
            ),
            name="예상 변동 범위",
            hoverinfo="skip",
        )
    )

    figure.update_layout(
        title=f"{stock_name} 최근 주가와 다음 거래일 예상",
        xaxis_title="날짜",
        yaxis_title="가격",
        height=570,
        hovermode="x unified",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            x=0,
        ),
        margin=dict(
            l=20,
            r=20,
            t=80,
            b=20,
        ),
    )

    return figure


def create_probability_chart(forecast):
    figure = go.Figure()

    figure.add_trace(
        go.Bar(
            x=[
                forecast["positive_probability"],
                forecast["negative_probability"],
            ],
            y=["상승 가능성", "하락 가능성"],
            orientation="h",
            marker_color=[
                "#e53935",
                "#1565c0",
            ],
            text=[
                f"{forecast['positive_probability']:.1f}%",
                f"{forecast['negative_probability']:.1f}%",
            ],
            textposition="auto",
        )
    )

    figure.update_layout(
        title="모델 방향 확률",
        xaxis=dict(
            title="확률 (%)",
            range=[0, 100],
        ),
        height=320,
        margin=dict(
            l=20,
            r=20,
            t=65,
            b=20,
        ),
        showlegend=False,
    )

    return figure


def create_factor_chart(forecast):
    factors = {
        "최근 5일 평균수익률": forecast["mean_return_5"],
        "최근 20일 평균수익률": forecast["mean_return_20"],
        "5일선 기울기": forecast["ma5_slope"],
        "20일선 기울기": forecast["ma20_slope"],
    }

    colors = [
        "#e53935" if value >= 0 else "#1565c0"
        for value in factors.values()
    ]

    figure = go.Figure()

    figure.add_trace(
        go.Bar(
            x=list(factors.values()),
            y=list(factors.keys()),
            orientation="h",
            marker_color=colors,
            text=[
                f"{value:+.3f}%"
                for value in factors.values()
            ],
            textposition="auto",
        )
    )

    figure.add_vline(
        x=0,
        line_dash="dash",
    )

    figure.update_layout(
        title="예상 방향에 반영된 핵심 요인",
        xaxis_title="수익률 또는 기울기 (%)",
        height=390,
        margin=dict(
            l=20,
            r=20,
            t=65,
            b=20,
        ),
    )

    return figure


# =========================================================
# 설명 문구
# =========================================================
def create_forecast_explanation(forecast):
    messages = []

    if forecast["mean_return_5"] > 0:
        messages.append(
            "최근 5거래일 평균 수익률이 양수라 단기 모멘텀이 상승 방향입니다."
        )
    else:
        messages.append(
            "최근 5거래일 평균 수익률이 음수라 단기 모멘텀이 약한 상태입니다."
        )

    if forecast["ma20_slope"] > 0:
        messages.append(
            "20일 이동평균선의 기울기는 상승 방향입니다."
        )
    else:
        messages.append(
            "20일 이동평균선의 기울기는 하락 방향입니다."
        )

    if forecast["rsi"] >= 70:
        messages.append(
            f"RSI는 {forecast['rsi']:.1f}로 과매수 구간이어서 상승 예측치를 일부 낮췄습니다."
        )
    elif forecast["rsi"] <= 30:
        messages.append(
            f"RSI는 {forecast['rsi']:.1f}로 과매도 구간이어서 반등 가능성을 일부 반영했습니다."
        )
    else:
        messages.append(
            f"RSI는 {forecast['rsi']:.1f}로 중립 범위입니다."
        )

    if forecast["macd"] > forecast["macd_signal"]:
        messages.append(
            "MACD가 신호선을 상회해 모멘텀 요인은 긍정적입니다."
        )
    else:
        messages.append(
            "MACD가 신호선을 하회해 모멘텀 요인은 부정적입니다."
        )

    messages.append(
        f"최근 20일 일간 변동성은 {forecast['daily_volatility']:.2f}%이며, "
        "이를 이용해 예상 상단과 하단을 계산했습니다."
    )

    return " ".join(messages)


# =========================================================
# 페이지 제목
# =========================================================
st.markdown(
    '<div class="main-title">🔮 내일 주가 예상</div>',
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="subtitle">
        최근 가격 흐름, 이동평균선, RSI, MACD 및 변동성을 이용해
        다음 거래일의 예상 방향과 가격 범위를 계산합니다.
    </div>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# 사이드바
# =========================================================
with st.sidebar:
    st.header("내일 주가 예상 설정")

    market_options = [
        "전체",
        "한국",
        "미국",
        "지수",
    ]

    selected_market = st.selectbox(
        "시장",
        market_options,
    )

    if selected_market == "전체":
        available_stocks = list(STOCKS.keys())
    else:
        available_stocks = [
            name
            for name, information in STOCKS.items()
            if information["market"] == selected_market
        ]

    selected_stock = st.selectbox(
        "예상 종목",
        available_stocks,
    )

    selected_lookback_name = st.selectbox(
        "분석 기간",
        list(LOOKBACK_OPTIONS.keys()),
        index=2,
    )

    st.divider()

    if st.button(
        "데이터 새로고침",
        use_container_width=True,
    ):
        st.cache_data.clear()
        st.rerun()

    st.caption(
        "이 페이지의 예상값은 통계적 참고치이며 실제 내일 주가를 보장하지 않습니다."
    )


selected_information = STOCKS[selected_stock]
selected_ticker = selected_information["ticker"]
selected_currency = selected_information["currency"]
selected_period = LOOKBACK_OPTIONS[
    selected_lookback_name
]


# =========================================================
# 데이터 조회 및 분석
# =========================================================
with st.spinner(
    f"{selected_stock} 데이터를 불러오고 다음 거래일을 계산하는 중입니다."
):
    stock_data, data_error = download_stock_data(
        ticker=selected_ticker,
        period=selected_period,
    )

if stock_data.empty:
    st.error(
        "Yahoo Finance에서 주가 데이터를 불러오지 못했습니다."
    )

    if data_error:
        st.code(data_error)

    st.info(
        "Streamlit Cloud 공유 IP가 Yahoo Finance에서 일시적으로 제한될 수 있습니다. "
        "잠시 후 데이터 새로고침을 눌러 다시 확인해 주세요."
    )

    st.stop()


forecast = calculate_tomorrow_forecast(
    stock_data
)

if forecast is None:
    st.error(
        "예상치를 계산하기 위한 거래일 데이터가 부족합니다. "
        "분석 기간을 6개월 이상으로 선택해 주세요."
    )
    st.stop()


# =========================================================
# 상단 정보
# =========================================================
st.caption(
    f"티커: {selected_ticker} · "
    f"최종 데이터: {forecast['latest_date'].strftime('%Y-%m-%d')} · "
    f"다음 예상 거래일: {forecast['next_date'].strftime('%Y-%m-%d')}"
)

metric_columns = st.columns(6)

metric_columns[0].metric(
    "최근 종가",
    format_price(
        forecast["current_price"],
        selected_currency,
    ),
    (
        f"{forecast['daily_change_percent']:+.2f}%"
        if forecast["daily_change_percent"] is not None
        else None
    ),
)

metric_columns[1].metric(
    "기준 예상가",
    format_price(
        forecast["expected_price"],
        selected_currency,
    ),
    f"{forecast['expected_return']:+.2f}%",
)

metric_columns[2].metric(
    "예상 하단",
    format_price(
        forecast["lower_price"],
        selected_currency,
    ),
)

metric_columns[3].metric(
    "예상 상단",
    format_price(
        forecast["upper_price"],
        selected_currency,
    ),
)

metric_columns[4].metric(
    "상승 가능성",
    f"{forecast['positive_probability']:.1f}%",
)

metric_columns[5].metric(
    "모델 신뢰도",
    forecast["confidence"],
)


# =========================================================
# 예상 방향 표시
# =========================================================
st.markdown(
    f"""
    <div class="forecast-card">
        <div class="forecast-name">
            {selected_stock} 다음 거래일 예상
        </div>
        <div class="forecast-ticker">
            {selected_ticker} · {forecast['next_date'].strftime('%Y-%m-%d')}
        </div>
        <div
            class="forecast-price"
            style="color:{forecast['direction_color']};"
        >
            {forecast['arrow']} {forecast['direction']}
        </div>
        <div>
            기준 예상가:
            <strong>
                {format_price(forecast['expected_price'], selected_currency)}
            </strong>
            ({forecast['expected_return']:+.2f}%)
        </div>
        <div>
            예상 범위:
            <strong>
                {format_price(forecast['lower_price'], selected_currency)}
                ~
                {format_price(forecast['upper_price'], selected_currency)}
            </strong>
        </div>
        <div class="forecast-label">
            예상 범위는 최근 20거래일 변동성을 반영한 통계적 범위입니다.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# 탭
# =========================================================
forecast_tab, factor_tab, history_tab, raw_tab = st.tabs(
    [
        "내일 예상",
        "예상 근거",
        "과거 검증",
        "원본 데이터",
    ]
)


# =========================================================
# 1. 내일 예상
# =========================================================
with forecast_tab:
    st.plotly_chart(
        create_forecast_chart(
            stock_data,
            forecast,
            selected_stock,
        ),
        use_container_width=True,
    )

    left_column, right_column = st.columns(2)

    with left_column:
        st.plotly_chart(
            create_probability_chart(
                forecast
            ),
            use_container_width=True,
        )

    with right_column:
        st.plotly_chart(
            create_factor_chart(
                forecast
            ),
            use_container_width=True,
        )

    st.markdown(
        f"""
        <div class="analysis-box">
            <strong>자동 해석</strong><br>
            {create_forecast_explanation(forecast)}
        </div>
        """,
        unsafe_allow_html=True,
    )


# =========================================================
# 2. 예상 근거
# =========================================================
with factor_tab:
    st.subheader("예상값 계산에 반영된 지표")

    factor_table = pd.DataFrame(
        {
            "지표": [
                "최근 5일 평균수익률",
                "최근 20일 평균수익률",
                "5일 이동평균 기울기",
                "20일 이동평균 기울기",
                "RSI(14)",
                "MACD",
                "MACD Signal",
                "20일 일간 변동성",
            ],
            "현재 값": [
                forecast["mean_return_5"],
                forecast["mean_return_20"],
                forecast["ma5_slope"],
                forecast["ma20_slope"],
                forecast["rsi"],
                forecast["macd"],
                forecast["macd_signal"],
                forecast["daily_volatility"],
            ],
            "단위": [
                "%",
                "%",
                "%",
                "%",
                "점",
                "가격 단위",
                "가격 단위",
                "%",
            ],
        }
    )

    st.dataframe(
        factor_table,
        use_container_width=True,
        hide_index=True,
        column_config={
            "현재 값": st.column_config.NumberColumn(
                format="%.4f"
            )
        },
    )

    st.markdown(
        """
        ### 계산 방식

        기준 예상수익률은 최근 5일·20일 평균수익률, 이동평균선 기울기,
        MACD와 RSI를 가중 결합해 계산합니다. 이후 최근 20일 변동성을
        이용해 예상값이 지나치게 커지는 것을 제한합니다.

        예상 상단과 하단은 기준 예상수익률에 최근 20일 일간 표준편차를
        더하고 빼서 산출합니다. 따라서 갑작스러운 뉴스, 실적 발표,
        금리 변화, 환율, 장전·시간외 거래는 반영하지 못합니다.
        """
    )


# =========================================================
# 3. 과거 검증
# =========================================================
with history_tab:
    st.subheader("최근 데이터 기반 방향 예측 간이 검증")

    indicators = calculate_indicators(
        stock_data
    )

    validation_rows = []

    # 최근 최대 60개 시점에 대해 다음 날 방향만 간이 검증
    start_position = max(
        65,
        len(indicators) - 60,
    )

    for position in range(
        start_position,
        len(indicators) - 1,
    ):
        historical_data = indicators.iloc[
            :position + 1
        ].copy()

        historical_forecast = (
            calculate_tomorrow_forecast(
                historical_data
            )
        )

        if historical_forecast is None:
            continue

        actual_today = safe_float(
            indicators["Close"].iloc[position]
        )

        actual_next = safe_float(
            indicators["Close"].iloc[position + 1]
        )

        if actual_today in (None, 0) or actual_next is None:
            continue

        actual_return = (
            actual_next / actual_today - 1
        ) * 100

        predicted_return = (
            historical_forecast[
                "expected_return"
            ]
        )

        predicted_direction = (
            1 if predicted_return > 0
            else -1 if predicted_return < 0
            else 0
        )

        actual_direction = (
            1 if actual_return > 0
            else -1 if actual_return < 0
            else 0
        )

        validation_rows.append(
            {
                "예측 기준일": indicators.index[
                    position
                ],
                "예상 수익률(%)": predicted_return,
                "실제 다음날 수익률(%)": actual_return,
                "방향 적중": (
                    predicted_direction
                    == actual_direction
                ),
            }
        )

    validation_data = pd.DataFrame(
        validation_rows
    )

    if validation_data.empty:
        st.warning(
            "검증 가능한 데이터가 부족합니다."
        )
    else:
        accuracy = (
            validation_data["방향 적중"].mean()
            * 100
        )

        average_error = (
            validation_data[
                "예상 수익률(%)"
            ]
            - validation_data[
                "실제 다음날 수익률(%)"
            ]
        ).abs().mean()

        validation_columns = st.columns(3)

        validation_columns[0].metric(
            "검증 거래일",
            f"{len(validation_data)}일",
        )

        validation_columns[1].metric(
            "방향 적중률",
            f"{accuracy:.1f}%",
        )

        validation_columns[2].metric(
            "평균 절대오차",
            f"{average_error:.2f}%p",
        )

        validation_figure = go.Figure()

        validation_figure.add_trace(
            go.Scatter(
                x=validation_data["예측 기준일"],
                y=validation_data[
                    "예상 수익률(%)"
                ],
                mode="lines",
                name="예상 수익률",
            )
        )

        validation_figure.add_trace(
            go.Scatter(
                x=validation_data["예측 기준일"],
                y=validation_data[
                    "실제 다음날 수익률(%)"
                ],
                mode="lines",
                name="실제 다음날 수익률",
            )
        )

        validation_figure.add_hline(
            y=0,
            line_dash="dash",
        )

        validation_figure.update_layout(
            title="예상 수익률과 실제 다음날 수익률",
            xaxis_title="예측 기준일",
            yaxis_title="수익률 (%)",
            height=520,
            hovermode="x unified",
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                x=0,
            ),
            margin=dict(
                l=20,
                r=20,
                t=80,
                b=20,
            ),
        )

        st.plotly_chart(
            validation_figure,
            use_container_width=True,
        )

        display_validation = (
            validation_data.copy()
        )

        display_validation[
            "예측 기준일"
        ] = display_validation[
            "예측 기준일"
        ].dt.strftime("%Y-%m-%d")

        st.dataframe(
            display_validation.sort_values(
                "예측 기준일",
                ascending=False,
            ),
            use_container_width=True,
            hide_index=True,
            column_config={
                "예상 수익률(%)":
                    st.column_config.NumberColumn(
                        format="%.3f%%"
                    ),
                "실제 다음날 수익률(%)":
                    st.column_config.NumberColumn(
                        format="%.3f%%"
                    ),
                "방향 적중":
                    st.column_config.CheckboxColumn(),
            },
        )

        st.caption(
            "과거 적중률이 높더라도 미래 성과를 보장하지 않습니다."
        )


# =========================================================
# 4. 원본 데이터
# =========================================================
with raw_tab:
    st.subheader(
        f"{selected_stock} 원본 데이터"
    )

    display_data = stock_data.copy()
    display_data.index.name = "날짜"
    display_data = display_data.sort_index(
        ascending=False
    )

    available_columns = [
        column
        for column in [
            "Open",
            "High",
            "Low",
            "Close",
            "Adj Close",
            "Volume",
        ]
        if column in display_data.columns
    ]

    display_data = display_data[
        available_columns
    ]

    st.dataframe(
        display_data,
        use_container_width=True,
    )

    st.download_button(
        label="CSV 파일 다운로드",
        data=display_data.to_csv(
            encoding="utf-8-sig"
        ),
        file_name=(
            f"{selected_ticker}_"
            f"{datetime.now().strftime('%Y%m%d')}.csv"
        ),
        mime="text/csv",
    )


st.divider()

st.warning(
    "이 페이지는 내일 주가를 확정적으로 예측하지 않습니다. "
    "예상가는 과거 가격 데이터만 이용한 통계적 참고치이며, "
    "뉴스·실적·정책·환율·장전 및 시간외 거래는 반영하지 못합니다."
)try:
    df, info = load_stock_data(ticker_symbol, period_map[period_option])
    currency = info.get('currency', 'USD')

    if df.empty:
        st.error("데이터를 불러올 수 없습니다.")
    else:
        # -------------------------------------------------------------
        # PAGE 1: 주가 대시보드
        # -------------------------------------------------------------
        if page == "📊 주가 대시보드":
            st.title(f"📊 {selected_name} ({ticker_symbol}) 실시간 대시보드")

            # 요약 지표 (Metrics)
            latest_price = df['Close'].iloc[-1]
            prev_price = df['Close'].iloc[-2] if len(df) > 1 else latest_price
            change = latest_price - prev_price
            pct_change = (change / prev_price) * 100

            col1, col2, col3, col4 = st.columns(4)
            col1.metric("현재가 / 종가", f"{latest_price:,.2f} {currency}", f"{change:+,.2f} ({pct_change:+.2f}%)")
            col2.metric("기간 최고가", f"{df['High'].max():,.2f} {currency}")
            col3.metric("기간 최저가", f"{df['Low'].min():,.2f} {currency}")
            col4.metric("평균 거래량", f"{int(df['Volume'].mean()):,}")

            st.markdown("---")

            # Plotly 차트 유형 선택
            chart_type = st.radio("차트 유형 선택:", ["캔들스틱 (Candlestick)", "선 그래프 (Line)"], horizontal=True)

            fig = go.Figure()

            if "캔들스틱" in chart_type:
                fig.add_trace(go.Candlestick(
                    x=df.index,
                    open=df['Open'],
                    high=df['High'],
                    low=df['Low'],
                    close=df['Close'],
                    name="주가"
                ))
            else:
                fig.add_trace(go.Scatter(
                    x=df.index,
                    y=df['Close'],
                    mode='lines',
                    name="종가",
                    line=dict(color='#00CC96', width=2)
                ))

            # 이동평균선 추가
            df['MA20'] = df['Close'].rolling(window=20).mean()
            fig.add_trace(go.Scatter(
                x=df.index,
                y=df['MA20'],
                mode='lines',
                name="20일 이동평균",
                line=dict(color='#FFA15A', width=1.5, dash='dash')
            ))

            fig.update_layout(
                title=f"{selected_name} 주가 추이",
                yaxis_title=f"가격 ({currency})",
                xaxis_title="날짜",
                template="plotly_white",
                height=500,
                xaxis_rangeslider_visible=False
            )

            st.plotly_chart(fig, use_container_width=True)

            with st.expander("📄 상세 데이터 보기"):
                st.dataframe(df.sort_index(ascending=False))

        # -------------------------------------------------------------
        # PAGE 2: 내일 주가 예측
        # -------------------------------------------------------------
        elif page == "🔮 내일 주가 예측":
            st.title(f"🔮 {selected_name} ({ticker_symbol}) 내일 예상 주가 예측")
            st.warning("⚠️ 본 예측 결과는 단순 선형 회귀(Linear Regression) 기술 분석에 기반한 참고용 지표이며, 투자의 절대적 기준이 될 수 없습니다.")

            # 학습에 사용할 기간 데이터 준비 (최근 60일 기준)
            data_fit = df.tail(60).copy()
            data_fit['Days'] = np.arange(len(data_fit))

            X = data_fit[['Days']].values
            y = data_fit['Close'].values

            # 선형 회귀 모델 학습
            model = LinearRegression()
            model.fit(X, y)

            # 내일(다음 거래일) 위치 예측
            next_day_index = np.array([[len(data_fit)]])
            predicted_price = model.predict(next_day_index)[0]

            latest_actual_price = data_fit['Close'].iloc[-1]
            diff = predicted_price - latest_actual_price
            diff_pct = (diff / latest_actual_price) * 100

            # 예측 결과 지표 표시
            col1, col2, col3 = st.columns(3)
            col1.metric("최근 종가", f"{latest_actual_price:,.2f} {currency}")
            col2.metric("내일 예상 주가", f"{predicted_price:,.2f} {currency}", f"{diff:+,.2f} ({diff_pct:+.2f}%)")
            col3.metric("예측 추세", "상승 예상" if diff > 0 else "하락 예상")

            st.markdown("---")

            # 예측 추세선 포함 차트 시각화
            future_days = np.append(X, next_day_index).reshape(-1, 1)
            trend_line = model.predict(future_days)

            # 날짜 배열 생성
            last_date = data_fit.index[-1]
            next_date = last_date + datetime.timedelta(days=1)
            date_range = list(data_fit.index) + [next_date]

            fig_pred = go.Figure()

            # 실제 종가
            fig_pred.add_trace(go.Scatter(
                x=data_fit.index,
                y=data_fit['Close'],
                mode='lines+markers',
                name='최근 실제 종가',
                line=dict(color='#636EFA', width=2)
            ))

            # 선형 추세선
            fig_pred.add_trace(go.Scatter(
                x=date_range,
                y=trend_line,
                mode='lines',
                name='회귀 추세선',
                line=dict(color='#EF553B', dash='dash')
            ))

            # 내일 예측 점
            fig_pred.add_trace(go.Scatter(
                x=[next_date],
                y=[predicted_price],
                mode='markers',
                name='내일 예상가',
                marker=dict(color='gold', size=12, symbol='star')
            ))

            fig_pred.update_layout(
                title=f"{selected_name} 최근 60일 추세 및 내일 주가 예측 차트",
                yaxis_title=f"가격 ({currency})",
                xaxis_title="날짜",
                template="plotly_white",
                height=500
            )

            st.plotly_chart(fig_pred, use_container_width=True)

except Exception as e:
    st.error(f"데이터를 처리하는 중 오류가 발생했습니다: {e}")
