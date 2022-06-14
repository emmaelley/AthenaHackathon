from flask import Flask, render_template, redirect, url_for, request
import pandas as pd
import folium
from geopy.geocoders import Nominatim
import matplotlib.colors as colors
import csv

geolocator = Nominatim(user_agent="myGeocoder")

def latLonFinder(address):
    try:
        location = geolocator.geocode(str(address))
        return pd.Series([location.latitude, location.longitude])
    except:
        return pd.Series([0,0])

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route("/loginOrganisation", methods=["GET","POST"])
def loginOrganisation():
    if request.method == "GET":
        return redirect(url_for('index'))
    elif request.method == "POST":
        userdata = dict(request.form)
        name = userdata["name"]
    return redirect(url_for('organisations', name = name))

@app.route("/loginDonor", methods=["GET","POST"])
def loginDonor():
    if request.method == "GET":
        return redirect(url_for('index'))
    elif request.method == "POST":
        userdata = dict(request.form)
        name = userdata["name"]
    return redirect(url_for('donors', name = name))

@app.route('/organisations/<name>')
def organisations(name):
    data = pd.read_csv('example_company_data.csv')
    return render_template('organisations.html', tables = [data.to_html()], titles = ['Available Technology'], name=name)

@app.route('/submitRequest/<name>')
def submitRequest(name):
    return render_template('SubmitRequest.html', name=name)

@app.route("/submitOrganisation", methods=["GET","POST"])
def submitOrganisation():
    if request.method == "GET":
        return redirect(url_for('index'))
    elif request.method == "POST":
        userdata = dict(request.form)
        charity_name = userdata["charity_name"][0]
        lot_id = userdata["lot_id"][0]
        quantity = userdata["quantity"][0]
    with open('example_request_data.csv', mode='a') as csv_file:
        data = csv.writer(csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        data.writerow([charity_name, lot_id, quantity])
        return "Thank you!"

@app.route('/map')
def map():
    data1 = pd.read_csv('example_company_data.csv')
    geolocator = Nominatim(user_agent="myGeocoder")
    data1[["lat","lon"]] = data1['address'].apply(latLonFinder)
    m = folium.Map(
    location=[51.509865,-0.118092],
    tiles="cartodbpositron",
    zoom_start=11)

    laptop = folium.FeatureGroup("Laptops")
    tablet = folium.FeatureGroup("Tablets")
    mobile_phone = folium.FeatureGroup("Mobile Phones")
    available = data1[(data1['progress']=='Requested') | (data1['progress']=='Available')]

    for company_name, cat, make, model, quantity, lat, lon in zip(available['company_name'], available['type'], available['make'],available['model'],available['quantity'],available['lat'],available['lon']):
        colors_dict = dict([("laptop","#fab30c"),("mobile phone","#2cb0f2"),("tablet","#fa0c8b")])
        group_dict = dict([("laptop",laptop),("mobile phone",mobile_phone),("tablet",tablet)])
        color = colors_dict.get(cat)
        popup_text="""{}<br> Category: {}<br> {} {}<br> Quantity: {}"""
        popup_text = popup_text.format(company_name, cat, make, model, quantity)
        label = folium.Popup(popup_text)
        folium.CircleMarker([lat, lon], radius=10, fill=True, popup = label, fill_color=color, color=color).add_to(group_dict.get(cat))

    laptop.add_to(m)
    tablet.add_to(m)
    mobile_phone.add_to(m)

    folium.LayerControl().add_to(m)
    return m._repr_html_()

@app.route('/donors/<name>')
def donors(name):
    return render_template('Donors.html',name=name)

@app.route("/submitDonor/<name>", methods=["GET","POST"])
def submitDonor(name):
    if request.method == "GET":
        return redirect(url_for('index'))
    elif request.method == "POST":
        userdata = dict(request.form)
        company_name = userdata["company_name"]
        cat = userdata["type"]
        make = userdata["make"]
        model = userdata["model"]
        address = userdata["address"]
        quantity = userdata["quantity"]
    with open('example_company_data.csv', mode='a') as csv_file:
        data2 = csv.writer(csv_file, delimiter=',')
        data2.writerow([6,str(company_name),str(cat),str(make),str(model),int(quantity),str(address), "Available"])
        csv_file.close()
        return render_template('thanksReturn.html', name = name)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
