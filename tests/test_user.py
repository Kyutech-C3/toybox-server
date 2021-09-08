from datetime import timedelta
from fastapi.param_functions import Form
from tests import TestingSessionLocal, client, fixture, override_get_db
from cruds.users.auth import create_access_token

def login():
	res = client.post('/api/v1/auth/token', data={
		'username': 'test@test.com',
		'password': 'insecurepasswordfortest'
	})
	print(res.request.body)
	assert res.status_code == 200
	return res.json()['access_token']

@fixture(scope='session', autouse=True)
def before_session():
	db = TestingSessionLocal()
	print("Delete all users on test database")
	db.execute("DELETE FROM public.user")
	db.commit()

	# Create test user
	res = client.post('/api/v1/auth/sign_up', json={
		'name': 'iamtestuser',
		'email': 'test@test.com',
		'display_name': 'I am test user',
		'password': 'insecurepasswordfortest'
	})
	assert res.status_code == 200

def test_get_me():
	access_token = login()
	res = client.get('/api/v1/users/@me', headers={
		"Authorization": f"Bearer { access_token }"
	})
	assert res.status_code == 200

def test_get_me_unauthorized():
	res = client.get('/api/v1/users/@me', headers={
		# Without Authorization header...
	})
	assert res.status_code == 401

def test_get_me_with_expired_access_token():
	# Create access_token which is expired before 10s
	access_token = create_access_token(
		data={"sub": "test@test.com", "token_type": "bearer"},
		expires_delta=timedelta(seconds=-10)
	)

	access_token = login()
	res = client.get('/api/v1/users/@me', headers={
		"Authorization": f"Bearer { access_token }"
	})
	assert res.status_code == 200
