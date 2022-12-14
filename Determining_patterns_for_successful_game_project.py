#!/usr/bin/env python
# coding: utf-8

# # Определение закономерностей для успешности игры

# **Описание проекта**
# 
# Задание предлагает нам возможность почувствовать себя в роли сотрудника интернет-магазина "Стримчик". Мне из открытых данных известны исторические данные о продажах игр, оценки пользователей и экспертов, жанры и платформы (например, Xbox или PlayStation). Нам нужно выявить определяющие успешность игры закономерности. Это позволит сделать ставку на потенциально популярный продукт и спланировать рекламные кампании. Перед нами данные за 2016 год, т.о нам нужно найти некие закономерности чтобы определить дальнейшее развитие компании в 2017 году. 
# 
# В наборе данных попадается аббревиатура ESRB (Entertainment Software Rating Board) — это ассоциация, определяющая возрастной рейтинг компьютерных игр. ESRB оценивает игровой контент и присваивает ему подходящую возрастную категорию, например, «Для взрослых», «Для детей младшего возраста» или «Для подростков».
# 
# 1. [Открытие данных](#step1)
# 2. [Подготовка данных](#prep_data)
# 3. [Исследовательский анализ данных](#research_data)
# 4. [Составление портрета пользователя каждого региона](#portrait)
# 5. [Проверка гипотез](#check_hypo)
# 6. [Общий вывод](#common_out)

# <a id='step_1'></a>
# 
# # Шаг 1: Открытие файла  и изучение общей информации

# In[1]:


import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
from scipy import stats as st
import warnings
warnings.filterwarnings('ignore')


# In[2]:


df = pd.read_csv('./games.csv')


# In[3]:


df


# In[4]:


df.info()


# In[5]:


df.isna().any()


# In[6]:


df['Rating'].value_counts()


# Ссылка на источник данных с обозначением различных ESRB

# [Cслыка 1](https://www.esrb.org/ratings-guide/)
# [Ссылка 2](https://ru.wikipedia.org/wiki/Entertainment_Software_Rating_Board)

# ## Вывод по Шаг_1

# Видно, что в данных есть нули причём колонка `Name` содержит всего 2 нулевых позиции, надо обязательно на них посмотреть. Также видно что колонка `User_score` содержит данные в неправильном типе => нужно заменить на float64.
# Также можно заметить что в ячейке `Rating` устаревшие данные так согласно источникам K-A это старая версия нынешней E. Таким образом понимаем что нужно найти логичные замены для NaN изменить типы данных и заменить значения в колонках нужные, чем собственно и займемся в следующем раздделе (Шаг 2.)

# <a id = 'prep_data'></a>
# # Шаг 2: Подготовка данных

# ### Перевод строк к нижнему регистру

# Первое с чего начнем это с того что приведем все имена колонок к нижнему регистру. Так будет удобнее к ним обращаться

# In[7]:


df.columns = df.columns.str.lower()


# In[8]:


df


# ### Обработка колонки `year_of_release`

# Заменяем NaN в колонке `year_of_release`, которую я заполнил годом в зависимости от платформы, ведь в зависимости от того на какую платформу была выпущена игра, тогда и год выпуска будет ограничен самим сроком службы платформы на которую игры была выпущена. Также произведем замену типа колонки на int64, потому что мне не нравится что ноль стоит рядом с годом)) Также и на графиках это выглядит некрасиво

# In[9]:


df.loc[:, 'year_of_release'] = df.loc[:, 'year_of_release'].fillna(
    df.groupby('platform')['year_of_release'].transform('median')
)


# In[10]:


df


# In[11]:


df['year_of_release'] = df['year_of_release'].astype('int64')


# ### Обработка колонки `name`

# Посмотрим на данные из `name` соответвующие NaN

# In[12]:


df[df['name'].isna()]


# Скинем эти данные ибо в них вообще почти нет данных и вряд ли они как то исказят данные если их убрать

# In[13]:


df = df.dropna(subset=['name'])


# ### Обработка колонки `critic_score`

# Заменяем `critic_score` на нужный тип и заполняем пропущенные значения. Для этого я создаю колонку `sum_sales` чтобы понять влияет ли кол-во суммарных продаж на оценку критиков

# In[14]:


df['sum_sales'] = df[['na_sales','eu_sales','jp_sales','other_sales']].sum(axis=1)


