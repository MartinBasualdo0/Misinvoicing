# %% [markdown]
# # Importamos librerías y el csv

# %%
import pandas as pd
import plotly.express as px

# %%
df_producto=pd.read_csv('./data/expo_doc_completo.csv', 
                        encoding='Latin-1',
                        # sep=';', 
            dtype={'ncm':'str','CUIT':'str','empresa':'str','enmienda':'str','ncm_descri':'str','sim':'str','pais':'str','pais_descri':'str','dia':'str','mes':'str','anio':'str','sec':str}
            )

# %% [markdown]
# # Manipulación de los datos: "Wrangling"

# %%
# Correcciones de lectura
df_producto.pais_descri=df_producto.pais_descri.apply(lambda x: x.capitalize()) #Mayuscula a los países
df_producto.empresa=df_producto.empresa.apply(lambda x: x.lower()) #Minuscula en los nombres de las empresas

#Fob por tonelada importada
df_producto['fob_unitario_ton']=df_producto.fob/df_producto.pnet*1000 #Creo la variable del fob unitario x ton

# Fechas para usarlas en los graficos: Se usa más adelante
desde=df_producto.sort_values(['anio','mes','dia'], ascending=True)['anio'][0]
hasta=df_producto.sort_values(['anio','mes','dia'], ascending=True)['anio'].iloc[-1]

inicio=df_producto.sort_values(['anio','mes'],ascending=True).reset_index(drop=True).mes[0]+'/01/'+df_producto.sort_values(['anio','mes'],ascending=True).reset_index(drop=True).anio[0]
mes=int(df_producto.sort_values(['anio','mes'],ascending=True).reset_index(drop=True).mes.iloc[-1])+1
fin=str(mes)+'/01/'+df_producto.sort_values(['anio','mes'],ascending=True).reset_index(drop=True).anio.iloc[-1]
monthDates = pd.DataFrame({
    'fecha': pd.date_range(start=inicio, end=fin, freq='M').strftime('%m-%Y')
})

# %% [markdown]
# ## Funciones

# %%
#Recortar descripción del país. Sino queda muy largo
def recortar_descri(pais,largo=15):
    if len(pais)<=largo:
        return pais
    else: return str(pais[:largo]+'...')

#Funcion para precio de referencia a partir de una agrupación mensual. Dolares/kg mensuales
def precio_ref(df):
    df_mensual=df.groupby(['mes','anio'],as_index=False).sum().sort_values(['anio','mes'])
    df_mensual['fob_unitario_ton_ref']=df_mensual.fob/df_mensual.pnet*1000
    df=pd.merge(left=df,right=df_mensual[['anio','mes','fob_unitario_ton_ref']], on=['anio','mes'],how='left')
    df['fob_unitario_ton_capit']=df.fob_unitario_ton*df.fob_unitario_ton_ref.iloc[-1]/df.fob_unitario_ton_ref
    df['diferencia_ref']=df.fob_unitario_ton-df.fob_unitario_ton_ref
    df['diferencia_ref_capi']=df.fob_unitario_ton_capit-df.fob_unitario_ton_ref.iloc[-1]
    return df

# Filtra la base de datos por NCM
def ncm_filtro(df,ncm):
    df=df.loc[df.ncm==ncm].reset_index(drop=True)
    df['fecha']=df.mes+'-'+df.anio
    df=df.sort_values(['anio','mes','dia'],ascending=True).reset_index(drop=True)
    return precio_ref(df)

# Devuelve códigos sim derivados de las NCM
def sim_unique(ncm):
    return df_producto[df_producto.ncm==ncm].sim.unique()

#Filtra la base por NCM y código sim
def sim_filtro(df,ncm, sim='default', pais='default'):
    ncm=str(ncm)
    if sim=='default' and pais=='default':
        return ncm_filtro(df,ncm)
    elif sim=='default' and pais!='default':
        pais=pais.capitalize()
        return ncm_filtro(df,ncm)[ncm_filtro(df,ncm).pais_descri==pais].reset_index(drop=True)
    elif sim!='default' and pais=='default':
        return ncm_filtro(df,ncm)[ncm_filtro(df,ncm).sim==sim].reset_index(drop=True)
    else: 
        pais=pais.capitalize()
        return ncm_filtro(df,ncm)[(ncm_filtro(df,ncm).sim==sim)&(ncm_filtro(df,ncm).pais_descri==pais)].reset_index(drop=True)

