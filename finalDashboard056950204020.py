from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# ตั้งค่าหน้าเว็บ
st.set_page_config(
    page_title="แดชบอร์ดวิเคราะห์คุณภาพการนอนหลับ",
    page_icon="😴",
    layout="wide",
)

# --- ส่วนอ่านและประมวลผลข้อมูล ---


@st.cache_data
def load_and_process_data():
    # อ่านไฟล์ sleep.csv หากไม่มีจะใช้ข้อมูลตัวอย่างตามภาพ
    try:
        df = pd.read_csv("sleep.csv")
    except FileNotFoundError:
        data = {
            "ชื่อ": ["สมชาย", "สมหญิง", "วิชัย", "มานะ", "ธานี"],
            "เวลาเข้านอน": ["23:00", "22:00", "22:00", "00:00", "23:30"],
            "เวลาตื่น": ["06:30", "06:00", "07:00", "04:20", "05:30"],
        }
        df = pd.DataFrame(data)

    def calculate_sleep(row):
        bed = datetime.strptime(str(row["เวลาเข้านอน"]).strip(), "%H:%M")
        wake = datetime.strptime(str(row["เวลาตื่นนอน"]).strip(), "%H:%M")
        if wake <= bed:
            wake += timedelta(days=1)

        total_minutes = int((wake - bed).total_seconds() / 60)
        hours = total_minutes // 60
        mins = total_minutes % 60

        duration_str = f"{hours} ชม. {mins} นาที"
        cycles = round(total_minutes / 90.0, 5)
        status = "เพียงพอ" if total_minutes >= 7 * 60 else "ไม่เพียงพอ"

        return pd.Series(
            [total_minutes, duration_str, cycles, status],
            index=[
                "total_minutes",
                "ระยะเวลานอน",
                "จำนวนรอบวงจรการนอน",
                "สถานะ",
            ],
        )

    calc_df = df.apply(calculate_sleep, axis=1)
    df = pd.concat([df, calc_df], axis=1)
    return df


df = load_and_process_data()

# --- 1. หัวข้อแดชบอร์ด ---
st.title("😴 แดชบอร์ดวิเคราะห์และประเมินคุณภาพการนอนหลับ")
st.caption(
    "คำนวณระยะเวลานอน จำนวนรอบวงจรการนอน (Sleep Cycle) และประเมินสถานะการนอนหลับ (เกณฑ์เพียงพอ >= 7 ชั่วโมง)"
)
st.write("---")

# --- 2. สรุปสถิติภาพรวม (Metrics) ---
st.subheader("📌 สรุปสถิติภาพรวม")

total_users = len(df)
sufficient_users = len(df[df["สถานะ"] == "เพียงพอ"])
insufficient_users = len(df[df["สถานะ"] == "ไม่เพียงพอ"])

max_sleep_row = df.loc[df["total_minutes"].idxmax()]
min_sleep_row = df.loc[df["total_minutes"].idxmin()]

col1, col2, col3, col4, col5 = st.columns(5)

col1.metric("ผู้ใช้งานทั้งหมด", f"{total_users} คน")
col2.metric("นอนเพียงพอ (>= 7 ชม.)", f"{sufficient_users} คน")
col3.metric("นอนไม่เพียงพอ", f"{insufficient_users} คน")
col4.metric(
    "นอนมากที่สุด",
    f"{max_sleep_row['ชื่อ']}",
    delta=max_sleep_row["ระยะเวลานอน"],
)
col5.metric(
    "นอนน้อยที่สุด",
    f"{min_sleep_row['ชื่อ']}",
    delta=f"-{min_sleep_row['ระยะเวลานอน']}",
    delta_color="inverse",
)

st.write("---")

# --- 3. กราฟวิเคราะห์เวลานอนและวงจรการนอนหลับ ---
st.subheader("📊 กราฟวิเคราะห์เวลานอนและวงจรการนอนหลับ")

chart_col1, chart_col2 = st.columns([1.2, 1])

with chart_col1:
    st.write("**ระยะเวลานอนรายบุคคล (นาที)**")

    # กำหนดสีแท่งกราฟตามสถานะ
    colors = [
        "#4CAF50" if s == "เพียงพอ" else "#E53935" for s in df["สถานะ"]
    ]

    fig_bar = go.Figure()
    fig_bar.add_trace(
        go.Bar(
            x=df["ชื่อ"],
            y=df["total_minutes"],
            marker_color=colors,
            text=[
                f"{row['ระยะเวลานอน']}" for _, row in df.iterrows()
            ],
            textposition="auto",
        )
    )

    # เส้นเกณฑ์มาตรฐาน 7 ชั่วโมง (420 นาที)
    fig_bar.add_shape(
        type="line",
        x0=-0.5,
        x1=len(df) - 0.5,
        y0=420,
        y1=420,
        line=dict(color="Navy", width=2, dash="dash"),
    )

    fig_bar.add_annotation(
        x=len(df) - 1,
        y=435,
        text="เกณฑ์เพียงพอ (7 ชม.)",
        showarrow=False,
        font=dict(color="Navy", size=11),
    )

    fig_bar.update_layout(
        xaxis_title="ผู้ใช้งาน",
        yaxis_title="ระยะเวลานอน (นาที)",
        yaxis=dict(range=[0, 500]),
        height=380,
        margin=dict(l=20, r=20, t=20, b=20),
    )
    st.plotly_chart(fig_bar, use_container_width=True)

with chart_col2:
    st.write("**สัดส่วนผู้ที่นอนเพียงพอ vs ไม่เพียงพอ**")

    status_counts = df["สถานะ"].value_counts()
    fig_pie = px.pie(
        values=status_counts.values,
        names=status_counts.index,
        hole=0.5,
        color=status_counts.index,
        color_discrete_map={"เพียงพอ": "#4CAF50", "ไม่เพียงพอ": "#E53935"},
    )
    fig_pie.update_traces(textinfo="percent", textfont_size=14)
    fig_pie.update_layout(
        height=380,
        margin=dict(l=20, r=20, t=20, b=20),
        legend=dict(orientation="v", yanchor="top", y=1, xanchor="left", x=1),
    )
    st.plotly_chart(fig_pie, use_container_width=True)

# --- 4. ตารางรายละเอียดการนอนหลับรายบุคคล ---
st.subheader("📋 รายละเอียดการนอนหลับรายบุคคล (`sleep_output.csv`)")

# จัดรูปแบบตารางแสดงผล
display_df = df[
    [
        "ชื่อ",
        "เวลาเข้านอน",
        "เวลาตื่นนอน",
        "ระยะเวลานอน",
        "จำนวนรอบวงจรการนอน",
        "สถานะ",
    ]
].copy()

st.dataframe(
    display_df.style.map(
        lambda val: (
            "color: green; font-weight: bold"
            if val == "เพียงพอ"
            else ("color: red; font-weight: bold" if val == "ไม่เพียงพอ" else "")
        ),
        subset=["สถานะ"],
    ),
    use_container_width=True,
)

# ปุ่มดาวน์โหลดไฟล์ CSV
csv = display_df.to_csv(index=False).encode("utf-8-sig")
st.download_button(
    label="📥 ดาวน์โหลดข้อมูล sleep_output.csv",
    data=csv,
    file_name="sleep_output.csv",
    mime="text/csv",
)