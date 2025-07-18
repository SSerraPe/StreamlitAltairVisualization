# Dashboard Interactivo Sarampión y Rubéola 2024
# Proyecto MESIO Summer School

import streamlit as st
import pandas as pd
import altair as alt
import urllib.request
import json

# ----------------------------
# Configuración de la página
# ----------------------------
st.set_page_config(
    page_title="Dashboard Sarampión y Rubéola 2024",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)
alt.data_transformers.enable('json')

# ----------------------------
# Carga de datos
# ----------------------------
@st.cache_data
def load_data():
    df = pd.read_csv('cases_year_clean.csv')
    df = df[df["year"] == 2024].copy()
    df["iso3"] = df["iso3"].str.strip().str.upper()
    df["measles_total"] = pd.to_numeric(df["measles_total"], errors="coerce")
    df["rubella_total"] = pd.to_numeric(df["rubella_total"], errors="coerce")
    df["total_population"] = pd.to_numeric(df["total_population"], errors="coerce")

    dfm = pd.read_csv('cases_month_clean.csv')
    dfm = dfm[dfm["year"] == 2024].copy()
    dfm["measles_total"] = pd.to_numeric(dfm["measles_total"], errors="coerce")
    dfm["rubella_total"] = pd.to_numeric(dfm["rubella_total"], errors="coerce")
    dfm["date"] = pd.to_datetime(dfm["year"].astype(str) + '-' + dfm["month"].astype(str).str.zfill(2) + '-01')
    return df, dfm

@st.cache_data
def load_geojson():
    url_geojson = 'https://raw.githubusercontent.com/johan/world.geo.json/master/countries.geo.json'
    with urllib.request.urlopen(url_geojson) as response:
        return json.load(response)

# ----------------------------
# Visualizaciones
# ----------------------------

def mapa_interactivo(df, countries, enfermedad, region):
    # Selector de país para interacción cruzada (clic en país)
    country_selector = alt.selection_point(fields=["properties.name"], name="SeleccionPais", clear=True)

    df_region = df[df["region"] == region].copy() if region != "Todas" else df.copy()

    # Mapa con casos según la enfermedad pasada como argumento
    heatmap = alt.Chart(alt.Data(values=countries['features'])).mark_geoshape().encode(
        color=alt.Color('casos:Q', scale=alt.Scale(scheme='orangered'), title='Número de casos'),
        tooltip=[
            alt.Tooltip('properties.name:N', title='País'),
            alt.Tooltip('casos:Q', title='Casos')
        ]
    ).transform_lookup(
        lookup='id',
        from_=alt.LookupData(df_region, 'iso3', [enfermedad])
    ).transform_calculate(
        casos=f'datum["{enfermedad}"]'
    ).add_params(
        country_selector
    ).project('equalEarth').properties(width=800, height=400)

    # Fondo del mapa
    background = alt.Chart(alt.Data(values=countries['features'])).mark_geoshape(
        fill='lightblue', stroke='white'
    ).project('equalEarth')

    return background + heatmap


def top10_paises(df, region):
    df_r = df.copy() if region == "Todas" else df[df['region'] == region].copy()
    df_r = df_r[(df_r["measles_total"] > 0) | (df_r["rubella_total"] > 0)]
    if df_r.empty:
        return alt.Chart().mark_text(text="Sin datos en la región", size=16)

    df_long = df_r.melt(id_vars=['iso3', 'country'], value_vars=['measles_total', 'rubella_total'], var_name='variable', value_name='casos')
    top10 = df_long.groupby(['country', 'variable'], as_index=False).sum().sort_values("casos", ascending=False).groupby("variable").head(10)

    return alt.Chart(top10).mark_bar().encode(
        y=alt.Y("country:N", sort='-x', title="País"),
        x=alt.X("casos:Q", title="Casos"),
        color=alt.Color("variable:N", title="Enfermedad"),
        tooltip=["country", "variable", "casos"]
    ).properties(width=400, height=450)

