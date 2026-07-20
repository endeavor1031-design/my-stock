import math
from datetime import datetime

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import yfinance as yf
from plotly.subplots import make_subplots


# =========================================================
# 페이지 설정
# =========================================================
st.set_page_config(
    page_title="AI 반도체 주식 전문 분석",
    page_icon="🧠",
    layout="wide",
)


# =========================================================
# AI 반도체 관련 종목
# =========================================================
AI_SEMICONDUCTOR_STOCKS = {
    # GPU / AI 가속기
    "엔비디아": {
        "ticker": "NVDA",
        "category": "AI 가속기",
        "country": "미국",
        "currency": "USD",
        "description": "GPU 및 AI 데이터센터 가속기",
    },
    "AMD": {
        "ticker": "AMD",
        "category": "AI 가속기",
        "country": "미국",
        "currency": "USD",
        "description": "GPU, CPU 및 AI 가속기",
    },
    "브로드컴": {
        "ticker": "AVGO",
        "category": "AI 가속기",
        "country": "미국",
        "currency": "USD",
        "description": "AI 네트워크 및 맞춤형 ASIC",
    },
    "ARM": {
        "ticker": "ARM",
        "category": "AI 설계",
        "country": "영국/미국",
        "currency": "USD",
        "description": "저전력 CPU 및 반도체 설계 IP",
    },
    "마벨 테크놀로지": {
        "ticker": "MRVL",
        "category": "AI 네트워크",
        "country": "미국",
        "currency": "USD",
        "description": "데이터센터 네트워크 및 맞춤형 반도체",
    },

    # 메모리
    "SK하이닉스": {
        "ticker": "000660.KS",
        "category": "AI 메모리",
        "country": "한국",
        "currency": "KRW",
        "description": "HBM 및 고성능 DRAM",
    },
    "삼성전자": {
        "ticker": "005930.KS",
        "category": "AI 메모리",
        "country": "한국",
        "currency": "KRW",
        "description": "HBM, DRAM, NAND 및 파운드리",
    },
    "마이크론": {
        "ticker": "MU",
        "category": "AI 메모리",
        "country": "미국",
        "currency": "USD",
        "description": "HBM, DRAM 및 NAND",
    },

    # 파운드리
    "TSMC": {
        "ticker": "TSM",
        "category": "파운드리",
        "country": "대만",
        "currency": "USD",
        "description": "첨단 반도체 위탁생산",
    },

    # 반도체 장비
    "ASML": {
        "ticker": "ASML",
        "category": "반도체 장비",
        "country": "네덜란드",
        "currency": "USD",
        "description": "EUV 노광장비",
    },
    "어플라이드 머티리얼즈": {
        "ticker": "AMAT",
        "category": "반도체 장비",
        "country": "미국",
        "currency": "USD",
        "description": "반도체 증착 및 공정 장비",
    },
    "램리서치": {
        "ticker": "LRCX",
        "category": "반도체 장비",
        "country": "미국",
        "currency": "USD",
        "description": "반도체 식각 및 증착 장비",
    },
    "KLA": {
        "ticker": "KLAC",
        "category": "반도체 장비",
        "country": "미국",
        "currency": "USD",
        "description": "반도체 검사 및 계측 장비",
    },

    # AI 서버
    "슈퍼마이크로컴퓨터": {
        "ticker": "SMCI",
        "category": "AI 서버",
        "country": "미국",
        "currency": "USD",
        "description": "AI 서버 및 데이터센터 시스템",
    },

    # ETF / 지수
    "반에크 반도체 ETF": {
        "ticker": "SMH",
        "category": "반도체 ETF",
        "country": "미국",
        "currency": "USD",
        "description": "글로벌 반도체 대표 ETF",
    },
    "필라델피아 반도체 지수": {
        "ticker": "^SOX",
        "category": "반도체 지수",
        "country": "미국",
        "currency": "USD",
        "description": "미국 주요 반도체 기업 지수",
    },
}


PERIOD_OPTIONS = {
    "1개월": "1mo",
    "3개월": "3mo",
    "6개월": "6mo",
    "1년": "1y",
    "2년": "2y",
    "5년": "5y",
}

INTERVAL_OPTIONS = {
    "일봉": "1d",
    "주봉": "1wk",
    "월봉": "1mo",
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

/* 회사 정보와 분석 설정은 네비게이션 다음에 배치 */
[data-testid="stSidebarUserContent"] {
    order: 2 !important;
}

/* 사이드바 전체 */
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

/* 기본 멀티페이지 메뉴 디자인 */
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
    margin-bottom: 0.2rem;
    color: #18213d;
}

.sub-title {
    color: #667085;
    margin-bottom: 1.4rem;
}

.company-card {
    border:
        1px solid rgba(128, 128, 128, 0.18);
    border-radius: 18px;
    padding: 16px;
    min-height: 155px;
    background:
        linear-gradient(
            180deg,
            rgba(255, 255, 255, 0.95),
            rgba(245, 248, 255, 0.90)
        );
    box-shadow:
        0 10px 22px rgba(74, 96, 170, 0.08);
    margin-bottom: 12px;
}

.company-name {
    font-size: 1.02rem;
    font-weight: 750;
    color: #18213d;
}

.company-ticker {
    font-size: 0.78rem;
    color: #888888;
    margin-bottom: 9px;
}

.company-price {
    font-size: 1.4rem;
    font-weight: 800;
    margin-bottom: 5px;
    color: #18213d;
}

.company-category {
    display: inline-block;
    margin-top: 8px;
    padding: 3px 8px;
    border-radius: 8px;
    font-size: 0.74rem;
    background:
        rgba(100, 100, 100, 0.13);
}

