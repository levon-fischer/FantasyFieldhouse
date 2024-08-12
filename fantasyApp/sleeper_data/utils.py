import requests
from collections import defaultdict


class SleeperAPI:
    BASE_URL = "https://api.sleeper.app/v1/"

    @staticmethod
    def fetch_data(endpoint):
        url = f"{SleeperAPI.BASE_URL}/{endpoint}"
        response = requests.get(url)
        return response.json() if response.status_code == 200 else None

    @staticmethod
    def fetch_user(username):
        return SleeperAPI.fetch_data(f"user/{username}")

    @staticmethod
    def fetch_user_leagues(user_id, season):
        return SleeperAPI.fetch_data(f"user/{user_id}/leagues/nfl/{season}")

    @staticmethod
    def fetch_league_details(league_id):
        return SleeperAPI.fetch_data(f"league/{league_id}")

    @staticmethod
    def fetch_league_rosters(league_id):
        return SleeperAPI.fetch_data(f"league/{league_id}/rosters")

    @staticmethod
    def fetch_league_users(league_id):
        return SleeperAPI.fetch_data(f"league/{league_id}/users")

    @staticmethod
    def fetch_matchups(league_id, week):
        return SleeperAPI.fetch_data(f"league/{league_id}/matchups/{week}")

    @staticmethod
    def fetch_playoff_bracket(league_id):
        return SleeperAPI.fetch_data(f"league/{league_id}/winners_bracket")

    @staticmethod
    def fetch_consolation_bracket(league_id):
        return SleeperAPI.fetch_data(f"league/{league_id}/losers_bracket")

    @staticmethod
    def fetch_draft_data(draft_id):
        return SleeperAPI.fetch_data(f"draft/{draft_id}")

    @staticmethod
    def fetch_draft_picks(draft_id):
        return SleeperAPI.fetch_data(f"draft/{draft_id}/picks")

    @staticmethod
    def fetch_players():
        return SleeperAPI.fetch_data(f"players/nfl")


def preprocess_bracket_data(league_id):
    playoff_bracket = SleeperAPI.fetch_playoff_bracket(league_id)
    consolation_bracket = SleeperAPI.fetch_consolation_bracket(league_id)

    bracket_data = defaultdict(dict)

    for match in playoff_bracket:
        process_matchup(match, bracket_data, "playoff")

    for match in consolation_bracket:
        process_matchup(match, bracket_data, "consolation")

    return bracket_data


def process_matchup(match, bracket, bracket_type):
    round_num = match.get("r")
    place = match.get("p")
    team1 = match.get("t1")
    team2 = match.get("t2")
    bracket[round_num][team1] = {"type": bracket_type, "seeding": place}
    bracket[round_num][team2] = {"type": bracket_type, "seeding": place}
