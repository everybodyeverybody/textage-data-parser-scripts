#!/usr/bin/env python3
import os
import re
import sys
import json
import logging
from enum import Enum
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, field
from typing import List, Callable, Dict, Any, Union

import requests  # type: ignore

log = logging.getLogger(__name__)


class Difficulty(Enum):
    # There is more complex logic around beginner
    # difficulties related to the versions they exist
    # in. We don't expect anyone to use this on beginner
    # mode stuff.
    # SP_BEGINNER = 1
    SP_NORMAL = 2
    SP_HYPER = 3
    SP_ANOTHER = 4
    SP_LEGGENDARIA = 5
    DP_NORMAL = 7
    DP_HYPER = 8
    DP_ANOTHER = 9
    DP_LEGGENDARIA = 10
    UNKNOWN = 99


def generate_song_metadata_difficulties(
    sp_normal=0,
    sp_hyper=0,
    sp_another=0,
    sp_leggendaria=0,
    dp_normal=0,
    dp_hyper=0,
    dp_another=0,
    dp_leggendaria=0,
) -> Dict[Difficulty, int]:
    return {
        Difficulty.SP_NORMAL: sp_normal,
        Difficulty.SP_HYPER: sp_hyper,
        Difficulty.SP_ANOTHER: sp_another,
        Difficulty.SP_LEGGENDARIA: sp_leggendaria,
        Difficulty.DP_NORMAL: dp_normal,
        Difficulty.DP_HYPER: dp_hyper,
        Difficulty.DP_ANOTHER: dp_another,
        Difficulty.DP_LEGGENDARIA: dp_leggendaria,
    }


@dataclass
class SongMetadata:
    textage_id: str
    title: str
    artist: str
    genre: str
    version_id: int
    difficulty: Dict[Difficulty, int] = field(
        default_factory=generate_song_metadata_difficulties
    )


def _download_textage_javascript(javascript_file: str, output_path: Path) -> Path:
    update = False
    textage_base_url = "https://textage.cc/score/"
    textage_last_modified_format = "%a, %d %b %Y %H:%M:%S %Z"
    # we used enumerate because we wanted the files in a specific
    # order mentioned in the html
    url = f"{textage_base_url}{javascript_file}"
    log.info(f"downloading {url}")
    last_modified_file = output_path / Path(f"{javascript_file}.last_modified")
    output_filename = output_path / Path(f"{javascript_file}")
    response = requests.get(url)
    # make sure to write about this as well, that its chinese w/o it
    response.encoding = "shift_jis"

    if response.status_code not in [200]:
        raise RuntimeError(f"could not download {url}: {response.status_code}")
    if "Last-Modified" not in response.headers:
        raise RuntimeError(
            f"server no longer returning last modified: {response.headers}"
        )
    if not os.path.exists(last_modified_file):
        update = True
    else:
        latest_last_modified = datetime.strptime(
            response.headers["Last-Modified"], textage_last_modified_format
        )
        with open(last_modified_file, "rt") as last_modified_reader:
            current_last_modified_str = last_modified_reader.readlines()[0].strip()
            current_last_modified = datetime.strptime(
                current_last_modified_str, textage_last_modified_format
            )
        if latest_last_modified > current_last_modified:
            update = True
    if update:
        log.info(f"updating {output_path}")
        with open(last_modified_file, "wt") as last_modified_writer:
            last_modified_writer.write(response.headers["Last-Modified"])
        with open(output_filename, "wt") as file_writer:
            file_writer.write(response.text)
    else:
        log.info(
            f"{output_path} not modified since {response.headers['Last-Modified']}"
        )
    return output_filename


def _convert_javascript_and_write_to_json(
    file: Path,
    block_start_regex: str,
    block_end_regex: str,
    specialized_parser: Callable,
):
    log.info(f"converting {file} to json")
    source_file_name = os.path.basename(file)
    source_file_path = os.path.dirname(file)
    parsed_file = source_file_path / Path(f"parsed_{source_file_name}.json")
    with open(file, "rt") as js_file_reader, open(parsed_file, "wt") as parsed_writer:
        capture_output = False
        line_count = 0
        for line in js_file_reader:
            line_count += 1
            if re.match(block_start_regex, line):
                parsed_writer.write("{\n")
                capture_output = True
                continue
            if capture_output:
                if re.match(block_end_regex, line):
                    parsed_writer.write("}")
                    break
                else:
                    # remove comments
                    line = re.sub(r"^//.*", "", line.strip())
                    # skip blanks
                    if re.match(r"^\s*$", line):
                        continue
                    parsed_line = specialized_parser(line)
                    parsed_writer.write(parsed_line)
    return parsed_file


