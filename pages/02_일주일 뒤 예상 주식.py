import math
from datetime import datetime, timedelta

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import yfinance as yf


st.set_page_config(
    page_title="일주일 뒤 주가 예상",
    page_icon="📅",
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
    "6개월": "6mo",
    "1년": "1y",
    "2년": "2y",
    "5년": "5y",
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

/* 네비게이션 6개를 맨 위에 배치 */
[data-testid="stSidebarNav"] {
    display: block !important;
    order: 1 !important;
    margin-top: 6px;
    margin-bottom: 14px;
}

/* 회사 정보와 설정은 네비게이션 다음 */
[data-testid="stSidebarUserContent"] {
    order: 2 !important;
}

/* 구버전 Streamlit 구조 대응 */
[data-testid="stSidebar"] > div:first-child {
    display: flex;
    flex-direction: column;
    background: transparent !important;
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

/* 입력 위젯 */
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

/* 네비게이션 디자인 */
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
    display: flex !important;
    align-items: center !important;
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

/* 네비게이션 메뉴별 이모지 */
[data-testid="stSidebarNav"]
li:nth-child(1) a::before {
    content: "📊";
}

[data-testid="stSidebarNav"]
li:nth-child(2) a::before {
    content: "🧠";
}

[data-testid="stSidebarNav"]
li:nth-child(3) a::before {
    content: "🔮";
}

[data-testid="stSidebarNav"]
li:nth-child(4) a::before {
    content: "📅";
}

[data-testid="stSidebarNav"]
li:nth-child(5) a::before {
    content: "🗓️";
}

[data-testid="stSidebarNav"]
li:nth-child(6) a::before {
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
# Yahoo Finance 조회
# =========================================================
@st.cache_data(ttl=1800, show_spinner=False)
def download_stock_data(ticker, period="1y"):
    errors = []

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

        errors.append("yf.download에서 빈 데이터가 반환되었습니다.")

    except Exception as error:
        errors.append(
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

        errors.append("Ticker.history에서 빈 데이터가 반환되었습니다.")

    except Exception as error:
        errors.append(
            f"Ticker.history: {type(error).__name__}: {error}"
        )

    return pd.DataFrame(), "\n".join(errors)


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

    return result


def next_business_days(last_date, count=5):
    dates = []
    current = pd.Timestamp(last_date)

    while len(dates) < count:
        current += timedelta(days=1)

        if current.weekday() < 5:
            dates.append(current)

    return dates


# =========================================================
# 5거래일 예상 계산
# =========================================================
def calculate_week_forecast(data):
    indicators = calculate_indicators(data)
    close = indicators["Close"].dropna()

    if len(close) < 70:
        return None

    latest = indicators.iloc[-1]
    previous = indicators.iloc[-2]
    returns = indicators["RETURN"].dropna()

    current_price = safe_float(latest["Close"])
    previous_price = safe_float(previous["Close"])

    mean_5 = safe_float(returns.tail(5).mean(), 0)
    mean_20 = safe_float(returns.tail(20).mean(), 0)
    mean_60 = safe_float(returns.tail(60).mean(), 0)

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
    signal = safe_float(latest["MACD_SIGNAL"], 0)

    macd_component = 0

    if current_price not in (None, 0):
        macd_component = (macd - signal) / current_price

    rsi = safe_float(latest["RSI"], 50)

    if rsi >= 75:
        rsi_component = -0.0025
    elif rsi >= 65:
        rsi_component = -0.0010
    elif rsi <= 25:
        rsi_component = 0.0025
    elif rsi <= 35:
        rsi_component = 0.0010
    else:
        rsi_component = 0

    expected_daily_return = (
        mean_5 * 0.28
        + mean_20 * 0.22
        + mean_60 * 0.10
        + ma5_slope * 0.15
        + ma20_slope * 0.10
        + macd_component * 0.10
        + rsi_component * 0.05
    )

    daily_volatility = safe_float(
        returns.tail(20).std(),
        0,
    )

    max_daily_signal = max(
        daily_volatility * 0.65,
        0.0025,
    )

    expected_daily_return = max(
        -max_daily_signal,
        min(max_daily_signal, expected_daily_return),
    )

    forecast_dates = next_business_days(
        indicators.index[-1],
        5,
    )

    rows = []

    for day_number, forecast_date in enumerate(
        forecast_dates,
        start=1,
    ):
        expected_price = current_price * (
            (1 + expected_daily_return) ** day_number
        )

        cumulative_return = (
            expected_price / current_price - 1
        )

        range_scale = daily_volatility * math.sqrt(
            day_number
        )

        lower_price = max(
            0,
            current_price
            * (1 + cumulative_return - range_scale),
        )

        upper_price = current_price * (
            1 + cumulative_return + range_scale
        )

        rows.append(
            {
                "거래일": day_number,
                "예상 날짜": forecast_date,
                "기준 예상가": expected_price,
                "예상 수익률(%)": cumulative_return * 100,
                "예상 하단": lower_price,
                "예상 상단": upper_price,
            }
        )

    forecast_table = pd.DataFrame(rows)
    final_row = forecast_table.iloc[-1]

    positive_probability = 50

    if daily_volatility > 0:
        weekly_signal = (
            final_row["예상 수익률(%)"] / 100
        ) / (
            daily_volatility * math.sqrt(5)
        )

        positive_probability = 50 + weekly_signal * 25

    positive_probability = max(
        20,
        min(80, positive_probability),
    )

    weekly_return = safe_float(
        final_row["예상 수익률(%)"],
        0,
    )

    if weekly_return > 1.0:
        direction = "상승 우세"
        direction_color = "#e53935"
        arrow = "▲"
    elif weekly_return < -1.0:
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

    daily_change = None

    if previous_price not in (None, 0):
        daily_change = (
            current_price / previous_price - 1
        ) * 100

    return {
        "table": forecast_table,
        "current_price": current_price,
        "daily_change": daily_change,
        "expected_daily_return": (
            expected_daily_return * 100
        ),
        "week_expected_price": safe_float(
            final_row["기준 예상가"]
        ),
        "week_expected_return": weekly_return,
        "week_lower": safe_float(
            final_row["예상 하단"]
        ),
        "week_upper": safe_float(
            final_row["예상 상단"]
        ),
        "positive_probability": positive_probability,
        "negative_probability": 100 - positive_probability,
        "direction": direction,
        "direction_color": direction_color,
        "arrow": arrow,
        "confidence": confidence,
        "daily_volatility": daily_volatility * 100,
        "mean_5": mean_5 * 100,
        "mean_20": mean_20 * 100,
        "mean_60": mean_60 * 100,
        "ma5_slope": ma5_slope * 100,
        "ma20_slope": ma20_slope * 100,
        "rsi": rsi,
        "macd": macd,
        "macd_signal": signal,
        "latest_date": indicators.index[-1],
    }


# =========================================================
# 차트
# =========================================================
def create_week_forecast_chart(
    data,
    forecast,
    stock_name,
):
    recent = data.tail(70).copy()
    forecast_table = forecast["table"]

    figure = go.Figure()

    figure.add_trace(
        go.Scatter(
            x=recent.index,
            y=recent["Close"],
            mode="lines",
            name="실제 종가",
            line=dict(width=2),
        )
    )

    path_dates = [
        recent.index[-1]
    ] + forecast_table["예상 날짜"].tolist()

    expected_path = [
        forecast["current_price"]
    ] + forecast_table["기준 예상가"].tolist()

    upper_path = [
        forecast["current_price"]
    ] + forecast_table["예상 상단"].tolist()

    lower_path = [
        forecast["current_price"]
    ] + forecast_table["예상 하단"].tolist()

    figure.add_trace(
        go.Scatter(
            x=path_dates,
            y=upper_path,
            mode="lines",
            name="예상 상단",
            line=dict(
                width=1,
                dash="dot",
            ),
        )
    )

    figure.add_trace(
        go.Scatter(
            x=path_dates,
            y=lower_path,
            mode="lines",
            name="예상 하단",
            line=dict(
                width=1,
                dash="dot",
            ),
            fill="tonexty",
            fillcolor="rgba(128,128,128,0.16)",
        )
    )

    figure.add_trace(
        go.Scatter(
            x=path_dates,
            y=expected_path,
            mode="lines+markers",
            name="기준 예상 경로",
            line=dict(
                width=3,
                dash="dash",
            ),
            marker=dict(size=8),
        )
    )

    figure.update_layout(
        title=f"{stock_name} 다음 5거래일 예상 경로",
        xaxis_title="날짜",
        yaxis_title="가격",
        height=600,
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
            y=[
                "5거래일 상승 가능성",
                "5거래일 하락 가능성",
            ],
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
        title="일주일 방향 가능성",
        xaxis=dict(
            title="확률 (%)",
            range=[0, 100],
        ),
        height=330,
        showlegend=False,
        margin=dict(
            l=20,
            r=20,
            t=65,
            b=20,
        ),
    )

    return figure


def create_factor_chart(forecast):
    factors = {
        "최근 5일 평균수익률": forecast["mean_5"],
        "최근 20일 평균수익률": forecast["mean_20"],
        "최근 60일 평균수익률": forecast["mean_60"],
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
        title="일주일 예상에 반영된 핵심 요인",
        xaxis_title="수익률 또는 기울기 (%)",
        height=400,
        margin=dict(
            l=20,
            r=20,
            t=65,
            b=20,
        ),
    )

    return figure


def create_explanation(forecast):
    messages = []

    if forecast["mean_5"] > 0:
        messages.append(
            "최근 5거래일 평균 수익률은 상승 방향입니다."
        )
    else:
        messages.append(
            "최근 5거래일 평균 수익률은 하락 방향입니다."
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
            f"RSI는 {forecast['rsi']:.1f}로 과매수 구간이어서 상승 예상치를 낮췄습니다."
        )
    elif forecast["rsi"] <= 30:
        messages.append(
            f"RSI는 {forecast['rsi']:.1f}로 과매도 구간이어서 반등 가능성을 반영했습니다."
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
        f"최근 20일 일간 변동성은 {forecast['daily_volatility']:.2f}%입니다. "
        "예상 범위는 기간이 길어질수록 제곱근 비율로 넓어집니다."
    )

    return " ".join(messages)


# =========================================================
# 과거 5거래일 예측 검증
# =========================================================
def backtest_week_forecast(data, test_count=40):
    rows = []
    start_position = max(
        70,
        len(data) - test_count - 5,
    )

    for position in range(
        start_position,
        len(data) - 5,
    ):
        historical_data = data.iloc[
            :position + 1
        ].copy()

        forecast = calculate_week_forecast(
            historical_data
        )

        if forecast is None:
            continue

        current_price = safe_float(
            data["Close"].iloc[position]
        )

        actual_future_price = safe_float(
            data["Close"].iloc[position + 5]
        )

        if (
            current_price in (None, 0)
            or actual_future_price is None
        ):
            continue

        actual_return = (
            actual_future_price / current_price - 1
        ) * 100

        predicted_return = forecast[
            "week_expected_return"
        ]

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

        rows.append(
            {
                "예측 기준일": data.index[position],
                "5거래일 예상 수익률(%)": predicted_return,
                "실제 5거래일 수익률(%)": actual_return,
                "방향 적중": (
                    predicted_direction
                    == actual_direction
                ),
            }
        )

    return pd.DataFrame(rows)


# =========================================================
# 화면
# =========================================================
st.markdown(
    '<div class="main-title">📅 일주일 뒤 주가 예상</div>',
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="subtitle">
        최근 수익률, 이동평균선, RSI, MACD 및 변동성을 이용해
        다음 5거래일의 기준 예상 경로와 가격 범위를 계산합니다.
    </div>
    """,
    unsafe_allow_html=True,
)

with st.sidebar:
    brand_html = (
        '<div class="hani-brand">'
        '<div class="hani-brand-row">'
        '<div class="hani-logo-shell">'
        '<div class="hani-logo-inner">'
        '<svg viewBox="0 0 100 100" '
        'xmlns="http://www.w3.org/2000/svg" '
        'aria-label="hani.inc logo">'
        '<defs>'
        '<linearGradient id="logoStrokeWeek" '
        'x1="0%" y1="0%" x2="100%" y2="100%">'
        '<stop offset="0%" stop-color="#ffffff"/>'
        '<stop offset="100%" stop-color="#dbe8ff"/>'
        '</linearGradient>'
        '</defs>'
        '<path d="M20 72V28M20 51H46M46 28V72" '
        'fill="none" '
        'stroke="url(#logoStrokeWeek)" '
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
        '시장 모멘텀과 변동성을 바탕으로<br>'
        '다음 5거래일을 분석하는 예측 대시보드'
        '</div>'
        '</div>'
    )

    st.markdown(
        brand_html,
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="sidebar-settings-title">'
        '일주일 예상 설정'
        '</div>',
        unsafe_allow_html=True,
    )

    selected_market = st.selectbox(
        "시장",
        [
            "전체",
            "한국",
            "미국",
            "지수",
        ],
    )

    if selected_market == "전체":
        available_names = list(
            STOCKS.keys()
        )
    else:
        available_names = [
            name
            for name, information
            in STOCKS.items()
            if information["market"]
            == selected_market
        ]

    selected_name = st.selectbox(
        "예상 종목",
        available_names,
    )

    selected_lookback_name = st.selectbox(
        "분석 기간",
        list(LOOKBACK_OPTIONS.keys()),
        index=1,
    )

    st.divider()

    if st.button(
        "데이터 새로고침",
        use_container_width=True,
    ):
        st.cache_data.clear()
        st.rerun()

    st.caption(
        "일주일은 달력상 7일이 아니라 "
        "다음 5거래일을 의미합니다."
    )


selected_info = STOCKS[selected_name]
selected_ticker = selected_info["ticker"]
selected_currency = selected_info["currency"]
selected_period = LOOKBACK_OPTIONS[
    selected_lookback_name
]

with st.spinner(
    f"{selected_name} 데이터를 불러오고 5거래일 예상치를 계산하는 중입니다."
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
        "Streamlit Cloud 공유 IP가 Yahoo Finance에서 제한된 경우 "
        "잠시 후 데이터 새로고침을 눌러 다시 확인해 주세요."
    )

    st.stop()


forecast = calculate_week_forecast(
    stock_data
)

if forecast is None:
    st.error(
        "5거래일 예상치를 계산하기 위한 데이터가 부족합니다. "
        "분석 기간을 1년 이상으로 선택해 주세요."
    )
    st.stop()


forecast_table = forecast["table"]
final_date = forecast_table.iloc[-1][
    "예상 날짜"
]

st.caption(
    f"티커: {selected_ticker} · "
    f"최종 데이터: {forecast['latest_date'].strftime('%Y-%m-%d')} · "
    f"5거래일 뒤 예상일: {final_date.strftime('%Y-%m-%d')}"
)

metric_columns = st.columns(6)

metric_columns[0].metric(
    "최근 종가",
    format_price(
        forecast["current_price"],
        selected_currency,
    ),
    (
        f"{forecast['daily_change']:+.2f}%"
        if forecast["daily_change"] is not None
        else None
    ),
)

metric_columns[1].metric(
    "5거래일 기준 예상가",
    format_price(
        forecast["week_expected_price"],
        selected_currency,
    ),
    f"{forecast['week_expected_return']:+.2f}%",
)

metric_columns[2].metric(
    "5거래일 예상 하단",
    format_price(
        forecast["week_lower"],
        selected_currency,
    ),
)

metric_columns[3].metric(
    "5거래일 예상 상단",
    format_price(
        forecast["week_upper"],
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

st.markdown(
    f"""
    <div class="forecast-card">
        <div class="forecast-name">
            {selected_name} 다음 5거래일 예상
        </div>
        <div class="forecast-ticker">
            {selected_ticker} · {final_date.strftime('%Y-%m-%d')}
        </div>
        <div
            class="forecast-price"
            style="color:{forecast['direction_color']};"
        >
            {forecast['arrow']} {forecast['direction']}
        </div>
        <div>
            5거래일 기준 예상가:
            <strong>
                {format_price(forecast['week_expected_price'], selected_currency)}
            </strong>
            ({forecast['week_expected_return']:+.2f}%)
        </div>
        <div>
            예상 범위:
            <strong>
                {format_price(forecast['week_lower'], selected_currency)}
                ~
                {format_price(forecast['week_upper'], selected_currency)}
            </strong>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


forecast_tab, path_tab, validation_tab, raw_tab = st.tabs(
    [
        "일주일 예상",
        "일별 예상 경로",
        "과거 검증",
        "원본 데이터",
    ]
)


with forecast_tab:
    st.plotly_chart(
        create_week_forecast_chart(
            stock_data,
            forecast,
            selected_name,
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
            {create_explanation(forecast)}
        </div>
        """,
        unsafe_allow_html=True,
    )


with path_tab:
    st.subheader("다음 5거래일 예상 경로")

    display_forecast = forecast_table.copy()

    display_forecast[
        "예상 날짜"
    ] = display_forecast[
        "예상 날짜"
    ].dt.strftime("%Y-%m-%d")

    st.dataframe(
        display_forecast,
        use_container_width=True,
        hide_index=True,
        column_config={
            "기준 예상가":
                st.column_config.NumberColumn(
                    format="%.2f"
                ),
            "예상 수익률(%)":
                st.column_config.NumberColumn(
                    format="%.2f%%"
                ),
            "예상 하단":
                st.column_config.NumberColumn(
                    format="%.2f"
                ),
            "예상 상단":
                st.column_config.NumberColumn(
                    format="%.2f"
                ),
        },
    )

    st.info(
        "예상 경로는 동일한 일간 모멘텀이 이어진다는 단순 가정으로 계산됩니다. "
        "실제 주가는 각 거래일의 뉴스와 수급에 따라 경로를 크게 벗어날 수 있습니다."
    )


with validation_tab:
    st.subheader("과거 5거래일 예측 간이 검증")

    validation_data = backtest_week_forecast(
        stock_data,
        test_count=40,
    )

    if validation_data.empty:
        st.warning(
            "과거 검증에 필요한 데이터가 부족합니다."
        )
    else:
        accuracy = (
            validation_data["방향 적중"].mean()
            * 100
        )

        average_error = (
            validation_data[
                "5거래일 예상 수익률(%)"
            ]
            - validation_data[
                "실제 5거래일 수익률(%)"
            ]
        ).abs().mean()

        columns = st.columns(3)

        columns[0].metric(
            "검증 횟수",
            f"{len(validation_data)}회",
        )

        columns[1].metric(
            "방향 적중률",
            f"{accuracy:.1f}%",
        )

        columns[2].metric(
            "평균 절대오차",
            f"{average_error:.2f}%p",
        )

        validation_figure = go.Figure()

        validation_figure.add_trace(
            go.Scatter(
                x=validation_data[
                    "예측 기준일"
                ],
                y=validation_data[
                    "5거래일 예상 수익률(%)"
                ],
                mode="lines",
                name="예상 수익률",
            )
        )

        validation_figure.add_trace(
            go.Scatter(
                x=validation_data[
                    "예측 기준일"
                ],
                y=validation_data[
                    "실제 5거래일 수익률(%)"
                ],
                mode="lines",
                name="실제 수익률",
            )
        )

        validation_figure.add_hline(
            y=0,
            line_dash="dash",
        )

        validation_figure.update_layout(
            title="예상 5거래일 수익률과 실제 수익률",
            xaxis_title="예측 기준일",
            yaxis_title="수익률 (%)",
            height=530,
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

        validation_display = (
            validation_data.copy()
        )

        validation_display[
            "예측 기준일"
        ] = validation_display[
            "예측 기준일"
        ].dt.strftime("%Y-%m-%d")

        st.dataframe(
            validation_display.sort_values(
                "예측 기준일",
                ascending=False,
            ),
            use_container_width=True,
            hide_index=True,
            column_config={
                "5거래일 예상 수익률(%)":
                    st.column_config.NumberColumn(
                        format="%.3f%%"
                    ),
                "실제 5거래일 수익률(%)":
                    st.column_config.NumberColumn(
                        format="%.3f%%"
                    ),
                "방향 적중":
                    st.column_config.CheckboxColumn(),
            },
        )


with raw_tab:
    st.subheader(
        f"{selected_name} 원본 데이터"
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
    "이 페이지는 5거래일 뒤 주가를 확정적으로 예측하지 않습니다. "
    "예상가는 과거 가격의 모멘텀과 변동성만 이용한 통계적 참고치입니다. "
    "뉴스, 실적, 금리, 환율, 정책 및 수급 변화는 반영하지 못합니다."
)
