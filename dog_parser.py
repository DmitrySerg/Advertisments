# -*- coding: utf-8 -*-
"""
Created on Mon Jun 13 20:02:20 2016

@author: Auditore
"""

import requests
import re
from bs4 import BeautifulSoup
import pandas as pd
import time
from datetime import datetime



def html_stripper(text):
    return re.sub('<[^<]+?>', '', str(text))
 
month = ['января','февраля','марта','апреля','мая','июня','июля','августа','сентября','октября','ноября','декабря']
order = {M: i+1 for i,M in enumerate(month)}
def date_helper(day, month):
    month = order[month]
    dateobject =  datetime(2016,int(month),int(day))  
    return dateobject
    
    
main_url = 'https://www.avito.ru'
url_begin = 'https://www.avito.ru/moskva/sobaki?p='
url_end = '&s=1'


doggy_data = pd.DataFrame()
number_of_pages = 541

count = len(doggy_data)-1
for j in range(number_of_pages+1):   
    start = time.time()
    url = url_begin+str(j)+url_end
    
    response = requests.get(url)
    html = response.content
    soup = BeautifulSoup(html)
    
    
    
    #### Получаем с текущей страницы все имеющиеся ссылки на собачек
    title_urls = soup.findAll('a', attrs={'class':'item-description-title-link'})
    
    #### Итерируем по всем ссылкам, получая информацию о всех собачках этой страницы
    for title_url in title_urls:
        count += 1
        #### Переходим на ссылку собачки
        dog_url = main_url + re.split('href="|" title=|">\n', str(title_url))[1]
        dog_page = requests.get(dog_url)
        dog_page = dog_page.content
        dog_page = BeautifulSoup(dog_page)
        
        #### Получаем идентификатор объявления 
        dog_id = dog_page.findAll('div', attrs={'class':'item-sku'})
        dog_id = int(re.split('"item_id">|</span>', str(dog_id))[1])
        
        #### Получаем количество просмотров
        try:
            num_views = str(dog_page.find('div', attrs={'class':'item-views'}))
            num_views = int(re.split('Просмотров: всего\xa0|,', num_views)[1])
        except:
            num_views = dog_page.find('span', attrs={'class':'js-show-stat pseudo-link'})
            num_views = int(re.split('всего\xa0|,', html_stripper(num_views))[1])
            
        #### Получаем цену
        price = str(dog_page.find('span', attrs={'p_i_price'}))
        price = re.split('"price">\n  | руб', price)[1]
        price_fin = ''
        for i in price: # чтобы не выскакивала ошибка при суммах >1 000
            if i.isnumeric():
                price_fin+=i
        try:
            price = int(price_fin)
        except:
            price = "NA"
            
        #### Получаем заголовок
        title = dog_page.find('h1', attrs={'class':'h1'})
        title = html_stripper(title)
        
        #### Получаем описание
        description = dog_page.find('div', attrs={'class':'description description-text'})
        description = html_stripper(description)
        
        #### Получаем дату создания объявления
        create_date = dog_page.find('div', attrs={'class':'item-subtitle'})
        create_date = html_stripper(create_date).split()
        
        if "сегодня" in create_date:
            create_date = datetime(2016, 6, 13)
        elif 'вчера' in create_date:
            create_date = datetime(2016, 6, 12)
        else:
            create_date = date_helper(create_date[1], create_date[2])
        
        
        doggy_data.loc[count, 'index'] = dog_id
        doggy_data.loc[count, 'num_views'] = num_views
        doggy_data.loc[count, 'price'] = price
        doggy_data.loc[count, 'description'] = description
        doggy_data.loc[count, 'title'] = title
        doggy_data.loc[count, 'create_date'] = create_date
        
    print("Time elapsed for",str(j),"page:", round((time.time()-start)/60, 4))   
        
    
doggy_data.to_csv('C:\\Users\\Auditore\\Desktop\\doggy_data.csv', sep=',', header=True)    