.analysis-box {
    border-left: 5px solid #6c63ff;
    padding: 12px 16px;
    border-radius: 8px;
    background:
        linear-gradient(
            90deg,
            rgba(108, 99, 255, 0.08),
            rgba(21, 101, 192, 0.04)
        );
    margin-bottom: 12px;
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
# 공통 처리
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

    if currency == "JPY":
        return f"¥{value:,.0f}"

    return f"${value:,.2f}"


def format_large_number(value, currency=None):
    value = safe_float(value)

    if value is None:
        return "-"

    symbol = {
        "KRW": "₩",
        "USD": "$",
        "JPY": "¥",
    }.get(currency, "")

    absolute_value = abs(value)

    if absolute_value >= 1_000_000_000_000:
        return f"{symbol}{value / 1_000_000_000_000:,.2f}조"

    if absolute_value >= 100_000_000:
        return f"{symbol}{value / 100_000_000:,.2f}억"

    if absolute_value >= 1_000_000:
        return f"{symbol}{value / 1_000_000:,.2f}백만"

    if absolute_value >= 10_000:
        return f"{symbol}{value / 10_000:,.2f}만"

    return f"{symbol}{value:,.0f}"


def clean_stock_data(data, ticker):
    if data is None or data.empty:
        return pd.DataFrame()

    result = data.copy()

    if isinstance(result.columns, pd.MultiIndex):
        try:
            if ticker in result.columns.get_level_values(-1):
                result = result.xs(
                    ticker,
                    axis=1,
                    level=-1,
                )
            else:
                result.columns = result.columns.get_level_values(0)
        except (KeyError, ValueError):
            result.columns = result.columns.get_level_values(0)

    result = result.loc[:, ~result.columns.duplicated()]

    try:
        result.index = pd.to_datetime(result.index)
    except Exception:
        return pd.DataFrame()

    try:
        result.index = result.index.tz_localize(None)
    except (TypeError, AttributeError):
        pass

    if "Close" not in result.columns:
        return pd.DataFrame()

    result = result.dropna(
        subset=["Close"],
        how="all",
    )

    return result.sort_index()


# =========================================================
# 데이터 다운로드
# =========================================================
@st.cache_data(ttl=600, show_spinner=False)
def download_stock_data(
    ticker,
    period="1y",
    interval="1d",
):
    attempts = [
        {
            "method": "history",
            "period": period,
            "interval": interval,
        },
        {
            "method": "download",
            "period": period,
            "interval": interval,
        },
        {
            "method": "history",
            "period": "1mo",
            "interval": "1d",
        },
    ]

    for attempt in attempts:
        try:
            if attempt["method"] == "history":
                stock = yf.Ticker(ticker)

                data = stock.history(
                    period=attempt["period"],
                    interval=attempt["interval"],
                    auto_adjust=False,
                    actions=False,
                    repair=True,
                    timeout=20,
                )

            else:
                data = yf.download(
                    tickers=ticker,
                    period=attempt["period"],
                    interval=attempt["interval"],
                    auto_adjust=False,
                    progress=False,
                    threads=False,
                    repair=True,
                    timeout=20,
                )

            data = clean_stock_data(
                data,
                ticker,
            )

            if not data.empty:
                return data

        except Exception:
            continue

    return pd.DataFrame()


@st.cache_data(ttl=1800, show_spinner=False)
def download_multiple_close_prices(
    tickers,
    period="1y",
):
    result = pd.DataFrame()

    for ticker in tickers:
        data = download_stock_data(
            ticker=ticker,
            period=period,
            interval="1d",
        )

        if not data.empty:
            result[ticker] = data["Close"]

    if result.empty:
        return pd.DataFrame()

    return result.sort_index().dropna(
        how="all"
    )


@st.cache_data(ttl=3600, show_spinner=False)
def get_company_information(ticker):
    """
    Yahoo Finance의 기업 정보를 불러옵니다.
    정보가 제공되지 않더라도 앱은 정상 작동합니다.
    """
    information = {}

    try:
        stock = yf.Ticker(ticker)
        information = stock.info or {}
    except Exception:
        information = {}

    return {
        "market_cap": information.get("marketCap"),
        "trailing_pe": information.get("trailingPE"),
        "forward_pe": information.get("forwardPE"),
        "price_to_book": information.get("priceToBook"),
        "enterprise_to_ebitda": information.get(
            "enterpriseToEbitda"
        ),
        "revenue_growth": information.get("revenueGrowth"),
        "earnings_growth": information.get("earningsGrowth"),
        "gross_margin": information.get("grossMargins"),
        "operating_margin": information.get(
            "operatingMargins"
        ),
        "profit_margin": information.get("profitMargins"),
        "return_on_equity": information.get(
            "returnOnEquity"
        ),
        "debt_to_equity": information.get("debtToEquity"),
        "analyst_target": information.get(
            "targetMeanPrice"
        ),
        "recommendation": information.get(
            "recommendationKey"
        ),
        "sector": information.get("sector"),
        "industry": information.get("industry"),
    }


# =========================================================
# 기술지표 계산
# =========================================================
def calculate_indicators(data):
    result = data.copy()

    close = result["Close"]

    result["MA20"] = close.rolling(20).mean()
    result["MA60"] = close.rolling(60).mean()
    result["MA120"] = close.rolling(120).mean()

    result["EMA12"] = close.ewm(
        span=12,
        adjust=False,
    ).mean()

    result["EMA26"] = close.ewm(
        span=26,
        adjust=False,
    ).mean()

    result["MACD"] = (
        result["EMA12"] - result["EMA26"]
    )

    result["MACD_SIGNAL"] = result["MACD"].ewm(
        span=9,
        adjust=False,
    ).mean()

    result["MACD_HIST"] = (
        result["MACD"] - result["MACD_SIGNAL"]
    )

    price_change = close.diff()
    gain = price_change.clip(lower=0)
    loss = -price_change.clip(upper=0)

    average_gain = gain.rolling(14).mean()
    average_loss = loss.rolling(14).mean()

    relative_strength = (
        average_gain
        / average_loss.replace(0, float("nan"))
    )

    result["RSI"] = (
        100 - 100 / (1 + relative_strength)
    )

    result.loc[
        (average_loss == 0) & (average_gain > 0),
        "RSI",
    ] = 100

    result["BB_MIDDLE"] = close.rolling(20).mean()
    standard_deviation = close.rolling(20).std()

    result["BB_UPPER"] = (
        result["BB_MIDDLE"]
        + 2 * standard_deviation
    )

    result["BB_LOWER"] = (
        result["BB_MIDDLE"]
        - 2 * standard_deviation
    )

    return result


def calculate_stock_statistics(data):
    if data.empty:
        return {}

    close = data["Close"].dropna()

    if len(close) < 2:
        return {}

    daily_return = close.pct_change().dropna()

    current_price = safe_float(close.iloc[-1])
    previous_price = safe_float(close.iloc[-2])
    start_price = safe_float(close.iloc[0])

    daily_change = (
        (current_price / previous_price - 1) * 100
        if previous_price not in (None, 0)
        else None
    )

    period_return = (
        (current_price / start_price - 1) * 100
        if start_price not in (None, 0)
        else None
    )

    annual_volatility = (
        daily_return.std()
        * math.sqrt(252)
        * 100
        if not daily_return.empty
        else None
    )

    annual_return = (
        daily_return.mean()
        * 252
        * 100
        if not daily_return.empty
        else None
    )

    risk_free_rate = 0.03

    sharpe_ratio = None

    if (
        not daily_return.empty
        and daily_return.std() != 0
    ):
        sharpe_ratio = (
            daily_return.mean() * 252
            - risk_free_rate
        ) / (
            daily_return.std()
            * math.sqrt(252)
        )

    cumulative = (
        1 + daily_return
    ).cumprod()

    rolling_maximum = cumulative.cummax()

    drawdown = (
        cumulative / rolling_maximum - 1
    )

    maximum_drawdown = (
        drawdown.min() * 100
        if not drawdown.empty
        else None
    )

    return {
        "current_price": current_price,
        "previous_price": previous_price,
        "daily_change": daily_change,
        "period_return": period_return,
        "annual_return": annual_return,
        "annual_volatility": annual_volatility,
        "sharpe_ratio": sharpe_ratio,
        "maximum_drawdown": maximum_drawdown,
        "period_high": safe_float(close.max()),
        "period_low": safe_float(close.min()),
        "average_volume": (
            safe_float(
                data["Volume"].tail(20).mean()
            )
            if "Volume" in data.columns
            else None
        ),
    }


# =========================================================
# AI 반도체 종합점수
# =========================================================
def calculate_analysis_score(
    data,
    company_info,
):
    """
    기술적 흐름, 수익성, 성장성, 위험을 합산한 단순 참고점수입니다.
    투자 추천 점수가 아닙니다.
    """
    if data.empty:
        return None, {}

    indicators = calculate_indicators(data)
    statistics = calculate_stock_statistics(data)

    current_close = safe_float(
        indicators["Close"].iloc[-1]
    )

    ma20 = safe_float(
        indicators["MA20"].iloc[-1]
    )

    ma60 = safe_float(
        indicators["MA60"].iloc[-1]
    )

    ma120 = safe_float(
        indicators["MA120"].iloc[-1]
    )

    rsi = safe_float(
        indicators["RSI"].iloc[-1]
    )

    macd = safe_float(
        indicators["MACD"].iloc[-1]
    )

    macd_signal = safe_float(
        indicators["MACD_SIGNAL"].iloc[-1]
    )

    momentum_score = 50

    if current_close is not None and ma20 is not None:
        momentum_score += 8 if current_close > ma20 else -8

    if current_close is not None and ma60 is not None:
        momentum_score += 8 if current_close > ma60 else -8

    if current_close is not None and ma120 is not None:
        momentum_score += 7 if current_close > ma120 else -7

    if (
        macd is not None
        and macd_signal is not None
    ):
        momentum_score += 7 if macd > macd_signal else -7

    if rsi is not None:
        if 45 <= rsi <= 65:
            momentum_score += 5
        elif rsi >= 75:
            momentum_score -= 5
        elif rsi <= 30:
            momentum_score += 2

    momentum_score = max(
        0,
        min(100, momentum_score),
    )

    growth_score = 50

    revenue_growth = safe_float(
        company_info.get("revenue_growth")
    )

    earnings_growth = safe_float(
        company_info.get("earnings_growth")
    )

    if revenue_growth is not None:
        if revenue_growth >= 0.30:
            growth_score += 25
        elif revenue_growth >= 0.15:
            growth_score += 18
        elif revenue_growth >= 0.05:
            growth_score += 8
        elif revenue_growth < 0:
            growth_score -= 20

    if earnings_growth is not None:
        if earnings_growth >= 0.30:
            growth_score += 25
        elif earnings_growth >= 0.15:
            growth_score += 18
        elif earnings_growth >= 0:
            growth_score += 6
        else:
            growth_score -= 18

    growth_score = max(
        0,
        min(100, growth_score),
    )

    profitability_score = 50

    operating_margin = safe_float(
        company_info.get("operating_margin")
    )

    return_on_equity = safe_float(
        company_info.get("return_on_equity")
    )

    if operating_margin is not None:
        if operating_margin >= 0.30:
            profitability_score += 25
        elif operating_margin >= 0.20:
            profitability_score += 18
        elif operating_margin >= 0.10:
            profitability_score += 8
        elif operating_margin < 0:
            profitability_score -= 25

    if return_on_equity is not None:
        if return_on_equity >= 0.30:
            profitability_score += 20
        elif return_on_equity >= 0.15:
            profitability_score += 12
        elif return_on_equity >= 0:
            profitability_score += 4
        else:
            profitability_score -= 20

    profitability_score = max(
        0,
        min(100, profitability_score),
    )

    risk_score = 70

    volatility = safe_float(
        statistics.get("annual_volatility")
    )

    maximum_drawdown = safe_float(
        statistics.get("maximum_drawdown")
    )

    if volatility is not None:
        if volatility >= 70:
            risk_score -= 30
        elif volatility >= 50:
            risk_score -= 20
        elif volatility >= 35:
            risk_score -= 10
        elif volatility <= 25:
            risk_score += 10

    if maximum_drawdown is not None:
        if maximum_drawdown <= -50:
            risk_score -= 25
        elif maximum_drawdown <= -35:
            risk_score -= 15
        elif maximum_drawdown <= -20:
            risk_score -= 5

    risk_score = max(
        0,
        min(100, risk_score),
    )

    total_score = (
        momentum_score * 0.35
        + growth_score * 0.25
        + profitability_score * 0.20
        + risk_score * 0.20
    )

    components = {
        "기술적 흐름": round(momentum_score, 1),
        "성장성": round(growth_score, 1),
        "수익성": round(profitability_score, 1),
        "위험관리": round(risk_score, 1),
    }

    return round(total_score, 1), components


# =========================================================
# 차트 함수
# =========================================================
def create_candlestick_chart(
    data,
    company_name,
    show_ma20=True,
    show_ma60=True,
    show_ma120=False,
    show_bollinger=False,
):
    chart_data = calculate_indicators(data)

    figure = make_subplots(
        rows=2,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.04,
        row_heights=[0.75, 0.25],
        subplot_titles=(
            f"{company_name} 주가",
            "거래량",
        ),
    )

    figure.add_trace(
        go.Candlestick(
            x=chart_data.index,
            open=chart_data["Open"],
            high=chart_data["High"],
            low=chart_data["Low"],
            close=chart_data["Close"],
            name="주가",
            increasing_line_color="#e53935",
            increasing_fillcolor="#e53935",
            decreasing_line_color="#1565c0",
            decreasing_fillcolor="#1565c0",
        ),
        row=1,
        col=1,
    )

    if show_ma20:
        figure.add_trace(
            go.Scatter(
                x=chart_data.index,
                y=chart_data["MA20"],
                name="20일 이동평균",
                mode="lines",
                line=dict(width=1.5),
            ),
            row=1,
            col=1,
        )

    if show_ma60:
        figure.add_trace(
            go.Scatter(
                x=chart_data.index,
                y=chart_data["MA60"],
                name="60일 이동평균",
                mode="lines",
                line=dict(width=1.5),
            ),
            row=1,
            col=1,
        )

    if show_ma120:
        figure.add_trace(
            go.Scatter(
                x=chart_data.index,
                y=chart_data["MA120"],
                name="120일 이동평균",
                mode="lines",
                line=dict(width=1.5),
            ),
            row=1,
            col=1,
        )

    if show_bollinger:
        figure.add_trace(
            go.Scatter(
                x=chart_data.index,
                y=chart_data["BB_UPPER"],
                name="볼린저 상단",
                mode="lines",
                line=dict(
                    width=1,
                    dash="dot",
                ),
            ),
            row=1,
            col=1,
        )

        figure.add_trace(
            go.Scatter(
                x=chart_data.index,
                y=chart_data["BB_LOWER"],
                name="볼린저 하단",
                mode="lines",
                fill="tonexty",
                line=dict(
                    width=1,
                    dash="dot",
                ),
                opacity=0.18,
            ),
            row=1,
            col=1,
        )

    if (
        "Volume" in chart_data.columns
        and "Open" in chart_data.columns
    ):
        volume_colors = [
            "#e53935"
            if close >= open_price
            else "#1565c0"
            for close, open_price in zip(
                chart_data["Close"],
                chart_data["Open"],
            )
        ]

        figure.add_trace(
            go.Bar(
                x=chart_data.index,
                y=chart_data["Volume"],
                name="거래량",
                marker_color=volume_colors,
                opacity=0.70,
            ),
            row=2,
            col=1,
        )

    figure.update_layout(
        height=700,
        hovermode="x unified",
        xaxis_rangeslider_visible=False,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="left",
            x=0,
        ),
        margin=dict(
            l=20,
            r=20,
            t=75,
            b=20,
        ),
    )

    figure.update_xaxes(
        rangeslider_visible=False
    )

    figure.update_yaxes(
        title_text="가격",
        row=1,
        col=1,
    )

    figure.update_yaxes(
        title_text="거래량",
        row=2,
        col=1,
    )

    return figure


