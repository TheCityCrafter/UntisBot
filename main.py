from datetime import date, timedelta
from time import sleep

import discord
import webuntis
from discord.ext import commands
from dotenv import load_dotenv
import os
import json



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

@bot.command(description="Starte den Bot")
@commands.has_permissions(administrator=True)
async def start(ctx):
    await ctx.respond("Done!", ephemeral=True)
    while True:
        sleep(10)

        # API

        CLASS = '11a'  # <-- Deine Klasse hier anpassen
        FILEPATH = 'canceledLessons.json'

        # === Zeitraum definieren ===
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

        # === WebUntis-Session ===
        session = webuntis.Session(
            username='',
            password='',
            server='',
            school='',
            useragent='Untis Canceled Lessons Bot'
        )
        s = session.login()

        # === Klasse holen ===
        klasse = s.klassen().filter(name=CLASS)[0]

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
                "lehrer": lesson.teachers[0].name if lesson.teachers else "kein Lehrer"
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
                print(f"{data['datum']} | {data['start']}–{data['end']} | {data['lesson']} mit {data['lehrer']}")
                await bot.get_channel(1369371980238819359).send(
                    f"Neuer Ausfall\n {data['datum']} | {data['start']}–{data['end']} | {data['lesson']} mit {data['lehrer']}")


load_dotenv()
bot.run(os.getenv("TOKEN"))