# Делим данные по 25,50 и 75 квартилям чтобы разделить суммарные продажи на 3 категории

# In[15]:


print(df['sum_sales'].quantile(q=0.25), df['sum_sales'].quantile(q=0.5), df['sum_sales'].quantile(q=0.75))


# In[16]:


def type(row):
    sales = row['sum_sales']
    if sales <= 0.17:
        return "Низкий"
    elif sales > 0.17 and sales <= 0.47:
        return "Средний"
    else:
        return "Высокий"


# In[17]:


df['type_by_sum_sales'] = df.apply(type, axis=1)


# In[18]:


df


# In[19]:


df.groupby('type_by_sum_sales')['critic_score'].median().sort_values()


# Видно что в среднем есть зависимость от рейтинга выставленного критиками игры и ее сборов

# In[20]:


df.loc[:, 'critic_score'] = df.loc[:, 'critic_score'].fillna(
    df.groupby('type_by_sum_sales')['critic_score'].transform('median'))


# In[21]:


df.info()


# ### Обработка колонки `user_score`

# Сначала посмотрим на значения NaN в колонке `user_score`

# In[22]:


df[df['user_score'].isna()]


# In[23]:


df[df['user_score'].isna()]['type_by_sum_sales'].value_counts()


# In[24]:


df[df['user_score'].isna()]['rating'].isna().sum()


# In[25]:


df[df['user_score'] == 'tbd']


# In[26]:


df[df['user_score'] == 'tbd']["type_by_sum_sales"].value_counts()


# In[27]:


df[df['user_score'] == 'tbd']['rating'].isna().sum()


# Итак видно, что в колонке `user_score` есть значения tbd которые обозначаю to be determined, что означает что позже скоры сформируются. Если обрезать таблицу по этому значению(tbd) то у нас есть рейтинги а в колонке с NaN, у нас эти рейтинги отсутсвуют. Какая то должна быть между этими вещами связь. Возможно так как данные из открытых источников, то пишут их люди, а списки эти не автоматически как то генерируются. Достаточно логично, что в каких то участках значения не будут заполняться и будет появляться NAN в колонке `user_score` и `rating`, а если за описание этих данных взялись то заполняют сразу обе колонки `user_score` и `rating`. Поэтому мне кажется что можно заполнить и tbd и NaN средними значениями по колонке.
# 
# 
# 
# Мне стало интересно возможно получилось так что очень много фильмов категории E и их уже просто устали вбивать) Я поискал данные и нашел [данные](https://www.esrb.org/blog/e-for-everyone-continues-to-be-most-frequently-assigned-video-game-rating/) о том что среди всех видеоигр, E занимает лидирующую позицию, но как написано по ссылке, занимает это значение 49 % следовательно возможно стоит посмотреть может при замене NAN на E в колонке `user_score`

# In[28]:


df['user_score'].value_counts()


# In[29]:


df['user_score'] = df['user_score'].replace('tbd', 0)


# In[30]:


df['user_score'] = df['user_score'].fillna(0)


# In[31]:


df['user_score'] = df['user_score'].astype('float64')


# In[32]:


df[df['user_score'] == 0]


# In[33]:


df[df['user_score'] != 0 ].groupby('type_by_sum_sales')['user_score'].median()


# Видна зависимости типа суммы продаж от от выставленных юзерами оценок, заполним NaN осознавая этот факт

# In[34]:


df['user_score'].replace(0, np.nan, inplace=True)


# In[35]:


df['user_score'] = df['user_score'].fillna(df.groupby('type_by_sum_sales')['user_score'].transform('median'))


# In[36]:


df['user_score']


# ### Обработка колонки `rating`

# In[37]:


df.info()


# In[38]:


df['rating'].value_counts()


# Из [википедии](https://ru.wikipedia.org/wiki/Entertainment_Software_Rating_Board) следует что K-A эквивалентна E => будем заменять K-A на E из колонки `rating`, т.к К-А это старое обозначение E

# **Заменяем K-A из колонки `rating` на E**

# In[39]:


df.loc[:, 'rating'] = df.loc[:, 'rating'].replace('K-A', 'E')


# In[40]:


df['rating'].value_counts()


# **Обьяснение об отсутствие замены NAN**

# In[41]:


df


# In[42]:


