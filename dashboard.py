import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Konfigurasi halaman
st.set_page_config(
    page_title="Dashboard Kualitas Udara Beijing",
    page_icon="🌫️",
    layout="wide"
)

# Gaya visual
sns.set_style("whitegrid")

@st.cache_data
def load_data():
    df = pd.read_csv('dashboard/main_data.csv')
    return df

df = load_data()

with st.sidebar:
    st.title("🌫️ Air Quality Beijing")
    st.markdown("**Nama:** Diandra Puspo Negoro")
    st.markdown("---")
    st.header("⚙️ Filter Data")

    # Filter Tahun
    selected_years = st.multiselect(
        "📅 Pilih Tahun",
        options=sorted(df['year'].unique().tolist()),
        default=sorted(df['year'].unique().tolist())
    )

    # Filter Stasiun
    selected_stations = st.multiselect(
        "📍 Pilih Stasiun",
        options=sorted(df['station'].unique().tolist()),
        default=sorted(df['station'].unique().tolist())
    )

# Terapkan filter
filtered_df = df[
    (df['year'].isin(selected_years)) &
    (df['station'].isin(selected_stations))
]

# --- JUDUL UTAMA ---
st.title("🌫️ Dashboard Kualitas Udara Beijing")
st.markdown("Gunakan filter di sidebar untuk menjelajahi pola kualitas udara berdasarkan stasiun dan tahun.")
st.markdown("---")

# --- METRIK RINGKASAN ---
if not filtered_df.empty:
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("📊 Rata-rata PM2.5", f"{filtered_df['PM2.5'].mean():.1f} µg/m³")
    col2.metric("💨 Rata-rata Kec. Angin", f"{filtered_df['WSPM'].mean():.1f} m/s")
    col3.metric("🌡️ Rata-rata Suhu", f"{filtered_df['TEMP'].mean():.1f} °C")
    col4.metric("📍 Jumlah Stasiun", f"{filtered_df['station'].nunique()}")
    st.markdown("---")


if filtered_df.empty:
    st.warning("⚠️ Tidak ada data untuk filter yang dipilih. Silakan ubah pilihan filter Anda.")
else:
    tab1, tab2, tab3 = st.tabs([
        "📈 Tren PM2.5",
        "🌤️ Pengaruh Cuaca",
        "📍 Pengelompokan Stasiun"
    ])


