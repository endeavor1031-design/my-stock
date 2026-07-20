import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import yfinance as yf
from plotly.subplots import make_subplots


# =========================================================
# 페이지 기본 설정
# =========================================================
st.set_page_config(
    page_title="hani.inc 글로벌 주요 주식 대시보드",
    page_icon="📈",
    layout="wide",
)


# =========================================================
# 종목 정보
# Yahoo Finance 티커 기준
# =========================================================
STOCKS = {
    # 한국
    "SK하이닉스": {
        "ticker": "000660.KS",
        "market": "한국",
        "currency": "KRW",
    },
    "삼성전자": {
        "ticker": "005930.KS",
        "market": "한국",
        "currency": "KRW",
    },
    "카카오": {
        "ticker": "035720.KS",
        "market": "한국",
        "currency": "KRW",
    },
    "현대차": {
        "ticker": "005380.KS",
        "market": "한국",
        "currency": "KRW",
    },
    "NAVER": {
        "ticker": "035420.KS",
        "market": "한국",
        "currency": "KRW",
    },

    # 미국
    "팔란티어": {
        "ticker": "PLTR",
        "market": "미국",
        "currency": "USD",
    },
    "애플": {
        "ticker": "AAPL",
        "market": "미국",
        "currency": "USD",
    },
    "마이크로소프트": {
        "ticker": "MSFT",
        "market": "미국",
        "currency": "USD",
    },
    "엔비디아": {
        "ticker": "NVDA",
        "market": "미국",
        "currency": "USD",
    },
    "테슬라": {
        "ticker": "TSLA",
        "market": "미국",
        "currency": "USD",
    },
    "알파벳": {
        "ticker": "GOOGL",
        "market": "미국",
        "currency": "USD",
    },
    "아마존": {
        "ticker": "AMZN",
        "market": "미국",
        "currency": "USD",
    },
    "메타": {
        "ticker": "META",
        "market": "미국",
        "currency": "USD",
    },

    # 일본
    "도요타": {
        "ticker": "7203.T",
        "market": "일본",
        "currency": "JPY",
    },
    "소니": {
        "ticker": "6758.T",
        "market": "일본",
        "currency": "JPY",
    },

    # 유럽
    "ASML": {
        "ticker": "ASML",
        "market": "유럽",
        "currency": "USD",
    },
    "SAP": {
        "ticker": "SAP",
        "market": "유럽",
        "currency": "USD",
    },

    # 지수 및 자산
    "S&P 500": {
        "ticker": "^GSPC",
        "market": "지수",
        "currency": "USD",
    },
    "나스닥 종합": {
        "ticker": "^IXIC",
        "market": "지수",
        "currency": "USD",
    },
    "코스피": {
        "ticker": "^KS11",
        "market": "지수",
        "currency": "KRW",
    },
    "비트코인": {
        "ticker": "BTC-USD",
        "market": "가상자산",
        "currency": "USD",
    },
}


PERIOD_OPTIONS = {
    "1개월": "1mo",
    "3개월": "3mo",
    "6개월": "6mo",
    "1년": "1y",
    "2년": "2y",
    "5년": "5y",
    "최대": "max",
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
    --up-color: #ef3e4a;
    --down-color: #1565c0;
    --sidebar-text: #ffffff;
    --sidebar-muted: rgba(255, 255, 255, 0.72);
}

