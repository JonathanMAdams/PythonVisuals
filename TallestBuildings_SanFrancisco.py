from bs4 import BeautifulSoup
import requests
import codecs
import os
import pandas as pd

url = 'https://en.wikipedia.org/wiki/List_of_tallest_buildings_in_San_Francisco'

fullTable = '<table class="wikitable">'

rPage = requests.get(url)
soup = BeautifulSoup(rPage.content, "lxml")

table = soup.find("table", {"class": "wikitable"})

rows = table.findAll("tr")
row_lengths = [len(r.findAll(['th', 'td'])) for r in rows[1:]]  # Exclude the header row
ncols = max(row_lengths)
nrows = len(rows)

# Convert rows and columns into a list of lists
for i in range(len(rows)):
    rows[i] = rows[i].findAll(['th', 'td'])

# Check header colspan
for i in range(len(rows[0])):
    col = rows[0][i]
    if col.get('colspan'):
        cSpanLen = int(col.get('colspan'))
        del col['colspan']
        for k in range(1, cSpanLen):
            rows[0].insert(i, col)

# Check rowspan of cells
for i in range(len(rows)):
    row = rows[i]
    for j in range(len(row)):
        col = row[j]
        del col['style']
        if col.get('rowspan'):
            rSpanLen = int(col.get('rowspan'))
            del col['rowspan']
            for k in range(1, rSpanLen):
                rows[i + k].insert(j, col)

# Rebuild table
for i in range(len(rows)):
    row = rows[i]
    fullTable += '<tr>'
    for j in range(len(row)):
        col = row[j]
        rowStr = str(col)
        fullTable += rowStr
    fullTable += '</tr>'

fullTable += '</table>'

# Change table links
fullTable = fullTable.replace('/wiki/', 'https://en.wikipedia.org/wiki/')
fullTable = fullTable.replace('\n', '')
fullTable = fullTable.replace('<br/>', '')

# Save file as URL
page = os.path.split(url)[1]
fname = 'output_{}.html'.format(page)
singleTable = codecs.open(fname, 'w', 'utf-8')
singleTable.write(fullTable)

# Scrape rebuilt table
soupTable = BeautifulSoup(fullTable, "lxml")

# Count columns in each row
row_lengths = [len(row.find_all(['th', 'td'])) for row in soupTable.find_all('tr')]

# Get maximum number of columns
num_cols = max(row_lengths)

# Adjust rows to have the same number of columns
for row in soupTable.find_all('tr'):
    while len(row.find_all(['th', 'td'])) < num_cols:
        row.append('<td></td>')

# Extract headers and rows
headers = [th.text.strip() for th in soupTable.find('tr').find_all(['th', 'td'])]
rows = [
    [cell.text.strip() for cell in row.find_all(['th', 'td'])]
    for row in soupTable.find_all('tr')[1:]  # Skip the header row
]

# Build dataframe
sanfran_skyscrapers = pd.DataFrame(rows, columns=headers)

# Get links for images
links = soupTable.findAll('a', {'class': 'mw-file-description'})
image_links = [link.get('href') for link in links]
sanfran_skyscrapers['Image'] = image_links

# Ensure data are read in correctly
print(sanfran_skyscrapers.head())
