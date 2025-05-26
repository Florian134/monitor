import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="JIRA Sprint Auswertung", layout="wide")

# Session-State initialisieren
if "sprints" not in st.session_state:
    st.session_state.sprints = {}

st.title("📊 JIRA Sprint Management Tool")

# Sprint Auswahl
selected_sprint = st.selectbox("Sprint auswählen", [f"Sprint {i}" for i in range(1, 100)])

# Sprintdaten eingeben
st.subheader(f"🔧 Daten für {selected_sprint} eingeben")

with st.form(key=f"form_{selected_sprint}"):
    total_tickets = st.number_input("Anzahl der Tickets gesamt", min_value=1, value=10)

    done = st.slider("Abgeschlossene Tickets", min_value=0, max_value=total_tickets)
    closed = st.slider("Geschlossene Tickets", min_value=0, max_value=total_tickets - done)

    stunden = st.number_input("Sprintstunden gesamt", min_value=0.0)

    st.markdown("**Ticket-Arten**")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        imp = st.number_input("Improvements", min_value=0, max_value=total_tickets, key="imp")
    with col2:
        bugs = st.number_input("Bugs", min_value=0, max_value=total_tickets, key="bugs")
    with col3:
        feats = st.number_input("Features", min_value=0, max_value=total_tickets, key="feats")
    with col4:
        maint = st.number_input("Maintenance", min_value=0, max_value=total_tickets, key="maint")

    submit = st.form_submit_button("Sprintdaten speichern")

# Validierung
def validate_inputs():
    if (imp + bugs + feats + maint) > total_tickets:
        return "Summe der Ticketarten überschreitet Gesamtanzahl!"
    if (done + closed) > total_tickets:
        return "Summe aus abgeschlossen und geschlossen ist zu hoch!"
    return None

# Daten speichern
if submit:
    error = validate_inputs()
    if error:
        st.error(error)
    else:
        st.session_state.sprints[selected_sprint] = {
            "Tickets": total_tickets,
            "Abgeschlossen": done,
            "Geschlossen": closed,
            "Stunden": stunden,
            "Improvements": imp,
            "Bugs": bugs,
            "Features": feats,
            "Maintenance": maint,
        }
        st.success("Sprintdaten gespeichert!")

# Visualisierung
if selected_sprint in st.session_state.sprints:
    data = st.session_state.sprints[selected_sprint]
    st.subheader("📈 Auswertung")

    # 1. Ticket-Status-Diagramm
    fig1, ax1 = plt.subplots()
    ax1.pie([data["Abgeschlossen"], data["Geschlossen"], data["Tickets"] - data["Abgeschlossen"] - data["Geschlossen"]],
            labels=["Abgeschlossen", "Geschlossen", "Offen"], autopct='%1.1f%%', startangle=90)
    ax1.axis('equal')
    st.pyplot(fig1)

    # 2. Ticket-Arten
    fig2, ax2 = plt.subplots()
    ax2.bar(["Improvements", "Bugs", "Features", "Maintenance"],
            [data["Improvements"], data["Bugs"], data["Features"], data["Maintenance"]])
    ax2.set_ylabel("Anzahl")
    ax2.set_title("Tickets nach Typ")
    st.pyplot(fig2)

    # 3. Overhead-Berechnung
    offene = data["Tickets"] - data["Abgeschlossen"] - data["Geschlossen"]
    overhead = (offene / data["Tickets"]) * data["Stunden"] if data["Tickets"] else 0

    st.metric("⌛ Geschätzter Overhead in nächsten Sprint", f"{overhead:.1f} Std")

    fig3, ax3 = plt.subplots()
    ax3.bar(["Aktuell verbrauchte Stunden", "Overhead nächste Sprint"], [data["Stunden"], overhead])
    ax3.set_ylabel("Stunden")
    ax3.set_title("Sprint-Zeitverteilung")
    st.pyplot(fig3)

    # Export Optionen
    export_col1, export_col2, export_col3 = st.columns(3)
    with export_col1:
        if st.download_button("📤 Excel Export", data=pd.DataFrame([data]).to_excel(index=False), file_name=f"{selected_sprint}.xlsx"):
            pass
    with export_col2:
        if st.button("🧹 Zurücksetzen"):
            st.session_state.sprints.pop(selected_sprint, None)
    with export_col3:
        st.stop()  # Anwendung "schließen"

