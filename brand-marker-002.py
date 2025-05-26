import matplotlib.pyplot as plt
import numpy as np

# Daten gemäß Statista-Dossiers
brands = {
    'adidas':        {'Awareness': 96, 'Popularity': 68, 'Usage': 64, 'Loyalty': 85, 'Buzz': 43},
    'Nike':          {'Awareness': 97, 'Popularity': 65, 'Usage': 57, 'Loyalty': 86, 'Buzz': 34},
    'Puma':          {'Awareness': 95, 'Popularity': 48, 'Usage': 38, 'Loyalty': 79, 'Buzz': 21},
    'Fila':          {'Awareness': 90, 'Popularity': 26, 'Usage': 16, 'Loyalty': 62, 'Buzz': 12},
    'Under Armour':  {'Awareness': 57, 'Popularity': 27, 'Usage': 22, 'Loyalty': 80, 'Buzz': 12}
}

metrics = ['Awareness', 'Popularity', 'Usage', 'Loyalty', 'Buzz']
brands_list = list(brands.keys())
num_metrics = len(metrics)
num_brands = len(brands_list)

# Datenmatrix
data = np.array([[brands[b][m] for m in metrics] for b in brands_list])

# Balkendiagramm
x = np.arange(num_metrics)
width = 0.15  # Breite je Markenbalken

fig, ax = plt.subplots(figsize=(10, 6))
for i, brand in enumerate(brands_list):
    ax.bar(x + i*width, data[i], width, label=brand)

# Achsen und Titel
ax.set_xlabel('KPI', fontsize=12)
ax.set_ylabel('Score (%)', fontsize=12)
ax.set_title('Brand KPI Vergleich – adidas vs. Wettbewerber', fontsize=14)
ax.set_xticks(x + width*(num_brands-1)/2)
ax.set_xticklabels(metrics)
ax.set_ylim(0, 100)
ax.legend()

# Prozentwerte auf Balken
for i in range(num_brands):
    for j in range(num_metrics):
        ax.text(x[j] + i*width, data[i, j] + 2,
                f"{data[i, j]}%", ha='center', va='bottom', fontsize=8)

plt.tight_layout()
plt.show()