#Filtra por el top N países    
def get_top_paises(df, n_paises='default'):
    if n_paises=='default': return df
    else:
        top_df=df.groupby(['pais','pais_descri'],as_index=False).sum().sort_values('fob',ascending=False).pais_descri.unique()[:n_paises]
        return df[df.pais_descri.isin(top_df)].reset_index(drop=True)

#Filtra por el top N empresas    
def get_top_empresas(df, n_empresas='default'):
    if n_empresas=='default': return df
    else:
        top_df=df.groupby(['cuit','empresa'],as_index=False).sum().sort_values('fob',ascending=False).empresa.unique()[:n_empresas]
        return df[df.empresa.isin(top_df)].reset_index(drop=True)

#Recorta la descripcion de la nomenclatura para que no sea muy larga    
def get_descri_nomen(df, palabras:int = 15):
    '''Entra lista de dataFrames y numero maximo de palabras'''
    for d in df.ncm_descri.unique():
        if type(d)!=float:
            if len(d.split(' '))>palabras:
                a=' '.join(d.split(' ')[:palabras])
                return a+'...'
            else: 
                return d

# %% [markdown]
# # Gráficos
# 
# Aclaración:
# 
# - df es la dataframe que manipula, siempre debe ser df_producto. 
# 
# - ncm es la nomenclatura a 8 dígitos. 
# 
# - y es la variable que se va a graficar en el eje y. Puede ser "diferencia_ref" (por defecto) o "fob_unitario_ton", dependiendo de lo que se busque ver. Opcional.
# 
# - sim es el codigo sim de la nomenclatura. Opcional.
# 
# - n_paises es el top n paises que se quiera ver. Están ordenados según FOB exportados. Opcional. 
# 
# - n_empresa es el top n empresas que se quiera ver. Ordenadas según FOB exportados. Opcional.
# 
# - color es la variable categorica que se quiera ver. O son las empresas ('empresas') o los países ('pais_descri). Opcional. 
# 
# - pais es el pais de destino que se quiera analizar. Filtra la base y muestra los resultados para ese país únicamente. Opcional.
# 

# %%
def precio_violinplot_capitalizado(df,ncm,sim='default', n_paises='default', max_range=None):
     ncm=str(ncm)
     df=sim_filtro(df,ncm,sim)
     df=get_top_paises(df,n_paises)
     df.pais_descri=df.pais_descri.apply(recortar_descri)
     producto=df.ncm_descri.unique()[0][:40]
     ncm=df.ncm.unique()[0]
     category_orders={}
     # color=[0]*len(df.pais)
     if sim=='default' and n_paises=='default':
          title_text=f'FOB por tonelada exportada {desde}-{hasta} de: <br>"{get_descri_nomen(df,9)}"<br>NCM:{ncm}<br> <sup> Capitalizado al último precio disponible. Precio de referencia a partir de datos mensuales'     
     elif sim=='default' and n_paises!='default':
          # color='pais_descri'
          category_orders={'pais_descri': df.groupby(['pais','pais_descri'],as_index=False).sum().sort_values('fob',ascending=False).pais_descri.unique()}
          # x='pais_descri'
          title_text=f'FOB por tonelada exportada {desde}-{hasta} de: <br>"{get_descri_nomen(df,12)}"<br>NCM:{ncm}<br> <sup> Capitalizado al último precio disponible. Precio de referencia a partir de datos mensuales, top {n_paises} países'
     elif sim!='default' and n_paises=='default':
          title_text=f'FOB por tonelada exportada {desde}-{hasta} de: <br>"{get_descri_nomen(df,12)}"<br>NCM:{ncm}-{sim}<br> <sup> Capitalizado al último precio disponible. Precio de referencia a partir de datos mensuales'
     elif sim!='default' and n_paises!='default':
          color='pais_descri'
          category_orders={'pais_descri': df.groupby(['pais','pais_descri'],as_index=False).sum().sort_values('fob',ascending=False).pais_descri.unique()}
          # x='pais_descri'
          title_text=f'FOB por tonelada exportada {desde}-{hasta} de: <br>"{get_descri_nomen(df,12)}"<br>NCM:{ncm}-{sim}<br> <sup> Capitalizado al último precio disponible. Precio de referencia a partir de datos mensuales, top {n_paises} países'
            
     if max_range:
          df = df[df.fob_unitario_ton_capit<max_range]
          

     violinplot=px.violin(
     data_frame = df.round(1),
     x='pais_descri',
     y='fob_unitario_ton_capit',
     category_orders=category_orders,
     box = True,
     points= 'all',
     color='pais_descri',
          labels={
          "pais_descri": "Destino",
          'fob_unitario_ton': 'Precio',
          'fob_unitario_ton_capit':'Precio capitalizado',
          'fob':'Fob',
          'pnet':'Kg',
          'fecha':'Fecha',
          'fob_unitario_ton_ref': 'Precio de referencia',
          'diferencia_ref':'Spread',
          'empresa':'Exportador',
          'docu':'Documento'
          },
     hover_data={'pais_descri',
                 'fecha',
                 'docu',
                 'sec',
                 'sim',
                    'fob_unitario_ton',
                    'fob_unitario_ton_capit',
                    'fob_unitario_ton_ref',
                    'diferencia_ref',
                    'empresa',
                    'fob',
                    'pnet'       
                                   }
     )

     violinplot.update_yaxes(title_text= 'Fob unitario', 
                                   # range=[producto['fob_unitario_ton_capit'].min()-100,producto['fob_unitario_ton_capit'].max()+100]
                                   )
     violinplot.update_xaxes(title_text='')

     violinplot.update_layout(separators=',.', font_family='Georgia', font_size=13,
                                   height=500, width=800,
                                   template = 'none',
                                   title=dict(text=title_text,
                                              y=0.95),
                                   # title_text=title_text,
                                   showlegend=False,
                                   margin=dict(t=150))
     
     violinplot.add_hline(y=df.fob_unitario_ton_ref.iloc[-1],line_dash="dash",line_color="blue")

     return violinplot