with tab1:
        st.header("Tren Konsentrasi PM2.5 dari 2013 hingga 2017")

        # Tren Tahunan
        yearly_avg = filtered_df.groupby('year')['PM2.5'].mean().reset_index()

        fig, ax = plt.subplots(figsize=(10, 5))
        ax.plot(yearly_avg['year'], yearly_avg['PM2.5'],
                marker='o', linewidth=2.5, color=PRIMARY_COLOR,
                markerfacecolor='white', markeredgewidth=2)

        for _, row in yearly_avg.iterrows():
            ax.annotate(f"{row['PM2.5']:.1f}",
                        xy=(row['year'], row['PM2.5']),
                        xytext=(0, 10), textcoords='offset points',
                        ha='center', fontsize=10, fontweight='bold')

        ax.axhline(15, color=ACCENT_COLOR_DARK, linestyle='--', linewidth=1.5, label='Batas Aman WHO (15 µg/m³)')
        ax.set_title('Rata-rata PM2.5 per Tahun', fontsize=16, fontweight='bold', pad=20)
        ax.set_xlabel('Tahun', fontsize=12)
        ax.set_ylabel('Rata-rata PM2.5 (µg/m³)', fontsize=12)
        ax.legend(fontsize=10)
        st.pyplot(fig)
        plt.close(fig)

        st.markdown("---")

        # Tren Bulanan
        st.subheader("Pola Musiman PM2.5 per Bulan")
        monthly_avg = filtered_df.groupby('month')['PM2.5'].mean().reset_index()
        bulan_label = ['Jan','Feb','Mar','Apr','Mei','Jun','Jul','Agu','Sep','Okt','Nov','Des']

        fig, ax = plt.subplots(figsize=(12, 5))
        bars = ax.bar(monthly_avg['month'], monthly_avg['PM2.5'],
                      color=PRIMARY_COLOR, edgecolor='white')

        # Warnai bulan tertinggi dan terendah
        idx_max = monthly_avg['PM2.5'].idxmax()
        idx_min = monthly_avg['PM2.5'].idxmin()
        bars[idx_max].set_color(ACCENT_COLOR_DARK)
        bars[idx_min].set_color(ACCENT_COLOR_LIGHT)

        ax.set_title('Rata-rata PM2.5 per Bulan', fontsize=16, fontweight='bold', pad=20)
        ax.set_xlabel('Bulan', fontsize=12)
        ax.set_ylabel('Rata-rata PM2.5 (µg/m³)', fontsize=12)
        ax.set_xticks(monthly_avg['month'])
        ax.set_xticklabels(bulan_label)
        ax.grid(axis='y', linestyle='--', alpha=0.7)

        legend_elem = [
            Patch(facecolor=ACCENT_COLOR_DARK, label='Bulan Terburuk'),
            Patch(facecolor=ACCENT_COLOR_LIGHT, label='Bulan Terbaik')
        ]
        ax.legend(handles=legend_elem, fontsize=10)
        st.pyplot(fig)
        plt.close(fig)

        st.markdown("---")

        # Tren Harian (per jam)
        st.subheader("Pola PM2.5 Sepanjang Hari")
        hourly_avg = filtered_df.groupby('hour')['PM2.5'].mean().reset_index()

        fig, ax = plt.subplots(figsize=(12, 5))
        ax.fill_between(hourly_avg['hour'], hourly_avg['PM2.5'], alpha=0.2, color=PRIMARY_COLOR)
        ax.plot(hourly_avg['hour'], hourly_avg['PM2.5'],
                marker='o', linewidth=2, color=PRIMARY_COLOR,
                markerfacecolor='white', markeredgewidth=2, markersize=5)

        idx_max = hourly_avg['PM2.5'].idxmax()
        idx_min = hourly_avg['PM2.5'].idxmin()
        ax.scatter(hourly_avg['hour'][idx_max], hourly_avg['PM2.5'][idx_max],
                   color=ACCENT_COLOR_DARK, s=120, zorder=5, label=f"Tertinggi Jam {hourly_avg['hour'][idx_max]:02d}:00")
        ax.scatter(hourly_avg['hour'][idx_min], hourly_avg['PM2.5'][idx_min],
                   color=ACCENT_COLOR_LIGHT, s=120, zorder=5, label=f"Terendah Jam {hourly_avg['hour'][idx_min]:02d}:00")

        ax.set_title('Rata-rata PM2.5 per Jam dalam Sehari', fontsize=16, fontweight='bold', pad=20)
        ax.set_xlabel('Jam', fontsize=12)
        ax.set_ylabel('Rata-rata PM2.5 (µg/m³)', fontsize=12)
        ax.set_xticks(range(24))
        ax.legend(fontsize=10)
        ax.grid(axis='y', linestyle='--', alpha=0.7)
        st.pyplot(fig)
        plt.close(fig)

        st.info("""
        **Insight:**
        - PM2.5 mengalami fluktuasi antar tahun dan **belum stabil** meskipun sempat membaik di 2016.
        - Polusi paling parah terjadi di **bulan November–Desember** karena kondisi atmosfer musim dingin.
        - Puncak harian terjadi pada **malam hari (sekitar jam 22:00)** karena dispersi polutan yang terhambat.
        """)

        with st.expander("Lihat Data Detail"):
            st.dataframe(yearly_avg.rename(columns={'year': 'Tahun', 'PM2.5': 'Rata-rata PM2.5'}))

