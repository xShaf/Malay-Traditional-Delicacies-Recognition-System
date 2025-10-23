import os
import unittest
import tempfile
from main import app
import database as db

class FlaskTestCase(unittest.TestCase):

    def setUp(self):
        self.db_fd, self.db_path = tempfile.mkstemp()
        app.config['TESTING'] = True
        self.app = app.test_client()
        db.init_db(self.db_path)

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(self.db_path)

    def test_index(self):
        rv = self.app.get('/')
        self.assertEqual(rv.status_code, 200)

    def test_add_kuih_page(self):
        rv = self.app.get('/add')
        self.assertEqual(rv.status_code, 200)

    def test_add_kuih(self):
        db.add_kuih('Test Kuih', 'test.jpg', 'Test History', db_name=self.db_path)
        conn = db.get_db(self.db_path)
        c = conn.cursor()
        c.execute("SELECT * FROM kuih WHERE name='Test Kuih'")
        kuih = c.fetchone()
        conn.close()
        self.assertIsNotNone(kuih)
        self.assertEqual(kuih[1], 'Test Kuih')

if __name__ == '__main__':
    unittest.main()