# %%
def precio_boxplot_capitalizado(ncm,df=df_producto,sim='default', n_paises='default', max_range=None):
     ncm=str(ncm)
     df=sim_filtro(df,ncm,sim)
     df=get_top_paises(df,n_paises)
     producto=df.ncm_descri.unique()[0][:40]
     ncm=df.ncm.unique()[0]
     if sim=='default' and n_paises=='default':
          title_text=f'FOB por tonelada exportada {desde}-{hasta} de: <br>"{get_descri_nomen(df,9)}"<br>NCM:{ncm}<br> <sup> Capitalizado al último precio disponible. Precio de referencia a partir de datos mensuales'     
     elif sim=='default' and n_paises!='default':
          title_text=f'FOB por tonelada exportada {desde}-{hasta} de: <br>"{get_descri_nomen(df,12)}"<br>NCM:{ncm}<br> <sup> Capitalizado al último precio disponible. Precio de referencia a partir de datos mensuales, top {n_paises} países'
     elif sim!='default' and n_paises=='default':
          title_text=f'FOB por tonelada exportada {desde}-{hasta} de: <br>"{get_descri_nomen(df,12)}"<br>NCM:{ncm}-{sim}<br> <sup> Capitalizado al último precio disponible. Precio de referencia a partir de datos mensuales'
     elif sim!='default' and n_paises!='default':
          title_text=f'FOB por tonelada exportada {desde}-{hasta} de: <br>"{get_descri_nomen(df,12)}"<br>NCM:{ncm}-{sim}<br> <sup> Capitalizado al último precio disponible. Precio de referencia a partir de datos mensuales, top {n_paises} países'
     if max_range:
          df = df[df.fob_unitario_ton_capit<max_range]       
     precio_soja_boxplot=px.box(
     df.round(1),
     # x='fecha',
     x='fob_unitario_ton_capit',
     # color='fecha',
     labels={
          "pais_descri": "Destino",
          'fob_unitario_ton': 'Precio',
          'fob_unitario_ton_capit':'Precio capitalizado',
          'fob':'Fob',
          'pnet':'Kg',
          'fecha':'Fecha',
          'fob_unitario_ton_ref': 'Precio de referencia',
          'diferencia_ref':'Spread',
          'empresa':'Exportador',
          'docu':'Documento'
          },
     hover_data={'pais_descri',
                 'fecha',
                 'docu',
                 'sec',
                 'sim',
                    'fob_unitario_ton',
                    'fob_unitario_ton_capit',
                    'fob_unitario_ton_ref',
                    'diferencia_ref',
                    'empresa',
                    'fob',
                    'pnet'       
                                   }
     )

     precio_soja_boxplot.update_yaxes(title_text= '', 
                                   # range=[producto['fob_unitario_ton_capit'].min()-100,producto['fob_unitario_ton_capit'].max()+100]
                                   )
     precio_soja_boxplot.update_xaxes(title_text='Fob unitario')

     precio_soja_boxplot.update_layout(separators=',.', font_family='Georgia', font_size=13,
                                   height=400, width=750,
                                   template = 'none',
                                   title=dict(text=title_text,
                                              y=0.95),
                                   # title_text=title_text,
                                   showlegend=False,
                                   margin=dict(t=150))
     
     precio_soja_boxplot.add_vline(x=df.fob_unitario_ton_ref.iloc[-1],line_dash="dash",line_color="blue")

     return precio_soja_boxplot

