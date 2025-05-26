import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import numpy as np



# --- Um die Anwendung zu starten, verwende den Befel: streamlit run DATA-Interpreter-test.py
st.set_page_config(page_title="RM - Online Projekt Management - JIRA Data Interpreter", layout="wide")
st.title("🚀 RM - Online Projekt Management")
st.markdown("Dieses Dashboard verwendet simulierte Daten, um ein typisches JIRA-Projektmanagement-Szenario zu demonstrieren.")

# --- Simulated Sample Data ---
def generate_mock_jira_data(n=120):
    np.random.seed(42)
    today = datetime.today()
    mitarbeiter = ['Alice', 'Bob', 'Charlie', 'Diana']
    sprints = ['Sprint 1', 'Sprint 2', 'Sprint 3']
    kunden = {'Alpha': 'Kunde A', 'Beta': 'Kunde B', 'Gamma': 'Kunde C'}

    data = {
        'projekt': np.random.choice(['Alpha', 'Beta', 'Gamma'], n),
        'verantwortlich': np.random.choice(mitarbeiter, n),
        'status': np.random.choice(['Offen', 'In Arbeit', 'Erledigt'], n, p=[0.3, 0.3, 0.4]),
        'sprint': np.random.choice(sprints, n),
        'story_points': np.random.choice([1, 2, 3, 5, 8, 13], n),
        'erstellt': [today - timedelta(days=np.random.randint(10, 40)) for _ in range(n)],
        'faelligkeit': [today + timedelta(days=np.random.randint(-10, 15)) for _ in range(n)],
        'wartezeit': [np.random.randint(0, 5) for _ in range(n)],
        'arbeitszeit': [np.random.randint(1, 10) for _ in range(n)],
        'milestone': np.random.choice(['Meilenstein 1', 'Meilenstein 2', 'Meilenstein 3'], n)
    }

    df = pd.DataFrame(data)
    df['abgeschlossen'] = df.apply(
        lambda row: row['erstellt'] + timedelta(days=row['wartezeit'] + row['arbeitszeit']) if row['status'] == 'Erledigt' else pd.NaT,
        axis=1
    )
    df['kunde'] = df['projekt'].map(kunden)
    return df

# Load mock dataset
df = generate_mock_jira_data()

# --- Filters ---
st.sidebar.header("🔎 Filter Optionen")
projekt = st.sidebar.multiselect("Projekt auswählen", options=df['projekt'].unique(), default=df['projekt'].unique())
verantwortlich = st.sidebar.multiselect("Verantwortliche auswählen", options=df['verantwortlich'].unique(), default=df['verantwortlich'].unique())
sprint = st.sidebar.multiselect("Sprint auswählen", options=df['sprint'].unique(), default=df['sprint'].unique())

# Filtered Data
df = df[df['projekt'].isin(projekt) & df['verantwortlich'].isin(verantwortlich) & df['sprint'].isin(sprint)]

# --- Metrics ---
st.subheader("📈 Projekt-Kennzahlen")
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Gesamtanzahl Aufgaben", len(df))
with col2:
    st.metric("Abgeschlossen", len(df[df['status'] == 'Erledigt']))
with col3:
    ueberfaellig = df[(df['status'] != 'Erledigt') & (df['faelligkeit'] < datetime.today())]
    st.metric("Überfällige Aufgaben", len(ueberfaellig))
with col4:
    puenktlich = df[(df['status'] == 'Erledigt') & (df['abgeschlossen'] <= df['faelligkeit'])]
    st.metric("Pünktlich (% der Aufgaben)", f"{(len(puenktlich)/len(df)*100):.1f}%" if len(df) > 0 else "N/A")

# --- 📦 Velocity Chart ---
def show_velocity_chart(data):
    st.markdown("### 📦 Velocity pro Sprint")
    st.markdown("Die Velocity zeigt, wie viele Story Points pro Sprint abgeschlossen wurden – ein Maß für die Teamleistung.")
    velocity_data = data[data['status'] == 'Erledigt'].groupby('sprint')['story_points'].sum().reset_index()
    fig = px.bar(velocity_data, x='sprint', y='story_points', title='📦 Velocity nach Sprint', text_auto=True,
                 labels={"sprint": "Sprint", "story_points": "Abgeschlossene Story Points"})
    st.plotly_chart(fig, use_container_width=True)

# --- 📉 Burndown Chart ---
def show_burndown_chart(data):
    st.markdown("### 📉 Burndown Chart")
    st.markdown("Der Burndown-Chart zeigt, wie viele Aufgaben über die Zeit innerhalb eines Sprints offen geblieben sind – wichtig für die Sprintplanung.")
    data['erstellt_tag'] = data['erstellt'].dt.date
    burn = data.groupby(['sprint', 'erstellt_tag']).size().groupby(level=0).cumsum().reset_index(name='offene_aufgaben')
    fig = px.line(burn, x='erstellt_tag', y='offene_aufgaben', color='sprint', title='📉 Aufgabenverlauf im Sprint',
                  labels={"erstellt_tag": "Datum", "offene_aufgaben": "Offene Aufgaben"})
    st.plotly_chart(fig, use_container_width=True)

