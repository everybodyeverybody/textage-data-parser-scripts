import logging
from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, Set, Tuple, Optional

log = logging.getLogger(__name__)


@dataclass
class StatePixel:
    state: str = ""
    name: str = ""
    y: int = 0
    x: int = 0
    b: int = 0
    g: int = 0
    r: int = 0


@dataclass
class Point:
    x: int
    y: int


@dataclass
class Score:
    fgreat: int = 0
    great: int = 0
    good: int = 0
    bad: int = 0
    poor: int = 0
    fast: int = 0
    slow: int = 0
    grade: str = "X"


@dataclass
class MetadataZone:
    top_left_y: int = 0
    bottom_right_y: int = 0
    top_left_x: int = 0
    bottom_right_x: int = 0
    state: str = ""
    area: str = ""


class Difficulty(Enum):
    SP_NORMAL = 2
    SP_HYPER = 3
    SP_ANOTHER = 4
    SP_LEGGENDARIA = 5
    DP_NORMAL = 7
    DP_HYPER = 8
    DP_ANOTHER = 9
    DP_LEGGENDARIA = 10
    UNKNOWN = 99


class Alphanumeric(Enum):
    ABCD = 0
    EFGH = 1
    IJKL = 2
    MNOP = 3
    QRST = 4
    UVWXYZ = 5
    OTHERS = 6


def generate_song_metadata_difficulties_and_note_counts(
    sp_normal: int = 0,
    sp_normal_notes: int = 0,
    sp_hyper: int = 0,
    sp_hyper_notes: int = 0,
    sp_another: int = 0,
    sp_another_notes: int = 0,
    sp_leggendaria: int = 0,
    sp_leggendaria_notes: int = 0,
    dp_normal: int = 0,
    dp_normal_notes: int = 0,
    dp_hyper: int = 0,
    dp_hyper_notes: int = 0,
    dp_another: int = 0,
    dp_another_notes: int = 0,
    dp_leggendaria: int = 0,
    dp_leggendaria_notes: int = 0,
) -> Dict[Difficulty, Tuple[int, int]]:
    return {
        Difficulty.SP_NORMAL: (sp_normal, sp_normal_notes),
        Difficulty.SP_HYPER: (sp_hyper, sp_hyper_notes),
        Difficulty.SP_ANOTHER: (sp_another, sp_another_notes),
        Difficulty.SP_LEGGENDARIA: (sp_leggendaria, sp_leggendaria_notes),
        Difficulty.DP_NORMAL: (dp_normal, dp_normal_notes),
        Difficulty.DP_HYPER: (dp_hyper, dp_hyper_notes),
        Difficulty.DP_ANOTHER: (dp_another, dp_another_notes),
        Difficulty.DP_LEGGENDARIA: (dp_leggendaria, dp_leggendaria_notes),
    }


@dataclass
class SongMetadata:
    # TODO: have this self serialize out to json
    textage_id: str
    title: str
    artist: str
    genre: str
    version_id: int
    alphanumeric: Alphanumeric
    # TODO: have this split up by type
    difficulty_and_notes: Dict[Difficulty, Tuple[int, int]] = field(
        default_factory=generate_song_metadata_difficulties_and_note_counts
    )
    soflan: bool = False
    version: str = ""
    min_bpm: int = 0
    max_bpm: int = 0

    def to_dict(self) -> dict:
        return {
            "textage_id": self.textage_id,
            "title": self.title,
            "artist": self.artist,
            "genre": self.genre,
            "version_id": self.version_id,
            "version": self.version,
            "alphanumeric": self.alphanumeric.name,
            "soflan": self.soflan,
            "min_bpm": self.min_bpm,
            "max_bpm": self.max_bpm,
            "difficulty_and_notes": {
                difficulty.name: {
                    "level": self.difficulty_and_notes[difficulty][0],
                    "notes": self.difficulty_and_notes[difficulty][1],
                }
                for difficulty in self.difficulty_and_notes.keys()
                if self.difficulty_and_notes[difficulty][0] != 0
                and self.difficulty_and_notes[difficulty][1] != 0
            },
        }

    def sort_by_alphanumeric(self) -> str:
        """
        Primary sorting method, also used as the secondary
        sorting method when generating the static site.
        """
        return f"{self.alphanumeric.value} {self.title}"

    def sort_by_version(self) -> str:
        """
        Return formatted version strings, then alphabetically.
        subtream has a special case in textage data we work around,
        by setting it to the last element of the version list,
        and then reformatting strings so it comes alphabetically
        between 1 and 2. (that's what all the 0 padding is for
        in the return string)
        """
        unchecked_version_id: int = self.version_id
        checked_version_id: float = 0.0
        # substream textage workaround
        if unchecked_version_id == -1:
            checked_version_id = 1.5
        else:
            checked_version_id = float(unchecked_version_id)
        return f"{checked_version_id:04.1f} {self.sort_by_alphanumeric()}"

    def __check_difficulty_rate(self, difficulty_level: int) -> str:
        """
        Set any blanks to appear after other entries by setting them to ZZZ.
        Otherwise prepend 0s to any single digit difficulties for string
        based sorting.
        """
        if difficulty_level < 1:
            return "ZZZ"
        return f"{difficulty_level:02d}"

    def sort_by_spn(self) -> str:
        rate = self.__check_difficulty_rate(
            self.difficulty_and_notes[Difficulty.SP_NORMAL][0]
        )
        return f"{rate} " + self.sort_by_alphanumeric()

    def sort_by_sph(self) -> str:
        rate = self.__check_difficulty_rate(
            self.difficulty_and_notes[Difficulty.SP_HYPER][0]
        )
        return f"{rate} " + self.sort_by_alphanumeric()

    def sort_by_spa(self) -> str:
        rate = self.__check_difficulty_rate(
            self.difficulty_and_notes[Difficulty.SP_ANOTHER][0]
        )
        return f"{rate} " + self.sort_by_alphanumeric()

    def sort_by_spl(self) -> str:
        rate = self.__check_difficulty_rate(
            self.difficulty_and_notes[Difficulty.SP_LEGGENDARIA][0]
        )
        return f"{rate} " + self.sort_by_alphanumeric()

    def sort_by_dpn(self) -> str:
        rate = self.__check_difficulty_rate(
            self.difficulty_and_notes[Difficulty.DP_NORMAL][0]
        )
        return f"{rate} " + self.sort_by_alphanumeric()

    def sort_by_dph(self) -> str:
        rate = self.__check_difficulty_rate(
            self.difficulty_and_notes[Difficulty.DP_HYPER][0]
        )
        return f"{rate} " + self.sort_by_alphanumeric()

    def sort_by_dpa(self) -> str:
        rate = self.__check_difficulty_rate(
            self.difficulty_and_notes[Difficulty.DP_ANOTHER][0]
        )
        return f"{rate} " + self.sort_by_alphanumeric()

    def sort_by_dpl(self) -> str:
        rate = self.__check_difficulty_rate(
            self.difficulty_and_notes[Difficulty.DP_LEGGENDARIA][0]
        )
        return f"{rate} " + self.sort_by_alphanumeric()


