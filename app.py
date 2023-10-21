import threading

import yt_dlp
from flask import Flask, render_template, request, abort
from werkzeug.exceptions import HTTPException
from yt_dlp import YoutubeDL
from yt_dlp.extractor.common import InfoExtractor
from yt_dlp.extractor.youtube import YoutubeIE, YoutubeYtBeIE
from yt_dlp.utils import YoutubeDLError

app = Flask(__name__)


def is_youtube_url(url: str) -> bool:
    allowed_info_extractors: list[type[InfoExtractor]] = [
        YoutubeIE,
        YoutubeYtBeIE,
    ]
    return any(ie.suitable(url) for ie in allowed_info_extractors)


@app.route('/', methods=['GET'])
def index() -> str:
    url = request.args.get("v")
    print(url)

    if url is None:
        return render_template("index.html")

    if not is_youtube_url(url):
        abort(400, "youtube links only pls")

    print(YoutubeIE.extract_id(url))

    parser, opts, all_urls, ydl_opts = yt_dlp.parse_options(argv=None)
    with YoutubeDL(ydl_opts) as youtube_dl:
        parser.destroy()
        try:
            # status_code: int = youtube_dl.download(url)
            video_info = youtube_dl.extract_info(url, download=False)
            print(f"id: {fmt['format_id']}, video: {fmt['vcodec']}, audio: {fmt['acodec']}" for fmt in video_info.get("formats"))
            # print(youtube_dl.__download_wrapper(youtube_dl.extract_info)(url, download=False))
        except YoutubeDLError:
            abort(500, "download cancelled :(")

    return render_template("index.html")


@app.route('/download-video', methods=['GET'])
def download() -> str:
    return render_template("download.html")


@app.errorhandler(404)
def not_found(_) -> tuple[str, int]:
    return render_template("404.html"), 404


@app.errorhandler(400)
def bad_request(error: HTTPException) -> tuple[str, int]:
    return error.description, 400


if __name__ == '__main__':
    app.run()
