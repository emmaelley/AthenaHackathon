from flask import Flask, render_template, redirect, url_for
import pandas as pd
import folium
import geopandas as gpd
import geopy
from geopy.geocoders import Nominatim
import matplotlib.colors as colors

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

@app.route('/organisations')
def organisations():
    data = pd.read_csv('example_company_data.csv')
    return render_template('organisations.html', tables = [data.to_html()], titles = ['Available Technology'])

@app.route('/submitRequest')
def submitRequest():
    return render_template('SubmitRequest.html')

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
    data = pd.read_csv('example_company_data.csv')
    geolocator = Nominatim(user_agent="myGeocoder")
    data[["lat","lon"]] = data['address'].apply(latLonFinder)
    m = folium.Map(
    location=[51.509865,-0.118092],
    tiles="cartodbpositron",
    zoom_start=11)

    laptop = folium.FeatureGroup("Laptops")
    tablet = folium.FeatureGroup("Tablets")
    mobile_phone = folium.FeatureGroup("Mobile Phones")
    available = data[(data['progress']=='Requested') | (data['progress']=='Available')]

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

@app.route('/donors')
def donors():
    return render_template('Donors.html')

@app.route("/submitDonor", methods=["GET","POST"])
def submitDonor():
    if request.method == "GET":
        return redirect(url_for('index'))
    elif request.method == "POST":
        userdata = dict(request.form)
        company_name = userdata["company_name"][0]
        cat = userdata["type"][0]
        make = userdata["make"][0]
        model = userdata["model"][0]
        address = userdata["address"][0]
        quantity = userdata["quantity"][0]
    if cat not in ["laptop","mobile phone","tablet"]:
      return "Please submit laptop, mobile phone or tablet in the type field."
    with open('example_company_data.csv', mode='a') as csv_file:
        data = csv.writer(csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        data.writerow([6,company_name,cat,make,model,quantity,address, "Available"])
        return "Thank you!"

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