html,
body,
[data-testid="stAppViewContainer"] {
    background: linear-gradient(180deg, #fbfcff 0%, #f4f6fb 100%);
}

[data-testid="stHeader"] {
    background: transparent;
}

/* 기본 Streamlit 멀티페이지 메뉴 유지 */
[data-testid="stSidebarNav"] {
    display: block !important;
    order: 2;
    margin-top: 8px;
    margin-bottom: 12px;
}

/* 사이드바 내부를 순서 조정 가능한 세로 레이아웃으로 구성 */
[data-testid="stSidebar"] > div:first-child {
    display: flex;
    flex-direction: column;
    background: transparent !important;
}

/* 브랜드 영역은 가장 위 */
[data-testid="stSidebar"] .hani-brand-wrapper {
    order: 1;
}

/* 브랜드 아래의 일반 설정 영역 */
[data-testid="stSidebar"] .sidebar-settings-wrapper {
    order: 3;
}

/* 사이드바 전체 그라데이션 */
[data-testid="stSidebar"] {
    background:
        radial-gradient(circle at 20% 10%, rgba(255, 104, 132, 0.36), transparent 25%),
        radial-gradient(circle at 85% 24%, rgba(94, 125, 255, 0.38), transparent 28%),
        radial-gradient(circle at 22% 82%, rgba(255, 71, 87, 0.30), transparent 26%),
        linear-gradient(
            165deg,
            #091536 0%,
            #132b68 30%,
            #34319a 58%,
            #732e9e 78%,
            #bf344e 100%
        ) !important;
    border-right: 1px solid rgba(255, 255, 255, 0.16);
}

[data-testid="stSidebar"] [data-testid="stMarkdownContainer"],
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3,
[data-testid="stSidebar"] span {
    color: var(--sidebar-text);
}

/* 입력 위젯 */
[data-testid="stSidebar"] [data-baseweb="select"] > div,
[data-testid="stSidebar"] [data-baseweb="input"] > div,
[data-testid="stSidebar"] div[role="radiogroup"] {
    background: rgba(255, 255, 255, 0.93);
    border: 1px solid rgba(255, 255, 255, 0.28);
    border-radius: 12px;
}

[data-testid="stSidebar"] [data-baseweb="select"] span,
[data-testid="stSidebar"] [data-baseweb="select"] svg,
[data-testid="stSidebar"] [data-baseweb="input"] input,
[data-testid="stSidebar"] div[role="radiogroup"] label p {
    color: #17213d !important;
}

[data-testid="stSidebar"] hr {
    border-color: rgba(255, 255, 255, 0.20);
}

/* 회사 브랜드 카드 */
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
    border: 1px solid rgba(255, 255, 255, 0.25);
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
    border: 1px solid rgba(255, 255, 255, 0.24);
}

.hani-logo-inner svg {
    width: 55px;
    height: 55px;
    filter: drop-shadow(0 4px 8px rgba(0, 0, 0, 0.24));
}

.hani-brand-name {
    color: #ffffff;
    font-size: 1.55rem;
    line-height: 1.04;
    font-weight: 900;
    letter-spacing: -0.035em;
}

.hani-brand-subtitle {
    color: rgba(255, 255, 255, 0.75);
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
    color: rgba(255, 255, 255, 0.79);
    font-size: 0.73rem;
    line-height: 1.5;
}

/* 사이드바 설정 제목 */
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
    font-size: 2.2rem;
    font-weight: 850;
    margin-bottom: 0.15rem;
    color: #18213d;
}

.sub-title {
    color: #667085;
    margin-bottom: 1.4rem;
}

.section-title {
    font-size: 1.45rem;
    font-weight: 850;
    color: #18213d;
    margin-bottom: 10px;
}

.price-metric-card {
    border: 1px solid rgba(128, 128, 128, 0.14);
    border-radius: 16px;
    padding: 14px;
    min-height: 118px;
    margin-bottom: 10px;
    background:
        linear-gradient(
            180deg,
            rgba(255, 255, 255, 0.94),
            rgba(245, 248, 255, 0.88)
        );
    box-shadow: 0 10px 22px rgba(74, 96, 170, 0.08);
}

.price-metric-label {
    font-size: 0.90rem;
    color: #667085;
    margin-bottom: 7px;
    font-weight: 700;
}

.price-metric-value {
    font-size: 1.48rem;
    font-weight: 850;
    margin-bottom: 4px;
    color: #18213d;
}

.price-metric-delta {
    font-size: 0.90rem;
    font-weight: 800;
}

div[data-testid="stMetric"] {
    border: 1px solid rgba(128, 128, 128, 0.14);
    border-radius: 16px;
    padding: 12px;
    background:
        linear-gradient(
            180deg,
            rgba(255, 255, 255, 0.94),
            rgba(244, 247, 255, 0.88)
        );
    box-shadow: 0 8px 20px rgba(80, 95, 150, 0.06);
}

[data-baseweb="tab-list"] {
    gap: 8px;
}

[data-baseweb="tab"] {
    background: rgba(255, 255, 255, 0.76);
    border-radius: 999px;
    padding: 10px 18px;
    border: 1px solid rgba(140, 160, 210, 0.14);
}

[data-baseweb="tab"][aria-selected="true"] {
    background:
        linear-gradient(
            90deg,
            #ef3e4a 0%,
            #6c63ff 54%,
            #1565c0 100%
        );
    color: white;
}

.footer-note {
    padding: 16px 18px;
    border-radius: 18px;
    background: rgba(255, 255, 255, 0.78);
    border: 1px solid rgba(140, 160, 210, 0.16);
    color: #4a5568;
    font-size: 0.93rem;
}

/* 기본 멀티페이지 메뉴를 디자인에 맞게 꾸밈 */
[data-testid="stSidebarNav"]::before {
    content: "NAVIGATION";
    display: block;
    margin: 2px 0 8px 4px;
    color: rgba(255, 255, 255, 0.70);
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
    background: rgba(255, 255, 255, 0.075);
    border: 1px solid rgba(255, 255, 255, 0.10);
    transition: all 0.18s ease;
}

