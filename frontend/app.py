import streamlit as st
import os
import pandas as pd
from datetime import datetime
import requests

API_BASE_URL = "http://backend:8000"

st.set_page_config(
    page_title="AI Construction Safety Monitor",
    page_icon="🏗️",
    layout="wide"
)

LOG_FILE = "violation_log.csv"

def get_status_badge(risk_level):
    if risk_level == "LOW":
        return "🟢 Güvenli"
    elif risk_level == "MEDIUM":
        return "🟡 Dikkat"
    elif risk_level == "HIGH":
        return "🔴 Kritik"
    return "⚪ Bilinmiyor"

def get_recommendations(api_result):
    recommendations = []

    no_helmet = api_result.get("no_helmet", 0)
    no_vest = api_result.get("no_vest", 0)
    risk_level = api_result.get("risk_level", "LOW")

    if no_helmet > 0:
        recommendations.append("Baret kullanmayan çalışanlar için sahada anlık KKE kontrolü yapılmalı.")

    if no_vest > 0:
        recommendations.append("Reflektif yelek kullanımı denetlenmeli ve eksikler giderilmeli.")

    if risk_level == "HIGH":
        recommendations.append("Saha sorumlusu tarafından ilgili bölgede acil güvenlik denetimi başlatılmalı.")
        recommendations.append("İhlal tespit edilen alan geçici olarak kontrol altına alınmalı.")

    if risk_level == "MEDIUM":
        recommendations.append("Vardiya öncesi kısa güvenlik bilgilendirmesi yapılmalı.")

    if risk_level == "LOW":
        recommendations.append("Mevcut saha düzeni korunmalı ve periyodik izleme sürdürülmeli.")

    return recommendations

def build_summary_record(file_name, api_result):
    return {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "file_name": file_name,
        "person_count": api_result.get("worker_count", 0),
        "helmet_count": api_result.get("helmet", 0),
        "vest_count": api_result.get("vest", 0),
        "no_helmet_count": api_result.get("no_helmet", 0),
        "no_vest_count": api_result.get("no_vest", 0),
        "risk_level": api_result.get("risk_level", "Bilinmiyor")
    }

def append_to_log(record, log_file=LOG_FILE):
    df_new = pd.DataFrame([record])

    if os.path.exists(log_file):
        df_old = pd.read_csv(log_file)
        df_all = pd.concat([df_old, df_new], ignore_index=True)
    else:
        df_all = df_new

    df_all.to_csv(log_file, index=False)
    return df_all

def load_log(log_file=LOG_FILE):
    if os.path.exists(log_file):
        return pd.read_csv(log_file)
    return pd.DataFrame(columns=[
        "timestamp",
        "file_name",
        "person_count",
        "helmet_count",
        "vest_count",
        "no_helmet_count",
        "no_vest_count",
        "risk_level"
    ])

st.title("🏗️ AI Construction Safety Monitor")
st.caption("Şantiye güvenliği için yapay zeka destekli PPE izleme paneli")

st.markdown("---")
st.subheader("🎥 Video Analizi")

video_file = st.file_uploader(
    "Video yükleyin",
    type=["mp4", "avi"]
)

if video_file is not None:
    os.makedirs("sample_data", exist_ok=True)
    video_path = os.path.join("sample_data", video_file.name)

    with open(video_path, "wb") as f:
        f.write(video_file.read())

    st.video(video_path)

    if st.button("Videoyu Analiz Et"):
        try:
            with st.spinner("Video analiz ediliyor... Bu işlem biraz sürebilir."):
                with open(video_path, "rb") as vf:
                    files = {
                        "file": (video_file.name, vf, video_file.type)
                    }

                    response = requests.post(
                        f"{API_BASE_URL}/analyze-video",
                        files=files,
                        timeout=300
                    )

                data = response.json()

            if "error" in data:
                st.error(f"Video analiz hatası: {data['error']}")
            else:
                st.success("Video analizi tamamlandı")

                st.subheader("📊 Video Analiz Özeti")

                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Toplam Frame", data.get("total_frames", 0))
                    st.metric("İşlenen Frame", data.get("processed_frames", 0))
                    st.metric("Frame Skip", data.get("frame_skip", 0))

                with col2:
                    st.metric("Toplam Baretsiz", data.get("total_no_helmet", 0))
                    st.metric("Toplam Yeleksiz", data.get("total_no_vest", 0))
                    st.metric("En Kötü Frame", data.get("worst_frame_index", -1))

                with col3:
                    st.metric("Ortalama Güvenlik Skoru", data.get("average_safety_score", 100))
                    st.metric("Risk Seviyesi", data.get("risk_level", "Bilinmiyor"))
                    st.metric("En Düşük Skor", data.get("worst_score", 100))

                st.subheader("🚨 Video Uyarıları")
                for alert in data.get("alerts", []):
                    st.warning(alert)

                st.subheader("🎬 İşlenmiş Video")
                output_video_path = data.get("output_video")

                if output_video_path and os.path.exists(output_video_path):
                    st.video(output_video_path)

                    with open(output_video_path, "rb") as video_out:
                        st.download_button(
                            label="İşlenmiş Videoyu İndir",
                            data=video_out,
                            file_name=os.path.basename(output_video_path),
                            mime="video/mp4"
                        )
                else:
                    st.warning("İşlenmiş video bulunamadı.")
        except Exception as e:
            st.error(f"Video analiz API bağlantı hatası: {e}")

