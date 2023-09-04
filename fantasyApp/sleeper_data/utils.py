import requests


class SleeperAPI:
    BASE_URL = "https://api.sleeper.app/v1/"

    @staticmethod
    def fetch_user(username):
        url = f"{SleeperAPI.BASE_URL}/user/{username}"
        response = requests.get(url)
        return response.json() if response.status_code == 200 else None

    @staticmethod
    def fetch_user_leagues(user_id, season):
        url = f"{SleeperAPI.BASE_URL}/user/{user_id}/leagues/nfl/{season}"
        response = requests.get(url)
        return response.json() if response.status_code == 200 else None

    @staticmethod
    def fetch_league_details(league_id):
        url = f"{SleeperAPI.BASE_URL}/league/{league_id}"
        response = requests.get(url)
        return response.json() if response.status_code == 200 else None

    @staticmethod
    def fetch_league_rosters(league_id):
        url = f"{SleeperAPI.BASE_URL}/league/{league_id}/rosters"
        response = requests.get(url)
        return response.json() if response.status_code == 200 else None

    @staticmethod
    def fetch_league_users(league_id):
        url = f"{SleeperAPI.BASE_URL}/league/{league_id}/users"
        response = requests.get(url)
        return response.json() if response.status_code == 200 else None

    @staticmethod
    def fetch_matchups(league_id, week):
        url = f"{SleeperAPI.BASE_URL}/league/{league_id}/matchups/{week}"
        response = requests.get(url)
        return response.json() if response.status_code == 200 else None

    @staticmethod
    def fetch_playoff_bracket(league_id):
        url = f"{SleeperAPI.BASE_URL}/league/{league_id}/winners_bracket"
        response = requests.get(url)
        return response.json() if response.status_code == 200 else None

    @staticmethod
    def fetch_consolation_bracket(league_id):
        url = f"{SleeperAPI.BASE_URL}/league/{league_id}/losers_bracket"
        response = requests.get(url)
        return response.json() if response.status_code == 200 else None


def process_single_matchup(match, bracket_type, bracket_data, total_teams):
    for t1, t2 in [(match["t1"], match["t2"]), (match["t2"], match["t1"])]:
        placement = match.get("p", None)
        if placement is not None:
            if bracket_type == "playoff":
                if t1 == match["l"]:
                    placement += 1
            else:
                placement = placement + (total_teams // 2)
                if t1 == match["l"]:
                    placement += 1
        bracket_data[(match["r"], t1)] = {
            "type": bracket_type,
            "opponent": t2,
            "winner": match["w"],
            "loser": match["l"],
            "placement": placement,
        }


def preprocess_bracket_data(league_id, total_teams):
    playoff_bracket = SleeperAPI.fetch_playoff_bracket(league_id)
    consolation_bracket = SleeperAPI.fetch_consolation_bracket(league_id)
    bracket_data = {}

    for match in playoff_bracket:
        process_single_matchup(match, "playoff", bracket_data, total_teams)

    for match in consolation_bracket:
        process_single_matchup(match, "consolation", bracket_data, total_teams)

    return bracket_data
