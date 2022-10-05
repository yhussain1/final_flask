import json
import unittest

from main import app
# set our application to testing mode
app.testing = True

class TestApi(unittest.TestCase):

    def test_main(self):
        with app.test_client() as client:
            # send data as POST form to endpoint
            sent = {'return_url': 'my_test_url'}
            result = client.post(
                '/',
                data=sent
            )
            # check result from server with expected data
            self.assertEqual(
                result.data,
                json.dumps(sent)
            )

# class AppTestCase(unittest.TestCase):
#     def setUp(self):
#         self.ctx = app.app_context()
#         self.ctx.push()
#         self.client = app.test_client()
#
#     def tearDown(self):
#         self.ctx.pop()
#
#     def test_home(self):
#         response = self.client.post("/", data={"content": "hello world"})
#         assert response.status_code == 200
#         assert "POST method called" == response.get_data(as_text=True)
#
# if __name__ == '__main__':
#     unittest.main()