def correlacion_enfermedades(df, region):
    df_corr = df[(df['measles_total'] > 0) & (df['rubella_total'] > 0)]
    if df_corr.empty:
        return alt.Chart().mark_text(text="Sin datos suficientes", size=16)
    
    if region != "Todas":
        df_corr = df_corr[df_corr['region'] == region]

    highlight = alt.selection_point(fields=['region'], bind='legend')

    line_ref = alt.Chart(pd.DataFrame({'x': [1, df_corr['measles_total'].max()]})).transform_calculate(y='datum.x').mark_line(strokeDash=[5, 5], color='gray').encode(
        x=alt.X('x:Q', scale=alt.Scale(type='log')),
        y=alt.Y('y:Q', scale=alt.Scale(type='log'))
    )

    scatter = alt.Chart(df_corr).mark_circle(size=80).encode(
        x=alt.X('measles_total:Q', scale=alt.Scale(type='log'), title='Sarampión (log)'),
        y=alt.Y('rubella_total:Q', scale=alt.Scale(type='log'), title='Rubéola (log)'),
        color=alt.Color('region:N'),
        opacity=alt.condition(highlight, alt.value(1), alt.value(0.1)),
        tooltip=['country:N', 'measles_total:Q', 'rubella_total:Q']
    ).add_params(highlight)

    return (scatter + line_ref).properties(width=400, height=400)

def correlacion_poblacion(df, region):
    df_r = df.copy() if region == "Todas" else df[df['region'] == region]
    corr_matrix = df_r[['measles_total', 'rubella_total', 'total_population']].dropna().corr()

    # Reset index y pasar a formato largo
    corr = corr_matrix.reset_index().melt(id_vars='index', var_name='variable', value_name='Correlacion')

    # Renombrar columnas
    corr = corr.rename(columns={'index': 'Variable1', 'variable': 'Variable2'})

    # Asegurar que Correlacion es numérica
    corr['Correlacion'] = pd.to_numeric(corr['Correlacion'], errors='coerce')

    # Etiquetas legibles
    var_labels = {
        'measles_total': 'Sarampión',
        'rubella_total': 'Rubéola',
        'total_population': 'Población'
    }
    corr['Variable1'] = corr['Variable1'].map(var_labels).astype(str)
    corr['Variable2'] = corr['Variable2'].map(var_labels).astype(str)

    base = alt.Chart(corr).mark_rect().encode(
        x=alt.X('Variable1:O', title=None),
        y=alt.Y('Variable2:O', title=None),
        color=alt.Color('Correlacion:Q', scale=alt.Scale(scheme='redblue', domain=[-1, 1])),
        tooltip=['Variable1', 'Variable2', 'Correlacion']
    )

    texto = base.mark_text(baseline='middle').encode(
        text=alt.Text('Correlacion:Q', format=".2f"),
        color=alt.condition("abs(datum.Correlacion) > 0.5", alt.value('white'), alt.value('black'))
    )
    return (base + texto).properties(width=400, height=450)

def evolucion_regiones(dfm, enfermedad):
    highlight = alt.selection_point(fields=['region'], bind='legend')
    return alt.Chart(dfm).mark_area().encode(
        x=alt.X('date:T'),
        y=alt.Y(f'sum({enfermedad}):Q', title='Casos'),
        color=alt.Color('region:N'),
        opacity=alt.condition(highlight, alt.value(1), alt.value(0.2)),
        tooltip=[
            'region:N',
            alt.Tooltip(f'sum({enfermedad}):Q', title='Casos')
        ]
    ).add_params(highlight).properties(width=700, height=300)