uploaded_file = st.file_uploader(
    "Bir şantiye görseli yükleyin",
    type=["jpg", "jpeg", "png"]
)

if uploaded_file is not None:
    os.makedirs("sample_data", exist_ok=True)
    image_path = os.path.join("sample_data", uploaded_file.name)

    with open(image_path, "wb") as f:
        f.write(uploaded_file.read())

    st.subheader("Analiz İşlemi")

    if st.button("API ile Analiz Et"):
        try:
            with st.spinner("Görsel API üzerinden analiz ediliyor..."):
                with open(image_path, "rb") as img_file:
                    files = {
                        "file": (uploaded_file.name, img_file, uploaded_file.type)
                    }

                    response = requests.post(
                        f"{API_BASE_URL}/analyze",
                        files=files,
                        timeout=60
                    )

                data = response.json()
                st.write("API'den gelen veri:", data)

            if "error" in data:
                st.error(f"API hata döndürdü: {data['error']}")
            else:
                st.session_state.api_result = data
                st.success("Analiz tamamlandı.")

        except Exception as e:
            st.error(f"API analiz hatası: {e}")

    if "api_result" in st.session_state:
        api_result = st.session_state.api_result

        risk_value = api_result.get("risk_level", api_result.get("risk", "Bilinmiyor"))
        status_badge = get_status_badge(risk_value)
        recommendations = get_recommendations(api_result)

        summary_record = build_summary_record(
            uploaded_file.name,
            api_result
        )

        if "last_record" not in st.session_state:
            st.session_state.last_record = None

        st.subheader("🚨 Sistem Uyarısı")

        if risk_value == "HIGH":
            st.error("Kritik güvenlik ihlali tespit edildi.")
        elif risk_value == "MEDIUM":
            st.warning("Orta seviyede güvenlik riski tespit edildi.")
        else:
            st.success("Saha güvenlik durumu iyi görünüyor.")

        st.subheader("Genel Durum")
        st.info(f"Durum: {status_badge} | Risk Seviyesi: {api_result['risk_level']}")

        col_left, col_right = st.columns([1.3, 1])

        with col_left:
            st.subheader("Yüklenen Görsel")
            st.image(image_path, caption="Orijinal Görsel", use_container_width=True)

            st.subheader("Model Çıktısı")
            st.image(
                api_result["output_image"],
                caption="Tespit Sonucu",
                use_container_width=True
            )

        with col_right:
            st.subheader("Analiz Özeti")

            metric_col1, metric_col2 = st.columns(2)
            with metric_col1:
                st.metric("Çalışan Sayısı", api_result.get("worker_count", 0))
                st.metric("Baret Sayısı", api_result.get("helmet", 0))
                st.metric("Yelek Sayısı", api_result.get("vest", 0))

                st.metric("Baretsiz Çalışan", api_result.get("no_helmet", 0))
                st.metric("Yeleksiz Çalışan", api_result.get("no_vest", 0))
                st.metric("Risk Seviyesi", api_result.get("risk_level", "Bilinmiyor"))

            st.subheader("Uyarılar")
            for alert in api_result.get("alerts", []):
                st.warning(alert)

            st.subheader("Önerilen Aksiyonlar")
            for rec in recommendations:
                st.write(f"- {rec}")

        st.markdown("---")

        st.subheader("Tespit Detayları")

        if api_result.get("boxes"):
            df_boxes = pd.DataFrame(api_result["boxes"])
            df_boxes["conf"] = df_boxes["conf"].round(3)

            st.dataframe(
                df_boxes[["class", "conf", "x1", "y1", "x2", "y2"]],
                use_container_width=True
            )
        else:
            st.info("Herhangi bir nesne tespit edilmedi.")

        st.markdown("---")

        st.subheader("Analiz Kaydı ve Rapor")

        summary_df = pd.DataFrame([summary_record])
        st.dataframe(summary_df, use_container_width=True)

        csv_bytes = summary_df.to_csv(index=False).encode("utf-8-sig")
        st.download_button(
            label="Bu Analizi CSV Olarak İndir",
            data=csv_bytes,
            file_name=f"analysis_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )

        if st.button("Analizi İhlal Geçmişine Kaydet"):
            all_logs = append_to_log(summary_record)
            st.session_state.last_record = summary_record
            st.success("Analiz kaydı violation_log.csv dosyasına eklendi.")

else:
    st.info("Başlamak için bir şantiye görseli yükleyin.")

    st.subheader("Bu uygulama ne yapar?")
    st.write("""
    Bu sistem, yüklenen şantiye görselleri üzerinde:
    - çalışan tespiti yapar,
    - baret ve yelek kullanımını analiz eder,
    - eksik KKE durumlarını belirler,
    - risk seviyesini hesaplar,
    - güvenlik aksiyonları önerir,
    - analiz sonuçlarını CSV raporu olarak indirmenizi sağlar.
    """)

    
st.markdown("---")
st.subheader("📈 İhlal Geçmişi ve Trend Analizi")

log_df = load_log()

def prepare_log_charts(log_df):
    if log_df.empty:
        return log_df, pd.DataFrame(), pd.DataFrame()

    chart_df = log_df.copy()
    chart_df["timestamp"] = pd.to_datetime(chart_df["timestamp"], errors="coerce")
    chart_df = chart_df.dropna(subset=["timestamp"])
    chart_df = chart_df.sort_values("timestamp")

    risk_counts = (
        chart_df["risk_level"]
        .value_counts()
        .rename_axis("risk_level")
        .reset_index(name="count")
    )

    return chart_df, risk_counts

if not log_df.empty:
    chart_df, risk_counts = prepare_log_charts(log_df)

    st.subheader("📌 Genel İstatistikler")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Toplam Analiz Sayısı", len(chart_df))
    with col2:
        st.metric("Ortalama Çalışan Sayısı", round(chart_df["person_count"].mean(), 2))
    with col3:
        st.metric("Ortalama Baretsiz Sayısı", round(chart_df["no_helmet_count"].mean(), 2))

    col4, col5, col6 = st.columns(3)
    with col4:
        st.metric("Ortalama Yeleksiz Sayısı", round(chart_df["no_vest_count"].mean(), 2))
    with col5:
        st.metric("En Son Risk Seviyesi", chart_df.iloc[-1]["risk_level"])
    with col6:
        st.metric("Maksimum Çalışan Sayısı", int(chart_df["person_count"].max()))

    st.markdown("---")

    st.subheader("⛑️ KKE İhlal Trendleri")
    trend_df = chart_df.set_index("timestamp")[["no_helmet_count", "no_vest_count"]]
    st.line_chart(trend_df)

    st.subheader("👷 Çalışan ve KKE Sayıları")
    count_df = chart_df.set_index("timestamp")[["person_count", "helmet_count", "vest_count"]]
    st.line_chart(count_df)

    st.subheader("🚨 Risk Seviyesi Dağılımı")
    risk_chart_df = risk_counts.set_index("risk_level")
    st.bar_chart(risk_chart_df)

    st.subheader("🕒 Son Analizler")
    st.dataframe(
        chart_df.sort_values("timestamp", ascending=False),
        use_container_width=True
    )

    log_csv = chart_df.to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        label="Tüm İhlal Geçmişini CSV Olarak İndir",
        data=log_csv,
        file_name="violation_log.csv",
        mime="text/csv"
    )
else:
    st.info("Henüz kayıtlı ihlal geçmişi bulunmuyor.")



    
    

st.subheader("API Bağlantı Testi")

if st.button("API durumunu kontrol et"):
    try:
        response = requests.get(
        f"{API_BASE_URL}/status",
        timeout=10
        )
        data = response.json()

        st.success("API bağlantısı başarılı")
        st.json(data)

    except Exception as e:
        st.error(f"API bağlantı hatası: {e}")