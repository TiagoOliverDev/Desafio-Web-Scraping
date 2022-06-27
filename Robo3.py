from dataclasses import field
from unittest import result
from numpy import size, str0
from playwright.sync_api import sync_playwright
from datetime import date, datetime
import time
import requests
from bs4 import BeautifulSoup
import pandas as pd
import json
from urllib.error import URLError, HTTPError

class Robo3:

    with sync_playwright() as p:
        browser = p.chromium.launch(headless= False, slow_mo=50)
        page = browser.new_page()
        
        try:
            page.goto("https://www.contabeis.com.br/conteudo/")
            print('\nURL acessada com sucesso!')           
        except HTTPError as erro:
            print('Erro de requisição HTTP: ' + erro.status, erro.reason)
        except URLError as erro:
            print('Erro ao acessar a URL: '+ erro.reason)

        time.sleep(2)
        html_content = page.inner_html('li.ativo') #Marcação da section Pai
        time.sleep(2)
    
        soup = BeautifulSoup(html_content, 'html.parser') #Parseando os dados para deixar mais organizado

        teste = soup.find("a", attrs={"class": "editoria-contabil"})
        teste2 = teste.attrs
        teste3 = teste2['href']
       # print(teste2)
       # print(teste3)
        try:
            page.goto("https://www.contabeis.com.br/"+teste3) #Acessando URL novamente para poder redirecionar para a página só de conteúdos contábeis
            time.sleep(2)          
        except HTTPError as erro:
            print('Erro de requisição HTTP: ' + erro.status, erro.reason)
        except URLError as erro:
            print('Erro ao acessar a URL: '+ erro.reason)
        
        html_content2 = page.inner_html('div.tituloInterno') #Marcação da section Pai
        soup2 = BeautifulSoup(html_content2, 'html.parser') 
        #print(soup2)
        parte01Categoria = soup2.em.get_text()
        parte02Categoria = soup2.b.get_text()
        categoria = parte01Categoria + ' ' + parte02Categoria #Unificando titulo da categoria contábil
        #print(parte01Categoria)
        #print(parte02Categoria)
        #print(categoria)

        html_content3 = page.inner_html('section.materiasList') #Marcação da section Pai
        time.sleep(2)

        soup3 = BeautifulSoup(html_content3, 'html.parser')

        try:
            postCont = []
            for posts in soup3.find_all("article", attrs={"class": "editoria-contabil"}):
                #print(post)
                content = []

                categoriaPost = categoria
                titulo = posts.strong.get_text()
                subTitulo = posts.h2.get_text()
                data = posts.em.get_text()
                linkImage = posts.img['data-src']  #Pegando o src da imagem
                linkImageCompleto = 'https://www.contabeis.com.br/'+linkImage #Unificando dominio com src da imagem para gerar um link
                linkPostagem = posts.ul['href']

                content.append(categoriaPost)
                content.append(titulo) 
                content.append(subTitulo) 
                content.append(data)  
                content.append(linkImageCompleto)
                content.append(linkPostagem)
                
                postCont.append(content) 

                print('------------------***********************------------------')
                print(categoriaPost)
                print(titulo)
                print(subTitulo)
                print(data)    
                print(linkImageCompleto)     
                print(linkPostagem)
                print('------------------***********************------------------')

        except:
            print("\nErro na estrutura de percorrer e capturar dados da página!")


        try:
            dados_df = pd.DataFrame(postCont, columns=['Categoria', 'Titulo', 'SubTitulo', 'Data', 'LinkImage', 'LinkPostagem'])
           
            print(dados_df)
                                        
            size = len(dados_df)
            print('\nsize:', size)
     
          
        except:
            print("\nErro na estrutura de DataFrame!")

        try:
            #Criando dicionario para o df
            dadosDicionario = {}
            dadosDicionario['Dados'] = dados_df.to_dict('records')
            #print(dadosDicionario)
           
        except:
            print("\nErro na estrutura de criação de dicionário para o DataFrame!")
        
        browser.close()
        
        try:
            #Converter e criar arquivo json
            js = json.dumps(dadosDicionario)
            fp = open('dadosContabilidadeCompleto.json', 'w')
            fp.write(js)
            fp.close()
            print("\nArquivo JSON criado com sucesso!")
        except:
            print("\nErro na estrutura de converção para arquivo JSON!")
   


       