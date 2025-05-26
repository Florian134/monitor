#Start der Anwendung: streamlit run DATA-Interpreter.py

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt
from io import BytesIO
from fpdf import FPDF

st.set_page_config(page_title="RM - Online Projekt Management - JIRA Data Interpreter", layout="wide")
st.title("🚀 RM - Online Projekt Management")

# --- CSV Import oder Mockdaten ---
st.sidebar.header("📂 Datenquelle")
uploaded_file = st.sidebar.file_uploader("Lade eine CSV-Datei hoch", type="csv")

def generate_mock_data(n=150):
    np.random.seed(42)
    today = datetime.today()
    mitarbeiter = ['Lucas', 'Florian', 'Simon', 'Jana']
    sprints = ['Sprint 1', 'Sprint 2', 'Sprint 3']
    kunden = {'Alpha': 'KSTA', 'Beta': 'BASEL', 'Gamma': 'OVB'}
    typ = ['Bug', 'Feature', 'Improvement']

    df = pd.DataFrame({
        'projekt': np.random.choice(list(kunden.keys()), n),
        'verantwortlich': np.random.choice(mitarbeiter, n),
        'sprint': np.random.choice(sprints, n),
        'typ': np.random.choice(typ, n),
        'status': np.random.choice(['Offen', 'In Arbeit', 'Erledigt'], n, p=[0.2, 0.3, 0.5]),
        'story_points': np.random.choice([1, 2, 3, 5, 8, 13], n),
        'milestone': np.random.choice(['M1', 'M2', 'M3'], n),
        'wartezeit': np.random.randint(0, 5, n),
        'arbeitszeit': np.random.randint(1, 8, n),
        'erstellt': [today - timedelta(days=np.random.randint(10, 40)) for _ in range(n)],
        'faelligkeit': [today + timedelta(days=np.random.randint(-5, 10)) for _ in range(n)],
    })

    df['abgeschlossen'] = df.apply(lambda x: x['erstellt'] + timedelta(days=x['wartezeit'] + x['arbeitszeit']) if x['status'] == 'Erledigt' else pd.NaT, axis=1)
    df['kunde'] = df['projekt'].map(kunden)
    df['verzoegerung'] = (df['abgeschlossen'] - df['faelligkeit']).dt.days.fillna(0)
    df['verzoegerung'] = df['verzoegerung'].apply(lambda x: x if x > 0 else 0)

    for kunde, faktor in zip(['Kunde A', 'Kunde B', 'Kunde C'], [1, 2, 3]):
        df.loc[df['kunde'] == kunde, 'verzoegerung'] += np.random.poisson(faktor, df[df['kunde'] == kunde].shape[0])

    return df

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    if 'verzoegerung' not in df.columns:
        st.error("❌ Die CSV-Datei enthält keine Spalte 'verzoegerung'. Bitte prüfen.")
        st.stop()
else:
    df = generate_mock_data()

# --- Filter ---
st.sidebar.header("🔎 Filter")
proj = st.sidebar.multiselect("Projekt(e)", df['projekt'].unique(), default=list(df['projekt'].unique()))
sprint = st.sidebar.multiselect("Sprint(s)", df['sprint'].unique(), default=list(df['sprint'].unique()))
mitarbeiter = st.sidebar.multiselect("Verantwortlich", df['verantwortlich'].unique(), default=list(df['verantwortlich'].unique()))

df = df[df['projekt'].isin(proj) & df['sprint'].isin(sprint) & df['verantwortlich'].isin(mitarbeiter)]

st.subheader("📈 Sprint-Zusammensetzung nach Aufgabentyp")
comp = df[df['status'] == 'Erledigt'].groupby(['sprint', 'typ']).size().reset_index(name='anzahl')
fig_comp = px.bar(comp, x='typ', y='anzahl', color='sprint', barmode='group', title='Zusammensetzung: Aufgabentypen je Sprint')
st.plotly_chart(fig_comp, use_container_width=True)

st.subheader("🥧 Kundenaufwände je Sprint (Anteil)")
for s in df['sprint'].unique():
    st.markdown(f"#### {s}")
    data = df[df['sprint'] == s].groupby('kunde')['arbeitszeit'].sum().reset_index()
    fig = px.pie(data, names='kunde', values='arbeitszeit', title=f'Kundenanteile in {s}')
    st.plotly_chart(fig, use_container_width=True)

