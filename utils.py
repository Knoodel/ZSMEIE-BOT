import motor.motor_asyncio
from dotenv import load_dotenv
import os


load_dotenv()
PASSWORD = os.getenv("PASSWORD")


def get_db_col():
    Cluster = motor.motor_asyncio.AsyncIOMotorClient(f'mongodb+srv://ItsMeNoodle:{PASSWORD}@cluster0.vkzgf.mongodb.net/myFirstDatabase?retryWrites=true&w=majority')
    db = Cluster['ZSMEIEbot']
    collection = db['ZSMEIEbot']
    return collection
