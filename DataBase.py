from sqlmodel import SQLModel, Field, select, func
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import desc
from datetime import datetime
from validationLayer import Status
from math import ceil
import asyncio
import pytz

DATABASE_URL = "sqlite+aiosqlite:///LoggerData.db"
async_engine = create_async_engine(DATABASE_URL, echo=False)
async_session_maker = sessionmaker(async_engine, class_=AsyncSession, expire_on_commit=False)
ist = pytz.timezone('Asia/Kolkata')
now_utc = datetime.now(pytz.utc)
now_ist = now_utc.astimezone(ist)

class LoggerInfo(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    ERROR_TYPE: Status
    DESCRIPTION: str
    TIMESTAMP : datetime

async def StartEngine():
    async with async_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


async def InsertLogError(error_type: str,description: str,time = now_ist):
    async with async_session_maker() as session:
        try :
            user = LoggerInfo(ERROR_TYPE=error_type,DESCRIPTION=description,TIMESTAMP=time)
            session.add(user)
            await session.commit()
            return True
        except Exception as error:
            print("Error", error)
            await session.rollback()
            return False
        
async def Delete_log(record_id: int):
    async with async_session_maker() as session:
        try:
            statement = select(LoggerInfo).where(LoggerInfo.id == record_id)
            result = await session.execute(statement)
            record = result.scalars().first()
            await session.delete(record)
            await session.commit()
            return True
        except Exception as error:
            print("Error", error)
            await session.rollback()
            return False


async def get_logs(page: int = 1, per_page: int = 10):
    async with async_session_maker() as session:
        try:
            offset = (page - 1) * per_page
            total_count = (await session.execute(select(func.count(LoggerInfo.id)))).scalar()
            total_pages = ceil(total_count / per_page)
            result = await session.execute(
                select(LoggerInfo)
                .order_by(LoggerInfo.id)  
                .limit(per_page)
                .offset(offset)
            )
            records = result.scalars().all()
            
            return {
                "records": records,
                "pagination": {
                    "total_records": total_count,
                    "total_pages": total_pages,
                    "current_page": page,
                    "per_page": per_page,
                    "has_prev": page > 1,
                    "has_next": page < total_pages
                }
            }
        except Exception as error:
            print("Error:", error)
            return None


"""async def main():
    x = await(get_logs())
    print(x['records'])

asyncio.run(main())"""
            



