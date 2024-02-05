import re
import json
import base64
import requests
from urllib.parse import unquote
from typing import Optional, Tuple, Dict, List
from utils import Utilities, CouldntFetchKeys

class VidplayExtractor:
    KEY_URL : str = "https://github.com/Ciarands/vidsrc-keys/blob/main/keys.json"

    @staticmethod
    def get_futoken(key: str, url: str, provider_url: str) -> str:
        req = requests.get(f"{provider_url}/futoken", {"Referer": url})
        fu_key = re.search(r"var\s+k\s*=\s*'([^']+)'", req.text).group(1)
        
        return f"{fu_key},{','.join([str(ord(fu_key[i % len(fu_key)]) + ord(key[i])) for i in range(len(key))])}"
    
    @staticmethod
    def get_vidplay_subtitles(url_data: str) -> Dict:
        subtitles_url = re.search(r"info=([^&]+)", url_data)
        if not subtitles_url:
            return {}
        
        subtitles_url_formatted = unquote(subtitles_url.group(1))
        req = requests.get(subtitles_url_formatted)
        
        if req.status_code == 200:
            return {subtitle.get("label"): subtitle.get("file") for subtitle in req.json()}
        
        return {}

    @staticmethod
    def encode_id(v_id: str) -> str:
        req = requests.get(VidplayExtractor.KEY_URL)

        if req.status_code != 200:
            raise CouldntFetchKeys("Failed to fetch decryption keys!")
        
        matches = re.search(r"\"rawLines\":\s*\[\"(.+)\"\]", req.text)
        if not matches:
            raise CouldntFetchKeys("Failed to extract rawLines from keys page!")

        key1, key2 = json.loads(matches.group(1).replace("\\", ""))
        decoded_id = Utilities.decode_data(key1, v_id)
        encoded_result = Utilities.decode_data(key2, decoded_id)
        
        encoded_base64 = base64.b64encode(encoded_result)
        decoded_result = encoded_base64.decode("utf-8")

        return decoded_result.replace("/", "_")
    
    def resolve_source(self, url: str, fetch_subtitles: bool, provider_url: str) -> Tuple[Optional[List], Optional[Dict]]:
        url_data = url.split("?")

        subtitles = {}
        if fetch_subtitles:
            subtitles = self.get_vidplay_subtitles(url_data[1])

        key = self.encode_id(url_data[0].split("/e/")[-1])
        futoken = self.get_futoken(key, url, provider_url)
        
        req = requests.get(f"{provider_url}/mediainfo/{futoken}?{url_data[1]}&autostart=true", headers={"Referer": url})
        if req.status_code != 200:
            print(f"[VidplayExtractor] Failed to retrieve media, status code: {req.status_code}...")
            return None, None

        req_data = req.json()
        if (req_data.get("result")) and (type(req_data.get("result")) == dict):
            sources = req_data.get("result").get("sources")
            return [value.get("file") for value in sources], subtitles
        
        return None, None
