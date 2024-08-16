from TallestBuildings_SanFrancisco import sanfran_skyscrapers

import pandas as pd
import folium
from folium import plugins
import matplotlib.colors as colors
import matplotlib.cm as cmx
import webcolors

# Get Image URLs
with open('image_urls.txt', 'r') as f:
    image_url_lines = f.readlines()

# Remove any trailing whitespace from each line
image_urls = [line.strip() for line in image_url_lines]

# Create a base map centered around San Francisco
m = folium.Map(location=[37.7749, -122.4194],
               zoom_start=13,
               tiles='CartoDB Positron'
               )

# Clean the Coordinates column
reg_strings = [r'^\d+°\d+′\d+″[NS]',
               r'^\d+°\d+′[NS]',
               r'^\d+°[NS]',
               r'^\d+',
               r' -',
               r' ',
               r'\ufeff']
for string in reg_strings:
    sanfran_skyscrapers['Coordinates'] = sanfran_skyscrapers['Coordinates'].str.replace(string, '', regex=True)

latitudes = []
longitudes = []
for item in sanfran_skyscrapers['Coordinates']:
    item_split_z = item.split('/')
    item_split_y = item_split_z[2].split(';')
    latitudes.append(float(item_split_y[0]))
    longitudes.append(float(item_split_y[1].split('(')[0]) * -1)

# Create viridis scale
cmap = cmx.get_cmap('viridis', 12)

# Ensure rank is numeric
sanfran_skyscrapers['Rank'] = pd.to_numeric(sanfran_skyscrapers['Rank'])

# Create a color mapper
norm = colors.Normalize(vmin=min(sanfran_skyscrapers['Rank']), vmax=max(sanfran_skyscrapers['Rank']))

# Map the integers to hex values
hex = [colors.rgb2hex(cmap(norm(rank))) for rank in sanfran_skyscrapers['Rank']]

# Create text_colors list; this ensures that marker text color/marksrs have sufficient contrast
text_colors = []
for color in hex:
    r, g, b = webcolors.hex_to_rgb(color)
    l1 = (0.2126*r/255) + (0.7152*g/255) + (0.0722*b/255)
    if l1 < (125/255):
        text_color = '#ffffff'
    else:
        text_color = '#000000'
    text_colors.append(text_color)

# Add a marker for each building
for i in range(0, len(sanfran_skyscrapers.index)):
    lat = latitudes[i]
    lon = longitudes[i]
    image_url = sanfran_skyscrapers["Image"].iloc[i]

    # Create the HTML for the popup
    html = f"""
    <div style="font-family: Avenir;">
        <h3 style="font-family: Avenir;">{sanfran_skyscrapers.iloc[i, 1]}</h3>
        <img src="{image_urls[i-1]}" width="200" height="200">
        <p><b>Rank:</b> {sanfran_skyscrapers.iloc[i, 0]}</p>
        <p><b>Floors:</b> {sanfran_skyscrapers["Floors"][i]}</p>
        <p><b>Year Completed:</b> {sanfran_skyscrapers["Year"][i]}</p>
        <p><a href="https://en.wikipedia.org/wiki/{sanfran_skyscrapers.iloc[i, 1].replace(" ", "_")}" target="_blank">
           Wikipedia Entry
          <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/b/b8/External_link_icon.svg/22px-External_link_icon.svg.png">
          </a></p>
    </div>
    """

    # Code to create markers has been edited
    folium.Marker(location=[lat, lon],
                  icon=folium.DivIcon(icon_size=(150,36),
                                      icon_anchor=(7,20),
                                      html=f"<span style='font-size: 12pt; background-color: {hex[i]}; padding: 5px; font-family: Avenir; color: {text_colors[i]}'>{sanfran_skyscrapers.iloc[i]['Rank']}</span>"),
                  popup=folium.Popup(html)).add_to(m)

# Add a fullscreen button
plugins.Fullscreen(position="topright").add_to(m)

# Save the map to an HTML file
m.save("sanfran_skyscrapers_map.html")