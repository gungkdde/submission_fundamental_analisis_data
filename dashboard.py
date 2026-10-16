import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

# Mengatur tema seaborn
sns.set_theme(style="darkgrid")

# ==============================
# 1. Menyiapkan Data (Load & Clean)
# ==============================
@st.cache_data
def load_data():
    # Load data
    day_df = pd.read_csv("day.csv")
    hour_df = pd.read_csv("hour.csv")
    
    # Clean data (Sesuai dengan di Notebook)
    day_df["dteday"] = pd.to_datetime(day_df["dteday"])
    hour_df["dteday"] = pd.to_datetime(hour_df["dteday"])
    
    season_mapping = {1: "Spring", 2: "Summer", 3: "Fall", 4: "Winter"}
    weather_mapping = {1: "Clear/Partly Cloudy", 2: "Misty/Cloudy", 3: "Light Snow/Rain", 4: "Heavy Rain/Ice Pellets"}
    
    day_df["season"] = day_df["season"].map(season_mapping)
    day_df["weathersit"] = day_df["weathersit"].map(weather_mapping)
    
    # Analisis Lanjutan: Binning Kategori Waktu
    def categorize_time(hour):
        if 6 <= hour <= 9:
            return 'Morning Rush'
        elif 10 <= hour <= 15:
            return 'Daytime'
        elif 16 <= hour <= 19:
            return 'Evening Rush'
        else:
            return 'Night'
            
    hour_df['time_category'] = hour_df['hr'].apply(categorize_time)
    
    return day_df, hour_df

day_df, hour_df = load_data()

# ==============================
# 2. Membuat Komponen Sidebar
# ==============================
with st.sidebar:
    st.title("🚲 Bike Sharing Analytics")
    st.image("https://raw.githubusercontent.com/dicodingacademy/assets/main/logo.png")
    
    # Filter rentang waktu
    min_date = day_df["dteday"].min()
    max_date = day_df["dteday"].max()
    
    start_date, end_date = st.date_input(
        label='Rentang Waktu',
        min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

# Menyaring data berdasarkan input sidebar
main_day_df = day_df[(day_df["dteday"] >= str(start_date)) & (day_df["dteday"] <= str(end_date))]
main_hour_df = hour_df[(hour_df["dteday"] >= str(start_date)) & (hour_df["dteday"] <= str(end_date))]

# ==============================
# 3. Membuat Konten Utama (Main Page)
# ==============================
st.header("Dashboard Analisis Penyewaan Sepeda")

# Menampilkan metrik utama
col1, col2, col3 = st.columns(3)
with col1:
    total_rentals = main_day_df['cnt'].sum()
    st.metric("Total Penyewaan", value=f"{total_rentals:,}")
with col2:
    total_registered = main_day_df['registered'].sum()
    st.metric("Pengguna Registered", value=f"{total_registered:,}")
with col3:
    total_casual = main_day_df['casual'].sum()
    st.metric("Pengguna Casual", value=f"{total_casual:,}")

st.markdown("---")

# Visualisasi 1: Pola Jam Sibuk
st.subheader("1. Pola Jam Sibuk Penyewaan Sepeda (Casual vs Registered)")
workingday_data = main_hour_df[main_hour_df['workingday'] == 1]
hourly_rentals = workingday_data.groupby('hr')[['casual', 'registered']].mean().reset_index()

fig, ax = plt.subplots(figsize=(12, 6))
ax.plot(hourly_rentals['hr'], hourly_rentals['registered'], label='Registered', marker='o', color='tab:blue')
ax.plot(hourly_rentals['hr'], hourly_rentals['casual'], label='Casual', marker='o', color='tab:orange')
ax.set_xlabel('Jam (0-23)')
ax.set_ylabel('Rata-rata Penyewaan')
ax.set_xticks(range(0, 24))
ax.legend()
st.pyplot(fig)

# Visualisasi 2: Dampak Cuaca (Fall & Winter)
st.subheader("2. Dampak Cuaca Terhadap Penyewaan (Musim Gugur & Dingin)")
weather_season_impact = main_day_df[main_day_df['season'].isin(['Fall', 'Winter'])].groupby(['season', 'weathersit'])['cnt'].mean().reset_index()

fig2, ax2 = plt.subplots(figsize=(10, 6))
sns.barplot(x='season', y='cnt', hue='weathersit', data=weather_season_impact, palette='viridis', ax=ax2)
ax2.set_xlabel('Musim')
ax2.set_ylabel('Rata-rata Penyewaan Harian')
ax2.legend(title='Kondisi Cuaca')
st.pyplot(fig2)

# Visualisasi 3: Analisis Lanjutan (Binning)
st.subheader("3. Analisis Lanjutan: Volume Penyewaan Berdasarkan Kategori Waktu")
time_binned_df = main_hour_df.groupby('time_category')[['cnt']].mean().sort_values(by='cnt', ascending=False).reset_index()

fig3, ax3 = plt.subplots(figsize=(8, 5))
sns.barplot(x='time_category', y='cnt', data=time_binned_df, palette='magma', ax=ax3)
ax3.set_xlabel('Kategori Waktu')
ax3.set_ylabel('Rata-rata Total Penyewaan')
st.pyplot(fig3)

st.caption("Copyright © 2026")