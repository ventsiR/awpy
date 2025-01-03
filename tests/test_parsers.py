"""Test the parser methods."""

import pandas as pd
import pytest
from demoparser2 import DemoParser

from awpy.parsers.events import parse_damages, parse_kills
from awpy.parsers.rounds import parse_rounds
from awpy.parsers.ticks import remove_nonplay_ticks


@pytest.fixture(scope="class")
def hltv_parser() -> DemoParser:
    """Test DemoParser for an HLTV demo.

    Teams: Spirit vs MOUZ (de_vertigo)
    Event: PGL CS2 Major Copenhagen 2024 Europe RMR B (CS2)
    Source: HLTV
    Link: https://www.hltv.org/stats/matches/mapstatsid/170716/spirit-vs-mouz
    """
    return DemoParser("tests/spirit-vs-mouz-m1-vertigo.dem")


@pytest.fixture(scope="class")
def faceit_parser() -> DemoParser:
    """Test DemoParser for a Faceit demo.

    Match ID: 1-a568cd9f-8817-4410-a3f3-2270f89135e2
    Link: https://www.faceit.com/en/cs2/room/1-a568cd9f-8817-4410-a3f3-2270f89135e2
    """
    return DemoParser("tests/faceit-fpl-1-a568cd9f-8817-4410-a3f3-2270f89135e2.dem")


@pytest.fixture(scope="class")
def hltv_events() -> dict[str, pd.DataFrame]:
    """Test events for an HLTV demo.

    Teams: Spirit vs MOUZ (de_vertigo)
    Event: PGL CS2 Major Copenhagen 2024 Europe RMR B (CS2)
    Source: HLTV
    Link: https://www.hltv.org/stats/matches/mapstatsid/170716/spirit-vs-mouz
    """
    parser = DemoParser("tests/spirit-vs-mouz-m1-vertigo.dem")
    game_events = parser.list_game_events()
    game_events = [e for e in game_events if e != "server_cvar"]
    return dict(
        parser.parse_events(
            game_events,
            player=[
                "X",
                "Y",
                "Z",
                "last_place_name",
                "flash_duration",
                "health",
                "armor_value",
                "inventory",
                "current_equip_value",
                "rank",
                "ping",
                "has_defuser",
                "has_helmet",
                "pitch",
                "yaw",
                "team_name",
                "team_clan_name",
            ],
            other=[
                # Bomb
                "is_bomb_planted",
                "which_bomb_zone",
                # State
                "is_freeze_period",
                "is_warmup_period",
                "is_terrorist_timeout",
                "is_ct_timeout",
                "is_technical_timeout",
                "is_waiting_for_resume",
                "is_match_started",
                "game_phase",
            ],
        )
    )


@pytest.fixture(scope="class")
def faceit_events() -> dict[str, pd.DataFrame]:
    """Test events for a Faceit demo.

    Match ID: 1-a568cd9f-8817-4410-a3f3-2270f89135e2
    Link: https://www.faceit.com/en/cs2/room/1-a568cd9f-8817-4410-a3f3-2270f89135e2
    """
    parser = DemoParser("tests/faceit-fpl-1-a568cd9f-8817-4410-a3f3-2270f89135e2.dem")
    game_events = parser.list_game_events()
    game_events = [e for e in game_events if e != "server_cvar"]
    return dict(
        parser.parse_events(
            game_events,
            player=[
                "X",
                "Y",
                "Z",
                "last_place_name",
                "flash_duration",
                "health",
                "armor_value",
                "inventory",
                "current_equip_value",
                "rank",
                "ping",
                "has_defuser",
                "has_helmet",
                "pitch",
                "yaw",
                "team_name",
                "team_clan_name",
            ],
            other=[
                # Bomb
                "is_bomb_planted",
                "which_bomb_zone",
                # State
                "is_freeze_period",
                "is_warmup_period",
                "is_terrorist_timeout",
                "is_ct_timeout",
                "is_technical_timeout",
                "is_waiting_for_resume",
                "is_match_started",
                "game_phase",
            ],
        )
    )