[data-testid="stSidebarNav"] a:hover {
    background: rgba(255, 255, 255, 0.18);
    border-color: rgba(255, 255, 255, 0.28);
    transform: translateX(3px);
}

[data-testid="stSidebarNav"] a[aria-current="page"] {
    background:
        linear-gradient(
            90deg,
            rgba(239, 62, 74, 0.48),
            rgba(108, 99, 255, 0.48),
            rgba(21, 101, 192, 0.48)
        );
    border-color: rgba(255, 255, 255, 0.30);
    box-shadow: 0 8px 18px rgba(0, 0, 0, 0.14);
}

[data-testid="stSidebarNav"] a span,
[data-testid="stSidebarNav"] a p {
    color: #ffffff !important;
    font-weight: 700 !important;
}

</style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# 공통 함수
# =========================================================
@st.cache_data(ttl=600, show_spinner=False)
def download_stock_data(ticker, period="1y", interval="1d"):
    """
    Yahoo Finance에서 개별 종목 데이터를 가져옵니다.
    결과는 10분 동안 캐시됩니다.
    """
    data = yf.download(
        ticker,
        period=period,
        interval=interval,
        auto_adjust=False,
        progress=False,
        threads=False,
    )

    if data is None or data.empty:
        return pd.DataFrame()

    # yfinance 버전에 따라 단일 티커도 MultiIndex가 반환될 수 있음
    if isinstance(data.columns, pd.MultiIndex):
        if ticker in data.columns.get_level_values(-1):
            try:
                data = data.xs(ticker, axis=1, level=-1)
            except KeyError:
                data.columns = data.columns.get_level_values(0)
        else:
            data.columns = data.columns.get_level_values(0)

    data = data.copy()
    data.index = pd.to_datetime(data.index)

    # 중복된 열 이름 제거
    data = data.loc[:, ~data.columns.duplicated()]

    return data


@st.cache_data(ttl=600, show_spinner=False)
def download_comparison_data(tickers, period="1y"):
    """
    여러 종목의 수정주가 또는 종가 데이터를 가져옵니다.
    """
    data = yf.download(
        tickers=tickers,
        period=period,
        interval="1d",
        auto_adjust=False,
        progress=False,
        group_by="column",
        threads=True,
    )

    if data is None or data.empty:
        return pd.DataFrame()

    close_data = pd.DataFrame()

    if isinstance(data.columns, pd.MultiIndex):
        first_level = data.columns.get_level_values(0)

        if "Adj Close" in first_level:
            close_data = data["Adj Close"].copy()
        elif "Close" in first_level:
            close_data = data["Close"].copy()
    else:
        if "Adj Close" in data.columns:
            close_data = data[["Adj Close"]].copy()
            close_data.columns = tickers[:1]
        elif "Close" in data.columns:
            close_data = data[["Close"]].copy()
            close_data.columns = tickers[:1]

    if isinstance(close_data, pd.Series):
        close_data = close_data.to_frame()

    close_data.index = pd.to_datetime(close_data.index)

    return close_data.dropna(how="all")


def safe_number(value, default=None):
    """
    None, NaN 등의 값을 안전하게 처리합니다.
    """
    try:
        if value is None or pd.isna(value):
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def format_price(value, currency):
    value = safe_number(value)

    if value is None:
        return "-"

    if currency == "KRW":
        return f"₩{value:,.0f}"

    if currency == "JPY":
        return f"¥{value:,.0f}"

    return f"${value:,.2f}"


def format_large_number(value, currency=""):
    value = safe_number(value)

    if value is None:
        return "-"

    absolute_value = abs(value)

    if absolute_value >= 1_000_000_000_000:
        number = value / 1_000_000_000_000
        unit = "조"
    elif absolute_value >= 100_000_000:
        number = value / 100_000_000
        unit = "억"
    elif absolute_value >= 10_000:
        number = value / 10_000
        unit = "만"
    else:
        return f"{value:,.0f}"

    currency_symbol = {
        "KRW": "₩",
        "USD": "$",
        "JPY": "¥",
    }.get(currency, "")

    return f"{currency_symbol}{number:,.2f}{unit}"


