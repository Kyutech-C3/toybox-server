from fastapi.param_functions import Form
from tests import TestingSessionLocal, client, fixture, override_get_db

@fixture(scope='session', autouse=True)
def before_session():
	db = TestingSessionLocal()
	print("Delete all users on test database")
	db.execute("DELETE FROM public.user")
	db.commit()

def test_sign_up():
	res = client.post('/api/v1/auth/sign_up', json={
		'name': 'iamtestuser',
		'email': 'test@test.com',
		'display_name': 'I am test user',
		'password': 'insecurepasswordfortest'
	})
	assert res.status_code == 200

def test_sign_in():
	res = client.post('/api/v1/auth/token', data={
		'username': 'test@test.com',
		'password': 'insecurepasswordfortest'
	})
	print(res.request.body)
	assert res.status_code == 200

def get_token():
	res = client.post('/api/v1/auth/token', data={
		'email': 'test@test.com',
		'password': 'insecurepasswordfortest'
	})
	if res.status_code == 200:
		return res.json()["access_token"]
	else:
		return None