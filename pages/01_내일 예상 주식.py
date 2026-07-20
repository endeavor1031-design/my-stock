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
:root {
    --up-color: #e53935;
    --down-color: #1565c0;
    --sidebar-text: #ffffff;
    --sidebar-muted: rgba(255, 255, 255, 0.72);
}

html,
body,
[data-testid="stAppViewContainer"] {
    background:
        linear-gradient(
            180deg,
            #fbfcff 0%,
            #f4f6fb 100%
        );
}

[data-testid="stHeader"] {
    background: transparent;
}

/* 사이드바 내부 구성 순서 */
[data-testid="stSidebarContent"] {
    display: flex !important;
    flex-direction: column !important;
}

/* 네비게이션 6개를 사이드바 맨 위에 배치 */
[data-testid="stSidebarNav"] {
    display: block !important;
    order: 1 !important;
    margin-top: 6px;
    margin-bottom: 14px;
}

/* 회사 정보와 예측 설정은 네비게이션 다음에 배치 */
[data-testid="stSidebarUserContent"] {
    order: 2 !important;
}

/* 사이드바 전체 그라데이션 */
[data-testid="stSidebar"] {
    background:
        radial-gradient(
            circle at 20% 10%,
            rgba(255, 104, 132, 0.36),
            transparent 25%
        ),
        radial-gradient(
            circle at 85% 24%,
            rgba(94, 125, 255, 0.38),
            transparent 28%
        ),
        radial-gradient(
            circle at 22% 82%,
            rgba(255, 71, 87, 0.30),
            transparent 26%
        ),
        linear-gradient(
            165deg,
            #091536 0%,
            #132b68 30%,
            #34319a 58%,
            #732e9e 78%,
            #bf344e 100%
        ) !important;
    border-right:
        1px solid rgba(255, 255, 255, 0.16);
}

[data-testid="stSidebar"] > div:first-child {
    display: flex;
    flex-direction: column;
    background: transparent !important;
}

[data-testid="stSidebar"]
[data-testid="stMarkdownContainer"],
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3,
[data-testid="stSidebar"] span {
    color: var(--sidebar-text);
}

/* 입력 위젯은 밝게 표시 */
[data-testid="stSidebar"]
[data-baseweb="select"] > div,
[data-testid="stSidebar"]
[data-baseweb="input"] > div,
[data-testid="stSidebar"]
div[role="radiogroup"] {
    background:
        rgba(255, 255, 255, 0.94);
    border:
        1px solid rgba(255, 255, 255, 0.28);
    border-radius: 12px;
}

[data-testid="stSidebar"]
[data-baseweb="select"] span,
[data-testid="stSidebar"]
[data-baseweb="select"] svg,
[data-testid="stSidebar"]
[data-baseweb="input"] input,
[data-testid="stSidebar"]
div[role="radiogroup"] label p {
    color: #17213d !important;
}

[data-testid="stSidebar"] hr {
    border-color:
        rgba(255, 255, 255, 0.20);
}

/* hani.inc 브랜드 카드 */
.hani-brand {
    position: relative;
    overflow: hidden;
    border-radius: 24px;
    padding: 18px;
    margin: 0 0 15px 0;
    background:
        linear-gradient(
            135deg,
            rgba(255, 255, 255, 0.18) 0%,
            rgba(255, 255, 255, 0.07) 100%
        );
    border:
        1px solid rgba(255, 255, 255, 0.25);
    box-shadow:
        0 18px 36px rgba(0, 0, 0, 0.25),
        inset 0 1px 0 rgba(255, 255, 255, 0.16);
    backdrop-filter: blur(16px);
}

.hani-brand::before {
    content: "";
    position: absolute;
    width: 170px;
    height: 170px;
    right: -88px;
    top: -98px;
    border-radius: 50%;
    background:
        radial-gradient(
            circle,
            rgba(255, 255, 255, 0.40) 0%,
            rgba(255, 255, 255, 0.02) 68%
        );
}

.hani-brand::after {
    content: "";
    position: absolute;
    width: 125px;
    height: 125px;
    left: -65px;
    bottom: -74px;
    border-radius: 40px;
    transform: rotate(30deg);
    background:
        linear-gradient(
            135deg,
            rgba(255, 73, 104, 0.75),
            rgba(255, 171, 86, 0.14)
        );
}

.hani-brand-row {
    position: relative;
    z-index: 2;
    display: flex;
    align-items: center;
    gap: 13px;
}

