#!/usr/bin/env python3
from enum import Enum
from dataclasses import dataclass, field
from typing import Dict


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
    version: str
    alphanumeric: Alphanumeric
    difficulty: Dict[Difficulty, int] = field(
        default_factory=generate_song_metadata_difficulties
    )

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
        rate = self.__check_difficulty_rate(self.difficulty[Difficulty.SP_NORMAL])
        return f"{rate} " + self.sort_by_alphanumeric()

    def sort_by_sph(self) -> str:
        rate = self.__check_difficulty_rate(self.difficulty[Difficulty.SP_HYPER])
        return f"{rate} " + self.sort_by_alphanumeric()

    def sort_by_spa(self) -> str:
        rate = self.__check_difficulty_rate(self.difficulty[Difficulty.SP_ANOTHER])
        return f"{rate} " + self.sort_by_alphanumeric()

    def sort_by_spl(self) -> str:
        rate = self.__check_difficulty_rate(self.difficulty[Difficulty.SP_LEGGENDARIA])
        return f"{rate} " + self.sort_by_alphanumeric()

    def sort_by_dpn(self) -> str:
        rate = self.__check_difficulty_rate(self.difficulty[Difficulty.DP_NORMAL])
        return f"{rate} " + self.sort_by_alphanumeric()

    def sort_by_dph(self) -> str:
        rate = self.__check_difficulty_rate(self.difficulty[Difficulty.DP_HYPER])
        return f"{rate} " + self.sort_by_alphanumeric()

    def sort_by_dpa(self) -> str:
        rate = self.__check_difficulty_rate(self.difficulty[Difficulty.DP_ANOTHER])
        return f"{rate} " + self.sort_by_alphanumeric()

    def sort_by_dpl(self) -> str:
        rate = self.__check_difficulty_rate(self.difficulty[Difficulty.DP_LEGGENDARIA])
        return f"{rate} " + self.sort_by_alphanumeric()
