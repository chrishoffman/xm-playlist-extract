import argparse
import requests
import csv
from datetime import datetime


API_URL = 'https://xmplaylist.com/api'
SONG_CACHE = {}

def get_songs(station_id, max_songs=50):
    songs = []
    total = 0
 
    page = get_page(station_id)
    while True:
        for item in page:
            total+=1
            track = item['track']
            if track['id'] in SONG_CACHE:
                continue
            SONG_CACHE[track['id']] = True

            song = {'title': track['name'], 'artist': track['artists'][0]}
            for link in item['links']:
                if link['site'] == 'itunes':
                    song['url'] = link['url']
                    break
            songs.append(song)

        if total >= max_songs:
            break
    
        last = rfc3339_to_timestamp_ms(page[-1]['start_time'])
        page = get_page(station_id, last)

    return songs

def get_page(station_id, last=None):    
    url = f'{API_URL}/station/{station_id}'
    if last:
        url += f'?last={last}'
    response = requests.get(url)
    return response.json()

def rfc3339_to_timestamp_ms(rfc3339):
    return int(datetime.fromisoformat(rfc3339).timestamp() * 1000)

def write_csv(songs, filename):
    with open(filename, 'w') as f:
        fieldnames = ['title', 'artist', 'url']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for song in songs:
            writer.writerow(song)

parser = argparse.ArgumentParser()
parser.add_argument('--station_id', dest='station_id', type=str, help='The station to get songs from')
parser.add_argument('--count', dest='count', type=int, help='The number of songs to get')
args = parser.parse_args()

res = get_songs(args.station_id, args.count)
write_csv(res, 'songs.csv')

