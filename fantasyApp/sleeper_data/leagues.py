from datetime import datetime

from celery import shared_task
from fantasyApp.sleeper_data.seasons import (
    add_season_from_data,
    add_season_from_api,
    update_league_ids,
)
from fantasyApp.sleeper_data.utils import SleeperAPI
from fantasyApp.models import League, Season
from fantasyApp import db
from flask import current_app


@shared_task(name="check_for_new_leagues")
def check_for_new_leagues(user_id):
    current_year = datetime.now().year

    # Fetch the user's current leagues
    leagues_data = SleeperAPI.fetch_user_leagues(user_id, current_year)

    if leagues_data:  # If the user has leagues
        current_app.logger.info(f"Found {len(leagues_data)} leagues for user {user_id}")
        for league_data in leagues_data:  # For each league
            # Check if the league exists in our database
            current_season_id = league_data["league_id"]
            league = League.query.filter_by(current_season_id=current_season_id).first()
            # If the league exists, skip it
            if league:
                current_app.logger.info(
                    f"League {current_season_id} already exists in our database"
                )
                continue

            # If the league does not exist, add it to our database
            current_app.logger.info(
                f"Adding league {current_season_id} to our database"
            )
            add_or_update_league(current_season_id)


def add_or_update_league(current_season_id):
    season_data = SleeperAPI.fetch_league_details(current_season_id)
    if season_data:  # If the season exists on Sleeper
        # Create a season for the league
        add_season_from_data(season_data=season_data, league_id=current_season_id)
        # Add the previous seasons for the league
        previous_season_id = season_data["previous_league_id"]
        while previous_season_id:
            # Check if the previous season exists in our database
            season = Season.query.filter_by(id=previous_season_id).first()
            # If the season exists, update the league_id for each season
            if season:
                current_app.logger.info(
                    f"Previous seasons exist for league {current_season_id}, updating league_ids"
                )
                update_league_ids(
                    season_id=previous_season_id, league_id=current_season_id
                )
                break
            else:  # Otherwise, add the previous season to our database
                previous_season_id = add_season_from_api(
                    previous_season_id, current_season_id
                )

        # Add the league to our database
        current_app.logger.info(
            f"Finished adding new seasons for league {current_season_id}"
        )
        league = League(current_season_id=current_season_id, name=season_data["name"])
        db.session.add(league)
        db.session.commit()
        current_app.logger.info(f"Added league {current_season_id} to our database")
