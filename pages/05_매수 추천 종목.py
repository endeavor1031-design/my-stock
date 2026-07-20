import math
from datetime import datetime

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import yfinance as yf


st.set_page_config(
    page_title="1주~1달 매수 관심 종목",
    page_icon="🏆",
    layout="wide",
)


# =========================================================
# 분석 종목
# =========================================================
STOCKS = {
    "SK하이닉스": {"ticker": "000660.KS", "currency": "KRW", "market": "한국", "group": "AI 반도체"},
    "삼성전자": {"ticker": "005930.KS", "currency": "KRW", "market": "한국", "group": "AI 반도체"},
    "NAVER": {"ticker": "035420.KS", "currency": "KRW", "market": "한국", "group": "플랫폼"},
    "카카오": {"ticker": "035720.KS", "currency": "KRW", "market": "한국", "group": "플랫폼"},
    "현대차": {"ticker": "005380.KS", "currency": "KRW", "market": "한국", "group": "자동차"},
    "엔비디아": {"ticker": "NVDA", "currency": "USD", "market": "미국", "group": "AI 반도체"},
    "AMD": {"ticker": "AMD", "currency": "USD", "market": "미국", "group": "AI 반도체"},
    "브로드컴": {"ticker": "AVGO", "currency": "USD", "market": "미국", "group": "AI 반도체"},
    "팔란티어": {"ticker": "PLTR", "currency": "USD", "market": "미국", "group": "AI 소프트웨어"},
    "마이크론": {"ticker": "MU", "currency": "USD", "market": "미국", "group": "AI 반도체"},
    "TSMC": {"ticker": "TSM", "currency": "USD", "market": "미국", "group": "AI 반도체"},
    "ASML": {"ticker": "ASML", "currency": "USD", "market": "미국", "group": "반도체 장비"},
    "애플": {"ticker": "AAPL", "currency": "USD", "market": "미국", "group": "빅테크"},
    "마이크로소프트": {"ticker": "MSFT", "currency": "USD", "market": "미국", "group": "빅테크"},
    "알파벳": {"ticker": "GOOGL", "currency": "USD", "market": "미국", "group": "빅테크"},
    "아마존": {"ticker": "AMZN", "currency": "USD", "market": "미국", "group": "빅테크"},
    "메타": {"ticker": "META", "currency": "USD", "market": "미국", "group": "빅테크"},
    "테슬라": {"ticker": "TSLA", "currency": "USD", "market": "미국", "group": "자동차"},
    "슈퍼마이크로컴퓨터": {"ticker": "SMCI", "currency": "USD", "market": "미국", "group": "AI 서버"},
    "반에크 반도체 ETF": {"ticker": "SMH", "currency": "USD", "market": "미국", "group": "반도체 ETF"},
}

TICKER_TO_NAME = {
    information["ticker"]: name
    for name, information in STOCKS.items()
}