st.subheader("📶 Meilenstein-Zeitbedarf pro Sprint")
milestone = df[df['status'] == 'Erledigt'].groupby(['sprint', 'milestone'])['arbeitszeit'].sum().reset_index()
fig_milestone = px.bar(milestone, x='milestone', y='arbeitszeit', color='sprint', barmode='stack', title='Zeit je Meilenstein')
st.plotly_chart(fig_milestone, use_container_width=True)

st.subheader("📊 Einfluss der Kunden auf Projektverzögerung")

x = pd.get_dummies(df['kunde'], drop_first=True)
y = df['verzoegerung'] * 8  # Stunden
model = LinearRegression().fit(x, y)
predicted = model.predict(x)

st.markdown("**Lineare Regressionsergebnisse (Einfluss je Kunde auf Verzögerung):**")
for i, name in enumerate(x.columns):
    st.write(f"{name}: {model.coef_[i]:.2f} Stunden Einfluss")

df['PVZ'] = predicted

df['gesamtzeit'] = df['arbeitszeit'] + df['wartezeit']
df['PVZ_prozent'] = df.apply(lambda row: min(100, row['PVZ'] / (row['gesamtzeit'] * 8) * 100) if row['gesamtzeit'] > 0 else 0, axis=1)

verz = df.groupby(['sprint', 'kunde'])[['PVZ', 'PVZ_prozent']].mean().reset_index()
fig_pvz = px.bar(verz, x='sprint', y='PVZ', color='kunde', text='kunde', barmode='group',
                 title='⏱️ Durchschnittliche Projektverzögerung (PVZ) pro Sprint',
                 labels={'PVZ': 'Verzögerung (Stunden)'})
fig_pvz.update_traces(textposition='outside')
st.plotly_chart(fig_pvz, use_container_width=True)

st.markdown("**📌 Projektverzögerungsvariable (PVZ):** PVZ beschreibt den Einfluss des Kunden auf die durchschnittliche Verzögerung eines Sprints, gemessen in Arbeitsstunden. Zusätzlich wird ihr Anteil an der Gesamtzeit als Prozentwert angegeben.")

st.subheader("📊 Storypoints nach Typ je Sprint")
story = df[df['status'] == 'Erledigt'].groupby(['sprint', 'typ'])['story_points'].sum().reset_index()
fig_story = px.bar(story, x='sprint', y='story_points', color='typ', barmode='stack',
                   title='🎯 Erledigte Storypoints je Sprint & Typ',
                   labels={'story_points': 'Storypoints'})
st.plotly_chart(fig_story, use_container_width=True)

st.subheader("📋 Datenübersicht")
st.dataframe(df)

st.download_button("💾 CSV Export", df.to_csv(index=False).encode('utf-8'), "sprint_daten.csv")

# 📤 PDF-Export für Marketingdiagramm
if st.button("📸 Exportiere Marketing-Chart als PDF"):
    fig_story.update_layout(title_font_size=24)
    img_bytes = fig_story.to_image(format="png")
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "Sprint Leistung: Storypoints (Marketingübersicht)", ln=True)
    tmp_file = BytesIO(img_bytes)
    with open("storypoints_chart.png", "wb") as f:
        f.write(tmp_file.read())
    pdf.image("storypoints_chart.png", x=10, y=30, w=180)
    pdf_output = BytesIO()
    pdf.output(pdf_output)
    st.download_button(label="📥 Marketing PDF herunterladen", data=pdf_output.getvalue(), file_name="marketing_sprint_leistung.pdf", mime="application/pdf")
    st.success(" PDF erfolgreich erstellt!")


    # --- Infos fuer den PIP-Installer-> Modul	Funktion im Code	Installation mit pip
#streamlit	Interaktive Web-App	pip install streamlit
#pandas	Datenverarbeitung	pip install pandas
#numpy	Zufallszahlen & Arrays	pip install numpy
#plotly	Interaktive Diagramme	pip install plotly
#scikit-learn (sklearn)	Lineare Regression	pip install scikit-learn
#matplotlib	(Für PDF: ggf. Diagrammtools)	pip install matplotlib
#fpdf	PDF-Erzeugung	pip install fpdf