df['rating'].isna().sum()


# Очень много нулей в колонке `rating`, но при этом такая колонка вряд ли с чем то коррелирует, т.е мы самостоятельно не можем присвоить ей значение в зависимости от каких то параметров. Посмотрим на распределение величин данной колонки.

# In[43]:


df['rating'].value_counts().plot.pie(
    title='Распределение категорий ESRB среди наших данных (col:"rating")', figsize=(10,10), autopct='%1.0f%%'
)
plt.show()


# Сделаем замену NaN на unknown, для дальнейшего анализа

# In[44]:


df['rating'] = df['rating'].fillna('Unknown')


# Я решил погуглить а нет ли общего распеределения для всех видеоигр вне зависимости от платформы. Я нашёл [статью](https://www.esrb.org/blog/e-for-everyone-continues-to-be-most-frequently-assigned-video-game-rating/) в которой видно такое распределение. Из неё следует что категория E является самым частым видов выпускаемых игр а именно составляем 49% . На нашем распределение видно похожий паттерн распределения, собственно видимо нам достаточно такого числа для описания всей генеральной совокупности игр. Но это все выводы какие как мне кажется можно привести. В угадайку играть и распределять значений ESRB мне кажется не очень хорошим явлением, поэтому в данной колонке будем довольствоваться тем что есть, а значения NAN оставим в покое.

# <a id = "research_data"></a>
# # Шаг3. Проведение исследовательского анализа данных

# Посмотрим сколько игр выпускалось в разные годы

# In[45]:


df.groupby('year_of_release')['name'].count().plot(
    kind='bar', figsize=(10,10), title='Распределение кол-ва выпущенных игр от года'
)

plt.show()


# Отвечая на вопрос важны ли нам данные за все периоды, скорее всего нет по сути нам лишь нужно выделить некий срез данных по которым можно строить хороший прогнозы

# Посмотрим как менялись продажи среди всех платформ по годам. Для этого возьмем 10 лидеров списка суммарных продаж и построим по ним распределение по годам, чтобы посмотреть продают ли на данный момент эти 10 лидеров всё также являются прибыльными и приносят денег и можно выявить лидеров по продажам за последние года, а также можно увидеть падает/убывает число проданных копий игры для каждой выбранной нами платформы 

# In[46]:


ind = df.groupby('platform')['sum_sales'].sum().sort_values(ascending=False).head(10).index


# In[47]:


new_df = df.pivot_table(index='year_of_release', columns='platform',values = 'sum_sales', aggfunc='sum')


# In[48]:


new_df[[i for i in ind]].dropna(axis=1, how='all').plot(
    figsize=(15,28), subplots=True, kind='bar', title='Распределение годов от суммарной прибыли')
plt.show()


# Почти все 10 лидеров по продажам за весь период являются устаревшими платформами пора который уже прошла а продажи катятся стремительно вниз. Поэтому посмотрим какие платформы были лидерами не за весь период а за 2016 предыдущий год например, ведь скорее всего лидеры 2016 года скорее всего останутся лиерами до прихода более новых платформ, таким образом мы сможем ограничить круг потенциально перспективных платформ, с которыми собственно стоит работать дальше нежели со старыми данными.

# In[49]:


new_df.loc[2016].dropna().sort_values(ascending=False)


# Постмотрели на продажи за 2016 год и видны фавориты: PS4, XOne, 3DS. Эти платформы являются фаворитами и превосходят ближайших конкурентов минимум на 3 порядка. Дальше посмотрим как распрелялось кол-во копий от платформ (актуальных на 2016 год) и от года.

# In[50]:


new_df[[i for i in new_df.loc[2016].dropna().sort_values(ascending=False).index]].dropna(axis=1, how='all').plot(
    figsize=(15,28), subplots=True, kind='bar', title='Распределение кол-ва копий на платформы (актуальные на 2016 год) от года'
)
plt.show()


# Посмотрим также на дату выпуска консолей

# In[51]:


year_of_platform_release = df.sort_values(by='year_of_release').pivot_table(
    index='platform', values='year_of_release', aggfunc='first').loc[
    [i for i in new_df.loc[2016].dropna().sort_values(ascending=False).index]]


# In[52]:


year_of_platform_release


