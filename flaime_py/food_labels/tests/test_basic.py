# flaime_py/food_labels/tests/test_basic.py
import logging
from django.test import TestCase

logger = logging.getLogger(__name__)


class BasicTest(TestCase):
    def setUp(self):
        logger.info("Setting up test")
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT count(*) FROM pg_stat_activity 
                WHERE datname = current_database()
            """)
            count = cursor.fetchone()[0]
            logger.info(f"Active connections during setup: {count}")

    def tearDown(self):
        logger.info("Tearing down test")
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT count(*) FROM pg_stat_activity 
                WHERE datname = current_database()
            """)
            count = cursor.fetchone()[0]
            logger.info(f"Active connections during teardown: {count}")

    def test_basic(self):
        logger.info("Running basic test")
        self.assertTrue(True)