# --- ✅ Positiver Burndown (Aufgaben abgeschlossen) ---
def show_positive_burndown(data):
    st.markdown("### ✅ Fortschrittskurve: Erledigte Aufgaben")
    st.markdown("Diese Darstellung zeigt, wie kontinuierlich Aufgaben im Sprint erledigt wurden – zur positiven Teammotivation und Sprintreflexion.")
    done = data[data['status'] == 'Erledigt']
    done['abgeschlossen_tag'] = done['abgeschlossen'].dt.date
    fertig = done.groupby(['sprint', 'abgeschlossen_tag']).size().groupby(level=0).cumsum().reset_index(name='erledigt_gesamt')
    fig = px.line(fertig, x='abgeschlossen_tag', y='erledigt_gesamt', color='sprint',
                  title='✅ Fortschritt erledigter Aufgaben',
                  labels={"abgeschlossen_tag": "Datum", "erledigt_gesamt": "Erledigte Aufgaben"})
    st.plotly_chart(fig, use_container_width=True)

# --- 🌟 Meilenstein Visualisierung ---
def show_milestone_progress(data):
    st.markdown("### 🌟 Sprint-Meilensteine & Fortschritte")
    st.markdown("Diese Grafik hebt Meilensteine und die Anzahl erledigter Aufgaben pro Sprint hervor – ideal zur Reflexion und Kommunikation von Erfolgen.")
    milestone_summary = data[data['status'] == 'Erledigt'].groupby(['sprint', 'milestone']).size().reset_index(name='erledigt')
    fig = px.bar(milestone_summary, x='milestone', y='erledigt', color='sprint', barmode='group',
                 title='🌟 Erfüllte Meilensteine je Sprint',
                 labels={"milestone": "Meilenstein", "erledigt": "Erledigte Aufgaben", "sprint": "Sprint"})
    st.plotly_chart(fig, use_container_width=True)

# --- 🕒 SLA & Due Date Compliance ---
def show_sla_compliance(data):
    st.markdown("### 🕒 SLA & Fristen-Einhaltung")
    st.markdown("Diese Auswertung zeigt, ob Aufgaben innerhalb der geplanten Fälligkeit abgeschlossen wurden (Service Level Agreement).")
    data['sla_eingehalten'] = data.apply(lambda x: x['abgeschlossen'] <= x['faelligkeit'] if pd.notna(x['abgeschlossen']) else False, axis=1)
    sla_summary = data.groupby('sla_eingehalten').size().reset_index(name='anzahl')
    sla_summary['sla_eingehalten'] = sla_summary['sla_eingehalten'].map({True: 'Eingehalten', False: 'Verpasst'})
    fig = px.pie(sla_summary, names='sla_eingehalten', values='anzahl', title='🕒 SLA-Erfüllung',
                 labels={"sla_eingehalten": "SLA Status", "anzahl": "Anzahl Aufgaben"})
    st.plotly_chart(fig, use_container_width=True)

# --- 📊 Sprint-Vergleich ---
def show_sprint_comparison(data):
    st.markdown("### 📌 Sprint-Vergleich: Team-Beteiligung & Wartezeiten")
    st.markdown("Dieser Vergleich zeigt, wie viele Arbeitstage und Wartezeiten pro Entwickler in den jeweiligen Sprints angefallen sind.")
    vergleich = data.groupby(['sprint', 'verantwortlich'])[['arbeitszeit', 'wartezeit']].sum().reset_index()
    fig = px.bar(vergleich, x='verantwortlich', y=['arbeitszeit', 'wartezeit'], color='sprint',
                 barmode='group', title="⏱️ Arbeitszeit vs. Wartezeit pro Entwickler", labels={
                     "verantwortlich": "Entwickler",
                     "value": "Tage",
                     "variable": "Typ"
                 })
    st.plotly_chart(fig, use_container_width=True)

# --- 📊 Kundenspezifische Sprintanalyse ---
def show_customer_effort_chart(data):
    st.markdown("### 🧑‍💼 Kundenaufwände nach Sprint")
    st.markdown("Diese Übersicht zeigt, welcher Kunde im jeweiligen Sprint den größten Arbeitsaufwand verursacht hat – ideal für Ressourcenplanung und Priorisierung.")
    kundenaufwand = data.groupby(['sprint', 'kunde'])['arbeitszeit'].sum().reset_index()
    fig = px.bar(kundenaufwand, x='kunde', y='arbeitszeit', color='sprint', barmode='group',
                 title='🧑‍💼 Arbeitszeit nach Kunde & Sprint',
                 labels={"kunde": "Kunde", "arbeitszeit": "Arbeitszeit (Tage)", "sprint": "Sprint"})
    st.plotly_chart(fig, use_container_width=True)

# --- Visualization Section ---
st.subheader("📊 Visuelle Analysen")
show_velocity_chart(df)
show_burndown_chart(df)
show_positive_burndown(df)
show_milestone_progress(df)
show_sla_compliance(df)
show_sprint_comparison(df)
show_customer_effort_chart(df)

# --- Data Preview ---
st.subheader("📋 Datenvorschau")
st.dataframe(df)

# --- Export ---
st.download_button("💾 CSV herunterladen", df.to_csv(index=False).encode('utf-8'), "jira_demo_daten.csv")
