from django.http import HttpResponse
from django.shortcuts import render
from datetime import datetime
from scipy import stats
from io import BytesIO
import matplotlib.pyplot as plt
import requests
import pymongo
import base64
import json

# pip install googletrans==3.1.0a0


def index(request):

    data = {
        "weather": api_weather(),
        "datetime": api_datetime(),
        "last_mounth": get_last_mounth(),
        "mounth": get_mounth(),
        "annee": list(range(1850, api_datetime()['annee']+1))
    }

    return render(request, 'index.html', data)


# api_weather ------------------------------------------------------------
def api_weather():

    # api weatherstack
    r_weather = requests.get("http://api.openweathermap.org/data/2.5/weather?q=brest,fr&APPID=beb97c1ce62559bba4e81e28de8be095&lang=fr")
    dt = r_weather.json()

    # api weatherstack for prec
    r_weather1 = requests.get("http://api.weatherstack.com/current?access_key=8efd0f7572925c9df338ee6d234b15b7&query=brest,france")
    dt1 = r_weather1.json()

    # icon
    icon = "http://openweathermap.org/img/wn/" + \
        dt['weather'][0]['icon'] + "@2x.png"

    # temperature
    temperature = int(dt['main']['temp']) - 273

    # humidite
    humidite = dt['main']['humidity']

    description = dt["weather"][0]["description"]

    # precipitation
    precipitation = dt1["current"]["precip"]

    data = {
        "icon": icon,
        "temperature": temperature,
        "humidite": humidite,
        "description": description,
        "precipitation": precipitation
    }

    return data


# api_datetime ------------------------------------------------------------
def api_datetime():

    # date et heure
    location = datetime.now().strftime("%Y-%m-%d %H:%M")

    t_mois = ["Janvier", "Fevrier", "Mars", "Avril", "Mai", "Juin", "Juillet",
              "Août", "Septembre", "Octobre", "novembre", "Decembre"]

    date1 = location.split(" ")[0].split("-")
    jour = int(date1[2])
    mois = int(date1[1])-1
    annee = int(date1[0])
    date = str(jour) + " " + t_mois[mois] + " " + str(annee)
    heure = location.split(" ")[1]

    data = {
        "jour": jour,
        "mois": mois,
        "annee": annee,
        "date": date,
        "heure": heure
    }

    return data


# mongodb_connexion ------------------------------------------------------------
def mongodb_connexion():
    # connexion mongodb
    myclient = pymongo.MongoClient("mongodb://mongo:27017/")
    mydb = myclient["meteo"]
    mycol1 = mydb["temperature"]
    mycol2 = mydb["precipitation"]

    data = {
        "mycol1": mycol1,
        "mycol2": mycol2
    }

    return data


# get_graph ------------------------------------------------------------
def get_graph():

    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_png = buffer.getvalue()
    graph = base64.b64encode(image_png)
    graph = graph.decode('utf-8')
    buffer.close()

    return graph


# get_plot ------------------------------------------------------------
def get_plot(x, y, xlabel, ylabel, regression, type, n):

    plt.switch_backend('AGG')
    plt.figure(figsize=(8, 5))
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)

    if type == 1:
        #les points
        plt.scatter(x, y)
        plt.plot(x, y)
    elif type == 2:
        plt.bar(x, y)

    if regression:

        x1 = x
        if n == 0:
            x1 = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]

        slope, intercept, r, p, std_err = stats.linregress(x1, y)

        def myfunc(h):
            return slope * h + intercept

        mymodel = list(map(myfunc, x1))
        plt.plot(x, mymodel, color='Red')

    graph = get_graph()

    return graph


# get_last_mounth ------------------------------------------------------------
def get_last_mounth(type=1, regression=False):

    # Les douze mois écoulés
    x = []
    m = api_datetime()['mois'] - 11
    for i in range(12):
        if m % 12 == 0:
            x.append(str(12))
        else:
            x.append(str(m % 12))
        m = m+1

    # température moyenne des douze mois écoulés
    y1 = mongodb_connexion()['mycol1'].find_one(
        {'annee': api_datetime()['annee']})

    y_temp = []
    for p in range(0, api_datetime()['mois']):
        y_temp.append(y1['mois'][p])

    if len(y_temp) < 12:
        k = len(y_temp)
        y2 = mongodb_connexion()['mycol1'].find_one(
            {'annee': api_datetime()['annee']-1})
        for i in reversed(y2['mois']):
            y_temp.insert(0, i)
            k = k+1
            if(k == 12):
                break

    chart1 = get_plot(x, y_temp, 'mois', 'temperature/C°',
                      regression, type, 0)

    # précipitation moyenne des douze mois écoulés
    y1 = mongodb_connexion()['mycol2'].find_one(
        {'annee': api_datetime()['annee']})

    y_precip = []
    for p in range(0, api_datetime()['mois']):
        y_precip.append(y1['mois'][p])

    if len(y_precip) < 12:
        k = len(y_precip)
        y2 = mongodb_connexion()['mycol2'].find_one(
            {'annee': api_datetime()['annee']-1})
        for i in reversed(y2['mois']):
            y_precip.insert(0, i)
            k = k+1
            if(k == 12):
                break

    chart2 = get_plot(x, y_precip, 'mois', 'precipitation/mm',
                      regression, type, 0)

    data = {
        "chart1": chart1,
        "chart2": chart2
    }

    return data


# get_mounth ------------------------------------------------------------
def get_mounth(type=1, regression=False, mois=0, annee_start=1980, annee_end=api_datetime()['annee']):

    # temperature
    x3 = mongodb_connexion()['mycol1'].find(
        {'annee': {'$gt': annee_start, '$lt': annee_end}}).sort('annee')

    x = []
    y = []

    for i in x3:
        if i['annee'] == api_datetime()['annee'] and mois >= api_datetime()['mois']:
            break
        x.append(i['annee'])
        y.append(i['mois'][mois])

    chart3 = get_plot(x, y, 'Annee', 'temperature/C°', regression, type, 1)

    # precipitation
    x4 = mongodb_connexion()['mycol2'].find(
        {'annee': {'$gt': annee_start, '$lt': annee_end}}).sort('annee')

    x = []
    y = []

    for i in x4:
        if i['annee'] == api_datetime()['annee'] and mois >= api_datetime()['mois']:
            break
        x.append(i['annee'])
        y.append(i['mois'][mois])

    chart4 = get_plot(x, y, 'Annee', 'precipitation/mm', regression, type, 1)

    data = {
        "chart3": chart3,
        "chart4": chart4
    }

    return data


# getchart ------------------------------------------------------------
def getchart(request):    
    
    type = int(request.GET.get('type', None))
    reg = int(request.GET.get('reg', None))
    regression = False
    if reg == 1:
        regression = True

    return HttpResponse(json.dumps({
        "chart1": get_last_mounth(type, regression)['chart1'],
        "chart2": get_last_mounth(type, regression)['chart2'],
    }))


# getchart2 ------------------------------------------------------------
def getchart2(request):
    type = int(request.GET.get('type', None))
    reg = int(request.GET.get('reg', None))
    mois = int(request.GET.get('mois', None))
    annee_start = int(request.GET.get('annee_start', None))
    annee_end = int(request.GET.get('annee_end', None))
    regression = False
    if reg == 1:
        regression = True

    return HttpResponse(json.dumps({
        "chart3": get_mounth(type, regression, mois, annee_start, annee_end)['chart3'],
        "chart4": get_mounth(type, regression, mois, annee_start, annee_end)['chart4'],
    }))