# =========================================================
# 디자인
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
        margin-bottom: 1.3rem;
    }

    .rank-card {
        border: 1px solid rgba(128,128,128,.24);
        border-radius: 15px;
        padding: 17px;
        min-height: 205px;
        margin-bottom: 12px;
        background: rgba(128,128,128,.04);
    }

    .rank-number {
        font-size: .78rem;
        color: #888888;
    }

    .rank-name {
        font-size: 1.08rem;
        font-weight: 800;
        margin-top: 2px;
    }

    .rank-ticker {
        color: #888888;
        font-size: .76rem;
        margin-bottom: 10px;
    }

    .rank-score {
        font-size: 1.55rem;
        font-weight: 850;
    }

    .tag {
        display: inline-block;
        margin-top: 7px;
        padding: 3px 8px;
        border-radius: 8px;
        font-size: .74rem;
        background: rgba(128,128,128,.13);
    }

    .analysis-box {
        border-left: 5px solid #777777;
        padding: 13px 16px;
        border-radius: 8px;
        background: rgba(128,128,128,.07);
        margin: 10px 0 15px 0;
    }

    div[data-testid="stMetric"] {
        border: 1px solid rgba(128,128,128,.20);
        border-radius: 12px;
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


def normalize_index(data):
    result = data.copy()
    result.index = pd.to_datetime(result.index)

    try:
        result.index = result.index.tz_localize(None)
    except (TypeError, AttributeError):
        pass

    return result.sort_index()


def extract_ticker_data(batch_data, ticker):
    if batch_data is None or batch_data.empty:
        return pd.DataFrame()

    data = batch_data.copy()

    if isinstance(data.columns, pd.MultiIndex):
        level_zero = list(data.columns.get_level_values(0))
        level_one = list(data.columns.get_level_values(1))

        try:
            if ticker in level_zero:
                result = data[ticker].copy()
            elif ticker in level_one:
                result = data.xs(
                    ticker,
                    axis=1,
                    level=1,
                ).copy()
            else:
                return pd.DataFrame()
        except (KeyError, ValueError):
            return pd.DataFrame()
    else:
        result = data.copy()

    result = result.loc[
        :,
        ~result.columns.duplicated(),
    ]

    if "Close" not in result.columns:
        return pd.DataFrame()

    result = result.dropna(
        subset=["Close"],
        how="all",
    )

    if result.empty:
        return pd.DataFrame()

    return normalize_index(result)


# =========================================================
# 전체 종목 일괄 조회
# =========================================================
@st.cache_data(ttl=1800, show_spinner=False)
def download_all_data(period="2y"):
    tickers = [
        information["ticker"]
        for information in STOCKS.values()
    ]

    errors = []

    try:
        data = yf.download(
            tickers=tickers,
            period=period,
            interval="1d",
            group_by="ticker",
            auto_adjust=False,
            actions=False,
            progress=False,
            threads=False,
            timeout=40,
        )

        if data is not None and not data.empty:
            return data, ""

        errors.append(
            "Yahoo Finance가 빈 데이터를 반환했습니다."
        )

    except Exception as error:
        errors.append(
            f"{type(error).__name__}: {error}"
        )

    return pd.DataFrame(), "\n".join(errors)


# =========================================================
# 지표 계산
# =========================================================
def calculate_indicators(data):
    result = data.copy()
    close = result["Close"]

    result["RETURN"] = close.pct_change()
    result["MA5"] = close.rolling(5).mean()
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
        result["EMA12"]
        - result["EMA26"]
    )

    result["SIGNAL"] = result["MACD"].ewm(
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
        / average_loss.replace(
            0,
            float("nan"),
        )
    )

    result["RSI"] = (
        100
        - 100 / (1 + relative_strength)
    )

    return result


# =========================================================
# 기간 예상수익률
# =========================================================
def calculate_expected_return(
    indicators,
    horizon_days,
):
    if len(indicators) < 140:
        return None

    latest = indicators.iloc[-1]
    previous = indicators.iloc[-2]

    close = safe_float(latest["Close"])
    returns = indicators["RETURN"].dropna()

    mean_5 = safe_float(
        returns.tail(5).mean(),
        0,
    )

    mean_20 = safe_float(
        returns.tail(20).mean(),
        0,
    )

    mean_60 = safe_float(
        returns.tail(60).mean(),
        0,
    )

    mean_120 = safe_float(
        returns.tail(120).mean(),
        0,
    )

    ma5_now = safe_float(latest["MA5"])
    ma5_previous = safe_float(previous["MA5"])
    ma20_now = safe_float(latest["MA20"])
    ma20_previous = safe_float(previous["MA20"])
    ma60_now = safe_float(latest["MA60"])
    ma60_previous = safe_float(previous["MA60"])
    ma120_now = safe_float(latest["MA120"])
    ma120_previous = safe_float(previous["MA120"])

    slopes = {}

    for label, now, before in [
        ("ma5", ma5_now, ma5_previous),
        ("ma20", ma20_now, ma20_previous),
        ("ma60", ma60_now, ma60_previous),
        ("ma120", ma120_now, ma120_previous),
    ]:
        if now is not None and before not in (None, 0):
            slopes[label] = now / before - 1
        else:
            slopes[label] = 0

    macd = safe_float(
        latest["MACD"],
        0,
    )

    signal = safe_float(
        latest["SIGNAL"],
        0,
    )

    macd_component = 0

    if close not in (None, 0):
        macd_component = (
            macd - signal
        ) / close

    rsi = safe_float(
        latest["RSI"],
        50,
    )

    if rsi >= 75:
        rsi_component = -0.002
    elif rsi >= 65:
        rsi_component = -0.0008
    elif rsi <= 25:
        rsi_component = 0.002
    elif rsi <= 35:
        rsi_component = 0.0008
    else:
        rsi_component = 0

    if horizon_days == 5:
        daily_signal = (
            mean_5 * 0.30
            + mean_20 * 0.22
            + mean_60 * 0.08
            + slopes["ma5"] * 0.16
            + slopes["ma20"] * 0.10
            + macd_component * 0.10
            + rsi_component * 0.04
        )
        volatility_window = 20
        signal_limit_multiplier = 0.65

    else:
        daily_signal = (
            mean_5 * 0.08
            + mean_20 * 0.25
            + mean_60 * 0.22
            + mean_120 * 0.10
            + slopes["ma20"] * 0.12
            + slopes["ma60"] * 0.10
            + slopes["ma120"] * 0.05
            + macd_component * 0.05
            + rsi_component * 0.03
        )
        volatility_window = 60
        signal_limit_multiplier = 0.45

    daily_volatility = safe_float(
        returns.tail(
            volatility_window
        ).std(),
        0,
    )

    maximum_daily_signal = max(
        daily_volatility
        * signal_limit_multiplier,
        0.0015,
    )

    daily_signal = max(
        -maximum_daily_signal,
        min(
            maximum_daily_signal,
            daily_signal,
        ),
    )

    cumulative_return = (
        (1 + daily_signal) ** horizon_days
        - 1
    )

    range_width = (
        daily_volatility
        * math.sqrt(horizon_days)
    )

    return {
        "expected_return": cumulative_return * 100,
        "lower_return": (
            cumulative_return
            - range_width
        ) * 100,
        "upper_return": (
            cumulative_return
            + range_width
        ) * 100,
        "daily_volatility": (
            daily_volatility * 100
        ),
        "rsi": rsi,
        "macd_positive": macd > signal,
        "ma20_positive": (
            close is not None
            and ma20_now is not None
            and close > ma20_now
        ),
        "ma60_positive": (
            close is not None
            and ma60_now is not None
            and close > ma60_now
        ),
        "ma120_positive": (
            close is not None
            and ma120_now is not None
            and close > ma120_now
        ),
    }


