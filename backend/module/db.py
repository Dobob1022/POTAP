from sqlalchemy import create_engine, String
from sqlalchemy.orm import sessionmaker, declarative_base, Mapped, mapped_column

DATABASE_URL = "sqlite:///./dev.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

#declare VmInfo model
class VmInfo(Base):
    __tablename__ = "vm_info"

    # Mapped와 mapped_column을 사용하기 위해 위에서 import 했습니다.
    id: Mapped[int] = mapped_column(primary_key=True)
    mac_address: Mapped[str] = mapped_column(String(17), unique=True, nullable=False)
    hostname: Mapped[str] = mapped_column(String(50), nullable=False)
    template: Mapped[str] = mapped_column(String(50), default="ubuntu_2404")
    status: Mapped[str] = mapped_column(String(20), default="started")

    def __repr__(self):
        return f"<VmInfo({self.mac_address} -> {self.hostname})>"

def init_db():
    """데이터베이스 테이블 생성"""
    Base.metadata.create_all(bind=engine)

def get_db():
    """FastAPI Dependency용 세션 제너레이터"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()



#db init
init_db()


#add new vm 
def add_vm(db_session, mac_address: str, hostname: str, template: str ,  status: str = "started"):
    """Add new VM into database"""
    new_vm = VmInfo(
        mac_address=mac_address,
        hostname=hostname,
        template=template,
        status=status
    )
    db_session.add(new_vm)
    db_session.commit()
    db_session.refresh(new_vm)
    return new_vm