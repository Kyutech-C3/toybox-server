import pytest
from .fixtures import client, use_test_db_fixture, community_factory_for_test, session_for_test, user_token_factory_for_test, user_factory_for_test, tag_for_test, user_for_test

@pytest.mark.usefixtures('use_test_db_fixture')
class TestTag:

    def test_post_tag(use_test_db_fixture, community_factory_for_test, user_token_factory_for_test):
        """
        タグを作成する
        """
        community = community_factory_for_test()
        name: str = "hoge"
        community_id: str = community.id
        color: str = "#FFFFFFFF"
        token = user_token_factory_for_test()

        res = client.post('/api/v1/tags', headers={
            "Authorization": f"Bearer { token.access_token }"
        }, json={
            "name": name,
            "community_id": community_id,
            "color": color
        })

        assert res.status_code == 200, 'tagの作成に成功する'

        res_json = res.json()
        print(res_json)
        assert res_json['name'] == name
        assert res_json['community']['id'] == community_id
        assert res_json['color'] == color

    def test_post_tag(use_test_db_fixture, community_factory_for_test, user_token_factory_for_test):
        """
        カラーコードを間違えたタグを作成する
        """
        community = community_factory_for_test()
        name: str = "hoge"
        community_id: str = community.id
        color: str = "あいうえお"
        token = user_token_factory_for_test()

        res = client.post('/api/v1/tags', headers={
            "Authorization": f"Bearer { token.access_token }"
        }, json={
            "name": name,
            "community_id": community_id,
            "color": color
        })

        assert res.status_code == 422, 'tagの作成に失敗する'

    def test_get_tags(use_test_db_fixture, tag_for_test, user_token_factory_for_test):
        """
        タグ一覧を取得する
        """
        tag_id: str = tag_for_test.id
        name: str = tag_for_test.name
        community_id: str = tag_for_test.community.id
        color: str = tag_for_test.color
        token = user_token_factory_for_test()

        res = client.get('/api/v1/tags', headers={
            "Authorization": f"Bearer { token.access_token }"
        })

        assert res.status_code == 200, 'タグ一覧の取得に成功する'

        res_json = res.json()

        assert res_json[0]['id'] == tag_id
        assert res_json[0]['name'] == name
        assert res_json[0]['community']['id'] == community_id
        assert res_json[0]['color'] == color

    def test_get_tags_by_community_id(use_test_db_fixture, tag_for_test, user_token_factory_for_test):
        """
        コミュニティーに存在するタグ一覧を取得する
        """
        tag_id: str = tag_for_test.id
        name: str = tag_for_test.name
        community_id: str = tag_for_test.community.id
        color: str = tag_for_test.color
        token = user_token_factory_for_test()

        res = client.get(f'/api/v1/tags?community_id={community_id}', headers={
            "Authorization": f"Bearer { token.access_token }"
        })

        assert res.status_code == 200, 'コミュニティーに存在するタグ一覧の取得に成功する'

        res_json = res.json()

        print(res_json)
        assert res_json[0]['id'] == tag_id
        assert res_json[0]['name'] == name
        assert res_json[0]['community']['id'] == community_id
        assert res_json[0]['color'] == color

    def test_get_tag_by_tag_id(use_test_db_fixture, tag_for_test, user_token_factory_for_test):
        """
        タグid指定でタグ情報を取得する
        """
        tag_id: str = tag_for_test.id
        name: str = tag_for_test.name
        community_id: str = tag_for_test.community.id
        color: str = tag_for_test.color
        token = user_token_factory_for_test()

        res = client.get(f'/api/v1/tags/{tag_id}', headers={
            "Authorization": f"Bearer { token.access_token }"
        })

        assert res.status_code == 200, 'タグid指定でタグ情報の取得に成功する'

        res_json = res.json()

        print(res_json)
        assert res_json['id'] == tag_id
        assert res_json['name'] == name
        assert res_json['community']['id'] == community_id
        assert res_json['color'] == color


    def test_put_tag(use_test_db_fixture, tag_for_test, user_token_factory_for_test):
        """
        タグを編集する
        """
        tag_id: str = tag_for_test.id
        name: str = "hogehoge"
        community_id: str = tag_for_test.community.id
        color: str = "#00000000"
        token = user_token_factory_for_test()

        res = client.put(f'/api/v1/tags/{tag_id}', headers={
            "Authorization": f"Bearer { token.access_token }"
        }, json={
            "name": name,
            "community_id": community_id,
            "color": color
        })

        assert res.status_code == 200, 'タグの編集に成功する'

        res_json = res.json()
        print(res_json)
        assert res_json['id'] == tag_id
        assert res_json['name'] == name
        assert res_json['community']['id'] == community_id
        assert res_json['color'] == color

    def test_put_tag(use_test_db_fixture, tag_for_test, user_token_factory_for_test):
        """
        タグを削除する
        """
        tag_id: str = tag_for_test.id
        name: str = "hogehoge"
        community_id: str = tag_for_test.community.id
        color: str = "#00000000"
        token = user_token_factory_for_test()

        res = client.delete(f'/api/v1/tags/{tag_id}', headers={
            "Authorization": f"Bearer { token.access_token }"
        })

        assert res.status_code == 200, 'タグの削除に成功する'

        res_json = res.json()
        print(res_json)
        assert res_json == {'status': 'OK'}