# =========================================================
# 간이 백테스트
# =========================================================
def backtest_direction(
    data,
    horizon_days,
    test_count=30,
):
    if len(data) < 180 + horizon_days:
        return None

    start = max(
        140,
        len(data)
        - test_count
        - horizon_days,
    )

    results = []

    for position in range(
        start,
        len(data) - horizon_days,
    ):
        historical = data.iloc[
            :position + 1
        ].copy()

        indicators = calculate_indicators(
            historical
        )

        forecast = calculate_expected_return(
            indicators,
            horizon_days,
        )

        if forecast is None:
            continue

        current_price = safe_float(
            data["Close"].iloc[position]
        )

        future_price = safe_float(
            data["Close"].iloc[
                position + horizon_days
            ]
        )

        if (
            current_price in (None, 0)
            or future_price is None
        ):
            continue

        actual_return = (
            future_price / current_price - 1
        ) * 100

        predicted_return = forecast[
            "expected_return"
        ]

        predicted_direction = (
            1
            if predicted_return > 0
            else -1
            if predicted_return < 0
            else 0
        )

        actual_direction = (
            1
            if actual_return > 0
            else -1
            if actual_return < 0
            else 0
        )

        results.append(
            predicted_direction
            == actual_direction
        )

    if not results:
        return None

    return sum(results) / len(results) * 100


