from os import link
from playwright.sync_api import sync_playwright
import time
from bs4 import BeautifulSoup
import pandas as pd
import json
from urllib.error import URLError, HTTPError

class Robo3:

    with sync_playwright() as p:
        browser = p.chromium.launch(headless= False, slow_mo=50)
        page = browser.new_page()
        
        try:
            page.goto("https://www.contabeis.com.br/conteudo/") #Acessando URL
            print('\nURL acessada com sucesso!')           
        except HTTPError as erro:
            print('Erro de requisição HTTP: ' + erro.status, erro.reason)
        except URLError as erro:
            print('Erro ao acessar a URL: '+ erro.reason)

        time.sleep(2)
        html_content = page.inner_html('li.ativo') #Marcação da section Pai
        time.sleep(2)
    
        soup = BeautifulSoup(html_content, 'html.parser') #Parseando os dados para deixar mais organizado

        link = soup.find("a", attrs={"class": "editoria-contabil"}) #Pegando redirecionamento para a página que contém somente conteúdos de contabilidade
        link2 = link.attrs 
        link3 = link2['href'] # Pegando somente o href do redirecionamento

        try:
            page.goto("https://www.contabeis.com.br/"+link3) #Unindo URL e ccessando URL novamente para poder redirecionar para a página só de conteúdos contábeis
            time.sleep(2)          
        except HTTPError as erro:
            print('Erro de requisição HTTP: ' + erro.status, erro.reason)
        except URLError as erro:
            print('Erro ao acessar a URL: '+ erro.reason)
        
        html_content2 = page.inner_html('div.tituloInterno') #Marcação da section Pai
        soup2 = BeautifulSoup(html_content2, 'html.parser')  #Parseando

        parte01Categoria = soup2.em.get_text() #Pegando somente o text da tag em
        parte02Categoria = soup2.b.get_text()  #Pegando somente o text da tag b
        categoria = parte01Categoria + ' ' + parte02Categoria #Unificando categoria da categoria contábil

        html_content3 = page.inner_html('section.materiasList') #Marcação da section Pai
        time.sleep(2)

        soup3 = BeautifulSoup(html_content3, 'html.parser')

        try:
            postCont = [] #Lista vazia
            for posts in soup3.find_all("article", attrs={"class": "editoria-contabil"}): #Percorrendo a tag article de class editoria-contabil
                content = []

                categoriaPost = categoria          #Pegando a categoria já unificada
                titulo = posts.strong.get_text()   #Pegando somente o text da tag strong
                subTitulo = posts.h2.get_text()    #Pegando somente o text da tag h2
                data = posts.em.get_text()         #Pegando somente o text da tag em
                linkImage = posts.img['data-src']  #Pegando somente o data-src da tag img (pedaço de link da imagem)
                linkImageCompleto = 'https://www.contabeis.com.br/'+linkImage #Unificando dominio com data-src da imagem para gerar um link válido da imagem
                linkPostagem = posts.ul['href']    #Pegando o link da postagem

                #Adicionando todos os dados dentro da lista content
                content.append(categoriaPost)
                content.append(titulo) 
                content.append(subTitulo) 
                content.append(data)  
                content.append(linkImageCompleto)
                content.append(linkPostagem)
                
                #Adicionando a lista content dentro da lista postCont
                postCont.append(content) 

                #Testes de print
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
            #Criação do dataframe usando pandas
            dados_df = pd.DataFrame(postCont, columns=['Categoria', 'Titulo', 'SubTitulo', 'Data', 'LinkImage', 'LinkPostagem'])
           
            print(dados_df)

            #Pegando o size dos elementos do dataframe (não consegui deixar dentro do JSON)                                 
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
        
        browser.close() #Fechando o browser
        
        try:
            #Converter e criar arquivo json
            js = json.dumps(dadosDicionario)
            fp = open('dadosContabilidadeCompleto.json', 'w')
            fp.write(js)
            fp.close()
            print("\nArquivo JSON criado com sucesso!")
        except:
            print("\nErro na estrutura de converção para arquivo JSON!")
   


       