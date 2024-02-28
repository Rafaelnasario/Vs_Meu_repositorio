#!/usr/bin/env python
# coding: utf-8

# In[ ]:


### Curso de Python para Finanças Quantitativas

#### Aula 9 - Estratégia do Diamante
#### Autor: Leandro Guerra - Outspoken Market
#### Download em: https://www.outspokenmarket.com/pythonfinancasquantitativas.html


# ![image.png](attachment:image.png)
# 

# In[1]:


import pandas as pd
import numpy as np
from datetime import datetime
import yfinance as yf
import matplotlib.pyplot as plt


# In[2]:


plt.style.use("fivethirtyeight")
# https://matplotlib.org/stable/gallery/style_sheets/style_sheets_reference.html


# In[3]:


# Carrega a base
ticker = "ITSA4.SA"
df = yf.download(ticker, "2010-01-01", "2021-12-31")

df


# In[4]:


# Cria as médias móveis para o diamante

p1 = 50
p2 = 200

df["MM_Curta"] = df["Adj Close"].rolling(window = p1).mean()
df["MM_Longa"] = df["Adj Close"].rolling(window = p2).mean()


# In[5]:


# Visualização

plt.figure(figsize=(12.5,4.5))
plt.plot(df["Adj Close"], label = ticker, linewidth = 2, color = "blue")
plt.plot(df["MM_Curta"], label = "MM_Curta", linewidth = 2, color = "red")
plt.plot(df["MM_Longa"], label = "MM_Longa", linewidth = 2, color = "green")
plt.title(ticker +  " Fechamento")
plt.xlabel("2018 à 2021")
plt.ylabel("Cotação")
plt.legend(loc = "lower right")
plt.show()


# In[6]:


# Cria a lógica das 6 fases do diamante

#Fase de aviso
df["Diamante"] = np.where(
                        ((df["Adj Close"] < df["MM_Curta"]) # Condiçao 1
                         & (df["Adj Close"] > df["MM_Longa"]) # Condiçao 2
                         & (df["MM_Curta"] > df["MM_Longa"]) # Condiçao 3
                        )
                        , "Fase_Aviso", "Nada"
                        )

#Fase de Distribuição
df["Diamante"] = np.where(
                        ((df["Adj Close"] < df["MM_Curta"])
                         & (df["Adj Close"] < df["MM_Longa"])
                         & (df["MM_Curta"] > df["MM_Longa"])
                        )
                        , "Fase_Distribuição", df["Diamante"]
                        )

#Fase Baixista
df["Diamante"] = np.where(
                        ((df["Adj Close"] < df["MM_Curta"])
                         & (df["Adj Close"] < df["MM_Longa"])
                         & (df["MM_Curta"] < df["MM_Longa"])
                        )
                        , "Fase_Baixista", df["Diamante"]
                        )

#Fase de Recuperação 
df["Diamante"] = np.where(
                        ((df["Adj Close"] > df["MM_Curta"])
                         & (df["Adj Close"] < df["MM_Longa"])
                         & (df["MM_Curta"] < df["MM_Longa"])
                        )
                        , "Fase_Recuperação", df["Diamante"]
                        )

#Fase de Acumulação 
df["Diamante"] = np.where(
                        ((df["Adj Close"] > df["MM_Curta"])
                         & (df["Adj Close"] > df["MM_Longa"])
                         & (df["MM_Curta"] < df["MM_Longa"])
                        )
                        , "Fase_Acumulação", df["Diamante"]
                        )

#Fase de Altista
df["Diamante"] = np.where(
                        ((df["Adj Close"] > df["MM_Curta"])
                         & (df["Adj Close"] > df["MM_Longa"])
                         & (df["MM_Curta"] > df["MM_Longa"])
                        )
                        , "Fase_Altista", df["Diamante"]
                        )


# In[7]:


# Ajustando a definição de "Lado de vendas" ou "Lado de compras"

df["Lado"] = np.where(
                        ((df["Diamante"] == "Fase_Recuperação")
                         | (df["Diamante"] == "Fase_Acumulação")
                         | (df["Diamante"] == "Fase_Altista")
                        )
                        , "Lado_de_Compras", "Lado_de_Vendas"
                        )


# In[9]:


df.dropna(inplace = True)
df.tail()


# In[10]:


# Construção dos alvos

# Alvo 1 - Retorno
df["Retorno"] = df["Adj Close"].pct_change(1)*100
df["Alvo1"] = df["Retorno"].shift(-1)

# Alvo 5 - Retorno
df["Retorno5"] = df["Adj Close"].pct_change(5)*100
df["Alvo5"] = df["Retorno5"].shift(-5)