with tab2:
        st.header("Pengaruh Kondisi Cuaca terhadap Konsentrasi PM2.5")

        # Heatmap Korelasi
        st.subheader("Korelasi Variabel Cuaca dengan PM2.5")

        corr_cols = ['PM2.5', 'TEMP', 'PRES', 'DEWP', 'RAIN', 'WSPM']
        corr_matrix = filtered_df[corr_cols].corr()
        corr_labels = ['PM2.5', 'Suhu\n(TEMP)', 'Tekanan\n(PRES)',
                       'Dew Point\n(DEWP)', 'Hujan\n(RAIN)', 'Kec.Angin\n(WSPM)']

        mask = np.zeros_like(corr_matrix, dtype=bool)
        mask[np.triu_indices_from(mask)] = True

        fig, ax = plt.subplots(figsize=(8, 6))
        sns.heatmap(corr_matrix, annot=True, fmt='.3f',
                    cmap='RdBu_r', center=0, vmin=-1, vmax=1,
                    xticklabels=corr_labels, yticklabels=corr_labels,
                    linewidths=0.5, ax=ax, mask=mask, annot_kws={'size': 9})
        ax.set_title('Heatmap Korelasi Variabel Cuaca vs PM2.5',
                     fontsize=14, fontweight='bold', pad=20)
        st.pyplot(fig)
        plt.close(fig)

        st.markdown("---")

        # PM2.5 per Kecepatan Angin
        st.subheader("Rata-rata PM2.5 Berdasarkan Kecepatan Angin")

        def kategorikan_angin(wspm):
            if wspm <= 1:
                return 'Calm\n(0-1 m/s)'
            elif wspm <= 2:
                return 'Light\n(1-2 m/s)'
            elif wspm <= 4:
                return 'Moderate\n(2-4 m/s)'
            else:
                return 'Strong\n(>4 m/s)'

        wind_df = filtered_df.copy()
        wind_df['kategori_angin'] = wind_df['WSPM'].apply(kategorikan_angin)

        order = ['Calm\n(0-1 m/s)', 'Light\n(1-2 m/s)', 'Moderate\n(2-4 m/s)', 'Strong\n(>4 m/s)']
        wspm_mean = wind_df.groupby('kategori_angin')['PM2.5'].mean().reindex(order)

        colors_wind = [ACCENT_COLOR_DARK, SECONDARY_COLOR, PRIMARY_COLOR, ACCENT_COLOR_LIGHT]

        fig, ax = plt.subplots(figsize=(10, 5))
        bars = ax.bar(wspm_mean.index, wspm_mean.values,
                      color=colors_wind, edgecolor='white', width=0.55)

        for bar, val in zip(bars, wspm_mean.values):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                    f'{val:.1f}', ha='center', va='bottom',
                    fontsize=11, fontweight='bold')

        ax.set_title('Rata-rata PM2.5 Berdasarkan Kecepatan Angin',
                     fontsize=14, fontweight='bold', pad=20)
        ax.set_xlabel('Kategori Kecepatan Angin', fontsize=12)
        ax.set_ylabel('Rata-rata PM2.5 (µg/m³)', fontsize=12)
        ax.grid(axis='y', linestyle='--', alpha=0.7)
        st.pyplot(fig)
        plt.close(fig)

        st.markdown("---")

        # PM2.5 per Arah Angin
        st.subheader("Rata-rata PM2.5 Berdasarkan Arah Angin")

        wind_dir_mean = filtered_df.groupby('wd')['PM2.5'].mean().reset_index()
        wind_dir_mean.columns = ['Arah Angin', 'Rata-rata PM2.5']
        wind_dir_mean = wind_dir_mean.sort_values('Rata-rata PM2.5', ascending=True)

        colors_wd = [ACCENT_COLOR_LIGHT if v < 70 else (SECONDARY_COLOR if v < 90 else ACCENT_COLOR_DARK)
                     for v in wind_dir_mean['Rata-rata PM2.5']]

        fig, ax = plt.subplots(figsize=(10, 6))
        ax.barh(wind_dir_mean['Arah Angin'], wind_dir_mean['Rata-rata PM2.5'],
                color=colors_wd, edgecolor='white', height=0.7)

        for i, val in enumerate(wind_dir_mean['Rata-rata PM2.5']):
            ax.text(val + 0.5, i, f'{val:.1f}', va='center', fontsize=9)

        ax.axvline(x=filtered_df['PM2.5'].mean(), color='gray',
                   linestyle='--', linewidth=1.2, alpha=0.7, label='Rata-rata Keseluruhan')

        legend_elem = [
            Patch(facecolor=ACCENT_COLOR_DARK, label='Tinggi (>90)'),
            Patch(facecolor=SECONDARY_COLOR, label='Sedang (70-90)'),
            Patch(facecolor=ACCENT_COLOR_LIGHT, label='Rendah (<70)')
        ]
        ax.legend(handles=legend_elem, fontsize=9, loc='lower right')
        ax.set_title('Rata-rata PM2.5 Berdasarkan Arah Angin',
                     fontsize=14, fontweight='bold', pad=20)
        ax.set_xlabel('Rata-rata PM2.5 (µg/m³)', fontsize=12)
        ax.set_ylabel('Arah Angin', fontsize=12)
        ax.grid(axis='x', linestyle='--', alpha=0.7)
        st.pyplot(fig)
        plt.close(fig)

        st.info("""
        **Insight:**
        - Kecepatan angin adalah faktor cuaca paling dominan (korelasi -0.27). Semakin kencang angin, semakin rendah PM2.5.
        - Angin dari arah timur-tenggara (ESE, SE) membawa PM2.5 tertinggi karena berasal dari kawasan industri.
        - Angin dari barat laut (WNW, NW, NNW) membawa udara paling bersih karena berasal dari dataran tinggi Mongolia.
        - Curah hujan hampir tidak berpengaruh signifikan terhadap konsentrasi PM2.5.
        """)

        with st.expander("Lihat Data Detail"):
            st.dataframe(wind_dir_mean.reset_index(drop=True))

