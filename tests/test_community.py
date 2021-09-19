import pytest
from .fixtures import client, use_test_db_fixture, user_factory_for_test, user_token_factory_for_test, session_for_test

@pytest.mark.usefixtures('use_test_db_fixture')
class TestCommunity:

    def test_post_community(use_test_db_fixture, user_token_factory_for_test):
        """
        Communityを投稿する
        """
        name: str = "test_community"
        description: str = "this is test community"
        token = user_token_factory_for_test()

        res = client.post('/api/v1/communities', headers={
            "Authorization": f"Bearer { token.access_token }"
        }, json={
            "name": name,
            "description": description,
        })

        assert res.status_code == 200, 'Communityの作成に成功する'

        res_json = res.json()
        assert res_json['name'] == name
        assert res_json['description'] == description