# Alvo 10 - Retorno
df["Retorno10"] = df["Adj Close"].pct_change(10)*100
df["Alvo10"] = df["Retorno10"].shift(-10)

# Criacao dos alvos categoricos
df["Alvo1_cat"] = np.where(df["Alvo1"] > 0 , 1, 0)
df["Alvo5_cat"] = np.where(df["Alvo5"] > 0 , 1, 0)
df["Alvo10_cat"] = np.where(df["Alvo10"] > 0 , 1, 0)


# In[11]:


# Qual é a média dos retornos dos dias sucessivos

np.round(pd.pivot_table(df, index = ["Lado", "Diamante"]
               , aggfunc = {"Alvo1_cat" : np.mean
                            , "Alvo5_cat": np.mean
                            , "Alvo10_cat": np.mean}), 3)*100


# In[12]:


# Adicionando tudo em uma função

def diamante(ticker, inicio, fim, media_curta, media_longa, alvo):
    df = yf.download(ticker, inicio, fim);
    df["MM_Curta"] = df["Adj Close"].rolling(window = media_curta).mean()
    df["MM_Longa"] = df["Adj Close"].rolling(window = media_longa).mean()
    # Cria a lógica das 6 fases do diamante

    #Fase de aviso
    df["Diamante"] = np.where(
                        ((df["Adj Close"] < df["MM_Curta"])
                         & (df["Adj Close"] > df["MM_Longa"])
                         & (df["MM_Curta"] > df["MM_Longa"])
                        )
                        , "1-Fase_Aviso", "Nada"
                        )

    #Fase de Distribuição
    df["Diamante"] = np.where(
                        ((df["Adj Close"] < df["MM_Curta"])
                         & (df["Adj Close"] < df["MM_Longa"])
                         & (df["MM_Curta"] > df["MM_Longa"])
                        )
                        , "2-Fase_Distribuição", df["Diamante"]
                        )

    #Fase Baixista
    df["Diamante"] = np.where(
                        ((df["Adj Close"] < df["MM_Curta"])
                         & (df["Adj Close"] < df["MM_Longa"])
                         & (df["MM_Curta"] < df["MM_Longa"])
                        )
                        , "3-Fase_Baixista", df["Diamante"]
                        )

    #Fase de Recuperação 
    df["Diamante"] = np.where(
                        ((df["Adj Close"] > df["MM_Curta"])
                         & (df["Adj Close"] < df["MM_Longa"])
                         & (df["MM_Curta"] < df["MM_Longa"])
                        )
                        , "1-Fase_Recuperação", df["Diamante"]
                        )

    #Fase de Acumulação 
    df["Diamante"] = np.where(
                        ((df["Adj Close"] > df["MM_Curta"])
                         & (df["Adj Close"] > df["MM_Longa"])
                         & (df["MM_Curta"] < df["MM_Longa"])
                        )
                        , "2-Fase_Acumulação", df["Diamante"]
                        )

    #Fase de Altista
    df["Diamante"] = np.where(
                        ((df["Adj Close"] > df["MM_Curta"])
                         & (df["Adj Close"] > df["MM_Longa"])
                         & (df["MM_Curta"] > df["MM_Longa"])
                        )
                        , "3-Fase_Altista", df["Diamante"]
                        )
    df["Lado"] = np.where(
                        ((df["Diamante"] == "1-Fase_Recuperação")
                         | (df["Diamante"] == "2-Fase_Acumulação")
                         | (df["Diamante"] == "3-Fase_Altista")
                        )
                        , "Lado_de_Compras", "Lado_de_Vendas"
                        )
    df.dropna(inplace = True)
    # Construção do alvo
    df["Retorno"] = df["Adj Close"].pct_change(alvo)
    df["Alvo"] = df["Retorno"].shift(-alvo)
    # Criacao do alvo categórico
    df["Alvo_cat"] = np.where(df["Alvo"] > 0 , 1, 0)
    pivot = np.round(pd.pivot_table(df, index = ["Lado", "Diamante"]
               , aggfunc = {"Alvo" : np.mean
                            , "Alvo_cat": np.mean}), 3)*100
    status = " \n Última fase: " + df["Diamante"].iloc[-1]
    analise = "Análise para " + ticker + " de " + inicio + " à " + fim
    alvo_p = "Alvo de " + str(alvo) + " dias"
    return print( "\n" + analise), print( "\n" + alvo_p), print(pivot), print(status)


# ![image.png](attachment:image.png)
# 

# In[17]:


diamante("BBAS3.SA", "2005-01-01", "2022-12-31", 50, 200, 15)

