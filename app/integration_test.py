import sys
import os
import asyncio
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("IntegrationTest")

# Mock environment
os.environ["BOT_TOKEN"] = "123456789:ABCDEF-GHIJKL-MNOPQRSTUV"
os.environ["ADMIN_ID"] = "12345678"

async def test_business_logic():
    logger.info("Testing business logic...")
    try:
        from users_db import user_db
        from smart_search import smart_search
        
        # 1. Test User DB
        user_id = 99999
        user = user_db.get_user(user_id)
        logger.info(f"✅ User DB: User retrieved/created: {user['user_id']}")
        
        # 2. Test Smart Search
        mock_creators = [{'name': 'Belle Delphine', 'id': 'belle', 'service': 'coomer'}]
        matches = smart_search.find_similar("beledelphine", mock_creators)
        if matches and matches[0]['id'] == 'belle':
            logger.info("✅ Smart Search: Fuzzy matching working.")
        else:
            logger.error("❌ Smart Search: Fuzzy matching failed.")
            return False
            
        # 3. Test Preview Limits
        user_db.update_user(user_id, daily_previews_used=2, last_preview_date=datetime.now().date().isoformat())
        can_use = user_db.check_preview_limit(user_id)
        logger.info(f"✅ Preview Limit: Can use 3rd preview? {can_use}")
        
        user_db.increment_previews(user_id)
        can_use_more = user_db.check_preview_limit(user_id)
        logger.info(f"✅ Preview Limit: Can use 4th preview? {can_use_more}")
        
        if can_use and not can_use_more:
            logger.info("✅ Preview Limit: Logic verified.")
        else:
            logger.error("❌ Preview Limit: Logic failed.")
            return False
            
        return True
    except Exception as e:
        logger.error(f"❌ Business logic test failed: {e}", exc_info=True)
        return False

if __name__ == "__main__":
    success = asyncio.run(test_business_logic())
    if success:
        logger.info("🚀 INTEGRATION TEST PASSED!")
        sys.exit(0)
    else:
        logger.error("💥 INTEGRATION TEST FAILED!")
        sys.exit(1)
