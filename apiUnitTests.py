import unittest
from unittest.mock import patch, MagicMock
import json
from spotifyDataRetrieval import get_token, get_auth_header, get_playlist_id, get_playlist_info,get_playlist_tracks

class TestSpotifyDataRetrieval(unittest.TestCase):
    #1
    # Test that a valid token is returned when the API call is successfull
    @patch("spotifyDataRetrieval.post")
    def test_get_token_success(self, mock_post):
        mock_response=MagicMock()
        mock_response.json.return_value = {"access_token": "mock_token"}
        mock_post.return_value= mock_response
        
        token= get_token()
        self.assertEqual(token, "mock_token")
    
    #2
    # Test that a KeyError is raised when no token is provided in the response
    @patch("spotifyDataRetrieval.post")
    def test_get_token_invalid_credentials(self, mock_post):
        mock_response = MagicMock()
        mock_response.json.return_value={}
        
        mock_post.return_value = mock_response
        with self.assertRaises(KeyError):
            get_token()
    
    #3
    # Test that a JSONDecodeError is raised when the response body is not valid JSON
    @patch("spotifyDataRetrieval.post")
    def test_get_token_api_failure(self, mock_post):
        mock_response = MagicMock()
        mock_response.json.side_effect = json.JSONDecodeError("Expecting value", "", 0)
        mock_post.return_value = mock_response

        with self.assertRaises(json.JSONDecodeError):
            get_token()
            
    #4
    # Test the header format for the given token
    def test_get_auth_header(self):
        token="54d5se4"
        expected_header= {"Authorization": f"Bearer {token}"}
        self.assertEqual(get_auth_header(token), expected_header)
    
    #5
    # Test that the correct playlist ID is extracted from a valid URL
    def test_get_playlist_id_valid_url(self):
        url = "https://open.spotify.com/playlist/5V3Bjk9SnOp9hz1cdwguvV?si=befaf075541c4810"
        expected_playlist_id = "5V3Bjk9SnOp9hz1cdwguvV"
        self.assertEqual(get_playlist_id(url), expected_playlist_id)
    
    #6
    # Test that a ValueError is raised when an invalid URL is provided
    def test_get_playlist_id_invalid_url(self):
        url =  "https://open.spotify.com/album/not_a_valid_playlist_url"
        with self.assertRaises(ValueError):
            get_playlist_id(url)
            
    #7
    # Test that a ValueError is raised when an empty string is provided as URL
    def test_get_playlist_id_empty_string(self):
        url= ""
        with self.assertRaises(ValueError):
            get_playlist_id(url)
                
    #8
    # Test the successful retrieval of playlist information
    @patch("spotifyDataRetrieval.get")
    def test_get_playlist_info_success(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code=200
        mock_response.json.return_value = {
            "name": "My Playlist",
            "description": "A test playlist",
            "owner": {"display_name": "TestUser"},
            "tracks": {"total": 10},
            "followers": {"total": 500}
        }
        mock_get.return_value = mock_response

        token = "5nbb5b"
        playlist_id = "5V3Bjk9SnOp9hz1cdwguvV"
        result = get_playlist_info(token, playlist_id)

        self.assertEqual(result["name"], "My Playlist")
        self.assertEqual(result["owner"], "TestUser")
        self.assertEqual(result["total_tracks"], 10)
        self.assertEqual(result["followers"], 500)
        
    #9
    # Test that None is returned when an invalid playlist ID is provided
    @patch("spotifyDataRetrieval.get")
    def test_get_playlist_info_invalid_id(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response

        token = "fake_token"
        playlist_id = "invalid_id"
        result = get_playlist_info(token, playlist_id)

        self.assertIsNone(result)
    
    #10
    # Test that playlist tracks are correctly retrieved
    @patch("spotifyDataRetrieval.get")
    def test_get_playlist_tracks_success(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "items": [
                {"track": {"name": "Song 1", "artists": [{"name": "Artist 1"}], "album": {"name": "Album 1", "release_date": "2023-01-01"}, "popularity": 80}},
                {"track": {"name": "Song 2", "artists": [{"name": "Artist 2"}], "album": {"name": "Album 2", "release_date": "2022-05-05"}, "popularity": 70}}
            ],
            "next": None
        }
        mock_get.return_value = mock_response

      
        result = get_playlist_tracks("mock_token", "mock_playlist_id")

        self.assertIsNotNone(result) 
        self.assertEqual(len(result), 2)
        
    #11
     # Test that playlist tracks are paginated correctly
    @patch("spotifyDataRetrieval.get")
    def test_get_playlist_tracks_pagination(self, mock_get):
        mock_response1 = MagicMock()
        mock_response1.status_code = 200
        mock_response1.json.return_value = {
            "items": [{"track": {"name": "Song 1", "artists": [{"name": "Artist 1"}], "album": {"name": "Album 1", "release_date": "2023-01-01"}, "popularity": 80}}],
            "next": "next_page_url"
        }
        mock_response2 = MagicMock()
        mock_response2.status_code = 200
        mock_response2.json.return_value = {
            "items": [{"track": {"name": "Song 2", "artists": [{"name": "Artist 2"}], "album": {"name": "Album 2", "release_date": "2022-05-05"}, "popularity": 70}}],
            "next": None
        }

        mock_get.side_effect = [mock_response1, mock_response2]

        token = "fake_token"
        playlist_id = "valid_id"
        result = get_playlist_tracks(token, playlist_id)

        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["name"], "Song 1")
        self.assertEqual(result[1]["name"], "Song 2")

    #12
    # Test that an exception is raised in case of network failure
    @patch("spotifyDataRetrieval.get")
    def test_get_playlist_tracks_network_failure(self, mock_get):
        mock_get.side_effect = Exception("Network Error")

        token = "fake_token"
        playlist_id = "valid_id"
        with self.assertRaises(Exception):
            get_playlist_tracks(token, playlist_id)
            
    #13
    # Test that an empty token results in the correct header format
    def test_get_auth_header_empty_token(self):
        token = ""
        expected_header = {"Authorization": "Bearer "}
        self.assertEqual(get_auth_header(token), expected_header)
        
    #14
    # Test that a KeyError is raised if the response has unexpected content
    @patch("requests.post")
    def test_get_token_malformed_response(self, mock_post):
        mock_response = MagicMock()
        mock_response.content = json.dumps({"unexpected_key": "value"}).encode("utf-8")
        mock_post.return_value = mock_response

        with self.assertRaises(KeyError):
            get_token()
            
    #15
    # Test that a ValueError is raised if the URL format is unexpected
    def test_get_playlist_id_unexpected_url_format(self):
        url = "https://spotify.com/playlist_id"
        with self.assertRaises(ValueError):
            get_playlist_id(url)
    #16
     # Test that None is returned if the token is expired
    @patch("spotifyDataRetrieval.get")
    def test_get_playlist_info_expired_token(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 401 
        mock_get.return_value = mock_response

        token = "expired_token"
        playlist_id = "valid_playlist_id"
        result = get_playlist_info(token, playlist_id)

        self.assertIsNone(result)
    #17
    # Test that an empty playlist returns an empty list of tracks
    @patch("spotifyDataRetrieval.get")
    def test_get_playlist_tracks_empty_playlist(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"items": [], "next": None}
        mock_get.return_value = mock_response

        token = "valid_token"
        playlist_id = "empty_playlist_id"
        result = get_playlist_tracks(token, playlist_id)

        self.assertEqual(len(result), 0)
    #18
    # Test that None is returned if the JSON response is invalid
    @patch("spotifyDataRetrieval.get")
    def test_get_playlist_tracks_invalid_json(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.side_effect = json.JSONDecodeError("Expecting value", "", 0)
        mock_get.return_value = mock_response

        token = "valid_token"
        playlist_id = "valid_playlist_id"

        result = get_playlist_tracks(token, playlist_id)
        self.assertIsNone(result) 
        
    #19
    # Test that None is returned if no tracks are found in the playlist
    @patch("spotifyDataRetrieval.get")
    def test_get_playlist_tracks_large_playlist(self, mock_get):
        mock_response1 = MagicMock()
        mock_response1.status_code = 200
        mock_response1.json.return_value = {
            "items": [{"track": {
                "name": f"Song {i}",
                "artists": [{"name": f"Artist {i}"}],
                "album": {"name": f"Album {i}", "release_date": "2025-01-01"},
                "popularity": 50
            }} for i in range(50)],
            "next": "next_page_url"
        }

        mock_response2 = MagicMock()
        mock_response2.status_code = 200
        mock_response2.json.return_value = {
            "items": [{"track": {
                "name": f"Song {i+50}",
                "artists": [{"name": f"Artist {i+50}"}],
                "album": {"name": f"Album {i+50}", "release_date": "2025-01-01"},
                "popularity": 50
            }} for i in range(50)],
            "next": None
        }

        mock_get.side_effect = [mock_response1, mock_response2]

        token = "valid_token"
        playlist_id = "large_playlist_id"
        
        result = get_playlist_tracks(token, playlist_id)
        
        print(f"Final result length: {len(result)}")

        self.assertEqual(len(result), 100)

    #20
    # Test that an empty list is returned if track data is missing in the response
    @patch("spotifyDataRetrieval.get")
    def test_get_playlist_tracks_missing_track_data(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "items": [{"track": None}],
            "next": None
        }
        mock_get.return_value = mock_response

        token = "valid_token"
        playlist_id = "valid_playlist_id"
        result = get_playlist_tracks(token, playlist_id)

        self.assertEqual(len(result), 0)
    #21
    # Test that "Unknown" is assigned if artist data is missing in a track
    @patch("spotifyDataRetrieval.get")
    def test_get_playlist_tracks_missing_artist_data(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "items": [
                {
                    "track": {
                        "name": "Song 1",
                        "artists": [],  
                        "album": {
                            "name": "Album 1",
                            "release_date": "2022-01-01"
                        }
                    }
                }
            ]
        }
        mock_get.return_value = mock_response

        token = "valid_token"
        playlist_id = "valid_playlist_id"
        result = get_playlist_tracks(token, playlist_id)

        
        self.assertEqual(result[0]["artists"], "Unknown")

       
        self.assertEqual(result[0]["name"], "Song 1")
        self.assertEqual(result[0]["album"], "Album 1")
        self.assertEqual(result[0]["release_date"], "2022-01-01")
        
    #22
    # Test that "Unknown" is returned for missing fields in the playlist info
    @patch("spotifyDataRetrieval.get")
    def test_get_playlist_info_missing_fields(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"name": "My Playlist",
                                           "description":"A test playlist"} 
        mock_get.return_value = mock_response

        token = "valid_token"
        playlist_id = "valid_playlist_id"
        result = get_playlist_info(token, playlist_id)

        self.assertIsNotNone(result.get("owner"))

        self.assertEqual(result["name"], "My Playlist")

        self.assertEqual(result.get("owner"), "Unknown")

        self.assertIsNone(result.get("total_tracks"))
        self.assertIsNone(result.get("followers"))
            
            
if __name__ =="__main__":
    unittest.main()