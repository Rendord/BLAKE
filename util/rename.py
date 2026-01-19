import os

for filename in os.listdir('manga_scans/jp2'):
    filepath = os.path.join('manga_scans/jp2', filename)
    if os.path.isfile(filepath):
        print(filename)
        new_filename = filename.replace('(2016)_(Digital)_(danke-Empire)', '')
        new_filename = new_filename.replace(' ', '_')
        os.rename(filepath, os.path.join('manga_scans/jp2', new_filename))