def filter_infinitas_only_songs(
    version_data: Dict[str, List[int]], song_titles: Dict[str, List[str]]
) -> Dict[str, List[str]]:
    """
    Filtering logic taken from debugging
    https://textage.cc/score/scrlist.js
    against the following textage URL showing all
    infinitas songs
    https://textage.cc/score/index.html?a021B000

    In the textage code, lc is the query parameter
    a021B000

    and mt represents the version data table bitfields
    """
    # https://textage.cc/score/scrlist.js
    # function push_check1
    infinitas_only_songs: Dict[str, List[str]] = {}
    for key, value in song_titles.items():
        if key not in version_data:
            continue
        version_flag = version_data[key][0]
        is_in_infinitas = version_flag & 2
        if is_in_infinitas != 0:
            infinitas_only_songs[key] = value
    return infinitas_only_songs


def _read_difficulty(version_data) -> Dict[str, Dict[Difficulty, int]]:
    # https://textage.cc/score/scrlist.js get_level
    difficulties_by_textage_id: Dict[str, Dict[Difficulty, int]] = {}
    for key in version_data.keys():
        difficulties_by_textage_id[key] = {}
        # TODO: parse dp difficulties
        spl = version_data[key][Difficulty.SP_LEGGENDARIA.value * 2 + 1]
        spa = version_data[key][Difficulty.SP_ANOTHER.value * 2 + 1]
        sph = version_data[key][Difficulty.SP_HYPER.value * 2 + 1]
        spn = version_data[key][Difficulty.SP_NORMAL.value * 2 + 1]
        dpl = version_data[key][Difficulty.DP_LEGGENDARIA.value * 2 + 1]
        dpa = version_data[key][Difficulty.DP_ANOTHER.value * 2 + 1]
        dph = version_data[key][Difficulty.DP_HYPER.value * 2 + 1]
        dpn = version_data[key][Difficulty.DP_NORMAL.value * 2 + 1]
        difficulties_by_textage_id[key][Difficulty.SP_LEGGENDARIA] = spl
        difficulties_by_textage_id[key][Difficulty.SP_ANOTHER] = spa
        difficulties_by_textage_id[key][Difficulty.SP_HYPER] = sph
        difficulties_by_textage_id[key][Difficulty.SP_NORMAL] = spn
        difficulties_by_textage_id[key][Difficulty.DP_LEGGENDARIA] = dpl
        difficulties_by_textage_id[key][Difficulty.DP_ANOTHER] = dpa
        difficulties_by_textage_id[key][Difficulty.DP_HYPER] = dph
        difficulties_by_textage_id[key][Difficulty.DP_NORMAL] = dpn
    return difficulties_by_textage_id


def _check_textage_metadata_files(
    textage_javascript_file: str,
    parser_start_regex: str,
    parser_end_regex: str,
    parser_callback: Callable,
) -> Dict[str, Any]:
    # TODO: refactor this further
    script_path = Path(os.path.dirname(os.path.realpath(sys.argv[0])))
    textage_metadata_path = script_path / Path(".textage-metadata")
    os.makedirs(textage_metadata_path, exist_ok=True)
    javascript = _download_textage_javascript(
        textage_javascript_file, textage_metadata_path
    )
    textage_data_file = _convert_javascript_and_write_to_json(
        javascript, parser_start_regex, parser_end_regex, parser_callback
    )
    with open(textage_data_file, "rt") as reader:
        textage_data = json.load(reader)
    return textage_data


def get_infinitas_song_metadata(
    song_titles: Dict[str, List[str]],
    version_data: Dict[str, List[int]],
) -> Dict[str, SongMetadata]:
    all_difficulties = _read_difficulty(version_data)
    infinitas_only_songs = filter_infinitas_only_songs(version_data, song_titles)
    # TODO: add bpm
    metadata = {
        textage_id: SongMetadata(
            textage_id=textage_id,
            title=" ".join(infinitas_only_songs[textage_id][5:]),
            artist=infinitas_only_songs[textage_id][4],
            genre=infinitas_only_songs[textage_id][3],
            version_id=int(infinitas_only_songs[textage_id][0]),
            difficulty=all_difficulties[textage_id],
        )
        for textage_id in infinitas_only_songs.keys()
    }
    return metadata


