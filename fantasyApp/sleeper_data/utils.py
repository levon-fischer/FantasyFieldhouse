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
