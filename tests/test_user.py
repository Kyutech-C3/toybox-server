from datetime import timedelta
import pytest
from .fixtures import client, use_test_db_fixture, session_for_test, user_for_test, user_token_factory_for_test

@pytest.mark.usefixtures('use_test_db_fixture')
class TestUser:

	def test_get_me(use_test_db_fixture, user_for_test, user_token_factory_for_test):
		"""
		自分の情報を取得
		"""
		token = user_token_factory_for_test()
		print('Token', token)
		res = client.get('/api/v1/users/@me', headers={
			"Authorization": f"Bearer { token.access_token }"
		})
		assert res.status_code == 200
		assert res.json()['email'] == 'test@test.com'

	def test_get_me_unauthorized(user_for_test, user_token_factory_for_test):
		"""
		アクセストークンなしで自分の情報の取得に失敗する
		"""
		user_token_factory_for_test()
		res = client.get('/api/v1/users/@me', headers={
			# Without Authorization header...
		})
		assert res.status_code == 403, 'アクセストークンなしで自分の情報の取得に失敗する'

	def test_get_me_with_expired_access_token(use_test_db_fixture, user_for_test, user_token_factory_for_test):
		"""
		期限切れのアクセストークンを用いて自分の情報の取得をしようとし、失敗する
		"""
		# Create access_token which is expired before 10s
		token = user_token_factory_for_test(access_token_expires_delta=timedelta(seconds=-10))

		res = client.get('/api/v1/users/@me', headers={
			"Authorization": f"Bearer { token.access_token }"
		})
		assert res.status_code == 401, '有効期限切れのアクセストークンを使った自分の情報の取得に失敗する'
	
