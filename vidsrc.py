import os
import argparse
import requests
import questionary

from bs4 import BeautifulSoup
from urllib.parse import unquote
from typing import Optional, Tuple, Dict, List

from utils import Utilities, VidSrcError
from sources.vidplay import VidplayExtractor
from sources.filemoon import FilemoonExtractor

SUPPORTED_SOURCES = ["Vidplay", "Filemoon"]

class VidSrcExtractor:
    BASE_URL : str = "https://vidsrc.to"
    DEFAULT_KEY : str = "8z5Ag5wgagfsOuhz"
    PROVIDER_URL : str = "https://vidplay.online" # vidplay.site / vidplay.online / vidplay.lol
    TMDB_BASE_URL : str = "https://www.themoviedb.org"
    USER_AGENT : str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0"

    def __init__(self, **kwargs) -> None:
        self.source_name = kwargs.get("source_name")
        self.fetch_subtitles = kwargs.get("fetch_subtitles")

    def decrypt_source_url(self, source_url: str) -> str:
        encoded = Utilities.decode_base64_url_safe(source_url)
        decoded = Utilities.decode_data(self.DEFAULT_KEY, encoded)
        decoded_text = decoded.decode('utf-8')

        return unquote(decoded_text)

    def get_source_url(self, source_id: str) -> str:
        req = requests.get(f"{self.BASE_URL}/ajax/embed/source/{source_id}")
        if req.status_code != 200:
            error_msg = f"Couldnt fetch {req.url}, status code: {req.status_code}..."
            raise VidSrcError(error_msg)

        data = req.json()
        encrypted_source_url = data.get("result", {}).get("url")
        return self.decrypt_source_url(encrypted_source_url)

    def get_sources(self, data_id: str) -> Dict:
        req = requests.get(f"{self.BASE_URL}/ajax/embed/episode/{data_id}/sources")
        if req.status_code != 200:
            error_msg = f"Couldnt fetch {req.url}, status code: {req.status_code}..."
            raise VidSrcError(error_msg)
        
        data = req.json()
        return {video.get("title"): video.get("id") for video in data.get("result")}

    def get_streams(self, media_type: str, code: str, season: Optional[str], episode: Optional[str]) -> Tuple[Optional[List], Optional[str]]:
        url = f"{self.BASE_URL}/embed/{media_type}/{code}"
        if season and episode:
            url += f"/{season}/{episode}"

        print(f"[>] Requesting {url}...")
        req = requests.get(url)
        if req.status_code != 200:
            print(f"[CouldntFetch] Couldnt fetch {req.url}, status code: {req.status_code}...")
            return None, None

        soup = BeautifulSoup(req.text, "html.parser")
        sources_code = soup.find('a', {'data-id': True})
        if not sources_code:
            print("[NoSourceFound] Could not fetch data-id, this could be due to an invalid imdb/tmdb code...")
            return None, None

        sources_code = sources_code.get("data-id")
        sources = self.get_sources(sources_code)
        source = sources.get(self.source_name)
        if not source:
            available_sources = ", ".join(list(sources.keys()))
            print(f"[NoSourceFound] No source found for \"{self.source_name}\"\nAvailable Sources: {available_sources}")
            return None, None

        source_url = self.get_source_url(source)
        if "vidplay" in source_url:
            print(f"[>] Fetching source for {self.source_name}...")

            extractor = VidplayExtractor()
            return extractor.resolve_source(url=source_url, fetch_subtitles=self.fetch_subtitles, provider_url=self.PROVIDER_URL)
        
        elif "filemoon" in source_url:
            print(f"[>] Fetching source for {self.source_name}...")

            if self.fetch_subtitles: 
                print(f"[NoSubtitles] \"{self.source_name}\" doesnt provide subtitles...")

            extractor = FilemoonExtractor()
            return extractor.resolve_source(url=source_url, fetch_subtitles=self.fetch_subtitles, provider_url=self.PROVIDER_URL)
        
        else:
            print(f"[NotImplemented] Sorry, this doesnt currently support {self.source_name} :(\n(if you message me and ask really nicely ill maybe look into reversing it though)...")
            return None, None
        
    def query_tmdb(self, query: str) -> Dict:
        req = requests.get(f"{self.TMDB_BASE_URL}/search", params={'query': query.replace(" ", "+").lower()}, headers={'user-agent': self.USER_AGENT})
        soup = BeautifulSoup(req.text, "html.parser")
        results = {}

        for result in soup.find_all("div", {"class": "details"}):
            data = result.find("a")
            title = data.find()

            if not title:
                continue
            
            title = title.text
            url = data.get("href")

            if not url:
                continue
            
            data_type, data_id = url[1:].split("/")
            results.update({title: {"media_type": data_type, "tmdb_id": data_id}})

        return results

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="VidSrcExtractor Command Line Interface")
    parser.add_argument("--source", "-src", dest="source_name", choices=SUPPORTED_SOURCES,
                        help="Specify the source name") 
    parser.add_argument("--search", "-s", dest="search_media", type=str,
                        help="Query the tmdb website for content")
    parser.add_argument("--fetch-subtitles", "-getsubs", dest="fetch_subtitles", action="store_true",
                        help="Specify if you want to fetch subtitles or not")
    parser.add_argument("--default-subtitles", "-lang", dest="default_subtitles", type=str,
                        help="Specify default subtitles")
    parser.add_argument("--media-type", "-type", dest="media_type", choices=["movie", "tv"],
                        help="Specify media type (movie or tv)")
    parser.add_argument("--media-id", "-id", dest="media_id", type=str,
                        help="Specify tmdb/imdb code to watch")
    parser.add_argument("--season", "-se", dest="season", type=str,
                        help="Specify the season number")
    parser.add_argument("--episode", "-ep", dest="episode", type=str,
                        help="Specify the episode number")
    args = parser.parse_args()

    source_name = args.source_name or questionary.select("Select Source", choices=SUPPORTED_SOURCES).ask()

    fetch_subtitles = args.fetch_subtitles
    if not fetch_subtitles:
        if source_name == "Filemoon": # This source doesnt provide subtitles as of 31/12/2023
            fetch_subtitles = False
        elif args.default_subtitles:
            fetch_subtitles = True
        else:
            fetch_subtitles = questionary.confirm("Fetch Subtitles").ask()

    vse = VidSrcExtractor(
        source_name = source_name,
        fetch_subtitles = fetch_subtitles,
    )

    media_id = args.media_id
    media_type = args.media_type

    if not args.media_id:
        query = args.search_media or questionary.text("Search Media: ").ask()
        search_results = vse.query_tmdb(query)

        select_media = questionary.select("Select Media", choices=list(search_results.keys())).ask()
        media_data = search_results.get(select_media)

        media_id = media_data.get("tmdb_id")
        media_type = media_data.get("media_type")

    if not media_id:
        media_id = questionary.text("Input imdb/tmdb code").ask()
    
    if not media_type:
        media_type = questionary.select("Select Media Type", choices=["Movie", "Tv"]).ask().lower()

    se = args.season or questionary.text("Input Season Number").ask() if media_type == "tv" else None
    ep = args.episode or questionary.text("Input Episode Number").ask() if media_type == "tv" else None

    streams, subtitles = vse.get_streams(media_type, media_id, se, ep)

    if streams and type(streams) == list:
        stream = streams[0]
        if len(streams) > 1:
            stream = questionary.select("Select Stream", choices=streams).ask()

        mpv_cmd = f"mpv --fs --msg-level=ffmpeg=no \"{stream}\""

        if subtitles:
            subtitle_list = list(subtitles.keys())
            subtitle_list.append("None")
            selection = args.default_subtitles
            
            if not selection:
                print("[>] This can be skipped by passing --default-subtitles {subtitle_language})")
                selection = questionary.select("Select Subtitles...", choices=subtitle_list).ask()

            if selection != "None":
                mpv_cmd += f" --sub-file=\"{subtitles.get(selection)}\""

        os.system(mpv_cmd)