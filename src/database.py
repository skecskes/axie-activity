from sqlalchemy import create_engine, Column, String, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session

Base = declarative_base(metadata=MetaData(schema='ronin'))


class Transfers(Base):
    __tablename__ = "transfers"

    id = Column(String, primary_key=True, index=True)
    token_type = Column(String)
    block_number = Column(String)
    contract = Column(String)
    from_address = Column(String, name="from")
    to_address = Column(String, name="to")
    value = Column(String)
    token_id = Column(String)
    transaction_hash = Column(String)
    transaction_index = Column(String)
    log_index = Column(String)


class DbClient:
    engine = create_engine(
            f"postgresql+psycopg2://postgres:postgres@localhost:5432/devdb",
            echo=False,
            isolation_level='READ COMMITTED',
            pool_size=20,
            max_overflow=0
        )

    def __init__(self):
        self.engine.execute("SET TIME ZONE 0") # UTC
        self.session = Session(self.engine)

    def get_transfers(self, ronin_address: str) -> [Transfers]:
        if not self._valid_address(ronin_address):
            raise Exception("Sorry, invalid ronin address")
        address = self._prepare_ronin_address(ronin_address)

        transfers = self.session\
            .query(Transfers)\
            .filter((Transfers.from_address == address) | (Transfers.to_address == address))\
            .order_by(Transfers.block_number.desc())\
            .all()

        return transfers

    @staticmethod
    def _valid_address(address: str) -> bool:
        length = len(address)
        return address.startswith("ronin:") and 46 == length

    @staticmethod
    def _prepare_ronin_address(address: str) -> str:
        (prefix, the_rest) = address.split("ronin:")
        return "0x" + the_rest