# =========================================================
# 종목 평가
# =========================================================
def evaluate_stock(
    name,
    information,
    data,
    risk_profile,
):
    if data.empty or len(data) < 180:
        return None

    indicators = calculate_indicators(data)
    close = indicators["Close"].dropna()

    if len(close) < 140:
        return None

    week = calculate_expected_return(
        indicators,
        5,
    )

    month = calculate_expected_return(
        indicators,
        20,
    )

    if week is None or month is None:
        return None

    current_price = safe_float(
        close.iloc[-1]
    )

    recent_return = (
        close.iloc[-1] / close.iloc[-21] - 1
    ) * 100 if len(close) >= 21 else None

    week_accuracy = backtest_direction(
        data,
        5,
        24,
    )

    month_accuracy = backtest_direction(
        data,
        20,
        24,
    )

    # ---------------------------------------------
    # 점수 구성
    # ---------------------------------------------
    score = 50.0

    # 5거래일 예상수익률: 최대 ±15점
    score += max(
        -15,
        min(
            15,
            week["expected_return"] * 3,
        ),
    )

    # 20거래일 예상수익률: 최대 ±20점
    score += max(
        -20,
        min(
            20,
            month["expected_return"] * 1.8,
        ),
    )

    # 추세
    score += 4 if month["ma20_positive"] else -4
    score += 5 if month["ma60_positive"] else -5
    score += 4 if month["ma120_positive"] else -4
    score += 4 if month["macd_positive"] else -4

    # RSI
    rsi = month["rsi"]

    if 45 <= rsi <= 65:
        score += 5
    elif 35 <= rsi < 45:
        score += 2
    elif 65 < rsi <= 72:
        score += 1
    elif rsi > 78:
        score -= 7
    elif rsi < 25:
        score -= 3

    # 과거 검증 성과
    if week_accuracy is not None:
        score += max(
            -5,
            min(
                5,
                (week_accuracy - 50) * 0.20,
            ),
        )

    if month_accuracy is not None:
        score += max(
            -6,
            min(
                6,
                (month_accuracy - 50) * 0.24,
            ),
        )

    # 위험도에 따른 변동성 감점
    volatility = month["daily_volatility"]

    risk_limits = {
        "보수적": 2.2,
        "중립": 3.2,
        "공격적": 4.5,
    }

    volatility_limit = risk_limits[
        risk_profile
    ]

    if volatility > volatility_limit:
        score -= min(
            18,
            (
                volatility
                - volatility_limit
            ) * 6,
        )
    elif volatility < 1.5:
        score += 3

    score = max(
        0,
        min(100, score),
    )

    # 추천 구간
    if score >= 78:
        grade = "매수 관심 높음"
        grade_color = "#e53935"
    elif score >= 65:
        grade = "분할매수 검토"
        grade_color = "#e53935"
    elif score >= 52:
        grade = "관망"
        grade_color = "#777777"
    elif score >= 38:
        grade = "주의"
        grade_color = "#1565c0"
    else:
        grade = "매수 비추천"
        grade_color = "#1565c0"

    expected_week_price = current_price * (
        1 + week["expected_return"] / 100
    )

    expected_month_price = current_price * (
        1 + month["expected_return"] / 100
    )

    return {
        "종목": name,
        "티커": information["ticker"],
        "시장": information["market"],
        "분류": information["group"],
        "통화": information["currency"],
        "현재가": current_price,
        "5거래일 예상가": expected_week_price,
        "20거래일 예상가": expected_month_price,
        "5거래일 예상수익률(%)": week["expected_return"],
        "20거래일 예상수익률(%)": month["expected_return"],
        "20거래일 예상하단(%)": month["lower_return"],
        "20거래일 예상상단(%)": month["upper_return"],
        "일간 변동성(%)": volatility,
        "RSI": rsi,
        "5거래일 방향 적중률(%)": week_accuracy,
        "20거래일 방향 적중률(%)": month_accuracy,
        "최근 20거래일 수익률(%)": recent_return,
        "점수": round(score, 1),
        "등급": grade,
        "등급색": grade_color,
        "20일선 상회": month["ma20_positive"],
        "60일선 상회": month["ma60_positive"],
        "120일선 상회": month["ma120_positive"],
        "MACD 긍정": month["macd_positive"],
    }


def create_reason(row):
    reasons = []

    if row["5거래일 예상수익률(%)"] > 0:
        reasons.append(
            f"1주 예상 {row['5거래일 예상수익률(%)']:+.2f}%"
        )
    else:
        reasons.append(
            f"1주 예상 {row['5거래일 예상수익률(%)']:+.2f}%"
        )

    reasons.append(
        f"1달 예상 {row['20거래일 예상수익률(%)']:+.2f}%"
    )

    if row["60일선 상회"]:
        reasons.append("60일선 상회")
    else:
        reasons.append("60일선 하회")

    if row["MACD 긍정"]:
        reasons.append("MACD 긍정")
    else:
        reasons.append("MACD 약세")

    reasons.append(
        f"RSI {row['RSI']:.1f}"
    )

    return " · ".join(reasons)


