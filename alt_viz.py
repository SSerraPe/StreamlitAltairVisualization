# Proyecto MESIO Summer School - Visualización Interactiva
# Casos de Sarampión y Rubéola en 2024

import pandas as pd
import altair as alt
import urllib.request
import json

# -----------------------------
# CARGA Y PREPROCESADO DE DATOS
# -----------------------------

# Cargar datos anuales (2024)
df = pd.read_csv('cases_year_clean.csv')
df = df[df["year"] == 2024].copy()
df["iso3"] = df["iso3"].str.strip().str.upper()
df["measles_total"] = pd.to_numeric(df["measles_total"], errors="coerce")
df["rubella_total"] = pd.to_numeric(df["rubella_total"], errors="coerce")
df["total_population"] = pd.to_numeric(df["total_population"], errors="coerce")

# Cargar datos mensuales (2024)
dfm = pd.read_csv('cases_month_clean.csv')
dfm = dfm[dfm["year"] == 2024].copy()
dfm["measles_total"] = pd.to_numeric(dfm["measles_total"], errors="coerce")
dfm["rubella_total"] = pd.to_numeric(dfm["rubella_total"], errors="coerce")
dfm["date"] = pd.to_datetime(dfm["year"].astype(str) + '-' + dfm["month"].astype(str).str.zfill(2) + '-01')

# Cargar GeoJSON (con id = iso3)
url_geojson = 'https://raw.githubusercontent.com/johan/world.geo.json/master/countries.geo.json'
with urllib.request.urlopen(url_geojson) as response:
    countries = json.load(response)

# ---------------------------------
# VISUALIZACION 1: MAPA INTERACTIVO
# ---------------------------------

# Selector de enfermedad interactivo
selector = alt.binding_select(
    options=['measles_total', 'rubella_total'],
    name='Enfermedad: '
)
variable = alt.param(name='variable', bind=selector, value='measles_total')

# Mapa principal con color dinámico según selección
heatmap = alt.Chart(alt.Data(values=countries['features'])).mark_geoshape().encode(
    color=alt.Color('casos:Q', scale=alt.Scale(scheme='orangered'), title='Número de casos'),
    tooltip=[
        alt.Tooltip('properties.name:N', title='País'),
        alt.Tooltip('casos:Q', title='Casos')
    ]
).transform_lookup(
    lookup='id',
    from_=alt.LookupData(df, 'iso3', ['measles_total', 'rubella_total'])
).transform_calculate(
    casos=f'datum[{variable.name}]'
).add_params(
    variable
).project('equalEarth').properties(width=800, height=400)

# Fondo gris del mapa
background = alt.Chart(alt.Data(values=countries['features'])).mark_geoshape(
    fill='lightblue', stroke='white'
).project('equalEarth')

# Combinar mapa final
viz_1 = background + heatmap

# ------------------------------
# VISUALIZACION 2: TOP 10 PAÍSES
# ------------------------------

# FILTRAR POR REGIÓN
region = "AFR"  # <-- CAMBIA AQUÍ LA REGIÓN A EXPLORAR
df_2 = df[df["region"] == region].copy()

# Eliminar países sin casos reportados
df_2 = df_2[(df_2["measles_total"] > 0) | (df_2["rubella_total"] > 0)]

# Si no hay datos válidos, muestra advertencia
if df_2.empty:
    print(f"No hay datos válidos de sarampión o rubéola para la región '{region}'.")
else:
    # Reorganizar en formato largo
    df_long = df_2.melt(
        id_vars=['iso3', 'country'],
        value_vars=['measles_total', 'rubella_total'],
        var_name='variable',
        value_name='casos'
    )

    # Agrupar y seleccionar el top 10 por enfermedad
    top10 = (
        df_long.groupby(['country', 'variable'], as_index=False)
        .sum()
        .sort_values("casos", ascending=False)
        .groupby("variable")
        .head(10)
    )

    # Graficar con Altair
    viz_2 = alt.Chart(top10).mark_bar().encode(
        y=alt.Y("country:N", sort='-x', title="País"),
        x=alt.X("casos:Q", title="Casos"),
        color=alt.Color("variable:N", title="Enfermedad"),
        tooltip=["country", "variable", "casos"]
    ).properties(
        width=400,
        height=300,
        title=f"Top 10 países con más casos en la región: {region}"
    )

# -----------------------------------------------
# VISUALIZACION 3: CORRELACIÓN ENTRE ENFERMEDADES
# -----------------------------------------------

# Filtrar solo año 2024
df_3 = df[df['year'] == '2024']

# Eliminar ceros y nulos (log(0) no está definido)
df_3 = df[(df['measles_total'] > 0) & (df['rubella_total'] > 0)]