# Итак что мы здесь можем увидеть. Видно что некогда самые продаваемые платформы уже устарели и на смену им пришли их новые версии(так например PS3 -> PS4 , X360 -> XOne) за исключение PC, но не смотря на это игры всё также продаются и приносят прибыль на устаревших платформах. Также можно заметить что период за который платформа успевает появиться и исчезнуть составляет порядка ~ 6-8 лет судя по продажам. На момент 2016 года приносили прибыль следующие платформы: PS4, XOne, 3DS, PC, WiiU, PSV, PS3, X360, Wii. При этом самыми большими значениями продаж обладали наиболее новые платформы такие как PS4 и XOne, при этом роста по числу продаж не наблюдается ни у одной платформы. Также можно заметить на графике "Распределение кол-ва выпущенных игр от года", видно что в период до 2012 года цены достаточно сильно колеблятся, что не может не сказать на предсказательной способности данных, т.о исходя из этих выводов я предполагаю что нужно сделать актуальным периодом время от ближайшего (относительно 2016 года) момента стабилизаци рынка (т.е 2012 год) и до 2016 года включительно, что даст нам хорошие данные для дальнейших предсказаний. Таким образом наш рассматриваемый актуальный период составляет от 2012 года до 2016. 
# 
# Построим «ящик с усами» по глобальным продажам игр в разбивке по платформам. Для этого сначала возьмём срез от данных по актуальному периоду (2012-2016) и по платформам которые приносят прибыль в 2016.

# In[53]:


new_df.loc[range(2012,2017), [i for i in year_of_platform_release.index]].dropna(
    axis=1, how='all')


# In[54]:


new_df.loc[
    range(2005,2017), [i for i in year_of_platform_release.index]].dropna(
    axis=1, how='all').boxplot(
    fontsize=15, rot=360, figsize=(10,10)
)
plt.title('ящик с усами» по глобальным продажам игр в период с 2005 - 2016 года в разбивке по платформам')
plt.show()


# In[55]:


new_df.loc[
    range(2012,2017), [i for i in year_of_platform_release.index]].dropna(
    axis=1, how='all').boxplot(
    fontsize=15, rot=360, figsize=(10,10)
)
plt.title('ящик с усами» из актуальных данных по глобальным продажам игр в разбивке по платформам')
plt.show()


# Видно что когда то такиt платформы как Wii, X360, PS3 продавали огромное кол-во копий игр. Так например Wii и вовсе больше всех копий продала за один год из промежутка с 2012 по 2017 год. Также можно заметить что число копий на новый консолях бывает больше кол-ва копий для старых платформ в болшинстве случае (как в случае с PS3,PS4,Wii,WiiU), но бывает и обратная ситуация(например X360, XOne). Скорее всего это обусловлено тем ,что Microsoft нужно подумать над своей стратегией развития так как продажи копий PS4 c XOne должны быть на ровне(судя по данным за 2012-2016 года). Давайте взглянем на диаграмму рассеяния для оценки критиков и оценки юзеров от суммарных продаж также для актуального периода. 

# In[56]:


actual_df = df[(df['year_of_release'].isin(
    range(2012,2017))) & (df['platform'].isin(year_of_platform_release.index))]


# In[57]:


actual_df[actual_df['platform'] == 'PS4'].plot(
    x='critic_score',
    y='sum_sales',
    kind='scatter', 
    title='Диаграмма рассеяния оценки критиков от суммарных продаж для PS4'
)

actual_df[actual_df['platform'] == 'PS4'].plot(
    x='user_score', 
    y='sum_sales',
    kind='scatter',
    title='Диаграмма рассеяния оценки юзеров от суммарных продаж для PS4'
)

plt.show()


# Посчитаем корреляцию для PS4 для параметров оценки критиков и оценки юзеров от суммарных продаж. 

# In[58]:


actual_df[actual_df['platform'] == 'PS4']['sum_sales'].corr(df[df['platform'] == 'PS4']['user_score'])


# In[59]:


actual_df[actual_df['platform'] == 'PS4']['sum_sales'].corr(df[df['platform'] == 'PS4']['critic_score'])


# Посчитаем корреляцию для PS3 для параметров оценки критиков и оценки юзеров от суммарных продаж. 

# In[60]:


actual_df[actual_df['platform'] == 'PS3']['sum_sales'].corr(df[df['platform'] == 'PS3']['user_score'])


# In[61]:


actual_df[actual_df['platform'] == 'PS3']['sum_sales'].corr(df[df['platform'] == 'PS3']['critic_score'])


# Посчитаем корреляцию для XOne для параметров оценки критиков и оценки юзеров от суммарных продаж. 

# In[62]:


actual_df[actual_df['platform'] == 'XOne']['sum_sales'].corr(df[df['platform'] == 'XOne']['user_score'])


# In[63]:


actual_df[actual_df['platform'] == 'XOne']['sum_sales'].corr(df[df['platform'] == 'XOne']['critic_score'])


# Посчитаем корреляцию для 3DS для параметров оценки критиков и оценки юзеров от суммарных продаж. 

# In[64]:


actual_df[actual_df['platform'] == '3DS']['sum_sales'].corr(df[df['platform'] == '3DS']['user_score'])


# In[65]:


actual_df[actual_df['platform'] == '3DS']['sum_sales'].corr(df[df['platform'] == '3DS']['critic_score'])


# **Вывод**
# 
# Какой вывод можно сделать смотря на эти данные, например то что оценки критиков и оценки юзеров не зависят линейно от суммарных продаж, но можно сказать таким образом если у нас есть игра и её продажи высокие то скорее всего и ретинг критиков этой игры был высоким, таким образом можно выразиться так: если разработчики хотят иметь хорошие продажи то им скорее всего для этого понадобятся хорошие рейтинги от критиков. Посмотрим на общие распределения жанров среди выбранных нами игр на 2005-2017 года и по выбранным платформам

# In[66]:


actual_df['genre'].value_counts().sort_values(ascending=False)


# In[67]:


actual_df['genre'].value_counts().plot.pie(
    autopct='%1.0f%%',figsize=(10,10), startangle=40, title='Распределение жанров на данных из актуального периода')
plt.show()


# Жанр `Action, Role-Playing, Sports, Adventure, Shooter` занимают 5 лидирующие позиции по кол-ву выпущеных игр этого жанра за период с 2012 по 2016 год. Посмотрим зависимость жанра от суммарных продаж за указанный период.

# In[68]:


actual_df.pivot_table(
    index='genre', values='sum_sales', aggfunc=['sum','mean','median'])


# Запишем вернюю строчку в переменную для удобства

# In[69]:


types_sum_sales = actual_df.pivot_table(
    index='genre', values='sum_sales', aggfunc=['sum','mean','median'])


# In[70]:


types_sum_sales['median'].sort_values(by='sum_sales', ascending=False)


# **Вывод**
# 
# Видно что самыми прибыльными в среднем жанрами являются :`Shooter` , `Sports`, `Platform`, `Role-Playing`, `Fighting`.
# 
# При этом самые выпускаемые жанры не всегда являются самыми прибыльными. 

# <a id='portrait'></a>
# # Шаг 4 Составляем портрет пользователя каждого региона (NA, EU, JP)

# Посмотрим как различаются самые популярные платформы среди регионов за 2012-2016 годы

# In[71]:


actual_df.groupby('platform')['jp_sales'].sum().sort_values(
    ascending=False).head()


# In[72]:


actual_df.groupby('platform')['eu_sales'].sum().sort_values(
    ascending=False).head()


# In[73]:


actual_df.groupby('platform')['na_sales'].sum().sort_values(
    ascending=False).head()


# Посмотрим также на суммарные продажи только за 2016 год 

# In[74]:


df[df['year_of_release'] == 2016].groupby('platform')['jp_sales'].sum().sort_values(
    ascending=False).head()


# In[75]:


df[df['year_of_release'] == 2016].groupby('platform')['eu_sales'].sum().sort_values(
    ascending=False).head()


# In[76]:


df[df['year_of_release'] == 2016].groupby('platform')['na_sales'].sum().sort_values(
    ascending=False).head()


# **Вывод**
# 
# Можно увидеть что в целом японский рынок, менее склонен к попупкам ,но скорее всего это обусловлено малочисленностью японии по сравнению с такими гигантами как европа и северная америка. Также видно что японцы поддерживают свой продукт(Так компании Nintendo и Sony являются японскими компаниями). В остальном видно что на остальных рынках за 2005-2016 годы лидирующие позиции делят между собой PS4 и XOne, что вполне понятно так как это  наверно самые популярные игровые платформы в мире и как раз за период с 2012-2016.Давайте теперь взгянем на популярные жарны для этих рынков.

