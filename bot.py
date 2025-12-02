from pyrogram import Client
from pyrogram.enums import ParseMode
import pyromod
from config import API_HASH, API_ID, BOT_TOKEN, CHANNEL_ID, MOVIE_CHANNEL_ID, LOGGER

class Bot(Client):
    def __init__(self):
        super().__init__(
            name="FileShareBot",
            api_id=API_ID,
            api_hash=API_HASH,
            bot_token=BOT_TOKEN,
            workers=50,
            plugins={"root": "plugins"},
            sleep_threshold=5,
            parse_mode=ParseMode.HTML
        )
        self.LOGGER = LOGGER

    async def start(self):
        await super().start()
        usr_bot_me = await self.get_me()
        self.username = usr_bot_me.username
        
        # Get database channels info
        try:
            self.db_channel = await self.get_chat(CHANNEL_ID)
            LOGGER(__name__).info(f"SHORT Database Channel: {self.db_channel.title}")
        except Exception as e:
            LOGGER(__name__).error(f"Error connecting to SHORT DB channel: {e}")
            LOGGER(__name__).error("Make sure bot is admin in the channel!")
            exit(1)
        
        try:
            self.movie_channel = await self.get_chat(MOVIE_CHANNEL_ID)
            LOGGER(__name__).info(f"MOVIE Database Channel: {self.movie_channel.title}")
        except Exception as e:
            LOGGER(__name__).error(f"Error connecting to MOVIE DB channel: {e}")
            LOGGER(__name__).error("Make sure bot is admin in the movie channel!")
            exit(1)
        
        LOGGER(__name__).info(f"Bot Started as @{self.username}!")
        LOGGER(__name__).info("=" * 50)
        LOGGER(__name__).info("Bot Configuration:")
        LOGGER(__name__).info(f"• SHORT Channel: {self.db_channel.title} ({CHANNEL_ID})")
        LOGGER(__name__).info(f"• MOVIE Channel: {self.movie_channel.title} ({MOVIE_CHANNEL_ID})")
        LOGGER(__name__).info("=" * 50)

    async def stop(self, *args):
        await super().stop()
        LOGGER(__name__).info("Bot Stopped!")

app = Bot()
app.run()