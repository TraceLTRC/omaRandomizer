import requests, json, time, webbrowser, datetime
from random import randrange
from collections import defaultdict

URL = 'https://oma.hwc.hr/api/pools/'

def print_beatmap(beatmap, auto_osu=False, auto_bloodcat=False):
    print(f"""Your beatmap is:
    {beatmap['mapName']} [{beatmap['difficultyName']}]
    Star Rating: {str(beatmap['starRating'])}
    Bloodcat Link: {'https://bloodcat.com/osu/s/' + str(beatmap['mapSetId'])}
    osu!direct Link: {'osu://b/' + str(beatmap['mapId'])}

    """)
    webbrowser.open('osu://b/' + str(beatmap['mapId']), autoraise=False)

def get_pool():
    json_pool = requests.get(URL).content
    pools = json.loads(json_pool)
    dated_pool = {'refreshDate': str(datetime.datetime.today()), 'pools': pools}
    with open("omaPool.json", "wt") as file_pool:
        json.dump(dated_pool, file_pool)
    return pools

try:
    with open("omaPool.json", "rt") as file_pool:
        dated_pool = json.load(file_pool)
    refreshDate = datetime.datetime.strptime(dated_pool['refreshDate'], r"%Y-%m-%d %H:%M:%S.%f")
    if ((datetime.datetime.today() - refreshDate) < datetime.timedelta(days=7)):
        print("Local pool isn't 7 days old. Reusing...")
        pools = dated_pool['pools']
    else:
        print("Local pool is 7 days old. Grabbing latest...")
        pools = get_pool()
except FileNotFoundError:
    pools = get_pool()
    print("Local pool does not exist. Grabbing latest...")

max_mmr = float(input("Max MMR = "))
min_mmr = float(input("Min MMR = "))
if max_mmr < min_mmr:
    min_mmr, max_mmr = max_mmr, min_mmr

filtered_pools = [pool for pool in pools if (min_mmr < float(pool['averageMMR']) < max_mmr)]
maps = defaultdict(list)

for pool in filtered_pools:
    for beatmap in pool['maps']:
        maps[beatmap['sheetId']].append(beatmap)

while True:
    try:
        mapset = input("Mapset = ").upper()
        if mapset == '':
            break
        elif mapset == 'INFO':
            for key in maps.keys():
                print(key + ": " + str(len(maps[key])))
            print("")
            continue
    except KeyboardInterrupt:
        break
    try:
        if len(maps[mapset]) == 0:
            print(f"You have played all {mapset} maps in the elo range!")
            for key in maps.keys():
                print(key + ": " + str(len(maps[key])))
            print("")
            continue
        rand_beatmap = randrange(0, len(maps[mapset]))
        beatmap = maps[mapset].pop(rand_beatmap)
        print_beatmap(beatmap)
        time.sleep(10)
    except KeyError:
        print("Mapset not recognized. These are the only these mapsets:")
        for key in maps.keys():
            print(key + " " + str(len(maps[key])))
            print("")
    except KeyboardInterrupt:
        continue
        
