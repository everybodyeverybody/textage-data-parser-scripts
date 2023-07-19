# textage-data-parser-scripts

Scripts for parsing data downloaded from textage.cc 
for beatmania IIDX metadata

This is part of a separate personal IIDX-related project to
screen-scrape infinitas score data and log it. I was asked to provide
this specific script, so here it is. This may change at any time.
This also may never change again. Such is life!

## Owner

cncmusicfactory on the beatmania IIDX discord server

## Setup

Make sure you have a recent-ish version of python3 (>3.8) available.

```
pip3 install -r requirements.txt
```

Then run

```
python3 list_current_ac_version_songs_not_in_infinitas.py
```

## Specific Script Notes

### list_current_ac_version_songs_not_in_infinitas

This gets the list of songs that are in IIDX 30 RESIDENT and the list
of songs that are in INFINITAS from [textage.cc](https://textage.cc/score/)
's javascript backend and writes a text list.

This caches the data to try and not make too many requests to their
page (should really be on a 6hr timer) and stores the js data locally
in `.textage-metadata`.

## Contribution Guidelines

If you would like to contribute code to this project,
please make sure it passes the following linters/formatters:
- `mypy`
- `black`
- `flake8 --ignore E501`

If you vendor/copy this into something else,
please be kind while scraping textage and link back to
this repo.

I would also like to donate to textage, if anyone knows
what to do about that, let me know.