def evolucion_pais(dfm, enfermedad):
    selector = alt.selection_point(
        name="Selecciona",
        fields=["country"],
        bind=alt.binding_select(options=sorted(dfm['country'].dropna().unique()), name='País: ')
    )

    fondo = alt.Chart(dfm).mark_line(opacity=0.1, color='lightgray').encode(
        x='date:T',
        y=alt.Y(f'{enfermedad}:Q', title='Casos'),
        detail='country:N'
    )

    resalta = alt.Chart(dfm).mark_line().encode(
        x=alt.X('date:T', title='Tiempo'),
        y=alt.Y(f'{enfermedad}:Q', title='Casos'),
        color=alt.Color('country:N', legend=None),
        tooltip=[
            'country:N',
            'month:O',
            alt.Tooltip(f'{enfermedad}:Q', title='Casos')
        ]
    ).transform_filter(selector).add_params(selector)

    return (fondo + resalta).properties(width=750, height=350, title='Evolución mensual por país').interactive()

# ----------------------------
# Interfaz principal
# ----------------------------
def main():
    st.title("Dashboard Interactivo – Casos de Sarampión y Rubéola en 2024")
    st.markdown("---")

    df, dfm = load_data()
    geojson = load_geojson()

    # SIDEBAR
    with st.sidebar:
        st.markdown("---")
        st.markdown(
            "<div style='font-size: 12px; text-align: center; color: gray;'>"
            "Serra Peña, Sebastián  ·  MESIO – Summer School 2024"
            "</div>",
            unsafe_allow_html=True
        )
        st.markdown("---")

        st.markdown("### Instrucciones de uso")
        st.markdown(
            """
            Este panel permite explorar los casos de sarampión y rubéola durante 2024.  
            Usa los controles para seleccionar la enfermedad y la región de interés.  
            Los gráficos se actualizarán automáticamente.
            """
        )

        st.markdown("### Controles")
        enfermedad = st.selectbox(
            "Selecciona la enfermedad:", 
            options=['measles_total', 'rubella_total'], 
            format_func=lambda x: 'Sarampión' if x == 'measles_total' else 'Rubéola'
        )

        region = st.selectbox(
            "Selecciona la región:", 
            options=["Todas"] + sorted(df['region'].dropna().unique().tolist())
        )

        st.markdown("---")
        st.markdown("### Estadísticas generales")

        total_paises = df['country'].nunique()
        total_casos = df[enfermedad].sum(skipna=True)
        st.markdown(f"**Total de países con datos:** {total_paises}")
        st.markdown(f"**Casos totales de {'Sarampión' if enfermedad == 'measles_total' else 'Rubéola'}:** {int(total_casos):,}")

    # VISUALIZACIONES PRINCIPALES
    col1, col2 = st.columns([2,1])
    with col1:
        st.subheader("Mapa mundial de casos reportados")
        st.caption("Distribución geográfica de casos por país en 2024.")
        st.altair_chart(mapa_interactivo(df, geojson, enfermedad, region), use_container_width=True)

    with col2:
        st.subheader("Top 10 países por número de casos")
        st.caption("Lista de países con mayor número de casos en la región seleccionada.")
        st.altair_chart(top10_paises(df, region), use_container_width=True)

    col3, col4 = st.columns(2)
    with col3:
        st.subheader("Relación entre enfermedades")
        st.caption("Correlación entre casos de sarampión y rubéola por país.")
        st.altair_chart(correlacion_enfermedades(df, region), use_container_width=True)

    with col4:
        st.subheader("Casos vs población")
        st.caption("Matriz de correlación entre enfermedades y población total por país.")
        st.altair_chart(correlacion_poblacion(df, region), use_container_width=True)

    st.subheader("Evolución temporal mensual")
    st.caption("Comparativa de la evolución mensual de casos según región o país.")
    tab1, tab2 = st.tabs(["Por región", "Por país"])
    with tab1:
        st.altair_chart(evolucion_regiones(dfm, enfermedad), use_container_width=True)
    with tab2:
        st.altair_chart(evolucion_pais(dfm, enfermedad), use_container_width=True)


if __name__ == '__main__':
    main()