def show_colored_price_metric(
    label,
    value,
    change=None,
    change_percent=None,
):
    """
    한국 주식시장 기준 색상:
    상승 = 빨간색
    하락 = 파란색
    보합 = 회색
    """
    if change_percent is None:
        color = "#777777"
        arrow = "―"
        delta_text = ""
    elif change_percent > 0:
        color = "#e53935"
        arrow = "▲"
        delta_text = (
            f"{arrow} {abs(change):,.2f} "
            f"({abs(change_percent):.2f}%)"
        )
    elif change_percent < 0:
        color = "#1565c0"
        arrow = "▼"
        delta_text = (
            f"{arrow} {abs(change):,.2f} "
            f"({abs(change_percent):.2f}%)"
        )
    else:
        color = "#777777"
        arrow = "―"
        delta_text = "― 0.00 (0.00%)"

    html = (
        f'<div class="price-metric-card">'
        f'<div class="price-metric-label">{label}</div>'
        f'<div class="price-metric-value">{value}</div>'
        f'<div class="price-metric-delta" style="color:{color};">'
        f'{delta_text}'
        f'</div>'
        f'</div>'
    )

    st.markdown(
        html,
        unsafe_allow_html=True,
    )


def calculate_indicators(data):
    """
    이동평균선과 RSI를 계산합니다.
    """
    result = data.copy()

    result["MA20"] = result["Close"].rolling(window=20).mean()
    result["MA60"] = result["Close"].rolling(window=60).mean()
    result["MA120"] = result["Close"].rolling(window=120).mean()

    price_change = result["Close"].diff()
    gain = price_change.clip(lower=0)
    loss = -price_change.clip(upper=0)

    average_gain = gain.rolling(window=14).mean()
    average_loss = loss.rolling(window=14).mean()

    relative_strength = average_gain / average_loss.replace(0, float("nan"))
    result["RSI"] = 100 - (100 / (1 + relative_strength))

    # 손실 평균이 0이면 RSI를 100으로 처리
    result.loc[
        (average_loss == 0) & (average_gain > 0),
        "RSI",
    ] = 100

    return result


def get_price_summary(data):
    if data.empty or "Close" not in data.columns:
        return None

    close = data["Close"].dropna()

    if close.empty:
        return None

    current_price = safe_number(close.iloc[-1])

    if len(close) >= 2:
        previous_price = safe_number(close.iloc[-2])
    else:
        previous_price = current_price

    if current_price is None or previous_price is None:
        return None

    price_change = current_price - previous_price

    if previous_price != 0:
        change_percent = price_change / previous_price * 100
    else:
        change_percent = 0

    period_high = safe_number(data["High"].max()) if "High" in data else None
    period_low = safe_number(data["Low"].min()) if "Low" in data else None

    if "Volume" in data:
        average_volume = safe_number(data["Volume"].tail(20).mean())
    else:
        average_volume = None

    return {
        "current_price": current_price,
        "previous_price": previous_price,
        "price_change": price_change,
        "change_percent": change_percent,
        "period_high": period_high,
        "period_low": period_low,
        "average_volume": average_volume,
    }


def create_price_chart(
    data,
    stock_name,
    chart_type,
    show_ma20,
    show_ma60,
    show_ma120,
):
    """
    가격과 거래량을 함께 보여주는 Plotly 차트입니다.
    """
    chart_data = calculate_indicators(data)

    figure = make_subplots(
        rows=2,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.04,
        row_heights=[0.74, 0.26],
        subplot_titles=(
            f"{stock_name} 가격",
            "거래량",
        ),
    )

    if chart_type == "캔들차트":
        figure.add_trace(
            go.Candlestick(
                x=chart_data.index,
                open=chart_data["Open"],
                high=chart_data["High"],
                low=chart_data["Low"],
                close=chart_data["Close"],
                name="OHLC",
                increasing_line_color="#e53935",
                increasing_fillcolor="#e53935",
                decreasing_line_color="#1565c0",
                decreasing_fillcolor="#1565c0",
            ),
            row=1,
            col=1,
        )
    else:
        figure.add_trace(
            go.Scatter(
                x=chart_data.index,
                y=chart_data["Close"],
                mode="lines",
                name="종가",
                line=dict(
                    width=2.4,
                    color="#4f46e5",
                ),
            ),
            row=1,
            col=1,
        )

    if show_ma20:
        figure.add_trace(
            go.Scatter(
                x=chart_data.index,
                y=chart_data["MA20"],
                mode="lines",
                name="20일 이동평균",
                line=dict(width=1.5, color="#ff5f6d"),
            ),
            row=1,
            col=1,
        )

    if show_ma60:
        figure.add_trace(
            go.Scatter(
                x=chart_data.index,
                y=chart_data["MA60"],
                mode="lines",
                name="60일 이동평균",
                line=dict(width=1.5, color="#6c63ff"),
            ),
            row=1,
            col=1,
        )

    if show_ma120:
        figure.add_trace(
            go.Scatter(
                x=chart_data.index,
                y=chart_data["MA120"],
                mode="lines",
                name="120일 이동평균",
                line=dict(width=1.5, color="#00bcd4"),
            ),
            row=1,
            col=1,
        )

    if "Volume" in chart_data.columns:
        volume_colors = [
            "#e53935" if close >= open_price else "#1565c0"
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
        height=680,
        margin=dict(l=20, r=20, t=70, b=20),
        hovermode="x unified",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="left",
            x=0,
        ),
        xaxis_rangeslider_visible=False,
        paper_bgcolor="rgba(255,255,255,0)",
        plot_bgcolor="rgba(255,255,255,0.70)",
        font=dict(color="#18213d"),
    )

    figure.update_xaxes(
        rangeslider_visible=False,
        showgrid=False,
    )

    figure.update_yaxes(
        title_text="가격",
        row=1,
        col=1,
        gridcolor="rgba(80, 100, 180, 0.10)",
    )

    figure.update_yaxes(
        title_text="거래량",
        row=2,
        col=1,
        gridcolor="rgba(80, 100, 180, 0.10)",
    )

    return figure


