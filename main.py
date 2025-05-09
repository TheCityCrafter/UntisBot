
from datetime import date, timedelta, datetime

import discord
import webuntis
from discord.ext import commands, tasks
from dotenv import load_dotenv
import os
import json
from past.builtins import xrange


load_dotenv()
CLASS = os.getenv("UNTIS_CLASS")

intents = discord.Intents.all()

activity = discord.Activity(type=discord.ActivityType.custom, state="Nicht aktiviert")

bot = discord.Bot(intents=intents,
                  debug_guilds=[os.getenv("DISCORD_SERVER_ID")],
                  status=discord.Status.online,
                  activity=activity)



class MyView(discord.ui.View):
    def __init__(self, *, timeout=None):
        super().__init__(timeout=timeout)


@bot.event
async def on_ready():
    print(f"{bot.user} ist online")



#Daten überprüfung

try:
    session = webuntis.Session(
        username=os.getenv("UNTIS_USER"),
        password=os.getenv("UNTIS_PASSWORD"),
        server=os.getenv("UNTIS_SERVER"),
        school=os.getenv("UNTIS_SCHOOL"),
        useragent='Untis Canceled Lessons Bot'
    )
    s = session.login()
    klasse = s.klassen().filter(name=CLASS)[0]
    testTimetable = s.timetable(klasse=klasse, start=date.today(), end=date.today())
except Exception as e:
   print(f"Fehler: {e}")
   exit()



@tasks.loop(seconds=10)
async def send_request():
    #API
    session.logout()
    session.login()
    FILEPATH = 'canceledLessons.json'
    startDate = date.today()
    endDate = startDate + timedelta(days=30)

    #Vorherige Einträge laden
    if os.path.exists(FILEPATH) and os.path.getsize(FILEPATH) > 0:
        with open(FILEPATH, 'r', encoding='utf-8') as f:
            try:
                knownCanceledLessons = json.load(f)
            except json.JSONDecodeError:
                print("Warnung: JSON-Datei war ungültig. Sie wird zurückgesetzt.")
                knownCanceledLessons = []
    else:
        knownCanceledLessons = []

    #Stundenplan abrufen
    timetable = s.timetable(klasse=klasse, start=startDate, end=endDate)
    ausfaelle = [l for l in timetable if l.code == 'cancelled']

    #Heutige Ausfälle zählen

    todayAusfaelle = [l for l in s.timetable(klasse=klasse, start=startDate, end=startDate) if l.code == 'cancelled']
    todayAusfaelleCount = 0
    for lesson in todayAusfaelle:
        todayAusfaelleCount += 1

    await bot.change_presence(
        activity=discord.Activity(type=discord.ActivityType.custom, state=f"Heutige Ausfälle: {todayAusfaelleCount}"))

    #Neue Ausfälle erkennen und speichern
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

    #JSON-Datei aktualisieren
    with open(FILEPATH, 'w', encoding='utf-8') as f:
        json.dump(knownCanceledLessons, f, indent=2, ensure_ascii=False)

    #Ausgabe neuer Ausfälle
    if not newCanceledLessons:
        print(f"Keine neuen Ausfälle")
    else:
        for data in newCanceledLessons:

            # Lehrer Kürzel mit Name ersetzten
            with open("teachers.json") as f:
                teachersData = json.load(f)
                teacherName = data['teacher']
                for i in xrange(0, len(teachersData)):
                    if teachersData[i]["acronym"] == data['teacher']:
                        teacherName = teachersData[i]["name"]

            with open("lessons.json") as f:
                lessonData = json.load(f)
                lessonName = data['lesson']
                for i in xrange(0, len(lessonData)):
                    if lessonData[i]["acronym"] == data['lesson']:
                        lessonName = lessonData[i]["name"]






            print("Neuer Ausfall: ")
            print(f"{data['datum']} | {data['start']}–{data['end']} | {lessonName} mit {teacherName}, {data}")

            embed = discord.Embed(title=f"<:education:1370074483758465025> {lessonName}",
                                  description=f"**Details zur Unterrichtsstunde:**\n<:teacher:1370074551475638412> {teacherName}\n<:calendar:1370046653230223361> {data['datum']}\n<:hourglass:1370074502146294011>{data['start']} - {data['end']} Uhr",
                                  colour=0xff0000,
                                  timestamp=datetime.now())

            embed.set_author(name="Ausfall")

            embed.set_footer(text="UntisBot",
                             icon_url="https://icones.pro/wp-content/uploads/2022/10/icone-robot-orange.png")

            await bot.get_channel(int(os.getenv("DISCORD_CHANNEL_ID"))).send(embed=embed)
            #await bot.get_channel(1369371980238819359).send("<@&1370078528615223339>")




@bot.command(description="Start the Bot")
@commands.has_permissions(administrator=True)
async def start(ctx):
    await ctx.respond("Done!", ephemeral=True)
    send_request.start()
    print("Ein Loop wurde gestartet")



@bot.command(description="Stop the Bot")
@commands.has_permissions(administrator=True)
async def stop(ctx):
    await ctx.respond("Done!", ephemeral=True)
    send_request.stop()
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.custom, state="Nicht aktiviert"))
    print("Ein Loop wurde beendet")





load_dotenv()
try:
    bot.run(os.getenv("BOT_TOKEN"))
except Exception as e:
    print(f"Fehler: {e}")
    exit()