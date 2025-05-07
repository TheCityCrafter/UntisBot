from datetime import date, timedelta, datetime
from time import sleep

import discord
import webuntis
from discord.ext import commands
from dotenv import load_dotenv
import os
import json


load_dotenv()
CLASS = os.getenv("CLASS")

intents = discord.Intents.all()

activity = discord.Activity(type=discord.ActivityType.custom, name="Hallo")

bot = discord.Bot(intents=intents,
                  debug_guilds=[802651359743705139],
                  status=discord.Status.dnd,
                  activity=activity)


class MyView(discord.ui.View):
    def __init__(self, *, timeout=None):
        super().__init__(timeout=timeout)


@bot.event
async def on_ready():
    print(f"{bot.user} ist online")

channel = bot.get_channel(1369371980238819359)

try:
    session = webuntis.Session(
        username=os.getenv("USER"),
        password=os.getenv("PASSWORD"),
        server=os.getenv("SERVER"),
        school=os.getenv("SCHOOL"),
        useragent='Untis Canceled Lessons Bot'
    )
    s = session.login()
    klasse = s.klassen().filter(name=CLASS)[0]
    testTimetable = s.timetable(klasse=klasse, start=date.today(), end=date.today())
except Exception as e:
   print(f"Fehler: {e}")
   exit()


@bot.command(description="Starte den Bot")
@commands.has_permissions(administrator=True)
async def start(ctx):
    await ctx.respond("Done!", ephemeral=True)
    while True:
        # API
        FILEPATH = 'canceledLessons.json'
        startDate = date.today()
        endDate = startDate + timedelta(days=30)

        # === Vorherige Einträge laden (mit Fehlerprüfung) ===
        if os.path.exists(FILEPATH) and os.path.getsize(FILEPATH) > 0:
            with open(FILEPATH, 'r', encoding='utf-8') as f:
                try:
                    knownCanceledLessons = json.load(f)
                except json.JSONDecodeError:
                    print("Warnung: JSON-Datei war ungültig. Sie wird zurückgesetzt.")
                    knownCanceledLessons = []
        else:
            knownCanceledLessons = []

        # === Stundenplan abrufen ===
        timetable = s.timetable(klasse=klasse, start=startDate, end=endDate)
        ausfaelle = [l for l in timetable if l.code == 'cancelled']

        # === Neue Ausfälle erkennen und speichern ===
        newCanceledLessons = []

        for lesson in ausfaelle:
            data = {
                "datum": lesson.start.date().isoformat(),
                "start": lesson.start.strftime('%H:%M'),
                "end": lesson.end.strftime('%H:%M'),
                "lesson": lesson.subjects[0].name if lesson.subjects else "kein Fach",
                "teacher": lesson.teachers[0].name if lesson.teachers else "kein Lehrer"
            }

            if data not in knownCanceledLessons:
                newCanceledLessons.append(data)
                knownCanceledLessons.append(data)

        # === JSON-Datei aktualisieren ===
        with open(FILEPATH, 'w', encoding='utf-8') as f:
            json.dump(knownCanceledLessons, f, indent=2, ensure_ascii=False)

        # === Ausgabe neuer Ausfälle ===
        if not newCanceledLessons:
            print("Keine neuen Ausfälle")
        else:
            for data in newCanceledLessons:
                print("Neuer Ausfall: ")
                print(f"{data['datum']} | {data['start']}–{data['end']} | {data['lesson']} mit {data['teacher']}")

                embed = discord.Embed(title=f":x: {data['lesson']}",
                                      description=f"**{data['lesson']}** mit {data['teacher']} entfällt!\n> {data['datum']} - {data['start']}–{data['end']}",
                                      colour=0xff0000,
                                      timestamp=datetime.now())

                embed.set_author(name="Untis-Aktualisierung")

                embed.set_footer(text="Untis-Bot")

                # await bot.get_channel(1369371980238819359).send(embed = embed)
        sleep(10)

load_dotenv()
try:
    bot.run(os.getenv("TOKEN"))
except Exception as e:
    print(f"Fehler: {e}")
    exit()