# In[77]:


actual_df.groupby('genre')['jp_sales'].sum().sort_values(
    ascending=False).head()


# In[78]:


actual_df.groupby('genre')['eu_sales'].sum().sort_values(
    ascending=False).head()


# In[79]:


actual_df.groupby('genre')['na_sales'].sum().sort_values(
    ascending=False).head()


# Посмотрим также на суммарные продажи только за 2016 год 

# In[80]:


df[df['year_of_release'] == 2016].groupby('genre')['jp_sales'].sum().sort_values(
    ascending=False).head()


# In[81]:


df[df['year_of_release'] == 2016].groupby('genre')['eu_sales'].sum().sort_values(
    ascending=False).head()


# In[82]:


df[df['year_of_release'] == 2016].groupby('genre')['na_sales'].sum().sort_values(
    ascending=False).head()


# **Вывод**
# 
# И снова японский рынок в период с 2012-2016 годы отличается от остальных по предпочтениям(так например в данных за 2012-2016 года видно что у японии на первом месте стоит жанр `Role-Plaing`, хотя у остальных он на последнем месте или вовсе отсутсвует), в свою очередь видно что остальные рынки достаточно схожи между собой. Такая же ситуация видна и при просмотре рынка за 2016 год. **Теперь давайте посмотрим влияет ли рейтинг ESRB на продажи.**

# Япония

# In[83]:


actual_df.groupby('rating')['jp_sales'].sum().sort_values(
    ascending=False).head()


# Европа

# In[84]:


actual_df.groupby('rating')['eu_sales'].sum().sort_values(
    ascending=False).head()


# Америка

# In[85]:


actual_df.groupby('rating')['na_sales'].sum().sort_values(
    ascending=False).head()


# За данные с 2012-2016 года видно никую разницы между влиянием рейтинга ESRB и суммарными продажами в отдельном регионе. Так сразу бросается в глаза что Япония склонна к попупке игр с рейтингом 'unknown', скорее всего это обусловлено просто самим рынком. Что я имею ввиду, Японцы достаточно необычные сами по себе и любят достаточно странные игры, которые в других частях мира могут остаться просто незамеченными. Из этого ещё можно также сделать вывод что не заполняются малоизвестные игры, вследствие этого возникают пропуски в рейтинге и юзер скоре. Но вообще тенденция на остальных рынках то что продукты категории E и M покупаются чаще нежели остальные категории. Посмотрим также данные за 2016 год.

# In[86]:


df[df['year_of_release'] == 2016].groupby('rating')['jp_sales'].sum().sort_values(
    ascending=False).head()


# In[87]:


df[df['year_of_release'] == 2016].groupby('rating')['eu_sales'].sum().sort_values(
    ascending=False).head()


# In[88]:


df[df['year_of_release'] == 2016].groupby('rating')['na_sales'].sum().sort_values(
    ascending=False).head()


# В данных за 2016 год также таковой нет разницы между суммарной продажей в отдельном регионе и рейтингом ESRB. Все лидирующие позиции по продажам делят одни и те же кпозицииатегории, но лидирующие позиции разделяют разные значения рейтингов.  

# **Вывод шаг 4**
# 
# Исходя из полученные данных какие можно сделать выводы.
# 
# 1) Японский рынок склонен к покупкам своих товаров(т.е какой нибудь Xbox там совсем имеет низкие продажи). 
# 
# 2) Наиболее прибыльными являются американский и европейский рынки
# 
# 3) Японцам предпочтительней жанр `Role-playing` в отличие от предпочтений на других рынках где предпочтения игроков почти схожи между собой 
# 
# 4) Самым продаваемый рейтинг во всех странах (кроме японии) `E`.
# 
# 5) На момент 2016 года самыми популярными платформами в японии являются `3DS` `PS4` в отличие от других рынков где лидирубщие позиции делят между собой `PS4` и `XOne`
# 
# 6) Причина которой может быть обусловлены пропуски в `user_score` и `rating` может быть обусловлена тем что эти игры нацелены на опреленные рынки, за пределы которых они не выходят=> Вследствие этого такие игры остаются известными локально, и поэтому я бы такие не стал заполнять, ибо на эти данные вряд ли будут смотреть
# 
# 7) Япония склонна к покупкам 'странных' игр в какой то степени исходя из вывода 6). Вряд ли даже настоящие рейтинги будут сильно отличаться, но так как они покупают что то необычное, то из за этого возникает перевес рейтинга 'unknown' именно в Японии.
# 
# 8) Ну и вообще японский игровой рынок отличается немного от остальных(наверно вследствие того что является сама технологическим лидером в этой области и в какой то степени диктует моду)