def create_rsi_chart(data, stock_name):
    chart_data = calculate_indicators(data)

    figure = go.Figure()

    figure.add_trace(
        go.Scatter(
            x=chart_data.index,
            y=chart_data["RSI"],
            mode="lines",
            name="RSI",
            line=dict(width=2.2, color="#6c63ff"),
        )
    )

    figure.add_hline(
        y=70,
        line_dash="dash",
        line_color="#e53935",
        annotation_text="과매수 기준 70",
        annotation_position="top left",
    )

    figure.add_hline(
        y=30,
        line_dash="dash",
        line_color="#1565c0",
        annotation_text="과매도 기준 30",
        annotation_position="bottom left",
    )

    figure.update_layout(
        title=f"{stock_name} RSI",
        height=380,
        yaxis=dict(
            title="RSI",
            range=[0, 100],
            gridcolor="rgba(80, 100, 180, 0.10)",
        ),
        xaxis_title="날짜",
        hovermode="x unified",
        margin=dict(l=20, r=20, t=60, b=20),
        paper_bgcolor="rgba(255,255,255,0)",
        plot_bgcolor="rgba(255,255,255,0.70)",
        font=dict(color="#18213d"),
    )

    return figure


def create_comparison_chart(close_data, ticker_to_name):
    """
    시작일을 100으로 놓고 종목별 누적 수익률을 비교합니다.
    """
    normalized = pd.DataFrame(index=close_data.index)

    line_palette = [
        "#ff5f6d",
        "#6c63ff",
        "#00bcd4",
        "#ff9800",
        "#00c853",
        "#7c4dff",
        "#ef5350",
        "#1565c0",
        "#f06292",
        "#26a69a",
    ]

    for ticker in close_data.columns:
        series = close_data[ticker].dropna()

        if series.empty:
            continue

        normalized[ticker] = close_data[ticker] / series.iloc[0] * 100

    figure = go.Figure()

    for idx, ticker in enumerate(normalized.columns):
        figure.add_trace(
            go.Scatter(
                x=normalized.index,
                y=normalized[ticker],
                mode="lines",
                name=ticker_to_name.get(ticker, ticker),
                line=dict(
                    width=2.5,
                    color=line_palette[idx % len(line_palette)],
                ),
            )
        )

    figure.add_hline(
        y=100,
        line_dash="dash",
        line_color="rgba(70, 80, 120, 0.45)",
        annotation_text="비교 시작점",
        annotation_position="bottom right",
    )

    figure.update_layout(
        title="종목별 상대 수익률 비교",
        xaxis_title="날짜",
        yaxis_title="기준가 100",
        height=580,
        hovermode="x unified",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="left",
            x=0,
        ),
        margin=dict(l=20, r=20, t=80, b=20),
        paper_bgcolor="rgba(255,255,255,0)",
        plot_bgcolor="rgba(255,255,255,0.70)",
        font=dict(color="#18213d"),
    )

    figure.update_yaxes(
        gridcolor="rgba(80, 100, 180, 0.10)",
    )

    return figure, normalized


def create_performance_table(close_data, ticker_to_name):
    rows = []

    for ticker in close_data.columns:
        series = close_data[ticker].dropna()

        if len(series) < 2:
            continue

        start_price = safe_number(series.iloc[0])
        current_price = safe_number(series.iloc[-1])
        highest_price = safe_number(series.max())
        lowest_price = safe_number(series.min())

        if start_price is None or current_price is None or start_price == 0:
            continue

        return_rate = (current_price / start_price - 1) * 100

        daily_return = series.pct_change().dropna()

        volatility = (
            daily_return.std() * (252 ** 0.5) * 100
            if not daily_return.empty
            else None
        )

        rows.append(
            {
                "종목": ticker_to_name.get(ticker, ticker),
                "티커": ticker,
                "기간 수익률(%)": round(return_rate, 2),
                "연환산 변동성(%)": (
                    round(volatility, 2)
                    if volatility is not None
                    else None
                ),
                "기간 최고가": round(highest_price, 2),
                "기간 최저가": round(lowest_price, 2),
            }
        )

    performance = pd.DataFrame(rows)

    if not performance.empty:
        performance = performance.sort_values(
            "기간 수익률(%)",
            ascending=False,
        ).reset_index(drop=True)

    return performance