def create_rsi_macd_chart(
    data,
    company_name,
):
    chart_data = calculate_indicators(data)

    figure = make_subplots(
        rows=2,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.10,
        subplot_titles=(
            f"{company_name} RSI",
            f"{company_name} MACD",
        ),
    )

    figure.add_trace(
        go.Scatter(
            x=chart_data.index,
            y=chart_data["RSI"],
            name="RSI",
            mode="lines",
            line=dict(width=2),
        ),
        row=1,
        col=1,
    )

    figure.add_hline(
        y=70,
        line_dash="dash",
        line_color="#e53935",
        annotation_text="과매수 70",
        row=1,
        col=1,
    )

    figure.add_hline(
        y=30,
        line_dash="dash",
        line_color="#1565c0",
        annotation_text="과매도 30",
        row=1,
        col=1,
    )

    macd_colors = [
        "#e53935" if value >= 0 else "#1565c0"
        for value in chart_data["MACD_HIST"].fillna(0)
    ]

    figure.add_trace(
        go.Scatter(
            x=chart_data.index,
            y=chart_data["MACD"],
            name="MACD",
            mode="lines",
        ),
        row=2,
        col=1,
    )

    figure.add_trace(
        go.Scatter(
            x=chart_data.index,
            y=chart_data["MACD_SIGNAL"],
            name="Signal",
            mode="lines",
        ),
        row=2,
        col=1,
    )

    figure.add_trace(
        go.Bar(
            x=chart_data.index,
            y=chart_data["MACD_HIST"],
            name="MACD Histogram",
            marker_color=macd_colors,
            opacity=0.65,
        ),
        row=2,
        col=1,
    )

    figure.update_layout(
        height=650,
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

    figure.update_yaxes(
        range=[0, 100],
        row=1,
        col=1,
    )

    return figure


def create_relative_return_chart(
    close_data,
    ticker_to_name,
):
    figure = go.Figure()

    for ticker in close_data.columns:
        series = close_data[ticker].dropna()

        if series.empty:
            continue

        normalized = (
            series / series.iloc[0] - 1
        ) * 100

        figure.add_trace(
            go.Scatter(
                x=normalized.index,
                y=normalized,
                name=ticker_to_name.get(
                    ticker,
                    ticker,
                ),
                mode="lines",
                line=dict(width=2),
            )
        )

    figure.add_hline(
        y=0,
        line_dash="dash",
        annotation_text="기준 수익률 0%",
    )

    figure.update_layout(
        title="AI 반도체 종목 상대 수익률",
        xaxis_title="날짜",
        yaxis_title="누적 수익률 (%)",
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


def create_correlation_heatmap(
    close_data,
    ticker_to_name,
):
    return_data = close_data.pct_change().dropna(
        how="all"
    )

    correlation = return_data.corr()

    labels = [
        ticker_to_name.get(
            ticker,
            ticker,
        )
        for ticker in correlation.columns
    ]

    figure = go.Figure(
        data=go.Heatmap(
            z=correlation.values,
            x=labels,
            y=labels,
            zmin=-1,
            zmax=1,
            colorscale="RdBu_r",
            text=correlation.round(2).values,
            texttemplate="%{text}",
            hovertemplate=(
                "%{x}<br>%{y}<br>"
                "상관계수: %{z:.2f}"
                "<extra></extra>"
            ),
        )
    )

    figure.update_layout(
        title="일간 수익률 상관관계",
        height=650,
        margin=dict(
            l=20,
            r=20,
            t=70,
            b=20,
        ),
    )

    return figure


def create_risk_return_scatter(
    close_data,
    ticker_to_name,
):
    figure = go.Figure()

    rows = []

    for ticker in close_data.columns:
        series = close_data[ticker].dropna()

        if len(series) < 20:
            continue

        daily_return = series.pct_change().dropna()

        annual_return = (
            daily_return.mean()
            * 252
            * 100
        )

        annual_volatility = (
            daily_return.std()
            * math.sqrt(252)
            * 100
        )

        rows.append(
            {
                "ticker": ticker,
                "name": ticker_to_name.get(
                    ticker,
                    ticker,
                ),
                "return": annual_return,
                "risk": annual_volatility,
            }
        )

    risk_return_data = pd.DataFrame(rows)

    if risk_return_data.empty:
        return figure

    figure.add_trace(
        go.Scatter(
            x=risk_return_data["risk"],
            y=risk_return_data["return"],
            mode="markers+text",
            text=risk_return_data["name"],
            textposition="top center",
            marker=dict(
                size=14,
            ),
            customdata=risk_return_data[
                ["name", "ticker"]
            ],
            hovertemplate=(
                "%{customdata[0]}"
                " (%{customdata[1]})<br>"
                "연환산 변동성: %{x:.2f}%<br>"
                "연환산 수익률: %{y:.2f}%"
                "<extra></extra>"
            ),
        )
    )

    figure.add_hline(
        y=0,
        line_dash="dash",
    )

    figure.update_layout(
        title="위험 대비 수익률",
        xaxis_title="연환산 변동성 (%)",
        yaxis_title="연환산 수익률 (%)",
        height=600,
        margin=dict(
            l=20,
            r=20,
            t=70,
            b=20,
        ),
    )

    return figure


def create_score_chart(score_components):
    names = list(score_components.keys())
    scores = list(score_components.values())

    figure = go.Figure()

    figure.add_trace(
        go.Bar(
            x=scores,
            y=names,
            orientation="h",
            text=[
                f"{score:.1f}점"
                for score in scores
            ],
            textposition="auto",
        )
    )

    figure.update_layout(
        title="AI 반도체 종합점수 구성",
        xaxis=dict(
            title="점수",
            range=[0, 100],
        ),
        yaxis_title="",
        height=400,
        margin=dict(
            l=20,
            r=20,
            t=65,
            b=20,
        ),
    )

    return figure


# =========================================================
# 비교표 생성
# =========================================================
def create_comparison_table(
    close_data,
    ticker_to_name,
):
    rows = []

    for ticker in close_data.columns:
        series = close_data[ticker].dropna()

        if len(series) < 2:
            continue

        daily_return = series.pct_change().dropna()

        period_return = (
            series.iloc[-1] / series.iloc[0] - 1
        ) * 100

        annual_volatility = (
            daily_return.std()
            * math.sqrt(252)
            * 100
            if not daily_return.empty
            else None
        )

        cumulative = (
            1 + daily_return
        ).cumprod()

        drawdown = (
            cumulative / cumulative.cummax() - 1
        )

        maximum_drawdown = (
            drawdown.min() * 100
            if not drawdown.empty
            else None
        )

        sharpe = None

        if (
            not daily_return.empty
            and daily_return.std() != 0
        ):
            sharpe = (
                daily_return.mean() * 252
                - 0.03
            ) / (
                daily_return.std()
                * math.sqrt(252)
            )

        rows.append(
            {
                "종목": ticker_to_name.get(
                    ticker,
                    ticker,
                ),
                "티커": ticker,
                "기간 수익률(%)": period_return,
                "연환산 변동성(%)": annual_volatility,
                "최대 낙폭(%)": maximum_drawdown,
                "샤프지수": sharpe,
            }
        )

    result = pd.DataFrame(rows)

    if not result.empty:
        result = result.sort_values(
            "기간 수익률(%)",
            ascending=False,
        ).reset_index(drop=True)

    return result


# =========================================================
# 종목 카드
# =========================================================
def show_stock_card(
    company_name,
    stock_information,
    statistics,
):
    ticker = stock_information["ticker"]
    currency = stock_information["currency"]
    category = stock_information["category"]

    if not statistics:
        st.markdown(
            f"""
            <div class="company-card">
                <div class="company-name">{company_name}</div>
                <div class="company-ticker">{ticker}</div>
                <div class="company-price">데이터 조회 실패</div>
                <div class="company-category">{category}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        return

    current_price = statistics.get("current_price")
    daily_change = statistics.get("daily_change")

    if daily_change is None:
        color = "#777777"
        arrow = "―"
        change_text = "-"
    elif daily_change > 0:
        color = "#e53935"
        arrow = "▲"
        change_text = f"{abs(daily_change):.2f}%"
    elif daily_change < 0:
        color = "#1565c0"
        arrow = "▼"
        change_text = f"{abs(daily_change):.2f}%"
    else:
        color = "#777777"
        arrow = "―"
        change_text = "0.00%"

    st.markdown(
        f"""
        <div class="company-card">
            <div class="company-name">{company_name}</div>
            <div class="company-ticker">{ticker}</div>
            <div class="company-price">
                {format_price(current_price, currency)}
            </div>
            <div style="color:{color}; font-weight:750;">
                {arrow} {change_text}
            </div>
            <div class="company-category">{category}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# =========================================================
# 자동 해석
# =========================================================
def create_technical_interpretation(
    data,
    statistics,
):
    if data.empty:
        return "분석할 데이터가 없습니다."

    indicators = calculate_indicators(data)

    close = safe_float(
        indicators["Close"].iloc[-1]
    )
    ma20 = safe_float(
        indicators["MA20"].iloc[-1]
    )
    ma60 = safe_float(
        indicators["MA60"].iloc[-1]
    )
    ma120 = safe_float(
        indicators["MA120"].iloc[-1]
    )
    rsi = safe_float(
        indicators["RSI"].iloc[-1]
    )
    macd = safe_float(
        indicators["MACD"].iloc[-1]
    )
    macd_signal = safe_float(
        indicators["MACD_SIGNAL"].iloc[-1]
    )

    messages = []

    if close is not None and ma20 is not None:
        if close > ma20:
            messages.append(
                "현재 주가는 20일 이동평균선 위에 있어 단기 흐름은 상대적으로 강합니다."
            )
        else:
            messages.append(
                "현재 주가는 20일 이동평균선 아래에 있어 단기 조정 흐름을 보이고 있습니다."
            )

    if (
        close is not None
        and ma60 is not None
        and ma120 is not None
    ):
        if close > ma60 and close > ma120:
            messages.append(
                "60일·120일 이동평균선을 모두 상회해 중장기 추세는 우호적입니다."
            )
        elif close < ma60 and close < ma120:
            messages.append(
                "60일·120일 이동평균선을 모두 하회해 중장기 추세 확인이 필요합니다."
            )

    if rsi is not None:
        if rsi >= 70:
            messages.append(
                f"RSI는 {rsi:.1f}로 과매수 구간에 있어 단기 변동성 확대 가능성이 있습니다."
            )
        elif rsi <= 30:
            messages.append(
                f"RSI는 {rsi:.1f}로 과매도 구간에 근접하거나 진입했습니다."
            )
        else:
            messages.append(
                f"RSI는 {rsi:.1f}로 중립 범위에 있습니다."
            )

    if (
        macd is not None
        and macd_signal is not None
    ):
        if macd > macd_signal:
            messages.append(
                "MACD가 신호선을 상회해 단기 모멘텀이 개선되는 모습입니다."
            )
        else:
            messages.append(
                "MACD가 신호선을 하회해 단기 모멘텀은 다소 약합니다."
            )

    volatility = safe_float(
        statistics.get("annual_volatility")
    )

    if volatility is not None:
        if volatility >= 60:
            messages.append(
                f"연환산 변동성은 {volatility:.1f}%로 매우 높은 수준입니다."
            )
        elif volatility >= 40:
            messages.append(
                f"연환산 변동성은 {volatility:.1f}%로 비교적 높은 수준입니다."
            )
        else:
            messages.append(
                f"연환산 변동성은 {volatility:.1f}%입니다."
            )

    return " ".join(messages)


# =========================================================
# 화면 제목
# =========================================================
st.markdown(
    '<div class="main-title">🧠 AI 반도체 주식 전문 분석</div>',
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="sub-title">
        GPU · HBM · 파운드리 · 반도체 장비 · AI 서버 기업을
        가격, 기술지표, 성장성, 수익성 및 위험 관점에서 비교합니다.
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
        '<linearGradient id="logoStrokePage0" '
        'x1="0%" y1="0%" x2="100%" y2="100%">'
        '<stop offset="0%" stop-color="#ffffff"/>'
        '<stop offset="100%" stop-color="#dbe8ff"/>'
        '</linearGradient>'
        '</defs>'
        '<path d="M20 72V28M20 51H46M46 28V72" '
        'fill="none" '
        'stroke="url(#logoStrokePage0)" '
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
        'AI 반도체 산업과 글로벌 기술주를<br>'
        '한곳에서 분석하는 스마트 대시보드'
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
        'AI 반도체 분석 설정'
        '</div>',
        unsafe_allow_html=True,
    )

    categories = [
        "전체"
    ] + sorted(
        {
            information["category"]
            for information
            in AI_SEMICONDUCTOR_STOCKS.values()
        }
    )

    selected_category = st.selectbox(
        "산업 분야",
        categories,
    )

    if selected_category == "전체":
        available_companies = list(
            AI_SEMICONDUCTOR_STOCKS.keys()
        )
    else:
        available_companies = [
            company_name
            for company_name, information
            in AI_SEMICONDUCTOR_STOCKS.items()
            if information["category"]
            == selected_category
        ]

    selected_company = st.selectbox(
        "상세 분석 종목",
        available_companies,
    )

    selected_period_name = st.selectbox(
        "조회 기간",
        list(PERIOD_OPTIONS.keys()),
        index=3,
    )

    selected_interval_name = st.selectbox(
        "차트 간격",
        list(INTERVAL_OPTIONS.keys()),
        index=0,
    )

    st.divider()

    st.subheader("차트 설정")

    show_ma20 = st.checkbox(
        "20일 이동평균",
        value=True,
    )

    show_ma60 = st.checkbox(
        "60일 이동평균",
        value=True,
    )

    show_ma120 = st.checkbox(
        "120일 이동평균",
        value=False,
    )

    show_bollinger = st.checkbox(
        "볼린저밴드",
        value=False,
    )

    st.divider()

    if st.button(
        "데이터 새로고침",
        use_container_width=True,
    ):
        st.cache_data.clear()
        st.rerun()

    st.caption(
        "상승은 빨간색, 하락은 파란색으로 표시됩니다."
    )

    st.markdown(
        '</div>',
        unsafe_allow_html=True,
    )


selected_information = (
    AI_SEMICONDUCTOR_STOCKS[
        selected_company
    ]
)

selected_ticker = selected_information[
    "ticker"
]

selected_currency = selected_information[
    "currency"
]

selected_period = PERIOD_OPTIONS[
    selected_period_name
]

selected_interval = INTERVAL_OPTIONS[
    selected_interval_name
]


# =========================================================
# 탭
# =========================================================
(
    market_tab,
    company_tab,
    comparison_tab,
    correlation_tab,
    score_tab,
    raw_data_tab,
) = st.tabs(
    [
        "AI 반도체 시장",
        "종목 상세 분석",
        "수익률·위험 비교",
        "상관관계",
        "AI 반도체 점수",
        "원본 데이터",
    ]
)


# =========================================================
# 1. AI 반도체 시장
# =========================================================
with market_tab:
    st.subheader("AI 반도체 핵심 종목")

    core_companies = [
        "엔비디아",
        "AMD",
        "브로드컴",
        "SK하이닉스",
        "삼성전자",
        "마이크론",
        "TSMC",
        "ASML",
        "슈퍼마이크로컴퓨터",
        "반에크 반도체 ETF",
    ]

    for start_index in range(
        0,
        len(core_companies),
        5,
    ):
        columns = st.columns(5)

        row_companies = core_companies[
            start_index:start_index + 5
        ]

        for column, company_name in zip(
            columns,
            row_companies,
        ):
            information = (
                AI_SEMICONDUCTOR_STOCKS[
                    company_name
                ]
            )

            with column:
                data = download_stock_data(
                    ticker=information["ticker"],
                    period="1mo",
                    interval="1d",
                )

                statistics = (
                    calculate_stock_statistics(data)
                )

                show_stock_card(
                    company_name=company_name,
                    stock_information=information,
                    statistics=statistics,
                )

    st.divider()
    st.subheader("핵심 종목 1년 수익률")

    market_comparison_names = [
        "엔비디아",
        "AMD",
        "브로드컴",
        "SK하이닉스",
        "삼성전자",
        "마이크론",
        "TSMC",
        "ASML",
        "반에크 반도체 ETF",
    ]

    market_comparison_tickers = [
        AI_SEMICONDUCTOR_STOCKS[name]["ticker"]
        for name in market_comparison_names
    ]

    market_ticker_to_name = {
        AI_SEMICONDUCTOR_STOCKS[name]["ticker"]: name
        for name in market_comparison_names
    }

    with st.spinner(
        "AI 반도체 시장 데이터를 불러오는 중입니다."
    ):
        market_close_data = (
            download_multiple_close_prices(
                tickers=market_comparison_tickers,
                period="1y",
            )
        )

    if market_close_data.empty:
        st.warning(
            "AI 반도체 시장 데이터를 불러오지 못했습니다."
        )
    else:
        market_figure = (
            create_relative_return_chart(
                close_data=market_close_data,
                ticker_to_name=market_ticker_to_name,
            )
        )

        st.plotly_chart(
            market_figure,
            use_container_width=True,
        )

        market_table = create_comparison_table(
            close_data=market_close_data,
            ticker_to_name=market_ticker_to_name,
        )

        st.dataframe(
            market_table,
            use_container_width=True,
            hide_index=True,
            column_config={
                "기간 수익률(%)":
                    st.column_config.NumberColumn(
                        format="%.2f%%"
                    ),
                "연환산 변동성(%)":
                    st.column_config.NumberColumn(
                        format="%.2f%%"
                    ),
                "최대 낙폭(%)":
                    st.column_config.NumberColumn(
                        format="%.2f%%"
                    ),
                "샤프지수":
                    st.column_config.NumberColumn(
                        format="%.2f"
                    ),
            },
        )


# =========================================================
# 2. 종목 상세 분석
# =========================================================
with company_tab:
    st.subheader(
        f"{selected_company} 전문 분석"
    )

    st.caption(
        f"{selected_information['ticker']} · "
        f"{selected_information['country']} · "
        f"{selected_information['category']} · "
        f"{selected_information['description']}"
    )

    with st.spinner(
        f"{selected_company} 데이터를 분석하는 중입니다."
    ):
        company_data = download_stock_data(
            ticker=selected_ticker,
            period=selected_period,
            interval=selected_interval,
        )

        company_info = get_company_information(
            selected_ticker
        )

    if company_data.empty:
        st.error(
            "주가 데이터를 불러오지 못했습니다. "
            "새로고침 버튼을 눌러 다시 시도해 주세요."
        )
    else:
        statistics = calculate_stock_statistics(
            company_data
        )

        metric_columns = st.columns(6)

        daily_change = statistics.get(
            "daily_change"
        )

        metric_columns[0].metric(
            "현재 가격",
            format_price(
                statistics.get("current_price"),
                selected_currency,
            ),
            (
                f"{daily_change:+.2f}%"
                if daily_change is not None
                else None
            ),
        )

        metric_columns[1].metric(
            f"{selected_period_name} 수익률",
            (
                f"{statistics['period_return']:+.2f}%"
                if statistics.get("period_return")
                is not None
                else "-"
            ),
        )

        metric_columns[2].metric(
            "연환산 변동성",
            (
                f"{statistics['annual_volatility']:.2f}%"
                if statistics.get("annual_volatility")
                is not None
                else "-"
            ),
        )

        metric_columns[3].metric(
            "최대 낙폭",
            (
                f"{statistics['maximum_drawdown']:.2f}%"
                if statistics.get("maximum_drawdown")
                is not None
                else "-"
            ),
        )

        metric_columns[4].metric(
            "샤프지수",
            (
                f"{statistics['sharpe_ratio']:.2f}"
                if statistics.get("sharpe_ratio")
                is not None
                else "-"
            ),
        )

        metric_columns[5].metric(
            "20일 평균 거래량",
            format_large_number(
                statistics.get("average_volume")
            ),
        )

        price_figure = create_candlestick_chart(
            data=company_data,
            company_name=selected_company,
            show_ma20=show_ma20,
            show_ma60=show_ma60,
            show_ma120=show_ma120,
            show_bollinger=show_bollinger,
        )

        st.plotly_chart(
            price_figure,
            use_container_width=True,
        )

        st.markdown(
            f"""
            <div class="analysis-box">
                <strong>자동 기술적 해석</strong><br>
                {
                    create_technical_interpretation(
                        company_data,
                        statistics,
                    )
                }
            </div>
            """,
            unsafe_allow_html=True,
        )

        rsi_macd_figure = (
            create_rsi_macd_chart(
                data=company_data,
                company_name=selected_company,
            )
        )

        st.plotly_chart(
            rsi_macd_figure,
            use_container_width=True,
        )

        st.subheader("기업 가치 및 실적 지표")

        fundamental_columns = st.columns(5)

        fundamental_columns[0].metric(
            "시가총액",
            format_large_number(
                company_info.get("market_cap"),
                selected_currency,
            ),
        )

        fundamental_columns[1].metric(
            "후행 PER",
            (
                f"{company_info['trailing_pe']:.2f}"
                if company_info.get("trailing_pe")
                is not None
                else "-"
            ),
        )

        fundamental_columns[2].metric(
            "선행 PER",
            (
                f"{company_info['forward_pe']:.2f}"
                if company_info.get("forward_pe")
                is not None
                else "-"
            ),
        )

        fundamental_columns[3].metric(
            "PBR",
            (
                f"{company_info['price_to_book']:.2f}"
                if company_info.get("price_to_book")
                is not None
                else "-"
            ),
        )

        fundamental_columns[4].metric(
            "애널리스트 목표가",
            format_price(
                company_info.get("analyst_target"),
                selected_currency,
            ),
        )

        growth_columns = st.columns(5)

        growth_columns[0].metric(
            "매출 성장률",
            (
                f"{company_info['revenue_growth'] * 100:.2f}%"
                if company_info.get("revenue_growth")
                is not None
                else "-"
            ),
        )

        growth_columns[1].metric(
            "이익 성장률",
            (
                f"{company_info['earnings_growth'] * 100:.2f}%"
                if company_info.get("earnings_growth")
                is not None
                else "-"
            ),
        )

        growth_columns[2].metric(
            "영업이익률",
            (
                f"{company_info['operating_margin'] * 100:.2f}%"
                if company_info.get("operating_margin")
                is not None
                else "-"
            ),
        )

        growth_columns[3].metric(
            "순이익률",
            (
                f"{company_info['profit_margin'] * 100:.2f}%"
                if company_info.get("profit_margin")
                is not None
                else "-"
            ),
        )

        growth_columns[4].metric(
            "자기자본이익률",
            (
                f"{company_info['return_on_equity'] * 100:.2f}%"
                if company_info.get("return_on_equity")
                is not None
                else "-"
            ),
        )

        st.caption(
            "기업 정보는 Yahoo Finance에서 제공되는 범위 내에서 표시되며 일부 종목은 값이 제공되지 않을 수 있습니다."
        )


# =========================================================
# 3. 수익률 및 위험 비교
# =========================================================
with comparison_tab:
    st.subheader(
        "AI 반도체 종목 수익률·위험 비교"
    )

    default_comparison = [
        "엔비디아",
        "AMD",
        "브로드컴",
        "SK하이닉스",
        "삼성전자",
        "마이크론",
        "TSMC",
        "ASML",
    ]

    selected_comparison_names = st.multiselect(
        "비교할 종목",
        options=list(
            AI_SEMICONDUCTOR_STOCKS.keys()
        ),
        default=default_comparison,
        max_selections=12,
    )

    comparison_period_name = st.selectbox(
        "비교 기간",
        list(PERIOD_OPTIONS.keys()),
        index=3,
        key="ai_comparison_period",
    )

    if len(selected_comparison_names) < 2:
        st.info(
            "비교할 종목을 2개 이상 선택해 주세요."
        )
    else:
        comparison_tickers = [
            AI_SEMICONDUCTOR_STOCKS[name]["ticker"]
            for name in selected_comparison_names
        ]

        ticker_to_name = {
            AI_SEMICONDUCTOR_STOCKS[name]["ticker"]: name
            for name in selected_comparison_names
        }

        with st.spinner(
            "선택한 AI 반도체 종목을 비교하는 중입니다."
        ):
            comparison_close_data = (
                download_multiple_close_prices(
                    tickers=comparison_tickers,
                    period=PERIOD_OPTIONS[
                        comparison_period_name
                    ],
                )
            )

        if comparison_close_data.empty:
            st.error(
                "비교 데이터를 불러오지 못했습니다."
            )
        else:
            comparison_figure = (
                create_relative_return_chart(
                    close_data=comparison_close_data,
                    ticker_to_name=ticker_to_name,
                )
            )

            st.plotly_chart(
                comparison_figure,
                use_container_width=True,
            )

            risk_return_figure = (
                create_risk_return_scatter(
                    close_data=comparison_close_data,
                    ticker_to_name=ticker_to_name,
                )
            )

            st.plotly_chart(
                risk_return_figure,
                use_container_width=True,
            )

            comparison_table = (
                create_comparison_table(
                    close_data=comparison_close_data,
                    ticker_to_name=ticker_to_name,
                )
            )

            st.dataframe(
                comparison_table,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "기간 수익률(%)":
                        st.column_config.NumberColumn(
                            format="%.2f%%"
                        ),
                    "연환산 변동성(%)":
                        st.column_config.NumberColumn(
                            format="%.2f%%"
                        ),
                    "최대 낙폭(%)":
                        st.column_config.NumberColumn(
                            format="%.2f%%"
                        ),
                    "샤프지수":
                        st.column_config.NumberColumn(
                            format="%.2f"
                        ),
                },
            )


# =========================================================
# 4. 상관관계
# =========================================================
with correlation_tab:
    st.subheader(
        "AI 반도체 종목 상관관계"
    )

    correlation_default = [
        "엔비디아",
        "AMD",
        "브로드컴",
        "SK하이닉스",
        "삼성전자",
        "마이크론",
        "TSMC",
        "ASML",
    ]

    correlation_names = st.multiselect(
        "상관관계를 계산할 종목",
        options=list(
            AI_SEMICONDUCTOR_STOCKS.keys()
        ),
        default=correlation_default,
        max_selections=12,
        key="correlation_names",
    )

    correlation_period_name = st.selectbox(
        "상관관계 계산 기간",
        list(PERIOD_OPTIONS.keys()),
        index=3,
        key="correlation_period",
    )

    if len(correlation_names) < 2:
        st.info(
            "상관관계를 계산할 종목을 2개 이상 선택해 주세요."
        )
    else:
        correlation_tickers = [
            AI_SEMICONDUCTOR_STOCKS[name]["ticker"]
            for name in correlation_names
        ]

        correlation_ticker_to_name = {
            AI_SEMICONDUCTOR_STOCKS[name]["ticker"]: name
            for name in correlation_names
        }

        with st.spinner(
            "상관관계를 계산하는 중입니다."
        ):
            correlation_close_data = (
                download_multiple_close_prices(
                    tickers=correlation_tickers,
                    period=PERIOD_OPTIONS[
                        correlation_period_name
                    ],
                )
            )

        if correlation_close_data.empty:
            st.error(
                "상관관계 데이터를 불러오지 못했습니다."
            )
        else:
            correlation_figure = (
                create_correlation_heatmap(
                    close_data=correlation_close_data,
                    ticker_to_name=(
                        correlation_ticker_to_name
                    ),
                )
            )

            st.plotly_chart(
                correlation_figure,
                use_container_width=True,
            )

            st.info(
                "상관계수가 1에 가까울수록 비슷하게 움직이고, "
                "0에 가까울수록 관계가 약하며, -1에 가까울수록 반대로 움직이는 경향이 강합니다."
            )


# =========================================================
# 5. AI 반도체 점수
# =========================================================
with score_tab:
    st.subheader(
        f"{selected_company} AI 반도체 종합점수"
    )

    with st.spinner(
        "기술적 흐름과 기업 지표를 평가하는 중입니다."
    ):
        score_data = download_stock_data(
            ticker=selected_ticker,
            period="1y",
            interval="1d",
        )

        score_company_info = (
            get_company_information(
                selected_ticker
            )
        )

    if score_data.empty:
        st.error(
            "점수 계산을 위한 데이터를 불러오지 못했습니다."
        )
    else:
        total_score, score_components = (
            calculate_analysis_score(
                data=score_data,
                company_info=score_company_info,
            )
        )

        if total_score is None:
            st.warning(
                "점수를 계산할 수 없습니다."
            )
        else:
            score_column, description_column = (
                st.columns([1, 2])
            )

            with score_column:
                st.metric(
                    "AI 반도체 종합점수",
                    f"{total_score:.1f} / 100",
                )

                if total_score >= 80:
                    score_grade = "매우 강한 흐름"
                elif total_score >= 65:
                    score_grade = "양호한 흐름"
                elif total_score >= 50:
                    score_grade = "중립"
                elif total_score >= 35:
                    score_grade = "주의 필요"
                else:
                    score_grade = "높은 위험 구간"

                st.markdown(
                    f"""
                    <div class="analysis-box">
                        <strong>평가 구간</strong><br>
                        {score_grade}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            with description_column:
                score_figure = create_score_chart(
                    score_components
                )

                st.plotly_chart(
                    score_figure,
                    use_container_width=True,
                )

            score_table = pd.DataFrame(
                {
                    "평가 항목": list(
                        score_components.keys()
                    ),
                    "점수": list(
                        score_components.values()
                    ),
                    "반영 비중": [
                        "35%",
                        "25%",
                        "20%",
                        "20%",
                    ],
                }
            )

            st.dataframe(
                score_table,
                use_container_width=True,
                hide_index=True,
            )

            st.warning(
                "이 점수는 주가 흐름과 Yahoo Finance에서 제공하는 일부 기업 지표를 단순 가중평균한 참고용 지표입니다. "
                "투자 매수·매도 추천이나 목표주가를 의미하지 않습니다."
            )


# =========================================================
# 6. 원본 데이터
# =========================================================
with raw_data_tab:
    st.subheader(
        f"{selected_company} 원본 데이터"
    )

    raw_data = download_stock_data(
        ticker=selected_ticker,
        period=selected_period,
        interval=selected_interval,
    )

    if raw_data.empty:
        st.warning(
            "표시할 데이터가 없습니다."
        )
    else:
        display_data = raw_data.copy()

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

        csv_data = display_data.to_csv(
            encoding="utf-8-sig"
        )

        st.download_button(
            label="CSV 파일 다운로드",
            data=csv_data,
            file_name=(
                f"{selected_ticker}_"
                f"{datetime.now().strftime('%Y%m%d')}.csv"
            ),
            mime="text/csv",
        )


# =========================================================
# 하단 안내
# =========================================================
st.divider()

st.caption(
    "본 페이지는 AI 반도체 산업 및 주식 데이터 학습을 위한 정보 제공용입니다. "
    "Yahoo Finance 데이터는 실시간 거래소 데이터와 다르거나 지연될 수 있으며, "
    "기업 재무지표 일부는 제공되지 않을 수 있습니다."
)
