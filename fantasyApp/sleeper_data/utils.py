import requests
from collections import defaultdict
from typing import Union, Dict, List, Any, Optional


class SleeperAPI:
    """
    A class to represent the Sleeper API and fetch data from it.
    """
    BASE_URL = "https://api.sleeper.app/v1/"

    @staticmethod
    def fetch_data(endpoint: str) -> Optional[Dict, List[Dict]]:
        """
        General method to fetch data from the Sleeper API.
        :param endpoint: The endpoint to fetch data from.
        :return: The JSON data returned from the API as a dictionary.
        """
        url = f"{SleeperAPI.BASE_URL}/{endpoint}"
        response = requests.get(url)
        return response.json() if response.status_code == 200 else None

    @staticmethod
    def fetch_user(username: str) -> dict:
        """
        Fetch user data from the Sleeper API.
        :param username:
        :return: a dictionary of user data that includes username, user_id, and display_name.
        """
        return SleeperAPI.fetch_data(f"user/{username}")

    @staticmethod
    def fetch_user_leagues(user_id: int, season: int) -> list[dict]:
        """
        Fetch all leagues in a particular season for a particular user from the Sleeper API.
        :param user_id: The sleeper ID of the user
        :param season: The season (year) to fetch leagues for
        :return: A list of dictionaries containing league data for that user's leagues in that season.
        """
        return SleeperAPI.fetch_data(f"user/{user_id}/leagues/nfl/{season}")

    @staticmethod
    def fetch_league_details(league_id: int) -> dict:
        """
        Fetch a specific league's details from the Sleeper API.
        :param league_id: The sleeper ID of the league
        :return: A dictionary containing league data that includes status, previous_league_id, name, settings, etc.
        """
        return SleeperAPI.fetch_data(f"league/{league_id}")

    @staticmethod
    def fetch_league_rosters(league_id: int) -> list[dict]:
        """
        Fetch all rosters in a league from the Sleeper API.
        :param league_id: The sleeper ID of the league
        :return: A list of dictionaries containing roster data for each roster in that league.
        """
        return SleeperAPI.fetch_data(f"league/{league_id}/rosters")

    @staticmethod
    def fetch_league_users(league_id: int) -> list[dict]:
        """
        Fetch all users in a league from the Sleeper API.
        :param league_id: The sleeper ID of the league
        :return: A list of dictionaries containing each user's username, display_name, avatar, and metadata which sometimes includes a nickname they gave their team..
        """
        return SleeperAPI.fetch_data(f"league/{league_id}/users")

    @staticmethod
    def fetch_matchups(league_id: int, week: int) -> list[dict]:
        """
        This retrieves all matchups in a league for a given week. Each dictionary in the list represents one team.
        The two teams with the same matchup_id match up against each other.
        The starters is in an ordered list of player_ids, and players is a list of all player_ids in this matchup
        The bench can be deduced by removing the starters from the players field.
        :param league_id: The sleeper ID of the league
        :param week: The week number to fetch matchups for
        :return: Returns a list of dictionaries containing matchup data for each matchup in that week.
        """
        return SleeperAPI.fetch_data(f"league/{league_id}/matchups/{week}")

    @staticmethod
    def fetch_playoff_bracket(league_id: int) -> list[dict]:
        """
        Fetches the playoff bracket for a league for 4, 6, and 8 team playoffs.
        Each dictionary represents a matchup between 2 teams.
        r: The round for this matchup, 1st, 2nd, 3rd round, etc.
        m: The match id of the matchup, unique for all matchups within a bracket.
        t1: The roster_id of a team in this matchup OR {w: 1} which means the winner of match id 1
        t2: The roster_id of a team in this matchup OR {w: 2} which means the winner of match id 2
        w: The roster_id of the winning team, if the match has been played
        l: The roster_id of the losing team, if the match has been played
        t1_from: Where t1 comes from, either winner or loser of the match id, necessary to show bracket progression
        t2_from: Where t2 comes from, either winner or loser of the match id, necessary to show bracket progression
        :param league_id: The sleeper ID of the league
        :return: A list of dictionaries containing playoff bracket data for that league.
        """
        return SleeperAPI.fetch_data(f"league/{league_id}/winners_bracket")

    @staticmethod
    def fetch_consolation_bracket(league_id: int) -> list[dict]:
        """
        Fetches the consolation bracket for a league for 4, 6, and 8 team playoffs.
        Each dictionary represents a matchup between 2 teams.
        r: The round for this matchup, 1st, 2nd, 3rd round, etc.
        m: The match id of the matchup, unique for all matchups within a bracket.
        t1: The roster_id of a team in this matchup OR {w: 1} which means the winner of match id 1
        t2: The roster_id of a team in this matchup OR {w: 2} which means the winner of match id 2
        w: The roster_id of the winning team, if the match has been played
        l: The roster_id of the losing team, if the match has been played
        t1_from: Where t1 comes from, either winner or loser of the match id, necessary to show bracket progression
        t2_from: Where t2 comes from, either winner or loser of the match id, necessary to show bracket progression
        :param league_id: The sleeper ID of the league
        :return: A list of dictionaries containing consolation bracket data for that league.
        """
        return SleeperAPI.fetch_data(f"league/{league_id}/losers_bracket")

    @staticmethod
    def fetch_draft_data(draft_id: int) -> dict:
        """
        Fetches a specific draft's data from the Sleeper API.
        :param draft_id: The sleeper ID of the draft
        :return: A dictionary containing draft data that includes draft_id, status, type, and metadata.
        """
        return SleeperAPI.fetch_data(f"draft/{draft_id}")

    @staticmethod
    def fetch_draft_picks(draft_id: int) -> list[dict]:
        """
        Fetches all picks in a draft from the Sleeper API.
        :param draft_id: The sleeper ID of the draft
        :return: A list of dictionaries containing pick data for each pick in that draft.
        """
        return SleeperAPI.fetch_data(f"draft/{draft_id}/picks")

    @staticmethod
    def fetch_players() -> dict:
        """
        Fetches all players in the NFL from the Sleeper API. Should only be called once per day
        :return: A dictionary containing player data for all players in the NFL. The key is the player_id.
        """
        return SleeperAPI.fetch_data(f"players/nfl")


def preprocess_bracket_data(league_id: int) -> dict:
    """
    This function fetches the playoff and consolation brackets for a league and processes the data to make it easier to work with.
    :param league_id: The sleeper ID of the league
    :return: A dictionary containing the bracket data for the league.
    """
    playoff_bracket = SleeperAPI.fetch_playoff_bracket(league_id)
    consolation_bracket = SleeperAPI.fetch_consolation_bracket(league_id)

    bracket_data = defaultdict(dict)

    for match in playoff_bracket:
        process_matchup(match, bracket_data, "playoff")

    for match in consolation_bracket:
        process_matchup(match, bracket_data, "consolation")

    return bracket_data


def process_matchup(match: dict, bracket: defaultdict, bracket_type: str) -> None:
    """
    This function pulls out the relevant data from a matchup and adds it to the bracket dictionary.
    :param match: A dictionary representing a matchup in the bracket.
    :param bracket: The dictionary containing the bracket data.
    :param bracket_type: The type of bracket, either "playoff" or "consolation".
    :return: None
    """
    round_num = match.get("r")
    place = match.get("p")
    team1 = match.get("t1")
    team2 = match.get("t2")
    bracket[round_num][team1] = {"type": bracket_type, "seeding": place}
    bracket[round_num][team2] = {"type": bracket_type, "seeding": place}