# =========================================================
# 시각화
# =========================================================
def create_score_chart(ranking):
    chart_data = ranking.head(12).sort_values(
        "점수",
        ascending=True,
    )

    colors = [
        "#e53935"
        if score >= 65
        else "#777777"
        if score >= 52
        else "#1565c0"
        for score in chart_data["점수"]
    ]

    figure = go.Figure()

    figure.add_trace(
        go.Bar(
            x=chart_data["점수"],
            y=chart_data["종목"],
            orientation="h",
            marker_color=colors,
            text=[
                f"{score:.1f}점"
                for score in chart_data["점수"]
            ],
            textposition="auto",
        )
    )

    figure.add_vline(
        x=65,
        line_dash="dash",
        annotation_text="분할매수 검토",
    )

    figure.update_layout(
        title="1주~1달 매수 관심도 순위",
        xaxis=dict(
            title="종합점수",
            range=[0, 100],
        ),
        height=650,
        margin=dict(
            l=20,
            r=20,
            t=75,
            b=20,
        ),
    )

    return figure


def create_risk_return_chart(ranking):
    figure = go.Figure()

    figure.add_trace(
        go.Scatter(
            x=ranking[
                "일간 변동성(%)"
            ],
            y=ranking[
                "20거래일 예상수익률(%)"
            ],
            mode="markers+text",
            text=ranking["종목"],
            textposition="top center",
            marker=dict(
                size=[
                    max(
                        10,
                        min(
                            30,
                            score / 3,
                        ),
                    )
                    for score in ranking["점수"]
                ],
                color=ranking["점수"],
                colorscale="RdYlBu_r",
                colorbar=dict(
                    title="점수"
                ),
                showscale=True,
            ),
            hovertemplate=(
                "%{text}<br>"
                "일간 변동성: %{x:.2f}%<br>"
                "20거래일 예상수익률: %{y:.2f}%"
                "<extra></extra>"
            ),
        )
    )

    figure.add_hline(
        y=0,
        line_dash="dash",
    )

    figure.update_layout(
        title="위험 대비 20거래일 예상수익률",
        xaxis_title="일간 변동성 (%)",
        yaxis_title="20거래일 예상수익률 (%)",
        height=620,
        margin=dict(
            l=20,
            r=20,
            t=70,
            b=20,
        ),
    )

    return figure