# <a id='check_hypo'></a>
# # Шаг 5. Проверка гипотез

# Проверяем гипотезу 1: **Cредние пользовательские рейтинги платформ Xbox One и PC одинаковые**
# 
# 
# Тест двухсторонний так как нам не важно кто больше важно лишь признать факт разницы. Далее пытаемся провести о равенстве средних двух генеральных совокупностей. В данном случае считаем дисперсии равными. Формулировка гипотезы выглядит как представленно ниже. 
# 
# H0 : med1 - med2 = 0
# 
# H1 : |med1 - med2| > 0
# 
# Формулировка гипотезы H0: средний пользовательский рейтинг платформ Xbox One и PC равен друг другу (Сверху как раз я это и пишу ведь если среднее это med1 и med2 для двух ген.совокупностей тогда med1=med2=A => med1 - med2 = 0; и это как раз формулировка H0)
# 
# Формулировка альтернативной гипотезы H1: средний пользовательский рейтинг платформ Xbox One и PC отличается(т.е не важно в какую строну, главное что медианы различные и как раз |med1 - med2| > 0 , здесь модуль поэтому неважно куда отклонится отклонится главное что > 0)

# Посчитаем среднее и стандартное отклонение для данных платформ

# **XOne**

# In[89]:


np.std(actual_df[actual_df['platform'] == 'XOne']['user_score'])


# In[90]:


np.mean(actual_df[actual_df['platform'] == 'XOne']['user_score'])


# **PC**

# In[91]:


np.std(actual_df[actual_df['platform'] == 'PC']['user_score'])


# In[92]:


np.mean(actual_df[actual_df['platform'] == 'PC']['user_score'])


# In[93]:


results = st.ttest_ind(
    actual_df[actual_df['platform'] == 'XOne']['user_score'], 
    actual_df[actual_df['platform'] == 'PC']['user_score']
)


# Здесь считает значение значение t-test'a с помощью метода `ttest_ind`. Передаю на вход юзер скоры от срезов по платформам. Уровень значимости берем как 0.05 т.к гипотеза друхсторонняя.

# In[94]:


if 0.05 > results.pvalue:
    print( 'p-value =',results.pvalue , ",Отвергаем H0 гипотезу")
else:
    print('Принимаем H0 ')


# **Вывод по "Гипотеза 1"**
# 
# Статистически доказано что средний пользовательский рейтинг платформ Xbox One и PC за актуальный период не отличается. И это даже видно на полученных средних и стандартных отклонениях они достаточно похожи друг на друга.

# Проверяем гипотезу 2: **Средние пользовательские рейтинги жанров Action (англ. «действие», экшен-игры) и Sports (англ. «спортивные соревнования») разные**
# 
# 
# Тест двухсторонний так как нам не важно кто больше важно лишь признать факт разницы. Далее пытаемся провести о равенстве средних двух генеральных совокупностей. В данном случае считаем дисперсии равными. Формулировка гипотезы выглядит как представленно ниже. 
# 
# H0 : med1 - med2 = 0
# 
# H1 : |med1 - med2| > 0
# 
# Формулировка гипотезы H0: средний пользовательский рейтинг жанров Action и Sports равен друг другу (Сверху как раз я это и пишу ведь если среднее это med1 и med2 для двух ген.совокупностей тогда med1=med2=A => med1 - med2 = 0; и это как раз формулировка H0)
# 
# Формулировка альтернативной гипотезы H1: средний пользовательский рейтинг платформ Xbox One и PC отличается(т.е не важно в какую строну, главное что медианы различные и как раз |med1 - med2| > 0 , здесь модуль поэтому неважно куда отклонится отклонится главное что > 0)

# Посчитаем среднее и стандартное отклонение для данных платформ

# **Action**

# In[95]:


np.std(actual_df[actual_df['genre'] == 'Action']['user_score'])


# In[96]:


