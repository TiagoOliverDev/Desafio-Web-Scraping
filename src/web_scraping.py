from playwright.sync_api import sync_playwright
import time
from bs4 import BeautifulSoup
import pandas as pd
import json
from urllib.error import URLError, HTTPError
import os


class Web_scraping:

    def acessar_url(self, page, url):
        try:
            page.goto(url)
            print('\nURL acessada com sucesso!')           
        except HTTPError as erro:
            print('Erro de requisição HTTP: ' + erro.status, erro.reason)
        except URLError as erro:
            print('Erro ao acessar a URL: '+ erro.reason)

    def parsear_html(self, html_content):
        return BeautifulSoup(html_content, 'html.parser')

    def coletar_dados_da_pagina(self, page, selector):
        html_content = page.inner_html(selector)
        return html_content

    def criar_dataframe(self, postCont):
        try:
            dados_df = pd.DataFrame(postCont, columns=['Categoria', 'Titulo', 'SubTitulo', 'Data', 'LinkImage', 'LinkPostagem'])
            print(dados_df)
            size = len(dados_df)
            print('\nsize:', size)
            return dados_df
        except:
            print("\nErro na estrutura de DataFrame!")
            return None

    def criar_dicionario_para_df(self, dados_df):
        try:
            dadosDicionario = {}
            dadosDicionario['Dados'] = dados_df.to_dict('records')
            return dadosDicionario
        except:
            print("\nErro na estrutura de criação de dicionário para o DataFrame!")
            return None

    def converter_para_json(self, dadosDicionario):
        try:
            js = json.dumps(dadosDicionario)
            if not os.path.exists('data'):
                os.makedirs('data')
            fp = open('data/dados_completo.json', 'w')
            fp.write(js)
            fp.close()
            print("\nArquivo JSON criado com sucesso! Olhe dentro da pasta 'data' na raiz do projeto.")
        except Exception as e:
            print("\nErro na estrutura de converção para arquivo JSON:", e)

    def fechar_browser(self, browser):
        browser.close()
        
    def executar_robo(self):
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False, slow_mo=50)
            page = browser.new_page()

            self.acessar_url(page, "https://www.contabeis.com.br/conteudo/")

            time.sleep(2)

            html_content = self.coletar_dados_da_pagina(page, 'li.ativo')

            soup = self.parsear_html(html_content)

            link = soup.find("a", attrs={"class": "editoria-contabil"})
            link2 = link.attrs
            link3 = link2['href']

            self.acessar_url(page, "https://www.contabeis.com.br/"+link3)

            html_content2 = self.coletar_dados_da_pagina(page, 'div.tituloInterno')

            soup2 = self.parsear_html(html_content2)

            parte01Categoria = soup2.em.get_text()
            parte02Categoria = soup2.b.get_text()
            categoria = parte01Categoria + ' ' + parte02Categoria

            html_content3 = self.coletar_dados_da_pagina(page, 'section.materiasList')

            time.sleep(2)

            soup3 = self.parsear_html(html_content3)

            postCont = []

            try:
                for posts in soup3.find_all("article", attrs={"class": "editoria-contabil"}):
                    content = []

                    categoriaPost = categoria
                    titulo = posts.strong.get_text()
                    subTitulo = posts.h2.get_text()
                    data = posts.em.get_text()
                    linkImage = posts.img['data-src']
                    linkImageCompleto = 'https://www.contabeis.com.br/'+linkImage
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

            dados_df = self.criar_dataframe(postCont)

            if dados_df is not None:
                dadosDicionario = self.criar_dicionario_para_df(dados_df)

                if dadosDicionario is not None:
                    self.converter_para_json(dadosDicionario)

            self.fechar_browser(browser)