def create_period_comparison_chart(ranking):
    chart_data = ranking.head(10)

    figure = go.Figure()

    figure.add_trace(
        go.Bar(
            x=chart_data["종목"],
            y=chart_data[
                "5거래일 예상수익률(%)"
            ],
            name="5거래일 예상",
        )
    )

    figure.add_trace(
        go.Bar(
            x=chart_data["종목"],
            y=chart_data[
                "20거래일 예상수익률(%)"
            ],
            name="20거래일 예상",
        )
    )

    figure.add_hline(
        y=0,
        line_dash="dash",
    )

    figure.update_layout(
        title="상위 종목 기간별 예상수익률",
        xaxis_title="종목",
        yaxis_title="예상수익률 (%)",
        barmode="group",
        height=520,
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


def show_rank_card(
    row,
    rank,
):
    currency = row["통화"]

    html = (
        f'<div class="rank-card">'
        f'<div class="rank-number">추천 관심도 {rank}위</div>'
        f'<div class="rank-name">{row["종목"]}</div>'
        f'<div class="rank-ticker">{row["티커"]} · {row["분류"]}</div>'
        f'<div class="rank-score" style="color:{row["등급색"]};">'
        f'{row["점수"]:.1f}점'
        f'</div>'
        f'<div style="color:{row["등급색"]}; font-weight:750;">'
        f'{row["등급"]}'
        f'</div>'
        f'<div style="margin-top:8px;">'
        f'현재가: <strong>{format_price(row["현재가"], currency)}</strong>'
        f'</div>'
        f'<div>'
        f'1주: <strong>{row["5거래일 예상수익률(%)"]:+.2f}%</strong>'
        f' · '
        f'1달: <strong>{row["20거래일 예상수익률(%)"]:+.2f}%</strong>'
        f'</div>'
        f'<div class="tag">'
        f'변동성 {row["일간 변동성(%)"]:.2f}%'
        f'</div>'
        f'</div>'
    )

    st.markdown(
        html,
        unsafe_allow_html=True,
    )


# =========================================================
# 화면
# =========================================================
st.markdown(
    '<div class="main-title">🏆 1주~1달 매수 관심 종목</div>',
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="subtitle">
        향후 5거래일과 20거래일 예상수익률, 기술 추세, 변동성,
        RSI·MACD 및 과거 방향 적중률을 종합해 관심 종목을 선별합니다.
    </div>
    """,
    unsafe_allow_html=True,
)


with st.sidebar:
    st.header("종목 선별 설정")

    selected_market = st.selectbox(
        "시장",
        [
            "전체",
            "한국",
            "미국",
        ],
    )

    selected_group = st.selectbox(
        "산업 분류",
        [
            "전체"
        ] + sorted(
            {
                information["group"]
                for information in STOCKS.values()
            }
        ),
    )

    risk_profile = st.select_slider(
        "위험 성향",
        options=[
            "보수적",
            "중립",
            "공격적",
        ],
        value="중립",
    )

    minimum_score = st.slider(
        "표시할 최소 점수",
        min_value=0,
        max_value=100,
        value=50,
        step=5,
    )

    top_count = st.slider(
        "상위 표시 종목 수",
        min_value=3,
        max_value=15,
        value=10,
        step=1,
    )

    st.divider()

    if st.button(
        "데이터 새로고침",
        use_container_width=True,
    ):
        st.cache_data.clear()
        st.rerun()

    st.caption(
        "매수 관심도는 자동 계산된 참고 점수이며 개인 맞춤 투자자문이 아닙니다."
    )


with st.spinner(
    "전체 종목 데이터를 한 번에 불러오고 순위를 계산하는 중입니다."
):
    batch_data, data_error = download_all_data(
        period="2y"
    )


if batch_data.empty:
    st.error(
        "Yahoo Finance에서 전체 종목 데이터를 불러오지 못했습니다."
    )

    if data_error:
        st.code(data_error)

    st.info(
        "Streamlit Cloud 공유 IP가 일시적으로 제한된 경우가 있습니다. "
        "잠시 후 데이터 새로고침을 눌러 다시 확인해 주세요."
    )

    st.stop()


rows = []
failed_names = []

for name, information in STOCKS.items():
    if (
        selected_market != "전체"
        and information["market"]
        != selected_market
    ):
        continue

    if (
        selected_group != "전체"
        and information["group"]
        != selected_group
    ):
        continue

    ticker = information["ticker"]

    data = extract_ticker_data(
        batch_data,
        ticker,
    )

    evaluation = evaluate_stock(
        name=name,
        information=information,
        data=data,
        risk_profile=risk_profile,
    )

    if evaluation is None:
        failed_names.append(name)
        continue

    rows.append(evaluation)


ranking = pd.DataFrame(rows)


if ranking.empty:
    st.warning(
        "현재 조건에서 분석 가능한 종목이 없습니다."
    )
    st.stop()


ranking = ranking.sort_values(
    [
        "점수",
        "20거래일 예상수익률(%)",
    ],
    ascending=[
        False,
        False,
    ],
).reset_index(drop=True)


filtered_ranking = ranking[
    ranking["점수"] >= minimum_score
].head(top_count).copy()


if filtered_ranking.empty:
    st.warning(
        "설정한 최소 점수를 충족한 종목이 없습니다. "
        "왼쪽에서 최소 점수를 낮춰 주세요."
    )
    st.stop()


# =========================================================
# 요약
# =========================================================
top_stock = filtered_ranking.iloc[0]
buy_candidates = filtered_ranking[
    filtered_ranking["점수"] >= 65
]

metric_columns = st.columns(5)

metric_columns[0].metric(
    "분석 종목 수",
    f"{len(ranking)}개",
)

metric_columns[1].metric(
    "매수 검토 구간",
    f"{len(buy_candidates)}개",
)

metric_columns[2].metric(
    "최상위 종목",
    top_stock["종목"],
)

metric_columns[3].metric(
    "최상위 점수",
    f"{top_stock['점수']:.1f}점",
)

metric_columns[4].metric(
    "최상위 1달 예상",
    f"{top_stock['20거래일 예상수익률(%)']:+.2f}%",
)


st.subheader("상위 관심 종목")

card_count = min(
    6,
    len(filtered_ranking),
)

for start in range(
    0,
    card_count,
    3,
):
    columns = st.columns(3)

    for offset, column in enumerate(
        columns
    ):
        index = start + offset

        if index >= card_count:
            break

        row = filtered_ranking.iloc[
            index
        ]

        with column:
            show_rank_card(
                row=row,
                rank=index + 1,
            )


st.markdown(
    f"""
    <div class="analysis-box">
        <strong>현재 모델의 최상위 관심 종목</strong><br>
        {top_stock["종목"]}은(는) 종합점수
        {top_stock["점수"]:.1f}점으로 가장 높습니다.
        5거래일 예상수익률은
        {top_stock["5거래일 예상수익률(%)"]:+.2f}%,
        20거래일 예상수익률은
        {top_stock["20거래일 예상수익률(%)"]:+.2f}%입니다.
        다만 20거래일 예상 범위는
        {top_stock["20거래일 예상하단(%)"]:+.2f}%에서
        {top_stock["20거래일 예상상단(%)"]:+.2f}%로 넓으며,
        단일 가격에 일괄 매수하기보다 분할 접근 여부를 검토해야 합니다.
    </div>
    """,
    unsafe_allow_html=True,
)


ranking_tab, comparison_tab, detail_tab, method_tab = st.tabs(
    [
        "종합 순위",
        "위험·수익 비교",
        "종목별 근거",
        "점수 계산 방식",
    ]
)


# =========================================================
# 종합 순위
# =========================================================
with ranking_tab:
    st.plotly_chart(
        create_score_chart(
            filtered_ranking
        ),
        use_container_width=True,
    )

    display_columns = [
        "종목",
        "티커",
        "분류",
        "점수",
        "등급",
        "5거래일 예상수익률(%)",
        "20거래일 예상수익률(%)",
        "20거래일 예상하단(%)",
        "20거래일 예상상단(%)",
        "일간 변동성(%)",
        "RSI",
        "5거래일 방향 적중률(%)",
        "20거래일 방향 적중률(%)",
    ]

    display_table = filtered_ranking[
        display_columns
    ].copy()

    st.dataframe(
        display_table,
        use_container_width=True,
        hide_index=True,
        column_config={
            "점수":
                st.column_config.ProgressColumn(
                    min_value=0,
                    max_value=100,
                    format="%.1f",
                ),
            "5거래일 예상수익률(%)":
                st.column_config.NumberColumn(
                    format="%.2f%%"
                ),
            "20거래일 예상수익률(%)":
                st.column_config.NumberColumn(
                    format="%.2f%%"
                ),
            "20거래일 예상하단(%)":
                st.column_config.NumberColumn(
                    format="%.2f%%"
                ),
            "20거래일 예상상단(%)":
                st.column_config.NumberColumn(
                    format="%.2f%%"
                ),
            "일간 변동성(%)":
                st.column_config.NumberColumn(
                    format="%.2f%%"
                ),
            "RSI":
                st.column_config.NumberColumn(
                    format="%.1f"
                ),
            "5거래일 방향 적중률(%)":
                st.column_config.NumberColumn(
                    format="%.1f%%"
                ),
            "20거래일 방향 적중률(%)":
                st.column_config.NumberColumn(
                    format="%.1f%%"
                ),
        },
    )

    csv_data = display_table.to_csv(
        index=False,
        encoding="utf-8-sig",
    )

    st.download_button(
        "순위표 CSV 다운로드",
        data=csv_data,
        file_name=(
            "stock_screening_"
            f"{datetime.now().strftime('%Y%m%d')}.csv"
        ),
        mime="text/csv",
    )


# =========================================================
# 위험·수익 비교
# =========================================================
with comparison_tab:
    st.plotly_chart(
        create_period_comparison_chart(
            filtered_ranking
        ),
        use_container_width=True,
    )

    st.plotly_chart(
        create_risk_return_chart(
            filtered_ranking
        ),
        use_container_width=True,
    )

    st.info(
        "오른쪽 위에 위치할수록 예상수익률과 변동성이 모두 높습니다. "
        "높은 예상수익률만 보지 말고 변동성과 예상 하단을 함께 확인해야 합니다."
    )


# =========================================================
# 종목별 근거
# =========================================================
with detail_tab:
    selected_detail_name = st.selectbox(
        "근거를 확인할 종목",
        filtered_ranking["종목"].tolist(),
    )

    detail_row = filtered_ranking[
        filtered_ranking["종목"]
        == selected_detail_name
    ].iloc[0]

    detail_columns = st.columns(6)

    detail_columns[0].metric(
        "종합점수",
        f"{detail_row['점수']:.1f}",
    )

    detail_columns[1].metric(
        "현재가",
        format_price(
            detail_row["현재가"],
            detail_row["통화"],
        ),
    )

    detail_columns[2].metric(
        "5거래일 예상",
        f"{detail_row['5거래일 예상수익률(%)']:+.2f}%",
    )

    detail_columns[3].metric(
        "20거래일 예상",
        f"{detail_row['20거래일 예상수익률(%)']:+.2f}%",
    )

    detail_columns[4].metric(
        "일간 변동성",
        f"{detail_row['일간 변동성(%)']:.2f}%",
    )

    detail_columns[5].metric(
        "RSI",
        f"{detail_row['RSI']:.1f}",
    )

    st.markdown(
        f"""
        <div class="analysis-box">
            <strong>{selected_detail_name} 평가 근거</strong><br>
            {create_reason(detail_row)}<br><br>
            현재 등급은 <strong>{detail_row["등급"]}</strong>입니다.
            20거래일 예상 범위는
            {detail_row["20거래일 예상하단(%)"]:+.2f}%에서
            {detail_row["20거래일 예상상단(%)"]:+.2f}%입니다.
        </div>
        """,
        unsafe_allow_html=True,
    )

    signal_table = pd.DataFrame(
        {
            "평가 항목": [
                "20일 이동평균선",
                "60일 이동평균선",
                "120일 이동평균선",
                "MACD",
                "5거래일 방향 적중률",
                "20거래일 방향 적중률",
            ],
            "현재 상태": [
                (
                    "주가가 위"
                    if detail_row["20일선 상회"]
                    else "주가가 아래"
                ),
                (
                    "주가가 위"
                    if detail_row["60일선 상회"]
                    else "주가가 아래"
                ),
                (
                    "주가가 위"
                    if detail_row["120일선 상회"]
                    else "주가가 아래"
                ),
                (
                    "긍정"
                    if detail_row["MACD 긍정"]
                    else "부정"
                ),
                (
                    f"{detail_row['5거래일 방향 적중률(%)']:.1f}%"
                    if detail_row["5거래일 방향 적중률(%)"]
                    is not None
                    else "-"
                ),
                (
                    f"{detail_row['20거래일 방향 적중률(%)']:.1f}%"
                    if detail_row["20거래일 방향 적중률(%)"]
                    is not None
                    else "-"
                ),
            ],
        }
    )

    st.dataframe(
        signal_table,
        use_container_width=True,
        hide_index=True,
    )


# =========================================================
# 계산 방식
# =========================================================
with method_tab:
    st.subheader("매수 관심도 점수 구성")

    method_table = pd.DataFrame(
        {
            "평가 요소": [
                "5거래일 예상수익률",
                "20거래일 예상수익률",
                "20·60·120일 이동평균선",
                "MACD",
                "RSI",
                "과거 방향 적중률",
                "변동성 위험",
            ],
            "역할": [
                "단기 모멘텀 평가",
                "1달 기대수익 평가",
                "중장기 추세 확인",
                "추세 변화 확인",
                "과매수·과매도 조정",
                "모델의 과거 방향성 참고",
                "위험 성향별 감점",
            ],
        }
    )

    st.dataframe(
        method_table,
        use_container_width=True,
        hide_index=True,
    )

    st.markdown(
        """
        ### 등급 기준

        - **78점 이상:** 매수 관심 높음
        - **65~77.9점:** 분할매수 검토
        - **52~64.9점:** 관망
        - **38~51.9점:** 주의
        - **38점 미만:** 매수 비추천

        위험 성향이 보수적일수록 변동성이 높은 종목의 점수가 더 크게
        낮아집니다. 공격적 설정에서도 예상수익률이 음수이거나 중장기
        추세가 약하면 높은 점수를 받기 어렵습니다.
        """
    )


if failed_names:
    with st.expander(
        "데이터 부족 또는 분석 제외 종목"
    ):
        st.write(
            ", ".join(failed_names)
        )


st.divider()

st.warning(
    "이 페이지는 특정 종목의 매수를 지시하는 개인 맞춤 투자자문이 아닙니다. "
    "점수와 예상수익률은 과거 가격 데이터만 이용한 자동 선별 결과입니다. "
    "실적 발표, 뉴스, 금리, 환율, 정책 및 급격한 수급 변화는 반영하지 못합니다. "
    "실제 투자 전에는 손실 가능성과 본인의 투자 기간을 별도로 검토해야 합니다."
)
