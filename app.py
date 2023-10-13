import threading

import yt_dlp
from flask import Flask, render_template, request, abort
from werkzeug.exceptions import HTTPException
from yt_dlp.extractor.common import InfoExtractor
from yt_dlp.extractor.youtube import YoutubeIE, YoutubeYtBeIE

app = Flask(__name__)


def is_youtube_url(url: str) -> bool:
    allowed_info_extractors: list[type[InfoExtractor]] = [
        YoutubeIE,
        YoutubeYtBeIE,
    ]
    return any(ie.suitable(url) for ie in allowed_info_extractors)


@app.route('/', methods=['GET'])
def index() -> str:
    # url = request.args.get("url")
    # print(url)
    # if not is_youtube_url(url):
    #     abort(400, "youtube links only pls")

    return render_template("index.html")


@app.route('/', methods=['POST'])
def download() -> str:
    url = request.form['url']

    if not is_youtube_url(url):
        abort(400, "youtube links only pls")

    yt_dlp_options = [
        "--no-playlist",
        "--hls-use-mpegts",  # todo probably do need this for sending to the client while it downloads
        "--no-part",
        "--paths", "./downloaded",
        # "--output", "aaaaaaa",  # todo see yt-dlp manual "OUTPUT TEMPLATE" section
        # "--format", "FORMAT",  # todo see yt-dlp manual "FORMAT SELECTION" section
        "--check-formats",
        "--progress",
        "--newline",
        # "--quiet",
        # "--verbose",
        url,
    ]
    # yt_dlp.main(yt_dlp_options)
    download_task = threading.Thread(target=yt_dlp.main, args=(yt_dlp_options,))
    download_task.start()
    return render_template("download.html", video=url)


@app.errorhandler(404)
def not_found(_) -> tuple[str, int]:
    return render_template("404.html"), 404


@app.errorhandler(400)
def bad_request(error: HTTPException) -> tuple[str, int]:
    return error.description, 400


if __name__ == '__main__':
    app.run()