@dataclass
class OCRSongTitles:
    en_title: str
    en_artist: str
    jp_title: str
    jp_artist: str


@dataclass
class SongReference:
    # TODO: update this to lookup shit by bpm, or maybe run queries instead?
    by_artist: Dict[str, Set[str]] = field(default_factory=dict)
    by_difficulty: Dict[Tuple[str, int], Set[str]] = field(default_factory=dict)
    by_title: Dict[str, str] = field(default_factory=dict)
    by_bpm: Dict[Tuple[int, int], Set[str]] = field(default_factory=dict)
    by_note_count: Dict[int, Set[str]] = field(default_factory=dict)

    def resolve_by_play_metadata(
        self,
        difficulty_tuple: Tuple[str, int],
        bpm_tuple: Tuple[int, int],
        note_count: int,
    ):
        # TODO: implement
        difficulty_set = self.by_difficulty[difficulty_tuple]
        bpm_set = self.by_bpm[bpm_tuple]
        notes_set = self.by_note_count[note_count]
        found_results = difficulty_set.intersection(bpm_set).intersection(notes_set)
        log.info(f"PLAY METADATA SET: {found_results}")
        return found_results

    def _resolve_artist_ocr(
        self, song_title: OCRSongTitles, found_difficulty_textage_ids: Set[str]
    ) -> Optional[str]:
        found_artist_textage_id = None
        found_en_artist_textage_ids = self.by_artist.get(song_title.en_artist, set([]))
        found_jp_artist_textage_ids = self.by_artist.get(song_title.jp_artist, set([]))
        found_artist_textage_ids = found_en_artist_textage_ids.union(
            found_jp_artist_textage_ids
        )
        if len(found_artist_textage_ids) > 0:
            matching_ids = found_artist_textage_ids.intersection(
                found_difficulty_textage_ids
            )
            log.info(f"Matching artist/difficulty IDs: {matching_ids}")
            if len(matching_ids) == 1:
                found_artist_textage_id = list(matching_ids)[0]
        return found_artist_textage_id

    def _resolve_title_ocr(
        self, song_title: OCRSongTitles, found_difficulty_textage_ids: Set[str]
    ) -> Optional[str]:
        found_title_textage_id = None
        found_en_title_textage_id = self.by_title.get(song_title.en_title, None)
        found_jp_title_textage_id = self.by_title.get(song_title.jp_title, None)
        log.info(f"found_en_title_textage_id: {found_en_title_textage_id}")
        log.info(f"found_jp_title_textage_id: {found_jp_title_textage_id}")
        if found_en_title_textage_id is not None and found_jp_title_textage_id is None:
            found_title_textage_id = found_en_title_textage_id
        elif (
            found_en_title_textage_id is None and found_jp_title_textage_id is not None
        ):
            found_title_textage_id = found_jp_title_textage_id
        elif (
            found_en_title_textage_id == found_jp_title_textage_id
            and found_en_title_textage_id is not None
        ):
            found_title_textage_id = found_en_title_textage_id
        return found_title_textage_id

    def resolve_ocr(
        self, song_title: OCRSongTitles, difficulty: str, level: int
    ) -> Optional[str]:
        difficulty_tuple: Tuple[str, int] = (difficulty, level)
        found_difficulty_textage_ids = self.by_difficulty.get(difficulty_tuple, set([]))
        if not found_difficulty_textage_ids:
            log.info(f"Could not lookup difficulty {difficulty_tuple}")
            return None
        found_title_textage_id = self._resolve_title_ocr(
            song_title, found_difficulty_textage_ids
        )
        log.info(f"found_title_textage_id: {found_title_textage_id}")
        if (
            found_title_textage_id is not None
            and found_title_textage_id in found_difficulty_textage_ids
        ):
            return found_title_textage_id
        else:
            log.info(f"Could not find {found_title_textage_id} in difficulties")

        found_artist_textage_id = self._resolve_artist_ocr(
            song_title, found_difficulty_textage_ids
        )
        if found_artist_textage_id is not None:
            return found_artist_textage_id
        log.debug("found_title_textage_id: {found_title_textage_id}")
        log.info(
            f"Could not find song_title: {song_title} "
            f"difficulty: {difficulty_tuple}"
        )
        return None
