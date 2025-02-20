"""Imports"""
import os
import discord
import asyncio
# import music21
# import cogs.midi2png
import random
from functions import blocked, updateinc
# from midi2audio import FluidSynth
from discord.commands import slash_command, Option
from discord.ext import commands
# from io import StringIO, BytesIO
# from PIL import Image
import re
import lists
import time

headers = {
    "User-Agent":
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36 Edge/91.0.864.59"
}

"""
Requirements
install package fluidsynth
midi2audio
music21
matplotlib
pillow
"""

color = discord.Colour

# Count the notes given
def countnotes(notes: str) -> str:
    import re
    if "X" not in notes[:5]:
        check = re.search("[^(a-gA-GzZ,'=_\^/\[\]\(\)\%\- \d)]+", notes)
        if check:
            return f"Error | Character `{notes[check.start()]}` in position {check.start()} is invalid"
    notes = "".join(["."*(int(n)-1) if n.isdigit() else n for n in notes])
    return len(re.sub("[^(a-gA-G).]+", "", notes))

class FunCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @slash_command(description="Play Tic-Tac-Toe with an AI or another user", usage="/tictactoe [user] [bet]")
    @commands.cooldown(1, 15, commands.BucketType.user)
    async def tictactoe(self, ctx, user: Option(discord.Member, "User to play with") = None, bet: Option(int, "Bet amount", min_value=10, max_value=5000) = None):
        await __import__('slash').tictactoe(self, ctx, user, bet)

    # @commands.cooldown(1, 10, commands.BucketType.user)
    # @commands.command(usage="ov play \`<notes>\` [instrument] [music name] [key] [default note length] [time signature]\nov play \`\`\`<notes>\`\`\` [instrument] [music name] [key] [default note length] [time signature]\nov play builtin <song name> [instrument] [music name] [key] [default note length] [time signature]\nov play <mp3 file> [instrument] [music name] [key] [default note length] [time signature]\nov play <text file with ABC notation> [instrument] [music name] [key] [default note length] [time signature]", description="Play music from ABC notation\nMiddle C is noted as `C`\nC in a higher octave is noted as `c`\nSo a full one octave C major scale from middle C is `CDEFGABc`\nFour octaves C major scale from middle C is `C,D,E,F,G,A,B,CDEFGABcdefgabc'd'e'f'g'a'b'`\nWhich `,` means one octave lower and `'` means one octave higher\nFor minim, dotted minim and semibrave notes, they are noted using `C2C3C4`\nQuavers, semiquavers are noted using `C/2C/4C/4`\nFor chords, it is noted using square brackets, `[CDE][FG]`", hidden=True)
    # async def play(self, ctx, *notes):
    #     if await blocked(ctx.author.id) == False:
    #         return

    #     #Check if bot has permissions to connect or speak
    #     if ctx.guild.me.guild_permissions.connect is False:
    #         await ctx.send("I don't have the permission to connect to a voice channel")
    #         ctx.command.reset_cooldown(ctx)
    #         return
    #     elif ctx.guild.me.guild_permissions.speak is False:
    #         await ctx.send("I don't have the permission to speak in voice channels")
    #         ctx.command.reset_cooldown(ctx)
    #         return

    #     # Check if bot is already in a voice channel
    #     if ctx.voice_client is not None:
    #         await ctx.send("I am already in a voice channel playing a song")
    #         ctx.command.reset_cooldown(ctx)
    #         return
        
    #     # Check if the user is in a voice channel
    #     if ctx.author.voice is None:
    #         await ctx.send("You are not in a voice channel")
    #         ctx.command.reset_cooldown(ctx)
    #         return

    #     # Check if user wants to play a file
    #     author = None
    #     queries = None
    #     file_given = False
    #     if ctx.message.attachments:
    #         # Check if it is an audio file that can be played directly
    #         if ctx.message.attachments[0].filename[-4:] == ".mp3" or ctx.message.attachments[0].filename[-4:] == ".wav":
    #             file_given = True
    #         # Check if it is a text file with ABC notation
    #         elif ctx.message.attachments[0].filename[-4:] == ".txt":
    #             content = await ctx.message.attachments[0].read()
    #             content = content.decode("utf-8")
    #             queries = notes
    #             notes = "```" + content + "```"
    #         else:
    #             await ctx.send("I can only read mp3, wav or text files!")
    #             return

    #     loop = asyncio.get_running_loop()

    #     if not file_given:
    #         # Creating the wav file
    #         if notes == ():
    #             await ctx.send("Give notes to play!")
    #             ctx.command.reset_cooldown(ctx)
    #             return
                
    #         if type(notes) == tuple:
    #             if len(notes) != 1 and ("X" in notes[0][:5] or "X" in notes[1][:5]):
    #                 notes = "\n".join(notes)
    #             else:
    #                 notes = " ".join(notes)
    #         if queries:
    #             queries = " ".join(queries)

    #         # Check if user wants to play built-in songs
    #         file = None
    #         if notes.startswith("builtin"):
    #             try:
    #                 builtin_song = f"cogs/builtin/{notes.split(' ')[1].lower()}.abc"
    #             except:
    #                 await ctx.send(f"**Available built-in songs** {', '.join([f[:-4] for f in os.listdir('cogs/builtin')])}")
    #             if not os.path.exists(builtin_song):
    #                 await ctx.send(f"Cannot find this built-in song!\n**Available built-in songs** {', '.join([f[:-4] for f in os.listdir('cogs/builtin')])}")
    #                 ctx.command.reset_cooldown(ctx)
    #                 return
    #             music_name = None
    #             if len(notes.split(" ")) != 2:
    #                 instrument, music_name, key, default_note_length, time_signature, *_ = [q for q in notes.split(" ", 2)[-1].strip().split(" ") if q != ""] + [None]*6
    #             else:
    #                 instrument = key = default_note_length = time_signature = None
    #             music_name = music_name or notes.split(' ')[1].lower().title()
    #             author = "Built-in song"
    #             f = open(builtin_song, "r")
    #             notes = f.read()
    #             f.close()
    #             file = StringIO(notes)
    #             file = discord.File(file, "song.txt")
    #             notecount = countnotes(notes)
    #             await ctx.send(f"Playing builtin song **{music_name}**, please wait...\n**{notecount} Total notes**\n**Estimated time** {round((notecount/50)+0.4, 2)} seconds", file=file)

    #         if not file:
    #             # Check if user given notes are in a code block
    #             if "`" not in notes:
    #                 await ctx.send("Your notes must be wrapped around with one backtick ` or triple backticks ```")
    #                 ctx.command.reset_cooldown(ctx)
    #                 return
    #             elif notes.count("`") not in [2, 6]:
    #                 await ctx.send("Only one backtick or triple backticks are allowed")
    #                 ctx.command.reset_cooldown(ctx)
    #                 return

    #             # Defining variables
    #             if notes.count("`") == 2:
    #                 instrument, music_name, key, default_note_length, time_signature, *_ = [q for q in notes.split("`")[-1].strip().split(" ") if q != ""] + [None]*6
    #                 notes = notes.split("`")[1]

    #             elif notes.count("`") == 6:
    #                 if not ctx.message.attachments or not queries:
    #                     instrument, music_name, key, default_note_length, time_signature, *_ = [q for q in notes.split("```")[-1].strip().split(" ") if q != ""] + [None]*6
    #                     notes = notes.split("```")[1]
    #                 else:
    #                     if queries:
    #                         instrument, music_name, key, default_note_length, time_signature, *_ = [q for q in queries.split(" ") if q != ""] + [None]*6
    #                         notes = notes.split("```")[1]

    #         # Assigning default variables
    #         instrument = instrument or "piano"
    #         key = key or "C"
    #         default_note_length = default_note_length or "1/4"
    #         time_signature = time_signature or "C"

    #         # Count notes
    #         notecount = countnotes(notes)

    #         if type(notecount) == str and notecount.startswith("Error"):
    #             await ctx.send(f"You entered some invalid characters\n{notecount.split(' | ')[-1]}")
    #             ctx.command.reset_cooldown(ctx)
    #             return

    #         if notecount < 5:
    #             await ctx.send("Too less notes! Must have at least 5 notes length")
    #             ctx.command.reset_cooldown(ctx)
    #             return
    #         elif notecount >= 2500 and ctx.author.id != 615037304616255491:
    #             await ctx.send("Too much notes! Maximum 2500 notes length")
    #             ctx.command.reset_cooldown(ctx)
    #             return

    #         instrument = instrument.lower()
    #         valid_instrument = ["piano", "violin", "flute"]
    #         if not instrument.startswith("!"):
    #             if instrument not in valid_instrument:
    #                 await ctx.send(f"Invalid insturment, can only be one of these `{', '.join(valid_instrument)}`")
    #                 ctx.command.reset_cooldown(ctx)
    #                 return
    #         else:
    #             instrument = instrument[1:]

    #         valid_note_length = ["1/2", "1/4", "1/8", "1/16"]
    #         if default_note_length not in valid_note_length:
    #             await ctx.send(f"Invalid note length! You can only enter one of these `{', '.join(valid_note_length)}`")
    #             ctx.command.reset_cooldown(ctx)
    #             return

    #         default_note_length = default_note_length.upper()
    #         valid_time_signature = ["C", "C|", "1/2", "1/4", "1/8", "1/16"]
    #         if default_note_length not in valid_note_length:
    #             await ctx.send(f"Invalid time signature! You can only enter one of these `{', '.join(valid_time_signature)}`")
    #             ctx.command.reset_cooldown(ctx)
    #             return

    #         key = key.capitalize()
    #         valid_key = "ABCDEFG"
    #         valid_key_modifier = "mb#"
    #         if key[0] not in [note for note in valid_key] or len(key) > 2 or (len(key) == 2 and key[1] not in valid_key_modifier):
    #             await ctx.send(f"Invalid key! You can only enter one of these\n`{', '.join([x+y for x,y in __import__('itertools').product(valid_key, valid_key_modifier)])}`")
    #             ctx.command.reset_cooldown(ctx)
    #             return

    #         music_name = music_name or f"{ctx.author.name}'s Masterpiece"

    #         if file is None:
    #             await ctx.send(f"Processing your notes, please wait...\n**{notecount} Total notes**\n**Estimated time** {round((notecount/50)+0.4, 2)} seconds")

    #         import time
    #         start = time.time()

    #         # Write the notes in an abc file
    #         if "X" not in notes[:5]:
    #             def file1(music_name, ctx, time_signature, default_note_length, key, notes):
    #               with open(f"cogs/temp/{ctx.author}.abc", "w") as f:
    #                   f.write("""
    #   X:1
    #   T:{0}'s Masterpiece
    #   T:{1}#{2}
    #   M:{3}
    #   L:{4}
    #   K:{5}
    #   {6}|
    #                   """.format(music_name, ctx.author.name, ctx.author.discriminator, time_signature, default_note_length, key, notes))
    #                   f.close()
    #             await loop.run_in_executor(None, file1, music_name, ctx, time_signature, default_note_length, key, notes)
    #         else:
    #             def file2(ctx, notes):
    #               with open(f"cogs/temp/{ctx.author}.abc", "w") as f:
    #                   f.write("""{0}""".format(notes))
    #                   f.close()
    #             await loop.run_in_executor(None, file2, ctx, notes)

    #         try:
    #             stream = await loop.run_in_executor(None, music21.converter.parse, f"cogs/temp/{ctx.author}.abc")
    #         except Exception as e:
    #             await ctx.send("Parsing notation to stream **Failed**")
    #             raise e
    #         finally:
    #             os.remove(f"cogs/temp/{ctx.author}.abc")

    #         try:
    #             await loop.run_in_executor(None, stream.write, 'midi', f"cogs/temp/{ctx.author}.mid")
    #         except Exception as e:
    #             await ctx.send("Converting stream to MIDI file **Failed**")
    #             raise e

    #         try:
    #             fs = await loop.run_in_executor(None, FluidSynth, f"cogs/soundfonts/{instrument}.sf2", 22050)
    #             await loop.run_in_executor(None, fs.midi_to_audio, f'cogs/temp/{ctx.author}.mid', f'cogs/temp/{ctx.author}.wav')
    #         except Exception as e:
    #             await ctx.send("Rendering MIDI file failed, try again after 2 minutes")
    #             os.remove(f"cogs/temp/{ctx.author}.mid")
    #             os.system("install-pkg fluidsynth")
    #             raise e

    #         end = time.time()

    #         author = author or ctx.author

    #         embed = discord.Embed(title=f"Playing {music_name}", description=f"By {author}", color=color.blurple())

    #         previous_img = None
    #         try:
    #             images = await cogs.midi2png.midi2png(f"cogs/temp/{ctx.author}.mid")
    #             os.remove(f"cogs/temp/{ctx.author}.mid")

    #             img_size = (400, 250)
    #             column = 1
    #             largest_column = column
    #             row = 1
    #             for image in images[:40]:
    #                 current_img = Image.open(BytesIO(image))
    #                 current_img = current_img.resize(img_size, Image.NEAREST)

    #                 if previous_img:
    #                     merged_img = Image.new('RGB', (img_size[0]*largest_column, img_size[1]*row), (0,0,0))
    #                     merged_img.paste(previous_img, (0,0))
    #                     merged_img.paste(current_img, (img_size[0]*(column-1), img_size[1]*(row-1)))
    #                     previous_img = merged_img
    #                 else:
    #                     previous_img = current_img
                    
    #                 if column % 4 == 0:
    #                     row += 1
    #                     largest_column = 4
    #                     column = 1
    #                 else:
    #                     column += 1
    #                     if row == 1:
    #                         largest_column = column
    #         except Exception as e:
    #             embed.add_field(name="Error", value="Converting to image failed")
    #             raise e

    #         embed.add_field(name=f"Finished processing", value=f"**Time took** {round(end-start, 2)} seconds\n**Average time** {round(notecount/(end-start), 2)} notes per second")
    #         if "X" not in notes[:5]:
    #             embed.add_field(name="Music information", value=f"**Instrument** {instrument.capitalize()}\n**Total notes** {notecount}\n**Key** {key}\n**Default note length** {default_note_length}\n**Time signature** {time_signature}")
    #         else:
    #             embed.add_field(name="Music information", value=f"**Instrument** {instrument.capitalize()}\n**Total notes** {notecount}")
    #         embed.set_footer(text="nice song!")

    #         if previous_img is not None:
    #             byte = BytesIO()

    #             previous_img.save(byte, format="png")
    #             byte.seek(0)
    #             file = discord.File(fp=byte,filename="song.png")
    #             embed.set_image(url="attachment://song.png")
    #             embed.description += f"\n\n**Image size** {previous_img.size}"
    #             await ctx.send(embed=embed, file=file)
    #         else:
    #             embed.description += "\n\n**No image**"
    #             await ctx.send(embed=embed)

    #     # Check if the user is still in a voice channel and connect to it after creating the .wav file
    #     if ctx.author.voice is None:
    #         await ctx.send("You are not in a voice channel")
    #         return
    #     else:
    #         if ctx.voice_client is not None:
    #             await ctx.send("I am already in a voice channel playing a song")
    #             return
    #         vc = await ctx.author.voice.channel.connect()

    #     # Playing the wav file
    #     try:
    #         song_file = f"cogs/temp/{ctx.author}.wav"
    #         if file_given:
    #             content = await ctx.message.attachments[0].read()
    #             def file3(song_file, content):
    #                 with open(song_file, mode="bx") as f:
    #                     f.write(content)
    #                     f.close()
    #             await loop.run_in_executor(None, file3, song_file, content)
    #         vc.play(discord.FFmpegOpusAudio(song_file))
    #     except Exception as e:
    #         os.remove(f"cogs/temp/{ctx.author}.wav")
    #         await vc.disconnect()
    #         await ctx.send("An error occurred when trying to play your notes")
    #         raise e

    #     # Disconnecting the voice channel after finish playing
    #     # Check if the bot is still playing
    #     while vc.is_playing():
    #         # Check if the user disconnected
    #         if ctx.author.voice is None:
    #             await vc.disconnect()
    #             await ctx.send("You disconnected from the voice channel")
    #             os.remove(f"cogs/temp/{ctx.author}.wav")
    #             return
    #         # Check if the user changed a voice channel
    #         elif ctx.author.voice.channel != ctx.guild.me.voice.channel:
    #             await vc.disconnect()
    #             await ctx.send("You switched to another voice channel")
    #             os.remove(f"cogs/temp/{ctx.author}.wav")
    #             return
    #         await asyncio.sleep(.1)

    #     # Check if bot gets removed from the voice channel in the middle of playing music
    #     os.remove(f"cogs/temp/{ctx.author}.wav")
    #     if ctx.voice_client != None:
    #         await vc.disconnect()
    #         if file_given:
    #             await ctx.send(f"Finished playing **{ctx.message.attachments[0].filename}** 👌")
    #         else:
    #             await ctx.send("Finished playing your masterpiece 👌")
        # else:
        #     await ctx.send("I got removed from the voice channel")
        #     return

    # @commands.cooldown(1, 20, commands.BucketType.user)
    # @commands.command(description="Guess the correct number", usage="ov guess")
    # async def guess(self, ctx):
    #     if await blocked(ctx.author.id) == False:
    #         return
    #     await ctx.reply("Guess a number between 1-10! You have 3 chances")
    #     r = random.randint(1, 10)
    #     def check(msg):
    #       return msg.author == ctx.author and msg.channel == ctx.channel
    #     chances = 3
    #     while chances != 0:
    #         try:
    #           chances != 3 and await ctx.send(f"You have {chances} chances left!")
    #           chances -= 1
    #           msg = await self.bot.wait_for('message', check=check, timeout=30)
    #           if msg.content.isdigit() is False:
    #             await ctx.reply("It's not a number!")
    #             continue
    #           elif int(msg.content) < 1 or int(msg.content) > 10:
    #             await ctx.send("You can only give numbers between 1-10!")
    #             continue

    #           if int(msg.content) == r:
    #             rc = random.randint(2, 10)
    #             await ctx.reply(f"You are right! The correct number is {r}, you earned ⦾ {rc}!")
    #             await updateinc(ctx.author.id, "cash", rc)
    #             return
    #           if chances:
    #             await ctx.send("Higher!") if int(msg.content) < r else int(msg.content) > r and await ctx.send("Smaller!")

    #         except asyncio.TimeoutError:
    #           await ctx.send(f"You didn't respond, no prize 4 you")
    #           return
    #     await ctx.send(f"Too bad! The correct number is {r}, no prize 4 you")

    # @commands.cooldown(1, 40, commands.BucketType.user)
    # @commands.command(description=f"Guess the word!\nAvailable categories `{', '.join(lists.hangman_category)}`", usage="ov hangman [category]")
    # async def hangman(self, ctx, category = None):
    #     if await blocked(ctx.author.id) is False:
    #         return
    #     if category is None:
    #         category = random.choice(lists.hangman_category)
    #     else:
    #         try:
    #             category = [x for x in lists.hangman_category if x.lower().replace(" ", "") == category.lower().replace(" ", "") or category.lower().replace(" ", "") in x.lower().replace(" ", "")]
    #             category = category[0]
    #         except:
    #             await ctx.send(f"Cannot find this category. You can only type one of these `{', '.join(lists.hangman_category)}`")
    #             return
    #     word = random.choice(lists.hangman_category_dispatcher[category]).replace("-", " ")
    #     guess = re.sub("[a-zA-Z]", "\_ ", word)
    #     chances = 6
    #     dispatcher = {6: "_____\n|   |\n|\n|\n|\n|_______", 5: "_____\n|   |\n|   O\n|\n|\n|_______", 4: "_____\n|   |\n|   O\n|   |\n|\n|_______", 3: "_____\n|   |\n|   O\n|  /|\n|\n|_______", 2: "_____\n|   |\n|   O\n|  /|\\\n|\n|_______", 1: "_____\n|   |\n|   O\n|  /|\\\n|  /\n|_______", 0: "_____\n|   |\n|   O\n|  /|\\\n|  / \\\n|_______"}
    #     embed = discord.Embed(title="Hangman!", description=f"Guess the word!\n**Category** {category}\n**{guess.replace('  ', ' ⠀')}**", color=color.blurple()).set_footer(text="Send letters one by one")
    #     embed.add_field(name="Chances", value=f"```\n{dispatcher[chances]}\n```")
    #     m = await ctx.send(embed=embed)
    #     def check(msg):
    #         return msg.author == ctx.author and msg.channel == ctx.channel
    #     timeout = 30
    #     while chances:
    #         try:
    #             start = round(time.time())
    #             message = await self.bot.wait_for('message', check=check, timeout=timeout)
    #             msg = message.content
    #             if len(msg) > 1:
    #                 await ctx.send("Send letters one by one!")
    #                 timeout -= (round(time.time())-start)
    #                 timeout = 0 if timeout < 0 else timeout
    #                 continue
    #             elif not msg.isalpha():
    #                 await ctx.send("Only ABC letters are allowed")
    #                 timeout -= (round(time.time())-start)
    #                 timeout = 0 if timeout < 0 else timeout
    #                 continue

    #             if msg.lower() in list(guess.lower()):
    #                 await ctx.send("You already guessed this letter!")
    #                 continue
    #             if msg.lower() in list(word.lower()):
    #                 guess = guess.split(" ")
    #                 guess = guess[:-1] if guess[-1] == "" else guess
    #                 for i in [index.start() for index in re.finditer(msg.lower(), word.lower())]:
    #                     guess[i] = list(word)[i]
    #                 guess = " ".join(guess)
    #                 await ctx.send(f"The letter `{msg.lower()}` is right!", delete_after=5)
    #                 await message.delete()
    #                 embed.description = f"Guess the word!\n**Category** {category}\n**{guess.replace('  ', ' ⠀')}**"
    #                 await m.edit(embed=embed)
    #                 if "_" not in list(guess.lower()):
    #                     rc = random.randint(15, 35)
    #                     await ctx.send(f"You guessed the word **{word}**! You earned ⦾ {rc}")
    #                     await updateinc(ctx.author.id, "cash", rc)
    #                     return
    #                 continue
    #             chances -= 1
    #             await ctx.send(f"The letter `{msg.lower()}` is incorrect!", delete_after=5)
    #             await message.delete()
    #             embed.set_field_at(0, name="Chances", value=f"```\n{dispatcher[chances]}\n```")
    #             await m.edit(embed=embed)
    #         except asyncio.TimeoutError:
    #             await ctx.send(f"You didn't respond, no prize 4 you")
    #             return
    #     await ctx.send(f"Too bad! You ran out of chances\nThe correct word is **{word}**!")

    @slash_command(description="Find the definition of a word", usage="/define <word>")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def define(self, ctx, query: Option(str, "Word to define")):
        await __import__('slash').define(self, ctx, query)

    @slash_command(description="Search image on google!", usage="/image <query>")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def image(self, ctx, query: Option(str, "Stuff to search")):
        await __import__('slash').image(self, ctx, query)

    # @commands.command(description="Guess a bot's prefix", usage="ov guessprefix <bot> [amount of message to search]", aliases=["gp"])
    # async def guessprefix(self, ctx, target: discord.Member, limit: int = 100):
    #     if not target.bot:
    #         await ctx.send("This user is not a bot!")
    #         return
    #     await ctx.send("Analyzing messages, please wait...")
    #     start = time.time()

    #     bot_channel_messages = [(await channel.history(limit=limit).filter(lambda message: message.author == target).flatten()) for channel in ctx.guild.channels if isinstance(channel, discord.TextChannel) and channel.permissions_for(target).send_messages and channel.permissions_for(ctx.guild.me).read_message_history]
    #     channel_messages = [(await channel.history(limit=limit+1).flatten()) for channel in ctx.guild.channels if isinstance(channel, discord.TextChannel) and channel.permissions_for(target).send_messages and channel.permissions_for(ctx.guild.me).read_message_history]
    #     messages = [sum(channel_messages, [])[sum(channel_messages, []).index(bot_message)+1].content for bot_message in sum(bot_channel_messages, []) if not sum(channel_messages, [])[sum(channel_messages, []).index(bot_message)+1].author.bot]

    #     if len(messages) == 0:
    #         await ctx.send("Couldn't guess the prefix for this bot because it hasn't been used recently")
    #         return

    #     letters = sorted(set([j for i in messages for j in i]), key=[j for i in messages for j in i].index)

    #     matchcount = {}
    #     for letter in letters:
    #         matches = [1 if letter in message else 0 for message in messages]
    #         matchcount[letter] = sum(matches)

    #     async def get_prefix(number: int, last_prefix = None):

    #         closest_match = sorted(set(matchcount.values()), reverse=True)[number]

    #         letters_in_prefix = [letters for letters in matchcount if matchcount[letters] == closest_match]

    #         matched_messages = []
    #         for message in messages:
    #             match = all([True if letter in message else False for letter in letters_in_prefix])
    #             if match:
    #                 matched_messages.append(message)

    #         letter_index = {}
    #         for message in matched_messages:
    #             for letter in letters_in_prefix:
    #                 for index, char in enumerate(message):
    #                     if char == letter:
    #                         try:
    #                             letter_index[index]
    #                         except:
    #                             letter_index[index] = []
    #                         letter_index[index].append(char)

    #         prefix_letter_index = {}
    #         for index in letter_index:
    #             if [letter for letter in set(letter_index[index]) if letter_index[index].count(letter) == len(matched_messages)]:
    #                 prefix_letter_index[index] = max([letter for letter in set(letter_index[index]) if letter_index[index].count(letter) == len(matched_messages)])

    #         if not last_prefix:
    #             valid_prefix_letter_index = [i for i in sorted(prefix_letter_index) if i-1 == sorted(prefix_letter_index).index(i)-1]
    #             prefix = "".join([prefix_letter_index[index] for index in sorted(valid_prefix_letter_index)]).lstrip()
    #             if prefix == "" or sorted(prefix_letter_index)[0] != 0:
    #                 prefix = None
    #                 closest_match = None
    #         else:
    #             prefix = last_prefix + "".join([prefix_letter_index[index] for index in sorted(prefix_letter_index)])
    #             if prefix == last_prefix:
    #                 prefix = None

    #         return prefix, closest_match

    #     prefix = []
    #     closest_match = []
    #     p, c = await get_prefix(0)
    #     prefix.insert(0, p)
    #     closest_match.insert(0, c)
    #     try:
    #         p, c = await get_prefix(1, p)
    #         prefix.insert(1, p)
    #         closest_match.insert(1, c)
    #     except:
    #         pass

    #     prefix = [letter for letter in prefix if letter != None]
    #     closest_match = [i for i in closest_match if i != None]

    #     possible_prefixes = []
    #     for i in range(len(prefix)):
    #         possible_prefixes.append(f"**``{prefix[i]}``**\n**Possibility** {round(closest_match[i]/len(messages)*100, 2)}%")

    #     embed = discord.Embed(title=f"Guessed prefix for {target}", description=f"**Time taken** {round(time.time()-start, 2)} seconds", color=color.blurple())
    #     if not len(prefix):
    #         embed.add_field(name="Couldn't guess any prefix", value="The bot hasn't been used recently or it has multiple prefixes")
    #     else:
    #         embed.add_field(name="Possible prefixes", value="\n\n".join(possible_prefixes))
    #     if len(messages) <= 20:
    #         embed.description += ("\n\n**Results might be unaccurate, use the bot more for an accurate result**")

    #     await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(FunCog(bot))