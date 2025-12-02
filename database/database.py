import motor.motor_asyncio
from config import DATABASE_URL, DATABASE_NAME, LOGGER

class Database:
    def __init__(self, uri, database_name):
        self._client = motor.motor_asyncio.AsyncIOMotorClient(uri)
        self.db = self._client[database_name]
        self.users = self.db.users
        self.files = self.db.files
        self.settings = self.db.settings

    async def add_user(self, user_id, first_name=None, username=None):
        user = await self.users.find_one({"_id": user_id})
        if not user:
            await self.users.insert_one({
                "_id": user_id,
                "first_name": first_name,
                "username": username
            })

    async def is_user_exist(self, user_id):
        user = await self.users.find_one({'_id': user_id})
        return bool(user)

    async def total_users_count(self):
        return await self.users.count_documents({})

    async def get_all_users(self):
        return self.users.find({})

    async def delete_user(self, user_id):
        await self.users.delete_one({'_id': user_id})

    async def add_file(self, file_id, file_ref, category="short"):
        await self.files.insert_one({
            "_id": file_id,
            "file_ref": file_ref,
            "category": category
        })

    async def get_file(self, file_id):
        file = await self.files.find_one({"_id": file_id})
        return file

    async def is_file_exist(self, file_id):
        file = await self.files.find_one({'_id': file_id})
        return bool(file)

    async def delete_file(self, file_id):
        await self.files.delete_one({'_id': file_id})

    async def total_files_count(self):
        return await self.files.count_documents({})

    async def get_setting(self, key):
        setting = await self.settings.find_one({"_id": key})
        return setting.get("value") if setting else None

    async def set_setting(self, key, value):
        await self.settings.update_one(
            {"_id": key},
            {"$set": {"value": value}},
            upsert=True
        )

    async def get_all_settings(self):
        settings_cursor = self.settings.find({})
        settings = {}
        async for setting in settings_cursor:
            settings[setting["_id"]] = setting.get("value")
        return settings

    async def get_force_sub_channels(self):
        channels = await self.get_setting("force_sub_channels")
        return channels if channels else []

    async def add_force_sub_channel(self, channel_id):
        channels = await self.get_force_sub_channels()
        if channel_id not in channels:
            channels.append(channel_id)
            await self.set_setting("force_sub_channels", channels)
            return True
        return False

    async def remove_force_sub_channel(self, channel_id):
        channels = await self.get_force_sub_channels()
        if channel_id in channels:
            channels.remove(channel_id)
            await self.set_setting("force_sub_channels", channels)
            return True
        return False

try:
    db = Database(DATABASE_URL, DATABASE_NAME)
    LOGGER(__name__).info("Database Connected Successfully!")
except Exception as e:
    LOGGER(__name__).error(f"Database Connection Error: {e}")
    exit(1)
