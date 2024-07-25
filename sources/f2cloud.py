import re
import json
import base64
import requests
from urllib.parse import unquote
from typing import Optional, Tuple, Dict, List
from utils import CouldntFetchKeys, Utilities

class F2CloudExtractor:
    KEY_URL = "https://github.com/Ciarands/vidsrc-keys/blob/main/keys.json"
    KEYS = {}

    def __init__(self, KEYS={}):
        if KEYS == {}:
            self.KEYS = F2CloudExtractor.get_keys()
        else:
            self.KEYS = KEYS

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
    def get_keys() -> dict:
        req = requests.get(F2CloudExtractor.KEY_URL)

        if req.status_code != 200:
            raise CouldntFetchKeys("Failed to fetch decryption keys!")

        matches = re.search(r"\"rawLines\":\s*\[\"(.+)\"\]", req.text)
        if not matches:
            raise CouldntFetchKeys("Failed to extract rawLines from keys page!")

        return json.loads(matches.group(1).replace("\\", ""))

    @staticmethod
    def get_key(keys, enc: bool, num: int) -> str:
        return keys["encrypt" if enc else "decrypt"][num]

    def get_embed_decryption_key(self) -> str:
        return F2CloudExtractor.get_key(self.KEYS, False, 1)

    def get_embed_encryption_key(self) -> str:
        return F2CloudExtractor.get_key(self.KEYS, True, 1)

    def get_h_encryption_key(self) -> str:
        return F2CloudExtractor.get_key(self.KEYS, True, 2)

    @staticmethod
    def encode(key: str, v_id: str) -> str:
        decoded_id = Utilities.decode_data(key, v_id)
        
        encoded_base64 = base64.b64encode(decoded_id)
        decoded_result = encoded_base64.decode("utf-8")

        return decoded_result.replace("/", "_").replace("+", "-")

    def encode_embed_id(self, v_id: str) -> str:
        key = self.get_embed_encryption_key()
        return F2CloudExtractor.encode(key, v_id)

    def encode_h(self,v_id: str) -> str:
        key = self.get_h_encryption_key()
        return F2CloudExtractor.encode(key, v_id)

    def decode_embed(self,source_url: str) -> str:
        encoded = Utilities.decode_base64_url_safe(source_url)
        decoded = Utilities.decode_data(self.get_embed_decryption_key(), encoded)
        decoded_text = decoded.decode('utf-8')

        return unquote(decoded_text)

    def resolve_source(self, url: str, fetch_subtitles: bool, provider_url: str) -> Tuple[Optional[List], Optional[Dict], Optional[str]]:
        url_data = url.split("?")

        subtitles = {}
        if fetch_subtitles:
            subtitles = self.get_vidplay_subtitles(url_data[1])

        enc_id = self.encode_embed_id(url_data[0].split("/e/")[-1])
        h = self.encode_h(url_data[0].split("/e/")[-1])
        
        req = requests.get(f"{provider_url}/mediainfo/{enc_id}?{url_data[1]}&autostart=true&ads=0&h={h}", headers={"Referer": url})
        if req.status_code != 200:
            print(f"[VidplayExtractor] Failed to retrieve media, status code: {req.status_code}...")
            return None, None, None

        req_data = req.json()
        try:
            req_data = json.loads(self.decode_embed(req_data.get("result")))
            if (type(req_data) == dict) and req_data.get("sources") != None:
                return [value.get("file") for value in req_data.get("sources")], subtitles, url
        except ValueError:
            return None, None, None
        
        return None, None, None

