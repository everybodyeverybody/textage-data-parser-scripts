import logging
from datetime import datetime, timezone
from typing import List
from local_dataclasses import SongMetadata, Difficulty, Alphanumeric

from list_current_ac_version_songs_not_in_infinitas import (
    get_current_version_song_metadata_not_in_infinitas as get_em,
)


def build_table(songs: List[SongMetadata]) -> str:

    header = """
        <tr>
            <td>Title</td>
            <td>Artist</td>
            <td>Genre</td>
            <td>Version</td>
            <td>Alphabetical</td>
            <td>SP Normal</td>
            <td>SP Hyper</td>
            <td>SP Another</td>
            <td>SP Leggendaria</td>
            <td>DP Normal</td>
            <td>DP Hyper</td>
            <td>DP Another</td>
            <td>DP Leggendaria</td>
        </tr>
    """

    tags_list = []
    for song in songs:
        sp_another = f"{song.difficulty[Difficulty.SP_ANOTHER]}"
        sp_legg = f"{song.difficulty[Difficulty.SP_LEGGENDARIA]}"
        dp_another = f"{song.difficulty[Difficulty.DP_ANOTHER]}"
        dp_legg = f"{song.difficulty[Difficulty.DP_LEGGENDARIA]}"
        if sp_another == "0":
            sp_another = ""
        if sp_legg == "0":
            sp_legg = ""
        if dp_another == "0":
            dp_another = ""
        if dp_legg == "0":
            dp_legg = ""
        song_row = (
            "<tr>"
            f"<td>{song.title}</td>"
            f"<td>{song.artist}</td>"
            f"<td>{song.genre}</td>"
            f"<td>{song.version}</td>"
            f"<td>{song.alphanumeric.name}</td>"
            f"<td>{song.difficulty[Difficulty.SP_NORMAL]}</td>"
            f"<td>{song.difficulty[Difficulty.SP_HYPER]}</td>"
            f"<td>{sp_another}</td>"
            f"<td>{sp_legg}</td>"
            f"<td>{song.difficulty[Difficulty.DP_NORMAL]}</td>"
            f"<td>{song.difficulty[Difficulty.DP_HYPER]}</td>"
            f"<td>{dp_another}</td>"
            f"<td>{dp_legg}</td>"
            "</tr>"
        )
        tags_list.append(song_row)
    row_tags = "\n".join(tags_list)
    return f"{header}\n{row_tags}"


def write_html(songs: List[SongMetadata]):
    utc_now = datetime.now(tz=timezone.utc).isoformat()
    html_template = (
        "<html>"
        "<title>Songs in IIDX Resident Not in Infinitas</title>"
        "<head><style> "
        "td {{ font-size: 14pt; font-family: sans-serif; line-height: 18pt; border: 1px solid #000000; padding: 2px; text-align: center; }} "
        "</style></head>"
        "<body>"
        "<div>Generated from <a href='https://textage.cc/score/'>Textage</a> by <a href='https://github.com/everybodyeverybody/textage-data-parser-scripts'>textage-data-parser-scripts</a></div>"
        "<div>Last Update: <b>{utc_now}</b></div>"
        "<table>"
        "{table}"
        "</table>"
        "</body>"
        "</html>"
    )
    row_tags = build_table(songs)
    html = html_template.format(utc_now=utc_now, table=row_tags)
    with open("index.html", "wt") as html_writer:
        html_writer.write(html)


def main():
    logging.basicConfig(level=logging.INFO)
    songs: List[SongMetadata] = [value for key, value in get_em().items()]
    write_html(songs)


if __name__ == "__main__":
    main()
