import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# 添加 backend 目录到 path 以便导入
sys.path.append(os.path.join(os.path.dirname(__file__), '../backend'))

# 从 config 读取数据库 URL，如果失败则尝试从环境变量读取
try:
    from config import settings
    DATABASE_URL = settings.DATABASE_URL
except ImportError:
    # 尝试直接构造，这里为了简单直接硬编码或读取环境变量
    # 注意：生产环境 .env.production 应该已经被 source 了，或者由 CI/CD 注入
    # 这里我们做一个兜底：尝试读取 docker-compose 里的默认值
    MYSQL_USER = os.getenv("MYSQL_USER", "points_user")
    MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "YunXiangPoints2025DB")
    MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
    MYSQL_PORT = os.getenv("MYSQL_PORT", "3306")
    MYSQL_DB = os.getenv("MYSQL_DATABASE", "points_platform")
    DATABASE_URL = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}"

print(f"Connecting to database...")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def upgrade_db():
    try:
        with engine.connect() as conn:
            # 1. 检查 users 表是否存在 wx_openid 列
            result = conn.execute(text("SHOW COLUMNS FROM users LIKE 'wx_openid'"))
            if not result.fetchone():
                print("Adding wx_openid column...")
                conn.execute(text("ALTER TABLE users ADD COLUMN wx_openid VARCHAR(64) UNIQUE"))
                conn.execute(text("CREATE INDEX ix_users_wx_openid ON users (wx_openid)"))
            else:
                print("wx_openid column already exists.")

            # 2. 检查 wx_unionid
            result = conn.execute(text("SHOW COLUMNS FROM users LIKE 'wx_unionid'"))
            if not result.fetchone():
                print("Adding wx_unionid column...")
                conn.execute(text("ALTER TABLE users ADD COLUMN wx_unionid VARCHAR(64) UNIQUE"))
                conn.execute(text("CREATE INDEX ix_users_wx_unionid ON users (wx_unionid)"))
            else:
                print("wx_unionid column already exists.")

            # 3. 检查 nickname
            result = conn.execute(text("SHOW COLUMNS FROM users LIKE 'nickname'"))
            if not result.fetchone():
                print("Adding nickname column...")
                conn.execute(text("ALTER TABLE users ADD COLUMN nickname VARCHAR(64)"))

            # 4. 检查 avatar_url
            result = conn.execute(text("SHOW COLUMNS FROM users LIKE 'avatar_url'"))
            if not result.fetchone():
                print("Adding avatar_url column...")
                conn.execute(text("ALTER TABLE users ADD COLUMN avatar_url VARCHAR(500)"))
            
            # 5. 修改 phone 为 nullable
            # 注意：MySQL 修改列定义比较复杂，这里假设如果 phone 是 NOT NULL 的话我们需要改成 NULL
            # 简单起见，我们直接尝试修改，如果已经修改过也不会报错（除非有约束冲突，但这里是放宽约束）
            print("Modifying phone column to allow NULL...")
            conn.execute(text("ALTER TABLE users MODIFY COLUMN phone VARCHAR(20) NULL"))

            conn.commit()
            print("Database upgrade completed successfully.")
            
    except Exception as e:
        print(f"Error upgrading database: {e}")
        # 不抛出异常，以免阻断部署（虽然理论上应该阻断，但为了健壮性我们先打印）
        sys.exit(1)

if __name__ == "__main__":
    upgrade_db()
