import pytest
from .fixtures import client, use_test_db_fixture, user_factory_for_test, user_token_factory_for_test, session_for_test, community_factory_for_test, user_for_test

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
    
    def test_get_community_list(use_test_db_fixture, community_factory_for_test):
        test_name: str = "maho"
        test_description: str = "kururinnpa"
        community = community_factory_for_test(name=test_name, description=test_description)
        res = client.get('/api/v1/communities')

        assert res.status_code == 200, 'Communityの一覧の取得に成功する'

        res_json = res.json()
        assert len(res_json) == 1
        assert res_json[0]['name'] == test_name
        assert res_json[0]['description'] == test_description

        test2_name: str = "kemomimi"
        test2_description: str = "mohumohu"
        community_factory_for_test(name=test2_name, description=test2_description)
        res = client.get('/api/v1/communities')
        
        assert res.status_code == 200, 'Communityの一覧の取得に成功する'

        res_json = res.json()
        assert len(res_json) == 2
        assert res_json[1]['name'] == test2_name
        assert res_json[1]['description'] == test2_description

    def test_get_community_oldestid(use_test_db_fixture, community_factory_for_test):
        test_name: str = "maho"
        test_description: str = "kururinnpa"
        community_factory_for_test(name=test_name, description=test_description)

        test2_name: str = "kemomimi"
        test2_description: str = "mohumohu"
        community_factory_for_test(name=test2_name, description=test2_description)
        res = client.get('/api/v1/communities?limit=1')

        assert res.status_code == 200, 'Communityの一覧の取得に成功する'
        res_json = res.json()
        assert len(res_json) == 1
        assert res_json[0]['name'] == test_name
        assert res_json[0]['description'] == test_description

        test_community_oldest_id = res_json[0]["id"]

        res = client.get(f'/api/v1/communities?limit=1&oldest_id={test_community_oldest_id}')
        
        assert res.status_code == 200, 'Communityの一覧の取得に成功する'

        res_json = res.json()
        assert len(res_json) == 1
        assert res_json[0]['name'] == test2_name
        assert res_json[0]['description'] == test2_description

        res = client.get('/api/v1/communities?limit=1&oldest_id=kitunemimiwosukore114')

        assert res.status_code == 400, 'Community_idの不一致'

        res_json = res.json()
        assert res_json['detail'] == "oldest_id is wrong"
    
    def test_get_community_id(use_test_db_fixture, community_factory_for_test):
        test_name: str = "maho"
        test_description: str = "kururinnpa"
        community1 = community_factory_for_test(name=test_name, description=test_description)
        test_community_id_1 = community1.id

        test2_name: str = "kemomimi"
        test2_description: str = "mohumohu"
        community2 = community_factory_for_test(name=test2_name, description=test2_description)
        test_community_id_2 = community2.id

        res = client.get(f'/api/v1/communities/{test_community_id_1}')

        assert res.status_code == 200, 'Communityの一覧の取得に成功する'

        res_json = res.json()
        assert res_json['name'] == test_name
        assert res_json['description'] == test_description

        res = client.get(f'/api/v1/communities/{test_community_id_2}')

        assert res.status_code == 200, 'Communityの一覧の取得に成功する'

        res_json = res.json()
        assert res_json['name'] == test2_name
        assert res_json['description'] == test2_description

        res = client.get('/api/v1/communities/hogehugaid0000')

        assert res.status_code == 404, 'Community_idの不一致'

        res_json = res.json()
        assert res_json['detail'] == "community isn't found"

    def test_put_community_by_id(use_test_db_fixture, community_factory_for_test, user_token_factory_for_test):
        token = user_token_factory_for_test()
        test_name: str = "maho"
        test_description: str = "kururinnpa"
        community1 = community_factory_for_test(name=test_name, description=test_description)
        test_community_id_1 = community1.id

        test2_name: str = "kemomimi"
        test2_description: str = "mohumohu"
        community2 = community_factory_for_test(name=test2_name, description=test2_description)
        test_community_id_2 = community2.id

        res = client.get('/api/v1/communities')

        assert res.status_code == 200, 'Communityの一覧の取得に成功する'

        res_json = res.json()
        assert res_json[0]['name'] == test_name
        assert res_json[0]['description'] == test_description
        assert res_json[1]['name'] == test2_name
        assert res_json[1]['description'] == test2_description

        change_name: str = "mahomaho"
        change_description: str = "mahomahooukoku"
        change2_name: str = "kitunemimi"
        change2_description: str = "sukore"    

        res = client.put(f'/api/v1/communities/{test_community_id_1}',headers={
            "Authorization": f"Bearer { token.access_token }"
        }, json={
            "name": change_name,
            "description": change_description,
        })

        res = client.put(f'/api/v1/communities/{test_community_id_2}',headers={
            "Authorization": f"Bearer { token.access_token }"
        }, json={
            "name": change2_name,
            "description": change2_description,
        })

        res = client.get('/api/v1/communities')

        assert res.status_code == 200, 'Communityの一覧の取得に成功する'

        res_json = res.json()
        assert res_json[0]['name'] == change_name
        assert res_json[0]['description'] == change_description
        assert res_json[1]['name'] == change2_name
        assert res_json[1]['description'] == change2_description

        res = client.put('/api/v1/communities/kemomimimohumohukawaii999',headers={
            "Authorization": f"Bearer { token.access_token }"
        }, json={
            "name": change2_name,
            "description": change2_description,
        })

        assert res.status_code == 404, 'Community_idの不一致'

        res_json = res.json()
        assert res_json['detail'] == "community_id is wrong"

    def test_delete_community(use_test_db_fixture, community_factory_for_test, user_token_factory_for_test):
        token = user_token_factory_for_test()
        test_name: str = "maho"
        test_description: str = "kururinnpa"
        community1 = community_factory_for_test(name=test_name, description=test_description)
        test_community_id_1 = community1.id

        test2_name: str = "kemomimi"
        test2_description: str = "mohumohu"
        community2 = community_factory_for_test(name=test2_name, description=test2_description)
        test_community_id_2 = community2.id

        res = client.delete(f'/api/v1/communities/{test_community_id_2}',headers={
            "Authorization": f"Bearer { token.access_token }"
        })

        assert res.status_code == 200, 'Communityの削除に成功する'
        
        res = client.get('/api/v1/communities')

        assert res.status_code == 200, 'Communityの一覧の取得に成功する'

        res_json = res.json()
        assert len(res_json) == 1
        assert res_json[0]['name'] == test_name
        assert res_json[0]['description'] == test_description
        res = client.delete(f'/api/v1/communities/mahohimekawaii999',headers={
            "Authorization": f"Bearer { token.access_token }"
        })

        assert res.status_code == 404, 'Community_idの不一致'

        res_json = res.json()
        assert res_json['detail'] == "community_id is wrong"



        








        

        
        