with tab3:
        st.header("Pengelompokan Stasiun Berdasarkan Profil Polusi")

        # Profil rata-rata per stasiun
        station_profile = filtered_df.groupby('station').agg(
            PM2_5 = ('PM2.5', 'mean'),
            PM10  = ('PM10',  'mean'),
            NO2   = ('NO2',   'mean'),
            CO    = ('CO',    'mean'),
            WSPM  = ('WSPM',  'mean')
        ).round(2).reset_index()

        # Binning manual
        bins   = [0, 75, 82, 999]
        labels = ['Polusi Rendah', 'Polusi Sedang', 'Polusi Tinggi']
        station_profile['Kelompok'] = pd.cut(station_profile['PM2_5'], bins=bins, labels=labels)

        kelompok_colors = {
            'Polusi Rendah' : ACCENT_COLOR_LIGHT,
            'Polusi Sedang' : SECONDARY_COLOR,
            'Polusi Tinggi' : ACCENT_COLOR_DARK
        }

        # Metrik ringkasan per kelompok
        col1, col2, col3 = st.columns(3)
        for col, label in zip([col1, col2, col3], labels):
            group = station_profile[station_profile['Kelompok'] == label]
            col.metric(
                label,
                f"{len(group)} Stasiun",
                f"Rata-rata PM2.5: {group['PM2_5'].mean():.1f} µg/m³"
            )

        st.markdown("---")

        # Bar chart PM2.5 per stasiun
        st.subheader("Rata-rata PM2.5 per Stasiun")

        station_sorted = station_profile.sort_values('PM2_5', ascending=True)
        colors_bar = [kelompok_colors[str(k)] for k in station_sorted['Kelompok']]

        fig, ax = plt.subplots(figsize=(10, 6))
        bars = ax.barh(station_sorted['station'], station_sorted['PM2_5'],
                       color=colors_bar, edgecolor='white', height=0.7)

        for bar, val in zip(bars, station_sorted['PM2_5']):
            ax.text(val + 0.3, bar.get_y() + bar.get_height()/2,
                    f'{val:.1f}', ha='left', va='center', fontsize=9)

        ax.axvline(x=station_profile['PM2_5'].mean(), color='gray',
                   linestyle='--', linewidth=1.2, alpha=0.7, label='Rata-rata Keseluruhan')

        legend_elem = [Patch(facecolor=c, label=l) for l, c in kelompok_colors.items()]
        ax.legend(handles=legend_elem, fontsize=9, loc='lower right')

        ax.set_title('Rata-rata PM2.5 per Stasiun', fontsize=14, fontweight='bold', pad=20)
        ax.set_xlabel('Rata-rata PM2.5 (µg/m³)', fontsize=12)
        ax.set_ylabel('Stasiun', fontsize=12)
        ax.grid(axis='x', linestyle='--', alpha=0.7)
        st.pyplot(fig)
        plt.close(fig)

        st.markdown("---")

        # Grouped bar chart perbandingan polutan per kelompok
        st.subheader("Perbandingan Polutan per Kelompok Stasiun")

        summary = station_profile.groupby('Kelompok', observed=True).agg(
            PM2_5 = ('PM2_5', 'mean'),
            NO2   = ('NO2',   'mean'),
            CO    = ('CO',    'mean')
        ).round(2)

        polutan_labels = ['PM2.5', 'NO2', 'CO (dibagi 10)']
        x = np.arange(len(polutan_labels))
        width = 0.25

        fig, ax = plt.subplots(figsize=(10, 5))
        for i, (kelompok, color) in enumerate(kelompok_colors.items()):
            if kelompok not in summary.index:
                continue
            vals = [
                summary.loc[kelompok, 'PM2_5'],
                summary.loc[kelompok, 'NO2'],
                summary.loc[kelompok, 'CO'] / 10
            ]
            ax.bar(x + i * width, vals, width,
                   label=kelompok, color=color, edgecolor='white')

        ax.set_title('Perbandingan Polutan per Kelompok Stasiun',
                     fontsize=14, fontweight='bold', pad=20)
        ax.set_xlabel('Polutan', fontsize=12)
        ax.set_ylabel('Nilai Rata-rata', fontsize=12)
        ax.set_xticks(x + width)
        ax.set_xticklabels(polutan_labels)
        ax.legend(fontsize=9)
        ax.grid(axis='y', linestyle='--', alpha=0.7)
        st.pyplot(fig)
        plt.close(fig)

        st.info("""
        **Insight:**
        - Stasiun dibagi menjadi 3 kelompok berdasarkan rata-rata PM2.5.
        - Polusi rendah: Changping, Huairou, Dingling — berada di pinggiran kota dengan aktivitas industri minimal.
        - Polusi sedang: Shunyi — zona transisi antara pusat dan pinggiran kota.
        - Polusi tinggi: Dongsi, Wanshouxigong, Nongzhanguan, dan lainnya — berada di pusat kota dengan emisi kendaraan dan industri tinggi.
        """)

        with st.expander("Lihat Data Detail"):
            st.dataframe(station_profile[['station', 'PM2_5', 'NO2', 'CO', 'WSPM', 'Kelompok']]
                         .sort_values('PM2_5', ascending=False)
                         .reset_index(drop=True))
            
# --- FOOTER ---
st.markdown("---")
st.caption("2024 | Dibuat oleh Diandra Puspo Negoro | Proyek Akhir Analisis Data Dicoding")