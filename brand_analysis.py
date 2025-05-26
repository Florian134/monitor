from bokeh.io import output_file, show
from bokeh.models import ColumnDataSource, LabelSet, FactorRange
from bokeh.plotting import figure
from bokeh.transform import dodge
import os, webbrowser

# 1. Daten gemäß Statista-Dossiers
brands = {
    'adidas':        {'Awareness': 96, 'Popularity': 68, 'Usage': 64, 'Loyalty': 85, 'Buzz': 43},
    'Nike':          {'Awareness': 97, 'Popularity': 65, 'Usage': 57, 'Loyalty': 86, 'Buzz': 34},
    'Puma':          {'Awareness': 95, 'Popularity': 48, 'Usage': 38, 'Loyalty': 79, 'Buzz': 21},
    'Fila':          {'Awareness': 90, 'Popularity': 26, 'Usage': 16, 'Loyalty': 62, 'Buzz': 12},
    'Under Armour':  {'Awareness': 57, 'Popularity': 27, 'Usage': 22, 'Loyalty': 80, 'Buzz': 12}
}

metrics     = ['Awareness','Popularity','Usage','Loyalty','Buzz']
competitors = [b for b in brands if b != 'adidas']

# 2. Punkteberechnung: Unterschied und Punkte (1 Punkt = 3%)
points_data = {'metric': metrics}
for comp in competitors:
    pts = []
    for m in metrics:
        diff = max(brands['adidas'][m] - brands[comp][m], 0)
        pts.append(round(diff / 3, 2))
    points_data[comp] = pts

source_points = ColumnDataSource(points_data)

# 3. Setup Ausgabe
html_path = "brand_analysis.html"
output_file(html_path, title="Brand KPI & Punkteanalyse")

# --- Erstes Diagramm: KPI Vergleich ---
p1 = figure(x_range=FactorRange(*brands.keys()), height=350, width=800,
            title="Statista Brand KPIs – adidas vs. Wettbewerber", toolbar_location=None)
offsets1 = {'Awareness': -0.4, 'Popularity': -0.2, 'Usage': 0.0, 'Loyalty': 0.2, 'Buzz': 0.4}
colors1  = {'Awareness': "#718dbf", 'Popularity': "#e84d60",
            'Usage': "#c9d9d3", 'Loyalty': "#ddb7b1", 'Buzz': "#a3c1ad"}
for m in metrics:
    p1.vbar(x=dodge('brand', offsets1[m], range=p1.x_range), top=m, width=0.18,
            source=ColumnDataSource({'brand': list(brands.keys()), m: [brands[b][m] for b in brands]}),
            color=colors1[m], legend_label=m)
p1.y_range.start, p1.yaxis.axis_label = 0, "Score (%)"
p1.xaxis.axis_label = "Marke"
p1.legend.location = "top_left"
p1.legend.click_policy = "hide"

# --- Zweites Diagramm: Markt vs. Markenwert ---
market_cap   = 42_300
license_rate = 0.08
brand_value  = market_cap * license_rate
cats         = ['Marktkap.', 'Lizenz-Wert']
vals         = [market_cap, brand_value]
pct          = [100, license_rate*100]
p2 = figure(x_range=cats, height=300, width=500,
            title="adidas: Markt- vs. Markenwert", toolbar_location=None)
p2.vbar(x=cats, top=vals, width=0.6, color=["#6baed6", "#fd8d3c"])
src2 = ColumnDataSource({'Kategorie': cats, 'Wert': vals, 'Prozent': pct})
labels2 = LabelSet(x='Kategorie', y='Wert', text='Prozent', source=src2,
                   text_font_size="10pt", x_offset=-20, y_offset=5, text_align="center")
p2.add_layout(labels2)
p2.yaxis.axis_label = "Wert (Mio. €)"

# --- Drittes Diagramm: Punkte, wo adidas führt ---
p3 = figure(x_range=metrics, height=350, width=800,
            title="Punktedifferenz: adidas vs. Wettbewerber (1 Pkt = 3%)", toolbar_location=None)
offsets3 = {'Nike': -0.3, 'Puma': -0.1, 'Fila': 0.1, 'Under Armour': 0.3}
colors3  = {'Nike': "#e41a1c", 'Puma': "#377eb8", 'Fila': "#4daf4a", 'Under Armour': "#984ea3"}
for comp in competitors:
    p3.vbar(x=dodge('metric', offsets3[comp], range=p3.x_range),
            top=comp, width=0.18, source=source_points,
            color=colors3[comp], legend_label=comp)
    labels = LabelSet(x=dodge('metric', offsets3[comp], range=p3.x_range),
                      y=comp, text=comp, source=source_points,
                      text_font_size="8pt", x_offset=-10, y_offset=2)
    p3.add_layout(labels)
p3.yaxis.axis_label = "Markenwertpunkte"
p3.xaxis.axis_label = "KPI"
p3.legend.location = "top_left"
p3.legend.click_policy = "mute"

# --- Ausgabe aller Plots ---
show(p1)
show(p2)
show(p3)

# Automatisch öffnen
url = 'file://' + os.path.realpath(html_path)
os.system(f'start {url}' if os.name == 'nt' else f'open "{url}"')
