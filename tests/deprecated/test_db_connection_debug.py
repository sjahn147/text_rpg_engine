"""
?°ì´?°ë² ?´ìŠ¤ ?°ê²° ?”ë²„ê¹??¤í¬ë¦½íŠ¸
.env ?Œì¼ê³??¤ì •???•ì¸?˜ê³  ?°ê²°???ŒìŠ¤?¸í•©?ˆë‹¤.
"""

import asyncio
import os
from dotenv import load_dotenv
from app.config.app_config import get_db_settings
from database.connection import DatabaseConnection

async def debug_database_connection():
    """?°ì´?°ë² ?´ìŠ¤ ?°ê²° ?”ë²„ê¹?""
    print("=== ?°ì´?°ë² ?´ìŠ¤ ?°ê²° ?”ë²„ê¹?===")
    
    # 1. .env ?Œì¼ ?•ì¸
    print("\n1. .env ?Œì¼ ?•ì¸:")
    if os.path.exists('.env'):
        print("??.env ?Œì¼ ì¡´ì¬")
        with open('.env', 'r', encoding='utf-8') as f:
            content = f.read()
            print(f"?´ìš©:\n{content}")
    else:
        print("??.env ?Œì¼ ?†ìŒ")
        return
    
    # 2. ?˜ê²½ ë³€??ë¡œë“œ ?•ì¸
    print("\n2. ?˜ê²½ ë³€??ë¡œë“œ ?•ì¸:")
    load_dotenv()
    print(f"DB_HOST: {os.getenv('DB_HOST', 'NOT_SET')}")
    print(f"DB_PORT: {os.getenv('DB_PORT', 'NOT_SET')}")
    print(f"DB_USER: {os.getenv('DB_USER', 'NOT_SET')}")
    print(f"DB_PASSWORD: {os.getenv('DB_PASSWORD', 'NOT_SET')}")
    print(f"DB_NAME: {os.getenv('DB_NAME', 'NOT_SET')}")
    
    # 2.5. .env ?Œì¼ ì§ì ‘ ?½ê¸°
    print("\n2.5. .env ?Œì¼ ì§ì ‘ ?½ê¸°:")
    with open('.env', 'r', encoding='utf-8') as f:
        lines = f.readlines()
        for line in lines:
            if line.strip() and not line.startswith('#'):
                key, value = line.strip().split('=', 1)
                print(f"{key}: {value}")
    
    # 3. ?¤ì • ê°ì²´ ?•ì¸
    print("\n3. ?¤ì • ê°ì²´ ?•ì¸:")
    db_settings = get_db_settings()
    print(f"db_settings.host: {db_settings.host}")
    print(f"db_settings.port: {db_settings.port}")
    print(f"db_settings.user: {db_settings.user}")
    print(f"db_settings.password: '{db_settings.password}'")
    print(f"db_settings.database: {db_settings.database}")
    
    # 3.5. ?ˆë¡œ???¤ì • ê°ì²´ ?ì„± ?ŒìŠ¤??
    print("\n3.5. ?ˆë¡œ???¤ì • ê°ì²´ ?ì„± ?ŒìŠ¤??")
    from app.config.app_config import DatabaseSettings
    new_settings = DatabaseSettings()
    print(f"new_settings.password: '{new_settings.password}'")
    
    # 4. ?°ì´?°ë² ?´ìŠ¤ ?°ê²° ?ŒìŠ¤??
    print("\n4. ?°ì´?°ë² ?´ìŠ¤ ?°ê²° ?ŒìŠ¤??")
    try:
        db = DatabaseConnection()
        print(f"?°ê²° ?¤ì •: {db.host}:{db.port}/{db.database} (user: {db.user})")
        
        # ?°ê²° ?€ ?ì„± ?œë„
        pool = await db.pool
        print("???°ì´?°ë² ?´ìŠ¤ ?°ê²° ?€ ?ì„± ?±ê³µ")
        
        # ?°ê²° ?ŒìŠ¤??
        test_result = await db.test_connection()
        if test_result:
            print("???°ì´?°ë² ?´ìŠ¤ ?°ê²° ?ŒìŠ¤???±ê³µ")
        else:
            print("???°ì´?°ë² ?´ìŠ¤ ?°ê²° ?ŒìŠ¤???¤íŒ¨")
        
        # ?°ê²° ì¢…ë£Œ
        await db.close()
        print("???°ì´?°ë² ?´ìŠ¤ ?°ê²° ì¢…ë£Œ")
        
    except Exception as e:
        print(f"???°ì´?°ë² ?´ìŠ¤ ?°ê²° ?¤íŒ¨: {str(e)}")
        print(f"?¤ë¥˜ ?€?? {type(e).__name__}")

if __name__ == "__main__":
    asyncio.run(debug_database_connection())