# Selección interactiva por región
highlight = alt.selection_point(fields=['region'], bind='legend')

# Línea y = x (en escala log)
line_ref = alt.Chart(pd.DataFrame({'x': [1, df['measles_total'].max()]})).transform_calculate(
    y='datum.x'
).mark_line(strokeDash=[5, 5], color='gray').encode(
    x=alt.X('x:Q', scale=alt.Scale(type='log')),
    y=alt.Y('y:Q', scale=alt.Scale(type='log'))
)

# Gráfico de dispersión interactivo
scatter = alt.Chart(df_3).mark_circle(size=80).encode(
    x=alt.X('measles_total:Q', scale=alt.Scale(type='log'), title='Casos Sarampión (escala log)'),
    y=alt.Y('rubella_total:Q', scale=alt.Scale(type='log'), title='Casos Rubéola (escala log)'),
    color=alt.Color('region:N', legend=alt.Legend(title='Región')),
    opacity=alt.condition(highlight, alt.value(1), alt.value(0.1)),
    tooltip=['country:N', 'measles_total:Q', 'rubella_total:Q']
).add_params(
    highlight
)

# Combinar dispersión con línea de referencia
viz_3 = (scatter + line_ref).properties(
    width=400,
    height=400,
    title='Relación entre casos de sarampión y rubéola por país (2024)'
)

# -----------------------------------
# VISUALIZACION 4: CASOS VS POBLACIÓN
# -----------------------------------

# Filtrar por región (ej. 'AFR')
region_focus = 'AFR'
df_region = df[df['region'] == region_focus]

# Calcular matriz de correlación
df_corr = df_region[['measles_total', 'rubella_total', 'total_population']].dropna()
corr_matrix = df_corr.corr(method='pearson')

# Convertir a formato largo para Altair
corr_long = corr_matrix.reset_index().melt(id_vars='index')
corr_long.columns = ['Variable1', 'Variable2', 'Correlación']

# Crear heatmap
heatmap = alt.Chart(corr_long).mark_rect().encode(
    x=alt.X('Variable1:O', title=''),
    y=alt.Y('Variable2:O', title=''),
    color=alt.Color('Correlación:Q', scale=alt.Scale(scheme='redblue', domain=[-1, 1])),
    tooltip=['Variable1', 'Variable2', 'Correlación']
).properties(
    width=300,
    height=300,
    title=f'Matriz de Correlación en {region_focus}'
)

# Añadir etiquetas numéricas
text = heatmap.mark_text(baseline='middle').encode(
    text=alt.Text('Correlación:Q', format=".2f"),
    color=alt.condition(
        "datum.Correlación > 0.5 || datum.Correlación < -0.5",
        alt.value('white'),
        alt.value('black')
    )
)

viz_4 = (heatmap + text).interactive()

# --------------------------------------------------
# VISUALIZACION 5: EVOLUCIÓN TEMPORAL POR CONTINENTE
# --------------------------------------------------

# Selección interactiva por región (desde la leyenda)
highlight = alt.selection_point(fields=['region'], bind='legend')

# Gráfico de área con highlight aplicado
viz_5 = alt.Chart(dfm).mark_area().encode(
    x=alt.X('date:T', title='Mes'),
    y=alt.Y('sum(measles_total):Q', title='Casos acumulados'),
    color=alt.Color('region:N', legend=alt.Legend(title="region")),
    opacity=alt.condition(highlight, alt.value(1), alt.value(0.2)),
    tooltip=['region:N', alt.Tooltip('sum(measles_total):Q', title='Casos')]
).add_params(
    highlight
).properties(
    width=700,
    height=300
)

# -----------------------------------------------
# VISUALIZACION 6: EVOLUCIÓN POR PAÍS (SELECCIÓN)
# -----------------------------------------------

# Lista única de países
countries = sorted(dfm['country'].unique().tolist())

# Dropdown de selección única
selector = alt.selection_point(
    name="Selecciona país",
    fields=["country"],
    bind=alt.binding_select(options=countries, name='País: ')
)

# Fondo gris con todos los países
background = alt.Chart(dfm).mark_line(opacity=0.1, color='lightgray').encode(
    x=alt.X('date:T', title='Fecha'),
    y=alt.Y('measles_total:Q', title='Casos de Sarampión'),
    detail='country:N'
)

# País seleccionado en color
highlight = alt.Chart(dfm).mark_line().encode(
    x='date:T',
    y='measles_total:Q',
    color=alt.Color('country:N', title='País'),
    tooltip=['country:N', 'month:O', 'measles_total:Q']
).transform_filter(selector).add_params(selector)

# Visualización combinada
viz_6 = (background + highlight).properties(
    width=750,
    height=350,
    title='Evolución mensual de casos de Sarampión por país (2024)'
).interactive()