# UntisBot
This Discord Bot notifies you when a new outage is entered in Untis
## Setup
****
### 1. Create a bot on the [Discord Developer Page](https://discord.dev) and generate a Token
**Important:** Remember to activate all intents on your bot.
****
### 2. Install Dependencies:
 All dependencies are listed in the requirements.txt. Most installation programs install them automatically (Pterodactyl Eggs, etc.).
****
### 3. Get your Untis School Server URL and Internal Name. <br>
A way to find these Informations is to go into the [Untis Website](https://webuntis.com) and search your school. After that copy the URL. The part until the first slash (/) is the Server URL. The Internal Name can be found in the url after "school=". If there is a plus in the name, replace it with a blank space. <br><br>
Example: https://example.webuntis.com/WebUntis/?school=Test+School#/basic/login <br><br>
Server:  https://example.webuntis.com <br>
Internal Name: Test School
****
### 4. Enter your Informations in the .env File:
   Following Informations are important:
   <br> 
   - Discord:
   - Bot Token
   - Channel ID
   - Server ID
   - Untis:
   - Your Untis username
   - Your Untis password
   - Untis School Server
   - Untis School Internal Name
   - Exact Name of your Class
****
### 5. Run the Bot

_Note: All Bot messages are in german but can be altered in the source code_

****
### Additional Information:
On Webuntis most of the time acronyms are used to indicate teachers or subjects. These can be adapted in lessons.json and teachers.json and changed to clear names. (See examples in the respective files)


## Common Errors:
1. bad credentials -> Wrong Username or Password
2. list index out of range -> Class not found
3. no right for timetable -> Your user doesn't have access to the class 
4. Request ID was not the same one as returned. -> Internal School Name is wrong
5. HTTPSConnectionPool -> School Server IP is wrong
6. Error Improper token has been passed. -> Wrong Discord Bot Token
<p>
If any other errors occur fell free to contact me on Discord: @thecitycrafter