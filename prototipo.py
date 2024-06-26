import streamlit as st
import pandas as pd
import plotly.express as px
import datetime

url_objetos = "https://dados.es.gov.br/datastore/dump/4680570b-63f9-4fb3-92a6-3097d4fd3a1a?bom=True"
df = pd.read_csv(url_objetos, sep=",")
df['DATA DO FATO'] = pd.to_datetime(df['DATA DO FATO']).dt.date
df['DIA DA SEMANA'] = pd.to_datetime(df['DATA DO FATO']).dt.day_name()
dias_semana = {
    'Monday': 'SEG',
    'Tuesday': 'TER',
    'Wednesday': 'QUA',
    'Thursday': 'QUI',
    'Friday': 'SEX',
    'Saturday': 'SAB',
    'Sunday': 'DOM'
}

df['DIA DA SEMANA'] = df['DIA DA SEMANA'].map(dias_semana)
df.drop(columns=['_id', 'Nº OCORRÊNCIA'], inplace=True)

st.set_page_config(layout="wide")

st.header('Dashboard de objetos furtados/roubados no Espirito Santo nos periodos de janeiro a abril de 2024')

municipio = st.sidebar.selectbox('Municipio', df['MUNICIPIO'].unique(), index= None)

df_filtered_by_municipio = df[df["MUNICIPIO"] == municipio]
col1,col2 = st.columns(2)

col3, col4, col5 = st.columns(3)

#col 1
df_municipio_ocorrencias = df.groupby('MUNICIPIO').size().reset_index(name='QUANTIDADE OCORRENCIA')
df_municipio_ocorrencias = df_municipio_ocorrencias.sort_values(by='QUANTIDADE OCORRENCIA', ascending=False)
df_municipio_ocorrencias = df_municipio_ocorrencias.head(10)
fig_ocorrencia_municipio = px.bar(df_municipio_ocorrencias, x="QUANTIDADE OCORRENCIA", y="MUNICIPIO", title="Ocorrência por Municipio (10 maiores)")
col1.plotly_chart(fig_ocorrencia_municipio, use_container_width=True)

#Col 2
if df_filtered_by_municipio.empty:   
    df_dia_semana_ocorrencias = df.groupby('DIA DA SEMANA').size().reset_index(name='QUANTIDADE OCORRENCIA')
    df_dia_semana_ocorrencias = df_dia_semana_ocorrencias.sort_values(by='QUANTIDADE OCORRENCIA', ascending=False)
else:
    df_dia_semana_ocorrencias = df_filtered_by_municipio.groupby('DIA DA SEMANA').size().reset_index(name='QUANTIDADE OCORRENCIA')
    df_dia_semana_ocorrencias = df_dia_semana_ocorrencias.sort_values(by='QUANTIDADE OCORRENCIA', ascending=False)
fig_ocorrencia_dia_semana =  px.bar(df_dia_semana_ocorrencias, x="DIA DA SEMANA", y="QUANTIDADE OCORRENCIA", title="Ocorrência por dia da semana")
col2.plotly_chart(fig_ocorrencia_dia_semana,use_container_width=True)

#col 3
if df_filtered_by_municipio.empty:   
    df_tipo_objeto_ocorrencias = df['TIPO OBJETO'].value_counts().reset_index()
    df_tipo_objeto_ocorrencias.columns = ['TIPO OBJETO', 'QUANTIDADE OCORRENCIA']
else:
    df_tipo_objeto_ocorrencias = df_filtered_by_municipio['TIPO OBJETO'].value_counts().reset_index()
    df_tipo_objeto_ocorrencias.columns = ['TIPO OBJETO', 'QUANTIDADE OCORRENCIA']
    
fig_ocorrencia_tipo_objeto =  px.bar(df_tipo_objeto_ocorrencias, x="TIPO OBJETO", y="QUANTIDADE OCORRENCIA", title="Ocorrência por Tipo do Objeto")
col3.plotly_chart(fig_ocorrencia_tipo_objeto,use_container_width=True)


#col 4

if df_filtered_by_municipio.empty:   
    df_horario_ocorrencia = df[df['HORA DO FATO'] != 'Indeterminada']
    df_horario_ocorrencia['HORA DO FATO'] = pd.to_datetime(df_horario_ocorrencia['HORA DO FATO'], format='%H:%M:%S').dt.time
else:
    df_horario_ocorrencia = df_filtered_by_municipio[df_filtered_by_municipio['HORA DO FATO'] != 'Indeterminada']
    df_horario_ocorrencia['HORA DO FATO'] = pd.to_datetime(df_horario_ocorrencia['HORA DO FATO'], format='%H:%M:%S').dt.time

def categorize_period(time):
    hour = time.hour
    if 0 <= hour < 6:
        return 'Madrugada'
    elif 6 <= hour < 12:
        return 'Manhã'
    elif 12 <= hour < 18:
        return 'Tarde'
    else:
        return 'Noite'

df_horario_ocorrencia['PERIODO DO DIA'] = df_horario_ocorrencia['HORA DO FATO'].apply(categorize_period)

periodo_dia_ocorrencia = df_horario_ocorrencia['PERIODO DO DIA'].value_counts().reset_index()
periodo_dia_ocorrencia.columns = ['PERIODO DO DIA', 'QUANTIDADE OCORRENCIA']

fig_periodo_dia_ocorrencia = px.pie(periodo_dia_ocorrencia, names='PERIODO DO DIA', values='QUANTIDADE OCORRENCIA', title='Ocorrências por Período do Dia')

col4.plotly_chart(fig_periodo_dia_ocorrencia,use_container_width=True)


#col 5

if df_filtered_by_municipio.empty:   
    df_furto_roubo = df[df['ACAO OBJETO'].isin(['FURTADO', 'ROUBADO'])]
else:
    df_furto_roubo = df_filtered_by_municipio[df_filtered_by_municipio['ACAO OBJETO'].isin(['FURTADO', 'ROUBADO'])]

quant_incidente_tipo = df_furto_roubo['ACAO OBJETO'].value_counts().reset_index()
quant_incidente_tipo.columns = ['TIPO DE INCIDENTE', 'QUANTIDADE OCORRENCIA']

fig_quant_incidente_tipo = px.pie(quant_incidente_tipo, names='TIPO DE INCIDENTE', values='QUANTIDADE OCORRENCIA', hole=0.4, title='Porcentagem de Incidentes de Furto e Roubo')

fig_quant_incidente_tipo.update_traces(textposition='inside', textinfo='percent+label')

col5.plotly_chart(fig_quant_incidente_tipo,use_container_width=True)
