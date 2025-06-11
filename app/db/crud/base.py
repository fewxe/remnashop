from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker


class CrudService:
    session_pool: async_sessionmaker[AsyncSession]

    def __init__(
        self,
        session_pool: async_sessionmaker[AsyncSession],
    ) -> None:
        super().__init__()
        self.session_pool = session_pool