@pytest.fixture(scope="class")
def parsed_state() -> pd.DataFrame:
    """Creates mock parsed state to be filtered."""
    columns = [
        "is_freeze_period",
        "is_warmup_period",
        "is_terrorist_timeout",
        "is_ct_timeout",
        "is_technical_timeout",
        "is_waiting_for_resume",
        "is_match_started",
        "game_phase",
        "other_data",
    ]
    data = [
        [False, False, False, False, False, False, True, 2, "event1"],
        [True, False, False, False, False, False, True, 2, "nonplay1"],
        [False, True, False, False, False, False, True, 3, "nonplay2"],
        [False, False, False, False, False, False, True, 3, "event2"],
        [False, False, False, False, False, False, True, 1, "nonplay3"],
    ]
    return pd.DataFrame(data, columns=columns)


class TestParsers:
    """Tests parser methods."""

    def test_remove_nonplay_ticks_bad_cols(self):
        """Tests that we raise an error if we are missing the necessary columns."""
        with pytest.raises(
            ValueError, match="is_freeze_period not found in dataframe."
        ):
            remove_nonplay_ticks(pd.DataFrame())

    def test_remove_nonplay_ticks(self, parsed_state: pd.DataFrame):
        """Tests that we filter out non-play ticks."""
        filtered_df = remove_nonplay_ticks(parsed_state)
        assert len(filtered_df) == 2
        assert "event1" in filtered_df["other_data"].to_numpy()
        assert "event2" in filtered_df["other_data"].to_numpy()

    def test_hltv_rounds(
        self, hltv_parser: DemoParser, hltv_events: dict[str, pd.DataFrame]
    ):
        """Tests that we can get correct rounds from HLTV demos."""
        hltv_rounds = parse_rounds(hltv_parser, hltv_events)
        assert hltv_rounds.reason.to_numpy().tolist() == [
            "ct_killed",
            "ct_killed",
            "ct_killed",
            "t_killed",
            "bomb_defused",
            "ct_killed",
            "bomb_exploded",
            "t_killed",
            "bomb_defused",
            "t_killed",
            "ct_killed",
            "ct_killed",
            "ct_killed",
            "ct_killed",
            "t_killed",
            "ct_killed",
            "t_killed",
            "t_killed",
            "t_killed",
            "ct_killed",
            "t_killed",
            "bomb_exploded",
            "t_killed",
        ]

    def test_hltv_kills(self, hltv_events: dict[str, pd.DataFrame]):
        """Tests that we can get correct kills from HLTV demos."""
        hltv_kills = parse_kills(hltv_events)
        # Checks kills and headshots
        assert hltv_kills.shape[0] == 159
        assert (
            hltv_kills[
                hltv_kills["attacker_team_name"] != hltv_kills["victim_team_name"]
            ].shape[0]
            == 158
        )
        assert (
            hltv_kills[
                hltv_kills["attacker_team_name"] != hltv_kills["victim_team_name"]
            ].headshot.sum()
            == 65
        )
        # Check assists
        hltv_assists = (
            hltv_kills[
                ~hltv_kills["assister_name"].isna() & ~hltv_kills["assistedflash"]
            ]
            .groupby("assister_name")
            .size()
        ).reset_index(name="assists")
        assert all(
            hltv_assists[hltv_assists["assister_name"] == "Brollan"].assists == 3
        )
        assert all(
            hltv_assists[hltv_assists["assister_name"] == "Jimphhat"].assists == 8
        )
        assert all(
            hltv_assists[hltv_assists["assister_name"] == "chopper"].assists == 3
        )
        assert all(hltv_assists[hltv_assists["assister_name"] == "donk"].assists == 7)
        assert all(hltv_assists[hltv_assists["assister_name"] == "magixx"].assists == 4)
        assert all(hltv_assists[hltv_assists["assister_name"] == "sh1ro"].assists == 6)
        assert all(hltv_assists[hltv_assists["assister_name"] == "siuhy"].assists == 5)
        assert all(hltv_assists[hltv_assists["assister_name"] == "torzsi"].assists == 3)
        assert all(
            hltv_assists[hltv_assists["assister_name"] == "xertioN"].assists == 7
        )
        assert all(hltv_assists[hltv_assists["assister_name"] == "zont1x"].assists == 8)

    def test_hltv_damages(self, hltv_events: dict[str, pd.DataFrame]):
        """Tests that we can get correct damages from HLTV demos."""
        hltv_damage = parse_damages(hltv_events)
        hltv_damage_total = round(
            hltv_damage[
                hltv_damage["attacker_team_name"] != hltv_damage["victim_team_name"]
            ]
            .groupby("attacker_name")
            .dmg_health_real.sum()
            / 23,
            1,
        ).reset_index(name="adr")
        assert all(
            hltv_damage_total[hltv_damage_total["attacker_name"] == "Brollan"].adr
            == 91.4
        )
        assert all(
            hltv_damage_total[hltv_damage_total["attacker_name"] == "Jimpphat"].adr
            == 87.7
        )
        assert all(
            hltv_damage_total[hltv_damage_total["attacker_name"] == "chopper"].adr
            == 62.1
        )
        assert all(
            hltv_damage_total[hltv_damage_total["attacker_name"] == "donk"].adr == 72.8
        )
        assert all(
            hltv_damage_total[hltv_damage_total["attacker_name"] == "magixx"].adr
            == 65.1
        )
        assert all(
            hltv_damage_total[hltv_damage_total["attacker_name"] == "sh1ro"].adr == 93.7
        )
        assert all(
            hltv_damage_total[hltv_damage_total["attacker_name"] == "siuhy"].adr == 84.7
        )
        assert all(
            hltv_damage_total[hltv_damage_total["attacker_name"] == "torzsi"].adr
            == 73.9
        )
        assert all(
            hltv_damage_total[hltv_damage_total["attacker_name"] == "xertioN"].adr
            == 65.5
        )
        assert all(
            hltv_damage_total[hltv_damage_total["attacker_name"] == "zont1x"].adr
            == 70.8
        )

    def test_faceit_kills(self, faceit_events: dict[str, pd.DataFrame]):
        """Tests that we can get correct number of kills from FACEIT demos."""
        faceit_kills = parse_kills(faceit_events)
        # Checks kills and headshots
        assert faceit_kills.shape[0] == 156
        assert (
            faceit_kills[
                faceit_kills["attacker_team_name"] != faceit_kills["victim_team_name"]
            ].shape[0]
            == 156
        )
        assert (
            faceit_kills[
                faceit_kills["attacker_team_name"] != faceit_kills["victim_team_name"]
            ].headshot.sum()
            == 90
        )
        # Check assists
        faceit_assists = (
            faceit_kills[~faceit_kills["assister_name"].isna()]
            .groupby("assister_name")
            .size()
        ).reset_index(name="assists")
        assert all(
            faceit_assists[faceit_assists["assister_name"] == "AMANEK"].assists == 3
        )
        assert all(
            faceit_assists[faceit_assists["assister_name"] == "Burmylov"].assists == 2
        )
        assert all(
            faceit_assists[faceit_assists["assister_name"] == "Ciocardau"].assists == 7
        )
        assert all(
            faceit_assists[faceit_assists["assister_name"] == "LobaIsLove"].assists == 4
        )
        assert all(
            faceit_assists[faceit_assists["assister_name"] == "Porya555"].assists == 6
        )
        assert all(
            faceit_assists[faceit_assists["assister_name"] == "Sdaim"].assists == 10
        )
        assert all(
            faceit_assists[faceit_assists["assister_name"] == "_Aaron"].assists == 4
        )
        assert all(
            faceit_assists[faceit_assists["assister_name"] == "bibu_"].assists == 4
        )
        assert all(
            faceit_assists[faceit_assists["assister_name"] == "jottAAA-"].assists == 4
        )
        assert all(
            faceit_assists[faceit_assists["assister_name"] == "lauNX-"].assists == 5
        )
