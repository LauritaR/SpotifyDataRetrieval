from dotenv import load_dotenv 
import os
import base64
from requests import post, get
import json

# loading secret variables
load_dotenv()
cid = os.getenv("SPOTIFY_CLIENT_ID")
secret = os.getenv("SPOTIFY_CLIENT_SECRET")

def get_token():
    auth_string = cid + ":" + secret
    auth_bytes = auth_string.encode("utf-8")
    auth_base64 = str(base64.b64encode(auth_bytes), "utf-8")

    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": "Basic " + auth_base64,
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {"grant_type": "client_credentials"}

    result = post(url, headers=headers, data=data)
    try:
        json_result = result.json()
        token = json_result["access_token"]
    except json.JSONDecodeError as e:
        raise json.JSONDecodeError("Invalid JSON response", "", 0) from e
    except KeyError:
        raise KeyError("access_token not found in the response")
    return token

def get_auth_header(token):
    return {"Authorization": "Bearer " + token}


def get_playlist_id(url):
    if "/playlist/" not in url:
        raise ValueError("Invalid playlist URL format")
    
    parts = url.split("/playlist/")
    
    if len(parts) < 2 or not parts[1]:
        raise ValueError("Invalid playlist URL format")
    
    playlist_id = parts[1].split("?")[0]
    
    return playlist_id
    

def get_playlist_info(token, playlist_id):
    url = f"https://api.spotify.com/v1/playlists/{playlist_id}"
    headers = get_auth_header(token)
    
    response = get(url, headers=headers)
    
    if response.status_code == 200:
        playlist_data = response.json()
        playlist_info = {
            "name": playlist_data.get("name", "Unknown"),
            "description": playlist_data.get("description", "No description available"),
            "owner": playlist_data.get("owner", {}).get("display_name", "Unknown"),
            "total_tracks": playlist_data.get("tracks", {}).get("total", None),
            "followers": playlist_data.get("followers", {}).get("total", None)
        }
        return playlist_info
    else:
        print(f"Failed to retrieve playlist info: {response.status_code}")
        return None

def get_playlist_tracks(token, playlist_id):
    url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
    headers = get_auth_header(token)
    
    track_details= []
    while url:
        response = get(url, headers=headers)
        
        if response.status_code == 200:
            try:
                json_result = response.json()
            except ValueError as e:
                print(f"Error decoding JSON response: {e}")
                return None
            
            if "items" not in json_result:
                print(f"Invalid response structure: 'items' not found.")
                return None
            
            for item in json_result["items"]:
                track = item.get("track")
                if track is None:
                    print(f"Track is missing for item: {item}")  
                    continue  
                track_info = {
                    "name": track.get("name", "Unknown"),
                    "artists": ", ".join([artist.get("name", "Unknown") for artist in track.get("artists", [])]) or "Unknown",
                    "album": track.get("album", {}).get("name", "Unknown"),
                    "release_date": track.get("album", {}).get("release_date", "Unknown"),  
                    "popularity": track.get("popularity", "Unknown")
                }
                track_details.append(track_info)
            else:
                    print("Track data is missing for an item, skipping it.")
            url = json_result.get("next")  
        else:
            print(f"Failed to retrieve track details: {response.status_code}")
            return None
    return track_details


token=get_token()
playlist_url = "https://open.spotify.com/playlist/5V3Bjk9SnOp9hz1cdwguvV?si=befaf075541c4810"
playlist_id= get_playlist_id(playlist_url)

playlist_info = get_playlist_info(token, playlist_id)
print("\nPlaylist info: \n")
print(playlist_info)

track_details=get_playlist_tracks(token, playlist_id)
print("\Track details: \n")
for track in track_details[:5]:
    print(track)
