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
