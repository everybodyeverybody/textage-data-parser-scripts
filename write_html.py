import logging
from datetime import datetime, timezone
from typing import List, Dict, Callable, Tuple
from local_dataclasses import SongMetadata, Difficulty, Alphanumeric

from list_current_ac_version_songs_not_in_infinitas import (
    get_current_version_song_metadata_not_in_infinitas as get_em,
)


def build_table(table_id: Tuple[str, str], songs: List[SongMetadata]) -> str:
    display = "none"
    # TODO: pass this in as a flag or something
    if table_id[0] == "alphanumeric":
        display = "block"
    table_block_start = (
        f"<div id='{table_id[0]}' class='table_area' style='display: {display}'>"
        f"<h3>{table_id[1]}</h3>\n"
        "<table>\n"
    )
    # TODO: make this column aware to allow for styling/highlighting via css
    table_block_end = f"</table></div>\n"
    header = """
        <tr>
            <td class='header'>Song</td>
            <td class='header'>Version</td>
            <td class='header'>Alpha</td>
            <td class='header' title='Single Play Normal'>SPN</td>
            <td class='header' title='Single Play Hyper'>SPH</td>
            <td class='header' title='Single Play Another'>SPA</td>
            <td class='header' title='Single Play Leggendaria'>SPL</td>
            <td class='header' title='Double Play Normal'>DPN</td>
            <td class='header' title='Double Play Hyper'>DPH</td>
            <td class='header' title='Double Play Another'>DPA</td>
            <td class='header' title='Double Play Leggendaria'>DPL</td>
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
            "<td class='song'>"
            f"<div class='title'>{song.title}</div>"
            f"<div class='genre'>{song.genre}</div>"
            f"<div class='artist'>{song.artist}</div>"
            "</td>"
            f"<td class='version'>{song.version}</td>"
            f"<td class='alphanumeric'>{song.alphanumeric.name}</td>"
            f"<td class='spn'>{song.difficulty[Difficulty.SP_NORMAL]}</td>"
            f"<td class='sph'>{song.difficulty[Difficulty.SP_HYPER]}</td>"
            f"<td class='spa'>{sp_another}</td>"
            f"<td class='spl'>{sp_legg}</td>"
            f"<td class='dpn'>{song.difficulty[Difficulty.DP_NORMAL]}</td>"
            f"<td class='dph'>{song.difficulty[Difficulty.DP_HYPER]}</td>"
            f"<td class='dpa'>{dp_another}</td>"
            f"<td class='dpl'>{dp_legg}</td>"
            "</tr>"
        )

        tags_list.append(song_row)
    row_tags = "\n".join(tags_list)
    return f"{table_block_start}\n{header}\n{row_tags}\n{table_block_end}\n"


def build_javascript(table_list: List[Tuple[str, str]]) -> str:
    javascript_template = """
    <script>
        const registeredTables = new Map();
        {registered_tables}
    """
    untemplated_js = """
        function showOneTable(visibleTableId) {
            if (registeredTables.get(visibleTableId) == undefined) {
                console.log("table not registered " + visibleTableId);
                return;
            }
            console.log("table to show: " +visibleTableId);
            var tables = document.querySelectorAll("div.table_area");
            for (const table of tables) {
                if (table.id == visibleTableId) {
                    console.log("showing " + table.id);
                    table.style.display = "block";
                } else {
                    console.log("hiding " + table.id);
                    table.style.display = "none";
                }
            }
            return;
        }
    </script>
    """
    registered_tables = "\n".join(
        [f"registeredTables.set('{table_id[0]}',true);" for table_id in table_list]
    )
    all_js = (
        javascript_template.format(registered_tables=registered_tables) + untemplated_js
    )
    return all_js


def build_buttons(sorted_tables: List[Tuple[str, str]]) -> str:
    buttons = []
    button_div = "<div id='sort_buttons'>{buttons}</div>"
    input_template = (
        "<input id='sort_{table_id}' "
        "type='button' "
        "value='{table_label}' "
        "onclick='showOneTable(\"{table_id}\")'>"
        "</input>"
    )
    for table_id in sorted_tables:
        buttons.append(
            input_template.format(table_id=table_id[0], table_label=table_id[1])
        )
    button_html = "\n".join(buttons)
    return button_div.format(buttons=button_html)


def write_html(sorted_tables: Dict[Tuple[str, str], str]):
    utc_now = datetime.now(tz=timezone.utc).isoformat()
    table_ids: List[Tuple[str, str]] = [table for table in sorted_tables.keys()]
    javascript = build_javascript(table_ids)
    buttons = build_buttons(table_ids)

    css = (
        "td { "
        "    font-family: sans-serif; "
        "    border: 1px solid #000000; "
        "    text-align: center; "
        "    padding: 0.2em;  "
        "} "
        "td.song { text-align: left; min-width: 30ch; }"
        "div.title { font-size: 1.2em; font-weight: bold; }"
        "div.genre { font-size: 0.6em; font-weight: bold; }"
        "div.artist { font-size: 0.6em; font-style: italic;  }"
        "td.version { min-width:12ch; font-weight: bold; font-size: 0.8em; }"
        "td.alphanumeric { min-width:8ch; font-weight: bold; font-size: 0.8em; }"
        "td.spn { min-width:4ch; font-weight: bold;  font-size: 1.4em; }"
        "td.sph { min-width:4ch; font-weight: bold;  font-size: 1.4em; }"
        "td.spa { min-width:4ch; font-weight: bold;  font-size: 1.4em; }"
        "td.spl { min-width:4ch; font-weight: bold;  font-size: 1.4em; }"
        "td.dpn { min-width:4ch; font-weight: bold;  font-size: 1.4em; }"
        "td.dph { min-width:4ch; font-weight: bold;  font-size: 1.4em; }"
        "td.dpa { min-width:4ch; font-weight: bold;  font-size: 1.4em; }"
        "td.dpl { min-width:4ch; font-weight: bold;  font-size: 1.4em; }"
        "td.header { background-color: #484848; font-weight: bold; color: #ffffff; }"
    )
    # TODO: learn about mobile css
    html_template = (
        "<!DOCTYPE html>"
        "<html>"
        "<title>Songs in IIDX Resident Not in Infinitas</title>"
        "<head><style>\n"
        "{css}"
        "\n"
        "</style></head>\n"
        "<body>\n"
        "{javascript}"
        "<div>Generated from <a href='https://textage.cc/score/'>Textage</a> by <a href='https://github.com/everybodyeverybody/textage-data-parser-scripts'>textage-data-parser-scripts</a></div>\n"
        "<div>Last Update: <b>{utc_now}</b></div>\n"
        "{buttons}"
        "{tables}"
        "</body>"
        "</html>"
    )
    tables = "\n".join([table for table in sorted_tables.values()])
    html = html_template.format(
        utc_now=utc_now, css=css, javascript=javascript, buttons=buttons, tables=tables
    )
    with open("index.html", "wt") as html_writer:
        html_writer.write(html)


def generate_all_sorted_tables(songs: List[SongMetadata]) -> Dict[Tuple[str, str], str]:
    tables_and_sort_methods: Dict[Tuple[str, str], Callable] = {
        (
            "alphanumeric",
            "By Title",
        ): SongMetadata.sort_by_alphanumeric,
        (
            "version",
            "By Version",
        ): SongMetadata.sort_by_version,
        (
            "spn",
            "By SP Normal",
        ): SongMetadata.sort_by_spn,
        (
            "sph",
            "By SP Hyper",
        ): SongMetadata.sort_by_sph,
        (
            "spa",
            "By SP Another",
        ): SongMetadata.sort_by_spa,
        (
            "spl",
            "By SP Leggendaria",
        ): SongMetadata.sort_by_spl,
        (
            "dpn",
            "By DP Normal",
        ): SongMetadata.sort_by_dpn,
        (
            "dph",
            "By DP Hyper",
        ): SongMetadata.sort_by_dph,
        (
            "dpa",
            "By DP Another",
        ): SongMetadata.sort_by_dpa,
        (
            "dpl",
            "By DP Leggendaria",
        ): SongMetadata.sort_by_dpl,
    }
    sorted_tables: Dict[Tuple[str, str], str] = {}
    for table_id, sort_method in tables_and_sort_methods.items():
        sorted_tables[table_id] = build_table(table_id, sorted(songs, key=sort_method))
    return sorted_tables


def main():
    logging.basicConfig(level=logging.INFO)
    songs: List[SongMetadata] = [value for key, value in get_em().items()]
    sorted_tables = generate_all_sorted_tables(songs)
    write_html(sorted_tables)


if __name__ == "__main__":
    main()
