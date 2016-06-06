from google.appengine.api import namespace_manager
import google.appengine.ext.ndb as ndb
import logging as log
import time
from extractors import teams
import secrets
import telegram

releases_to_check = ['Hunter x Hunter']


class Release(ndb.Model):
    name = ndb.StringProperty(indexed=False)
    date = ndb.DateTimeProperty(auto_now_add=True)


def check_releases():
    log.info("Checking releases at " + str(time.strftime("%c")))
    for team in teams:
        log.info("Fetching releases from " + team.name + "...")
        try:
            for release in filter(lambda x: is_monitored(x), team.fetch_f()):
                send_notification_if_needed(team, release)
        except Exception:
            log.warning("Unable to fetch releases from " + team.name + ". Going to skip it.")


def send_notification_if_needed(team, release):
    previous_namespace = namespace_manager.get_namespace()
    try:
        namespace_manager.set_namespace(team.db_namespace)
        item = ndb.Key('Release', release).get()
        if not item:
            try:
                op_bot = telegram.Bot(token=secrets.op_bot_token)
                message = "Hey, cacciatori! Nuovo capitolo disponibile!\n" + team.name + ": " + release + "\n\nBuona lettura!"
                op_bot.sendMessage(chat_id=secrets.telegram_chat_id, text=message)
                Release(id=release, name=release).put()
            except Exception as e:
                log.warning("Unable to send Telegram notification.")
                log.warning(e.message)
    except Exception as e:
        log.warning("Unable to store data on Datastore.")
        log.warning(e.message)
    finally:
        namespace_manager.set_namespace(previous_namespace)


def get_status():
    return "Hunter x Hunter Scan Bot is running."


def is_monitored(manga):
    for release in releases_to_check:
        if release.lower() in manga.lower():
            return True
    return False
