import json

# Load the JSON data from the file
filename = 'Data_Download/eq_data_30_day_m1.json'
with open(filename) as f:
    all_eq_data = json.load(f)

# readable_file = 'Data_Download/readable_eq_data.json' # 创建一个新的JSON文件，用于存储可读的地震数据
# with open(readable_file, 'w') as f:
#     json.dump(all_eq_data, f, indent=4) # 将地震数据写入新的JSON文件，并设置缩进为4个空格

all_eq_dicts = all_eq_data['features']

mags, titles, lons, lats = [], [], [], []
for eq_dict in all_eq_dicts:
    mag = eq_dict['properties']['mag']
    title = eq_dict['properties']['title']
    lon = eq_dict['geometry']['coordinates'][0]
    lat = eq_dict['geometry']['coordinates'][1]
    mags.append(mag)
    titles.append(title)
    lons.append(lon)
    lats.append(lat)

print(mags[:10])
print(titles[:2])
print(lons[:5])
print(lats[:5])