from schemas.user import Token as TokenSchema, User as UserSchema
import pytest
from db.models import User
from fastapi.param_functions import Form
from .fixtures import client, use_test_db_fixture, session_for_test, user_for_test, user_token_factory_for_test
from cruds.users.auth import create_refresh_token, get_user
from datetime import timedelta

@pytest.mark.usefixtures('use_test_db_fixture')
class TestAuth:

	def test_exchange_access_token_with_refresh_token(user_for_test, user_token_factory_for_test):
		"""
		リフレッシュトークンを使ってアクセストークンを更新
		"""
		res = client.post('/api/v1/auth/token', json={
			'refresh_token': user_token_factory_for_test().refresh_token,
		})

		assert res.status_code == 200, 'アクセストークンの更新が成功する'
		body_dict = res.json()

		assert body_dict['access_token'] != None, 'アクセストークンがちゃんと返っている'

		access_token = body_dict['access_token']
		refresh_token = body_dict['refresh_token']
		expired_at = body_dict['expired_at']
		
		res = client.get('/api/v1/users/@me', headers={
			'Authorization': f'Bearer {access_token}'
		})
		assert res.status_code == 200, '更新したアクセストークンでリクエストが成功する'

		res = client.post('/api/v1/auth/token', json={
			'refresh_token': refresh_token,
			'expired_at': expired_at
		})
		assert res.status_code == 200, '更新されたリフレッシュトークンでアクセストークンの更新が可能'

	def test_exchange_access_token_with_expired_access_token(use_test_db_fixture, user_for_test, user_token_factory_for_test):
		"""
		有効期限切れのリフレッシュトークンを用いるとアクセストークンの更新ができない
		"""
		# Create access_token which is expired before 10s
		token = user_token_factory_for_test(access_token_expires_delta=timedelta(seconds=-10))

		res = client.get('/api/v1/users/@me', headers={
			"Authorization": f"Bearer { token.access_token }"
		})
		assert res.status_code == 401, '有効期限切れのアクセストークンを使った自分の情報の取得に失敗する'