# =========================================================
# 본문 제목
# =========================================================
st.markdown(
    '<div class="main-title">📈 글로벌 주요 주식 대시보드</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="sub-title">'
    'Yahoo Finance 데이터와 Plotly를 활용한 글로벌 금융시장 분석'
    '</div>',
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
        '<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg" aria-label="hani.inc logo">'
        '<defs>'
        '<linearGradient id="logoStroke" x1="0%" y1="0%" x2="100%" y2="100%">'
        '<stop offset="0%" stop-color="#ffffff"/>'
        '<stop offset="100%" stop-color="#dbe8ff"/>'
        '</linearGradient>'
        '</defs>'
        '<path d="M20 72V28M20 51H46M46 28V72" fill="none" stroke="url(#logoStroke)" stroke-width="9" stroke-linecap="round" stroke-linejoin="round"/>'
        '<path d="M58 69L68 55L77 61L89 40" fill="none" stroke="#ffffff" stroke-width="6" stroke-linecap="round" stroke-linejoin="round"/>'
        '<circle cx="89" cy="40" r="5" fill="#ffdf7e"/>'
        '<circle cx="68" cy="55" r="4" fill="#ff7b91"/>'
        '</svg>'
        '</div>'
        '</div>'
        '<div>'
        '<div class="hani-brand-name">hani.inc</div>'
        '<div class="hani-brand-subtitle">MARKET INTELLIGENCE<br>DATA &amp; ANALYTICS</div>'
        '</div>'
        '</div>'
        '<div class="hani-brand-line"></div>'
        '<div class="hani-brand-copy">'
        '글로벌 주식과 AI 반도체 시장을<br>'
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
        '<div class="sidebar-settings-title">대시보드 설정</div>',
        unsafe_allow_html=True,
    )

    market_options = ["전체"] + sorted(
        list({stock["market"] for stock in STOCKS.values()})
    )

    selected_market = st.selectbox(
        "시장 선택",
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

    default_stock = (
        "SK하이닉스"
        if "SK하이닉스" in available_stocks
        else available_stocks[0]
    )

    selected_stock_name = st.selectbox(
        "상세 분석 종목",
        available_stocks,
        index=available_stocks.index(default_stock),
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

    chart_type = st.radio(
        "차트 유형",
        ["캔들차트", "라인차트"],
        horizontal=True,
    )

    st.divider()

    st.subheader("이동평균선")

    show_ma20 = st.checkbox(
        "20일 이동평균선",
        value=True,
    )

    show_ma60 = st.checkbox(
        "60일 이동평균선",
        value=True,
    )

    show_ma120 = st.checkbox(
        "120일 이동평균선",
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
        "Yahoo Finance 데이터는 일정 시간 지연될 수 있습니다."
    )

    st.markdown(
        '</div>',
        unsafe_allow_html=True,
    )


selected_ticker = STOCKS[selected_stock_name]["ticker"]
selected_currency = STOCKS[selected_stock_name]["currency"]
selected_period = PERIOD_OPTIONS[selected_period_name]
selected_interval = INTERVAL_OPTIONS[selected_interval_name]


# =========================================================
# 탭 구성
# =========================================================
overview_tab, detail_tab, comparison_tab, data_tab = st.tabs(
    [
        "시장 현황",
        "종목 상세 분석",
        "수익률 비교",
        "원본 데이터",
    ]
)


# =========================================================
# 1. 시장 현황
# =========================================================
with overview_tab:
    st.markdown('<div class="section-title">주요 종목 현황</div>', unsafe_allow_html=True)

    dashboard_stocks = [
        "SK하이닉스",
        "삼성전자",
        "카카오",
        "팔란티어",
        "애플",
        "엔비디아",
        "테슬라",
        "S&P 500",
    ]

    first_row = dashboard_stocks[:4]
    second_row = dashboard_stocks[4:]

    for row_stocks in [first_row, second_row]:
        columns = st.columns(4)

        for column, stock_name in zip(columns, row_stocks):
            ticker = STOCKS[stock_name]["ticker"]
            currency = STOCKS[stock_name]["currency"]

            with column:
                stock_data = download_stock_data(
                    ticker=ticker,
                    period="5d",
                    interval="1d",
                )

                summary = get_price_summary(stock_data)

                if summary is None:
                    show_colored_price_metric(
                        label=f"{stock_name} · {ticker}",
                        value="데이터 없음",
                    )
                else:
                    show_colored_price_metric(
                        label=f"{stock_name} · {ticker}",
                        value=format_price(
                            summary["current_price"],
                            currency,
                        ),
                        change=summary["price_change"],
                        change_percent=summary["change_percent"],
                    )

    st.divider()
    st.markdown('<div class="section-title">필수 종목 상대 수익률</div>', unsafe_allow_html=True)

    essential_names = [
        "SK하이닉스",
        "삼성전자",
        "카카오",
        "팔란티어",
    ]

    essential_tickers = [
        STOCKS[name]["ticker"]
        for name in essential_names
    ]

    ticker_to_name = {
        STOCKS[name]["ticker"]: name
        for name in essential_names
    }

    with st.spinner("필수 종목 데이터를 불러오는 중입니다."):
        comparison_data = download_comparison_data(
            essential_tickers,
            period="1y",
        )

    if comparison_data.empty:
        st.warning("필수 종목의 비교 데이터를 불러오지 못했습니다.")
    else:
        valid_columns = [
            ticker
            for ticker in essential_tickers
            if ticker in comparison_data.columns
        ]

        comparison_data = comparison_data[valid_columns]

        figure, normalized_data = create_comparison_chart(
            comparison_data,
            ticker_to_name,
        )

        st.plotly_chart(
            figure,
            use_container_width=True,
        )

        performance_table = create_performance_table(
            comparison_data,
            ticker_to_name,
        )

        st.dataframe(
            performance_table,
            use_container_width=True,
            hide_index=True,
        )


# =========================================================
# 2. 종목 상세 분석
# =========================================================
with detail_tab:
    st.markdown(
        f'<div class="section-title">{selected_stock_name} 상세 분석</div>',
        unsafe_allow_html=True,
    )

    st.caption(
        f"티커: {selected_ticker} · "
        f"시장: {STOCKS[selected_stock_name]['market']} · "
        f"기간: {selected_period_name} · "
        f"간격: {selected_interval_name}"
    )

    with st.spinner(
        f"{selected_stock_name} 데이터를 불러오는 중입니다."
    ):
        detail_data = download_stock_data(
            ticker=selected_ticker,
            period=selected_period,
            interval=selected_interval,
        )

    if detail_data.empty:
        st.error(
            "주가 데이터를 불러오지 못했습니다. "
            "잠시 후 다시 시도하거나 다른 기간을 선택해 주세요."
        )
    else:
        summary = get_price_summary(detail_data)

        if summary is not None:
            metric_columns = st.columns(5)

            with metric_columns[0]:
                show_colored_price_metric(
                    label="현재 가격",
                    value=format_price(
                        summary["current_price"],
                        selected_currency,
                    ),
                    change=summary["price_change"],
                    change_percent=summary["change_percent"],
                )

            metric_columns[1].metric(
                "기간 최고가",
                format_price(
                    summary["period_high"],
                    selected_currency,
                ),
            )

            metric_columns[2].metric(
                "기간 최저가",
                format_price(
                    summary["period_low"],
                    selected_currency,
                ),
            )

            metric_columns[3].metric(
                "20일 평균 거래량",
                format_large_number(
                    summary["average_volume"]
                ),
            )

            period_return = (
                detail_data["Close"].iloc[-1]
                / detail_data["Close"].dropna().iloc[0]
                - 1
            ) * 100

            metric_columns[4].metric(
                "조회 기간 수익률",
                f"{period_return:+.2f}%",
            )

        price_figure = create_price_chart(
            data=detail_data,
            stock_name=selected_stock_name,
            chart_type=chart_type,
            show_ma20=show_ma20,
            show_ma60=show_ma60,
            show_ma120=show_ma120,
        )

        st.plotly_chart(
            price_figure,
            use_container_width=True,
        )

        st.markdown('<div class="section-title">기술적 분석</div>', unsafe_allow_html=True)

        indicator_data = calculate_indicators(detail_data)

        latest_rsi = safe_number(
            indicator_data["RSI"].iloc[-1]
        )

        latest_close = safe_number(
            indicator_data["Close"].iloc[-1]
        )

        latest_ma20 = safe_number(
            indicator_data["MA20"].iloc[-1]
        )

        latest_ma60 = safe_number(
            indicator_data["MA60"].iloc[-1]
        )

        indicator_columns = st.columns(3)

        if latest_rsi is None:
            rsi_status = "계산 데이터 부족"
        elif latest_rsi >= 70:
            rsi_status = "과매수 구간"
        elif latest_rsi <= 30:
            rsi_status = "과매도 구간"
        else:
            rsi_status = "중립 구간"

        indicator_columns[0].metric(
            "RSI(14)",
            (
                f"{latest_rsi:.2f}"
                if latest_rsi is not None
                else "-"
            ),
            rsi_status,
            delta_color="off",
        )

        if latest_close is not None and latest_ma20 is not None:
            ma20_difference = (
                latest_close / latest_ma20 - 1
            ) * 100
            ma20_text = f"{ma20_difference:+.2f}%"
        else:
            ma20_text = "-"

        indicator_columns[1].metric(
            "20일 이동평균 대비",
            ma20_text,
        )

        if latest_close is not None and latest_ma60 is not None:
            ma60_difference = (
                latest_close / latest_ma60 - 1
            ) * 100
            ma60_text = f"{ma60_difference:+.2f}%"
        else:
            ma60_text = "-"

        indicator_columns[2].metric(
            "60일 이동평균 대비",
            ma60_text,
        )

        rsi_figure = create_rsi_chart(
            detail_data,
            selected_stock_name,
        )

        st.plotly_chart(
            rsi_figure,
            use_container_width=True,
        )


# =========================================================
# 3. 수익률 비교
# =========================================================
with comparison_tab:
    st.markdown('<div class="section-title">종목별 수익률 비교</div>', unsafe_allow_html=True)

    st.write(
        "서로 다른 통화와 가격 수준을 가진 종목을 비교하기 위해 "
        "조회 시작일 가격을 100으로 환산합니다."
    )

    default_comparison = [
        "SK하이닉스",
        "삼성전자",
        "카카오",
        "팔란티어",
        "엔비디아",
        "S&P 500",
    ]

    selected_comparison_names = st.multiselect(
        "비교할 종목을 선택하세요",
        options=list(STOCKS.keys()),
        default=default_comparison,
        max_selections=10,
    )

    comparison_period_name = st.selectbox(
        "비교 기간",
        list(PERIOD_OPTIONS.keys()),
        index=3,
        key="comparison_period",
    )

    if len(selected_comparison_names) < 2:
        st.info("비교를 위해 종목을 2개 이상 선택해 주세요.")
    else:
        comparison_tickers = [
            STOCKS[name]["ticker"]
            for name in selected_comparison_names
        ]

        comparison_ticker_to_name = {
            STOCKS[name]["ticker"]: name
            for name in selected_comparison_names
        }

        with st.spinner("비교 데이터를 불러오는 중입니다."):
            close_data = download_comparison_data(
                tickers=comparison_tickers,
                period=PERIOD_OPTIONS[comparison_period_name],
            )

        if close_data.empty:
            st.error("비교 데이터를 불러오지 못했습니다.")
        else:
            ordered_columns = [
                ticker
                for ticker in comparison_tickers
                if ticker in close_data.columns
            ]

            close_data = close_data[ordered_columns]

            comparison_figure, normalized_data = (
                create_comparison_chart(
                    close_data,
                    comparison_ticker_to_name,
                )
            )

            st.plotly_chart(
                comparison_figure,
                use_container_width=True,
            )

            st.markdown('<div class="section-title">기간 성과 요약</div>', unsafe_allow_html=True)

            performance_table = create_performance_table(
                close_data,
                comparison_ticker_to_name,
            )

            st.dataframe(
                performance_table,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "기간 수익률(%)": st.column_config.NumberColumn(
                        format="%.2f%%"
                    ),
                    "연환산 변동성(%)": st.column_config.NumberColumn(
                        format="%.2f%%"
                    ),
                },
            )


# =========================================================
# 4. 원본 데이터
# =========================================================
with data_tab:
    st.markdown(
        f'<div class="section-title">{selected_stock_name} 원본 주가 데이터</div>',
        unsafe_allow_html=True,
    )

    raw_data = download_stock_data(
        ticker=selected_ticker,
        period=selected_period,
        interval=selected_interval,
    )

    if raw_data.empty:
        st.warning("표시할 데이터가 없습니다.")
    else:
        display_data = raw_data.copy()
        display_data.index.name = "날짜"
        display_data = display_data.sort_index(ascending=False)

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

        display_data = display_data[available_columns]

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
            file_name=f"{selected_ticker}_stock_data.csv",
            mime="text/csv",
        )


# =========================================================
# 하단 안내
# =========================================================
st.divider()

st.markdown(
    """
    <div class="footer-note">
        <strong>hani.inc notice</strong><br>
        본 대시보드는 정보 제공 및 학습 목적으로 제작되었습니다.
        Yahoo Finance 데이터는 실시간 거래소 데이터와 차이가 있거나
        일정 시간 지연될 수 있으며, 투자 판단의 유일한 근거로 사용해서는 안 됩니다.
    </div>
    """,
    unsafe_allow_html=True,
)