def plot_precio(df,ncm,y='diferencia_ref',sim='default', n_paises='default', n_empresa='default' ,color='pais_descri',pais='default',max_range=None):
     '''color=pais_descri o empresa
     y='diferencia_ref' o  fob_unitario_ton'''
     ncm=str(ncm)
     df=sim_filtro(df,ncm,sim,pais)
     df=get_top_paises(df,n_paises)
     df=get_top_empresas(df,n_empresa)
     df.pais_descri=df.pais_descri.apply(recortar_descri)
     df.empresa=df.empresa.apply(recortar_descri)
     producto=df.ncm_descri.unique()[0][:40]
     ncm=df.ncm.unique()[0]
     if sim=='default' and n_paises=='default':
          title_text=f'FOB por tonelada exportada {desde}-{hasta} de: <br>"{get_descri_nomen(df,9)}"<br>NCM:{ncm}<br> <sup> Precio de referencia a partir de datos mensuales'     
     elif sim=='default' and n_paises!='default':
          title_text=f'FOB por tonelada exportada {desde}-{hasta} de: <br>"{get_descri_nomen(df,12)}"<br>NCM:{ncm}<br> <sup> Precio de referencia a partir de datos mensuales, top {n_paises} países'
     elif sim!='default' and n_paises=='default':
          title_text=f'FOB por tonelada exportada {desde}-{hasta} de: <br>"{get_descri_nomen(df,12)}"<br>NCM:{ncm}-{sim}<br> <sup> Precio de referencia a partir de datos mensuales'
     elif sim!='default' and n_paises!='default':
          title_text=f'FOB por tonelada exportada {desde}-{hasta} de: <br>"{get_descri_nomen(df,12)}"<br>NCM:{ncm}-{sim}<br> <sup> Precio de referencia a partir de datos mensuales, top {n_paises} países'
     
     if n_empresa != 'default':
          title_text=title_text+f', top {n_empresa} empresas'
     if pais != 'default':
          title_text=title_text+f'. Destino: {pais.capitalize()}'
          
     if y== 'diferencia_ref':  y_title='Diferencia en USD'
     elif y== 'fob_unitario_ton': y_title='FOB por tonelada'         
     
     if max_range:
          df = df[df[y]<max_range]
                 
     precio_soja_plot=px.scatter(
     df.round(1),
     x='fecha',
     y=y,
     color=color,
     category_orders={"fecha": monthDates.fecha,
                      'empresa': df.empresa.sort_values(ascending=True),},
     labels={
          "pais_descri": "Destino",
          'fob_unitario_ton': 'Precio',
          'fob_unitario_ton_capit':'Precio capitalizado',
          'fob':'Fob',
          'pnet':'Kg',
          'fecha':'Fecha',
          'fob_unitario_ton_ref': 'Precio de referencia',
          'diferencia_ref':'Spread',
          'empresa':'Exportador',
          'docu':'Documento'
          },
     hover_data={'pais_descri',
                 'fecha',
                 'docu',
                 'sec',
                 'sim',
                    'fob_unitario_ton',
                    # 'fob_unitario_ton_capit',
                    'fob_unitario_ton_ref',
                    'diferencia_ref',
                    'empresa',
                    'fob',
                    'pnet'       
                                   }
     )


     precio_soja_plot.update_yaxes(title_text= y_title, 
                                   # range=[df['diferencia_ref'].min()-100,df['diferencia_ref'].max()+100]
                                   )
     precio_soja_plot.update_xaxes(title_text='',type='category')

     precio_soja_plot.update_traces(marker=dict(size=12,
                                   line=dict(width=2,
                                             color='DarkSlateGrey')),
                    selector=dict(mode='markers'))

     precio_soja_plot.update_layout(separators=',.', font_family='Georgia', font_size=13,
                                   height=700, width=900,
                                   template = 'none',
                                   title=dict(text=title_text,
                                              y=0.95),
                                   # title_text=title_text,
                                   # showlegend=False,
                                   margin=dict(t=150))
                                   

     return precio_soja_plot

