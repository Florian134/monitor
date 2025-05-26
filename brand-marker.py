# Aktualisiertes Skript für `brand-marker.py` mit Farben und Wertbeschriftung

from bokeh.io import output_file, show
from bokeh.models import ColumnDataSource, LabelSet
from bokeh.plotting import figure
from bokeh.transform import dodge
import webbrowser, os

# 1. Datengrundlage
brands = {
    'adidas': {'funnel': {'awareness': 0.978, 'familiarity': 0.868, 'consideration': 0.809, 'purchase': 0.579, 'loyalty': 0.399},
               'license_rate': 0.08, 'brand_value': 16.7},
    'Nike':   {'funnel': {'awareness': 0.990, 'familiarity': 0.890, 'consideration': 0.850, 'purchase': 0.610, 'loyalty': 0.420},
               'license_rate': 0.09, 'brand_value': 31.3},
    'Puma':   {'funnel': {'awareness': 0.950, 'familiarity': 0.800, 'consideration': 0.750, 'purchase': 0.550, 'loyalty': 0.350},
               'license_rate': 0.07, 'brand_value': 9.0}
}

# 2. Punkteberechnung
lic_rates = [b['license_rate'] for b in brands.values()]
bv_values  = [b['brand_value']   for b in brands.values()]
min_lr, max_lr = min(lic_rates), max(lic_rates)
min_bv, max_bv = min(bv_values),  max(bv_values)

data = {'brand': [], 'strength_score': [], 'license_score': [], 'value_score': [], 'total_score': []}
for name, d in brands.items():
    strength      = (d['funnel']['loyalty'] / d['funnel']['purchase']) * 100
    license_score = (d['license_rate'] - min_lr) / (max_lr - min_lr) * 100
    value_score   = (d['brand_value']   - min_bv) / (max_bv - min_bv) * 100
    total         = 0.4 * strength + 0.3 * license_score + 0.3 * value_score
    data['brand'].append(name)
    data['strength_score'].append(round(strength,1))
    data['license_score'].append(round(license_score,1))
    data['value_score'].append(round(value_score,1))
    data['total_score'].append(round(total,1))

source = ColumnDataSource(data)

# 3. Visualisierung
output_path = "brand_valuation_comparison.html"
output_file(output_path, title="Markenbewertung adidas vs. Nike & Puma")

p = figure(x_range=list(data['brand']), height=400, width=800,
           title="Markenbewertungskomponenten", toolbar_location=None)

# Balken mit individuellen Farben
p.vbar(x=dodge('brand', -0.25, range=p.x_range), top='strength_score', width=0.2,
       source=source, color="#718dbf", legend_label="Stärke-Index")
p.vbar(x=dodge('brand',  0.0,  range=p.x_range), top='license_score', width=0.2,
       source=source, color="#e84d60", legend_label="Lizenz-Score")
p.vbar(x=dodge('brand',  0.25, range=p.x_range), top='value_score', width=0.2,
       source=source, color="#c9d9d3", legend_label="Brand Value-Score")

# Wertbeschriftung auf den Balken
labels_strength = LabelSet(x=dodge('brand', -0.25, range=p.x_range), y='strength_score', text='strength_score',
                          source=source, text_font_size="9pt", x_offset=-13, y_offset=2)
labels_license  = LabelSet(x=dodge('brand',  0.0,  range=p.x_range), y='license_score', text='license_score',
                          source=source, text_font_size="9pt", x_offset=-8,  y_offset=2)
labels_value    = LabelSet(x=dodge('brand',  0.25, range=p.x_range), y='value_score', text='value_score',
                          source=source, text_font_size="9pt", x_offset=-8,  y_offset=2)

p.add_layout(labels_strength)
p.add_layout(labels_license)
p.add_layout(labels_value)

# Achsen, Legende, Layout
p.y_range.start = 0
p.legend.location = "top_left"
p.legend.click_policy = "mute"
p.xaxis.axis_label = "Marke"
p.yaxis.axis_label = "Score (0–100)"

show(p)

# Browser öffnen
url = 'file://' + os.path.realpath(output_path)
os.system(f'start {url}' if os.name == 'nt' else f'open {url}')