.hani-logo-shell {
    width: 70px;
    height: 70px;
    min-width: 70px;
    border-radius: 21px;
    padding: 1px;
    background:
        linear-gradient(
            135deg,
            #ff4d67 0%,
            #ffae57 35%,
            #765cff 68%,
            #3f7cff 100%
        );
    box-shadow:
        0 13px 28px rgba(0, 0, 0, 0.30),
        0 0 24px rgba(122, 92, 255, 0.30);
}

.hani-logo-inner {
    width: 100%;
    height: 100%;
    border-radius: 20px;
    display: flex;
    align-items: center;
    justify-content: center;
    background:
        linear-gradient(
            145deg,
            rgba(255, 255, 255, 0.24),
            rgba(255, 255, 255, 0.07)
        );
    border:
        1px solid rgba(255, 255, 255, 0.24);
}

.hani-logo-inner svg {
    width: 55px;
    height: 55px;
    filter:
        drop-shadow(
            0 4px 8px rgba(0, 0, 0, 0.24)
        );
}

.hani-brand-name {
    color: #ffffff;
    font-size: 1.55rem;
    line-height: 1.04;
    font-weight: 900;
    letter-spacing: -0.035em;
}

.hani-brand-subtitle {
    color:
        rgba(255, 255, 255, 0.75);
    font-size: 0.67rem;
    line-height: 1.3;
    margin-top: 5px;
    font-weight: 750;
    letter-spacing: 0.08em;
}

.hani-brand-line {
    position: relative;
    z-index: 2;
    height: 1px;
    margin: 15px 0 11px 0;
    background:
        linear-gradient(
            90deg,
            transparent,
            rgba(255, 255, 255, 0.48),
            transparent
        );
}

.hani-brand-copy {
    position: relative;
    z-index: 2;
    color:
        rgba(255, 255, 255, 0.79);
    font-size: 0.73rem;
    line-height: 1.5;
}

/* 기본 페이지 메뉴 디자인 */
[data-testid="stSidebarNav"]::before {
    content: "NAVIGATION";
    display: block;
    margin: 2px 0 8px 4px;
    color:
        rgba(255, 255, 255, 0.70);
    font-size: 0.70rem;
    font-weight: 800;
    letter-spacing: 0.14em;
}

[data-testid="stSidebarNav"] ul {
    padding-left: 0;
}

[data-testid="stSidebarNav"] li {
    margin-bottom: 4px;
}

[data-testid="stSidebarNav"] a {
    border-radius: 13px;
    padding: 9px 11px;
    background:
        rgba(255, 255, 255, 0.075);
    border:
        1px solid rgba(255, 255, 255, 0.10);
    transition:
        all 0.18s ease;
}

[data-testid="stSidebarNav"] a:hover {
    background:
        rgba(255, 255, 255, 0.18);
    border-color:
        rgba(255, 255, 255, 0.28);
    transform:
        translateX(3px);
}

[data-testid="stSidebarNav"]
a[aria-current="page"] {
    background:
        linear-gradient(
            90deg,
            rgba(239, 62, 74, 0.48),
            rgba(108, 99, 255, 0.48),
            rgba(21, 101, 192, 0.48)
        );
    border-color:
        rgba(255, 255, 255, 0.30);
    box-shadow:
        0 8px 18px rgba(0, 0, 0, 0.14);
}

[data-testid="stSidebarNav"] a span,
[data-testid="stSidebarNav"] a p {
    color: #ffffff !important;
    font-weight: 700 !important;
}

.sidebar-settings-title {
    color: #ffffff;
    font-size: 1.24rem;
    font-weight: 850;
    margin: 18px 0 10px 0;
}

/* 본문 */
.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
}

.main-title {
    font-size: 2.25rem;
    font-weight: 850;
    margin-bottom: 0.15rem;
    color: #18213d;
}

.subtitle {
    color: #667085;
    margin-bottom: 1.35rem;
}

.forecast-card {
    border:
        1px solid rgba(128, 128, 128, 0.18);
    border-radius: 18px;
    padding: 18px;
    min-height: 175px;
    background:
        linear-gradient(
            135deg,
            rgba(255, 255, 255, 0.96),
            rgba(243, 247, 255, 0.92)
        );
    box-shadow:
        0 12px 26px rgba(74, 96, 170, 0.09);
    margin-bottom: 14px;
}

.forecast-name {
    font-size: 1.05rem;
    font-weight: 800;
    color: #18213d;
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
    border-left: 5px solid #6c63ff;
    padding: 13px 16px;
    border-radius: 8px;
    background:
        linear-gradient(
            90deg,
            rgba(108, 99, 255, 0.08),
            rgba(21, 101, 192, 0.04)
        );
    margin: 10px 0 15px 0;
}

