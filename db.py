from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL= "mysql+pymysql://2Z8qsWdQucFViDE.root:CKM2LuGHnQEo7a6q@gateway01.ap-southeast-1.prod.aws.tidbcloud.com:4000/test?ssl_ca=<CA_PATH>&ssl_verify_cert=true&ssl_verify_identity=true"

engine= create_engine(
    DATABASE_URL,
    pool_pre_ping=True, #check database connection
    connect_args={
        "ssl":{ #secure connection
            "ssl":True
        }
    }
)

SessionLocal= sessionmaker(bind=engine) #factory that gives new ddatabase session , crud
Base= declarative_base()