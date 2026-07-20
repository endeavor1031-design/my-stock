import datetime
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import yfinance as yf
from sklearn.linear_model import LinearRegression

# 페이지 기본 설정
st.set_page_config(
    page_title="글로벌 주식 대시보드 및 내일 주가 예측",
    page_icon="📈",
    layout="wide"
)

# 주요 글로벌 지수 및 종목 데이터 정의
MARKET_TICKERS = {
    "미국 S&P 500": "^GSPC",
    "미국 나스닥 (NASDAQ)": "^IXIC",
    "한국 코스피 (KOSPI)": "^KS11",
    "일본 닛케이 225": "^N225",
    "애플 (AAPL)": "AAPL",
    "엔비디아 (NVDA)": "NVDA",
    "테슬라 (TSLA)": "TSLA",
    "삼성전자": "005930.KS"
}

# 사이드바 설정
st.sidebar.title("📌 대시보드 메뉴")
page = st.sidebar.radio("페이지 선택", ["📊 주가 대시보드", "🔮 내일 주가 예측"])

selected_name = st.sidebar.selectbox(
    "종목/지수를 선택하세요:",
    list(MARKET_TICKERS.keys())
)

period_option = st.sidebar.selectbox(
    "조회 기간 (대시보드용):",
    ["1개월", "3개월", "6개월", "1년", "3년", "5년"],
    index=3
)

period_map = {
    "1개월": "1mo",
    "3개월": "3mo",
    "6개월": "6mo",
    "1년": "1y",
    "3년": "3y",
    "5년": "5y"
}

ticker_symbol = MARKET_TICKERS[selected_name]

# 데이터 캐싱 (속도 최적화)
@st.cache_data(ttl=3600)
def load_stock_data(symbol, period):
    ticker = yf.Ticker(symbol)
    df = ticker.history(period=period)
    info = ticker.info
    return df, info

try:
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