div[data-testid="stMetric"] {
    border:
        1px solid rgba(128, 128, 128, 0.16);
    border-radius: 15px;
    padding: 12px;
    background:
        linear-gradient(
            180deg,
            rgba(255, 255, 255, 0.94),
            rgba(245, 248, 255, 0.90)
        );
    box-shadow:
        0 8px 20px rgba(80, 95, 150, 0.06);
}

[data-baseweb="tab-list"] {
    gap: 8px;
}

[data-baseweb="tab"] {
    background:
        rgba(255, 255, 255, 0.78);
    border-radius: 999px;
    padding: 10px 18px;
    border:
        1px solid rgba(140, 160, 210, 0.14);
}

[data-baseweb="tab"][aria-selected="true"] {
    background:
        linear-gradient(
            90deg,
            #e53935 0%,
            #6c63ff 54%,
            #1565c0 100%
        );
    color: white;
}

/* 네비게이션 6개 메뉴 앞 이모지 */
[data-testid="stSidebarNav"] li:nth-child(1) a::before {
    content: "📊";
}

[data-testid="stSidebarNav"] li:nth-child(2) a::before {
    content: "🧠";
}

[data-testid="stSidebarNav"] li:nth-child(3) a::before {
    content: "🔮";
}

[data-testid="stSidebarNav"] li:nth-child(4) a::before {
    content: "📅";
}

[data-testid="stSidebarNav"] li:nth-child(5) a::before {
    content: "🗓️";
}

[data-testid="stSidebarNav"] li:nth-child(6) a::before {
    content: "🏆";
}

[data-testid="stSidebarNav"] li a::before {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 1.45rem;
    margin-right: 0.35rem;
    font-size: 1rem;
    line-height: 1;
    flex-shrink: 0;
}

[data-testid="stSidebarNav"] li a {
    display: flex !important;
    align-items: center !important;
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
    st.markdown(
        '<div class="hani-brand-wrapper">',
        unsafe_allow_html=True,
    )

    brand_html = (
        '<div class="hani-brand">'
        '<div class="hani-brand-row">'
        '<div class="hani-logo-shell">'
        '<div class="hani-logo-inner">'
        '<svg viewBox="0 0 100 100" '
        'xmlns="http://www.w3.org/2000/svg" '
        'aria-label="hani.inc logo">'
        '<defs>'
        '<linearGradient id="logoStrokeTomorrow" '
        'x1="0%" y1="0%" x2="100%" y2="100%">'
        '<stop offset="0%" stop-color="#ffffff"/>'
        '<stop offset="100%" stop-color="#dbe8ff"/>'
        '</linearGradient>'
        '</defs>'
        '<path d="M20 72V28M20 51H46M46 28V72" '
        'fill="none" '
        'stroke="url(#logoStrokeTomorrow)" '
        'stroke-width="9" '
        'stroke-linecap="round" '
        'stroke-linejoin="round"/>'
        '<path d="M58 69L68 55L77 61L89 40" '
        'fill="none" '
        'stroke="#ffffff" '
        'stroke-width="6" '
        'stroke-linecap="round" '
        'stroke-linejoin="round"/>'
        '<circle cx="89" cy="40" r="5" '
        'fill="#ffdf7e"/>'
        '<circle cx="68" cy="55" r="4" '
        'fill="#ff7b91"/>'
        '</svg>'
        '</div>'
        '</div>'
        '<div>'
        '<div class="hani-brand-name">hani.inc</div>'
        '<div class="hani-brand-subtitle">'
        'MARKET INTELLIGENCE<br>'
        'DATA &amp; ANALYTICS'
        '</div>'
        '</div>'
        '</div>'
        '<div class="hani-brand-line"></div>'
        '<div class="hani-brand-copy">'
        '시장 흐름과 기술지표를 바탕으로<br>'
        '다음 거래일을 분석하는 예측 대시보드'
        '</div>'
        '</div>'
    )

    st.markdown(
        brand_html,
        unsafe_allow_html=True,
    )

    st.markdown(
        '</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="sidebar-settings-wrapper">',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="sidebar-settings-title">'
        '내일 주가 예상 설정'
        '</div>',
        unsafe_allow_html=True,
    )

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
        available_stocks = list(
            STOCKS.keys()
        )
    else:
        available_stocks = [
            name
            for name, information
            in STOCKS.items()
            if information["market"]
            == selected_market
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
        "예상값은 과거 가격 데이터를 이용한 "
        "통계적 참고치이며 실제 주가를 보장하지 않습니다."
    )

    st.markdown(
        '</div>',
        unsafe_allow_html=True,
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
)