def filter_current_version_songs(
    version_data: Dict[str, List[int]], song_titles: Dict[str, List[str]]
) -> Dict[str, List[str]]:
    current_version_songs: Dict[str, List[str]] = {}
    for tag, title in song_titles.items():
        if tag not in version_data:
            log.warning(f"could not find {tag}:{title}")
            continue
        # scrlist.js line 682
        current_version_flag = version_data[tag][0]
        is_in_current_version = current_version_flag & 1
        if is_in_current_version == 0:
            log.warning(f"skipping {tag}:{title}")
            continue
        current_version_songs[tag] = title
    return current_version_songs


def get_current_version_songs_not_in_infinitas(
    version_data: Dict[str, List[int]], song_titles: Dict[str, List[str]]
) -> List[str]:
    current_version_songs = filter_current_version_songs(version_data, song_titles)
    infinitas_only_songs = filter_infinitas_only_songs(version_data, song_titles)
    inf_keys = set(list(infinitas_only_songs.keys()))
    cur_ver_keys = set(list(current_version_songs.keys()))
    not_in_inf_keys = cur_ver_keys.difference(inf_keys)
    not_in_inf_song_titles = []
    for key in not_in_inf_keys:
        not_in_inf_song_titles.append("".join(song_titles[key][5:]))
    return sorted(not_in_inf_song_titles)


def get_textage_version_data():
    def __convert_version_bitfield_to_json(bitfield: str) -> str:
        key, values = bitfield.split(":", maxsplit=1)
        if key == "'__dmy__'":
            return ""
        values = re.sub("A", "10", values)
        values = re.sub("B", "11", values)
        values = re.sub("C", "12", values)
        values = re.sub("D", "13", values)
        values = re.sub("E", "14", values)
        values = re.sub("F", "15", values)
        values = re.sub(r"//\d+", "", values)
        values = re.sub(',"<span.*span>"', "", values)
        key = re.sub("'", '"', key)
        return f"{key}:{values}\n"

    return _check_textage_metadata_files(
        textage_javascript_file="actbl.js",
        parser_start_regex=r"^\s*actbl={.*$",
        parser_end_regex=r"\s*}\s*;\s*",
        parser_callback=__convert_version_bitfield_to_json,
    )


def get_textage_song_titles():
    def __remove_title_table_html(title_values: str) -> str:
        key, values = title_values.split(":", maxsplit=1)
        if key == "'__dmy__'":
            return ""
        values = re.sub(r".fontcolor\(.*?\)", "", values)
        values = re.sub("<span style='.*?'>", "", values)
        values = re.sub(r"<\\/span>", "", values)
        values = re.sub(r"<div class=.*?>", "", values)
        values = re.sub(r"<\\/div>", "", values)
        values = re.sub(r"<br>", "", values)
        values = re.sub(r"<b>", "", values)
        values = re.sub(r"<\\/b>", "", values)
        values = re.sub(r"^\[SS", "[-1", values)
        values = re.sub(r"\t", "", values)
        key = re.sub("'", '"', key)
        return f"{key}:{values}\n"

    return _check_textage_metadata_files(
        textage_javascript_file="titletbl.js",
        parser_start_regex=r"^\s*titletbl={.*$",
        parser_end_regex=r"\s*}\s*;\s*",
        parser_callback=__remove_title_table_html,
    )


def get_textage_note_counts_and_bpm() -> Dict[str, List[Union[int, str]]]:
    def __read_nodes_and_bpm(notes_and_bpm_line: str) -> str:
        line = re.sub("'", '"', notes_and_bpm_line)
        return f"{line}\n"

    return _check_textage_metadata_files(
        textage_javascript_file="datatbl.js",
        parser_start_regex=r"^datatbl\s*=\s*{.*$",
        parser_end_regex=r"\s*}\s*;\s*",
        parser_callback=__read_nodes_and_bpm,
    )


if __name__ == "__main__":
    """
    This is the proof of concept for what I provided the discord.
    """
    logging.basicConfig(level=logging.INFO)
    version_data = get_textage_version_data()
    song_titles = get_textage_song_titles()
    notes_and_bpm = get_textage_note_counts_and_bpm()
    songs = get_current_version_songs_not_in_infinitas(version_data, song_titles)
    inf_res_filename = "songs_in_res_not_in_inf.txt"
    log.info(f"WRITING SONGS to {inf_res_filename}")
    with open(inf_res_filename, "wt") as writer:
        for song_title in songs:
            writer.write(f"{song_title}\n")