np.mean(actual_df[actual_df['genre'] == 'Action']['user_score'])


# **Sports**

# In[97]:


np.std(actual_df[actual_df['genre'] == 'Sports']['user_score'])


# In[98]:


np.mean(actual_df[actual_df['genre'] == 'Sports']['user_score'])


# In[99]:


results  = st.ttest_ind(
    actual_df[actual_df['genre'] == 'Action'][['user_score']], 
    actual_df[actual_df['genre'] == 'Sports'][['user_score']]
)


# In[100]:


results.pvalue


# In[101]:


if 0.05 > results.pvalue:
    print( 'p-value =',results.pvalue , ",Отвергаем H0 гипотезу")
else:
    print('Принимаем H0 ')


# **Вывод по "Гипотеза 2"**
# 
# Средний пользовательский рейтинг жанров Action и Sports отличается друг от друга, на основание статистического теста с уровнем значимости 5%. Причём по всей видимости больше значения у жанра `Action`, на основание среднего и стандартного отклонения для представленных выше двух жанров

# <a id = 'common_out'></a>
# # Шаг 6: Общий вывод

# **Вывод**
# 
# Собственно сначала данные были достаточно засоренные NAN-ами, пришлось сначала их чистить путём подставления соответсвующих значений по колонкам. Все колонки были заменены за исключением колонки `rating` так как не нашлось каких то зависимостей значения этой колонки от других колонок, но и правда ради того кол-ва что у нас есть вполне хватит для проведения стат.тестов. По результатам анализа данных делается вывод что оценки критиков и оценки юзеров не зависят линейно от суммарных продаж, но можно сказать таким образом :если у нас есть игра и её продажи высокие то скорее всего и ретинг критиков этой игры был высоким.Или например так: если разработчики хотят иметь хорошие продажи то им скорее всего для этого понадобятся хорошие рейтинги от критиков.Жанр Action, Role-Playing, Sports, Adventure, Shooter занимают 5 лидирующих позиций по кол-ву выпущеных игр этого жанра за актуальный период. Видно что самыми прибыльными в среднем жанрами являются :Shooter , Sports, Platform, Role-Playing, Fighting. Также в актуальный период таковой нет разницы между суммарной продажей в отдельном регионе и рейтингом ESRB. Все лидирующие позиции по продажам делят одни и те же категории, но лидирующие позиции по числу выпущенный игр данной категории разделяют разные значения рейтингов. 
# 
# Самыми прибыльными платформами являются PS4, XOne, 3DS, с огромным отставанием от всех PS4 которая продаёт больше всех. 
# 
# 
# 
# Также видно что Японский рынок отличается немного от других рынков, потому что как мне кажется они склонны покупать более 'странные' или менее известные игры. Наиболее перспективными платформами являются PS4,XOne,PS3 для Северной Америки и Европы, если таргетироваться на Японию то PS4 3DS и PSV. Таким образом видно что Playstation доминирует на всех рынках. 
# 
# 
# И снова японский рынок в период с 2012-2016 годы отличается от остальных по предпочтениям в жанрах(так например в данных за 2012-2016 года видно что у японии на первом месте стоит жанр `Role-Plaing`, хотя у остальных он на последнем месте или вовсе отсутсвует), в свою очередь видно что остальные рынки достаточно схожи между собой. Такая же ситуация видна и при просмотре рынка за 2016 год.
# 
# 
# Можно увидеть что в целом японский рынок, менее склонен к попупкам ,но скорее всего это обусловлено малочисленностью японии по сравнению с такими гигантами как европа и северная америка. Также видно что японцы поддерживают свой продукт(Так компании Nintendo и Sony являются японскими компаниями). В остальном видно что на остальных рынках за 2005-2016 годы лидирующие позиции делят между собой PS4 и XOne, что вполне понятно так как это  наверно самые популярные игровые платформы в мире и как раз за период с 2012-2016
# 
# 
# Вообщем желательно чтобы игра была с хорошим рейтигом, была из перечня жанров: Shooter , Sports, Platform, Role-Playing, Fighting. Также нужно смотреть на потенциальный рынок игры ведь можно выпустить для Японии и иметь хорошие продажи а во всё остальном мире проажи будут не очень. Ну и хорошо бы чтобы сама игры была хорошая обьективно) Это все параметры которые мне удалось вроде выявить для успеха. 
