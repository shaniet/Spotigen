#for spotipy
import os
import json
import time
import spotipy
import random

#for craiyon
from craiyon import Craiyon
from PIL import Image # pip install pillow
from io import BytesIO
import base64



## Set Up Spotipy
#----------------

#api tokens
spotify_client_id = os.environ['SPOTIPY_CLIENT_ID']
spotify_secret = os.environ['SPOTIPY_CLIENT_SECRET']
spotify_redirect_uri = os.environ['SPOTIPY_REDIRECT_URI']

# Scope to get a User's Top Artists and Tracks, create and modify a public playlist, and to upload an image
scope = 'user-top-read playlist-read-collaborative playlist-modify-public ugc-image-upload'


oauth_object = spotipy.SpotifyOAuth(client_id = spotify_client_id,
                                    client_secret = spotify_secret,
                                    redirect_uri = spotify_redirect_uri,
                                    scope =scope)
token_dict = oauth_object.get_access_token()
token = token_dict['access_token']
#----------------






## Create our spotify object
spotify_object = spotipy.Spotify(auth=token)

#get top tracks
topTracks = spotify_object.current_user_top_tracks(limit = 3)
tracks=[]
for item in topTracks["items"]:
    tracks.append(item['id'])

#get top artists
topArtists = spotify_object.current_user_top_artists(limit = 2)
artists=[]
for item in topArtists["items"]:
    artists.append(item['id'])

#get recommendation genre seed

recGenre = spotify_object.recommendation_genre_seeds()

#get reccomendations based off seeds
recID = []
recommendations= spotify_object.recommendations(seed_artists = artists, seed_tracks = tracks, seed_genre = recGenre)

for item in recommendations["tracks"]:
    recID.append(item["id"])







## Audio analysis
#----------------

##bins:
#danceability bin (range from 0.0-1.0) : location
dancebin = {0.0: "cozy bed", 0.2: "driving in car", 0.4: "beach", 0.6: "rave", 0.8: "explosion" }

#energy bin (range from 0.0 -1.0) : color
energybin = {0.0: "rain", 0.2: "deep blue", 0.4: "hot pink", 0.6: "sunset", 0.8: "sun"}

#tempo bin (range form 0 - 250 +) :
tempobin = {0.0: "Rain Foreest" , 1.0: "New York", 2.0: "Berlin"}

danceability = []
energy = []
tempo = []

for track in tracks:
    feature = spotify_object.audio_features(track)
    danceability.append(feature[0]["danceability"])
    energy.append(feature[0]["energy"])
    tempo.append(feature[0]["tempo"])


#average the bin lists
danceability = sum(danceability)/len(danceability)
energy = sum(energy)/len(energy)
tempo = sum(tempo)/len(tempo)


danceability = ((((danceability * 100) // 20) * 2)/ 10)
energy = ((((energy  * 100) // 20) * 2)/ 10)
tempo = tempo// 100
#----------------




##Create the string we will use to generate the image
string = " "
string += tempobin[tempo] + " "  + energybin[energy] + " " + dancebin[danceability] + " digital art"





## Create a new Playlist and add the reccomended songs
#----------------
#get user id
user = spotify_object.current_user()["id"]

#create new playlist
newPlaylist = spotify_object.user_playlist_create(user, "Your Playlist")

#get playlist id
playlistID = newPlaylist["id"]

#add playlist based off reccomendations
spotify_object.playlist_add_items(playlistID, recID)

#-----------------





## Generate an image using the customized string
#-----------------
generator = Craiyon() # Instantiates the api wrapper
result = generator.generate(string) # Generates 9 images by default and you cannot change that
images = result.images # A list containing image data as base64 encoded strings

image = open("image.png", "wb") #save the generated image as a png
imgdata = base64.b64decode(images[0]) #get the first image
image.write(imgdata)
image.close()

#convert the generated image to a b64 string format

with open("image.png", "rb") as img_file: #convert the png back to a b64
    b64_string = base64.b64encode(img_file.read())

#----------------





## Upload the generated image to the playlist
#----------------
spotify_object.playlist_upload_cover_image(playlistID,b64_string)
#----------------




#----------------------------------------------------------------------------------


#to print any feature in proper format:
# print(json.dumps(feature, sort_keys=False, indent=4))
