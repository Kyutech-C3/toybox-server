from schemas.community import Community
import pytest
from .fixtures import client, community_factory_for_test, user_factory_for_test, use_test_db_fixture, session_for_test, user_token_factory_for_test, work_for_test_public, work_for_test_private

@pytest.mark.usefixtures('use_test_db_fixture')
class TestWork:

    def test_post_work(use_test_db_fixture, community_factory_for_test, user_token_factory_for_test):
        """
        Workを投稿する
        """
        title: str = "test_work"
        description: str = "this is test work"
        github_url: str = "https://github.com"
        work_url: str = "https://rsa-qk.pigeons.house/"
        private: bool = False
        token = user_token_factory_for_test()
        community = community_factory_for_test()

        res = client.post('/api/v1/works', headers={
            "Authorization": f"Bearer { token.access_token }"
        }, json={
            "title": title,
            "description": description,
            "community_id": community.id,
            "github_url": github_url,
            "work_url": work_url,
            "private": private
        })

        assert res.status_code == 200, 'Workの投稿に成功する'

        res_json = res.json()
        assert res_json['title'] == title
        assert res_json['description'] == description
        assert res_json['github_url'] == github_url
        assert res_json['work_url'] == work_url
        dict_community = dict(community)
        dict_community['created_at'] = dict_community['created_at'].isoformat(sep='T')
        dict_community['updated_at'] = dict_community['updated_at'].isoformat(sep='T')
        assert res_json['community'] == dict_community
        assert res_json['private'] == private

    def test_get_work(use_test_db_fixture, user_token_factory_for_test, work_for_test_public, work_for_test_private):
        """
        サインインの有り無しで他人のWorkを閲覧する
        """
        res_public = client.get(f'/api/v1/works/{work_for_test_public.id}')

        assert res_public.status_code == 200, 'サインイン無しでpublicのWorkの取得に成功する'

        res_public_json = res_public.json()
        assert res_public_json['id'] == work_for_test_public.id
        assert res_public_json['title'] == work_for_test_public.title
        assert res_public_json['description'] == work_for_test_public.description
        assert res_public_json['description_html'] == work_for_test_public.description_html
        assert res_public_json['github_url'] == work_for_test_public.github_url
        assert res_public_json['work_url'] == work_for_test_public.work_url
        dict_work_for_test_public_community = dict(work_for_test_public.community)
        dict_work_for_test_public_community['created_at'] = dict_work_for_test_public_community['created_at'].isoformat(sep='T')
        dict_work_for_test_public_community['updated_at'] = dict_work_for_test_public_community['updated_at'].isoformat(sep='T')
        assert res_public_json['community'] == dict_work_for_test_public_community
        assert res_public_json['private'] == work_for_test_public.private
        dict_work_for_test_public_user = dict(work_for_test_public.user)
        dict_work_for_test_public_user['created_at'] = dict_work_for_test_public_user['created_at'].isoformat(sep='T')
        dict_work_for_test_public_user['updated_at'] = dict_work_for_test_public_user['updated_at'].isoformat(sep='T')
        assert res_public_json['user'] == dict_work_for_test_public_user

        res_private = client.get(f'/api/v1/works/{work_for_test_private.id}')

        assert res_private.status_code == 403, 'サインイン無しでprivateのWorkの取得に失敗する'

        token = user_token_factory_for_test()
        res_public = client.get(f'/api/v1/works/{work_for_test_public.id}', headers={
            "Authorization": f"Bearer { token.access_token }"
        })

        assert res_public.status_code == 200, 'サインイン有りでpublicのWorkの取得に成功する'
        
        res_public_json = res_public.json()
        assert res_public_json['id'] == work_for_test_public.id
        assert res_public_json['title'] == work_for_test_public.title
        assert res_public_json['description'] == work_for_test_public.description
        assert res_public_json['description_html'] == work_for_test_public.description_html
        assert res_public_json['github_url'] == work_for_test_public.github_url
        assert res_public_json['work_url'] == work_for_test_public.work_url
        dict_work_for_test_public_community = dict(work_for_test_public.community)
        dict_work_for_test_public_community['created_at'] = dict_work_for_test_public_community['created_at'].isoformat(sep='T')
        dict_work_for_test_public_community['updated_at'] = dict_work_for_test_public_community['updated_at'].isoformat(sep='T')
        assert res_public_json['community'] == dict_work_for_test_public_community
        assert res_public_json['private'] == work_for_test_public.private
        dict_work_for_test_public_user = dict(work_for_test_public.user)
        dict_work_for_test_public_user['created_at'] = dict_work_for_test_public_user['created_at'].isoformat(sep='T')
        dict_work_for_test_public_user['updated_at'] = dict_work_for_test_public_user['updated_at'].isoformat(sep='T')
        assert res_public_json['user'] == dict_work_for_test_public_user

        res_private = client.get(f'/api/v1/works/{work_for_test_private.id}', headers={
            "Authorization": f"Bearer { token.access_token }"
        })

        assert res_private.status_code == 200, 'サインイン有りでprivateのWorkの取得に成功する'
        
        res_private_json = res_private.json()
        assert res_private_json['id'] == work_for_test_private.id
        assert res_private_json['title'] == work_for_test_private.title
        assert res_private_json['description'] == work_for_test_private.description
        assert res_private_json['description_html'] == work_for_test_private.description_html
        assert res_private_json['github_url'] == work_for_test_private.github_url
        assert res_private_json['work_url'] == work_for_test_private.work_url
        dict_work_for_test_private_community = dict(work_for_test_private.community)
        dict_work_for_test_private_community['created_at'] = dict_work_for_test_private_community['created_at'].isoformat(sep='T')
        dict_work_for_test_private_community['updated_at'] = dict_work_for_test_private_community['updated_at'].isoformat(sep='T')
        assert res_private_json['community'] == dict_work_for_test_private_community
        assert res_private_json['private'] == work_for_test_private.private
        dict_work_for_test_private_user = dict(work_for_test_private.user)
        dict_work_for_test_private_user['created_at'] = dict_work_for_test_private_user['created_at'].isoformat(sep='T')
        dict_work_for_test_private_user['updated_at'] = dict_work_for_test_private_user['updated_at'].isoformat(sep='T')
        assert res_private_json['user'] == dict_work_for_test_private_user

    def test_get_works(use_test_db_fixture, user_factory_for_test, user_token_factory_for_test, work_for_test_public, work_for_test_private):
        """
        サインインの有り無しでWork一覧を入手する
        """
        res_no_auth = client.get(f'/api/v1/works')

        assert res_no_auth.status_code == 200, 'サインイン無しでpublicのみのWorkListの取得に成功する'

        res_no_auth_json = res_no_auth.json()
        assert len(res_no_auth_json)==1
        get_work = res_no_auth_json[0]
        assert get_work['id'] == work_for_test_public.id
        assert get_work['title'] == work_for_test_public.title
        assert get_work['description'] == work_for_test_public.description
        assert get_work['description_html'] == work_for_test_public.description_html
        assert get_work['github_url'] == work_for_test_public.github_url
        assert get_work['work_url'] == work_for_test_public.work_url
        dict_work_for_test_public_community = dict(work_for_test_public.community)
        dict_work_for_test_public_community['created_at'] = dict_work_for_test_public_community['created_at'].isoformat(sep='T')
        dict_work_for_test_public_community['updated_at'] = dict_work_for_test_public_community['updated_at'].isoformat(sep='T')
        assert get_work['community'] == dict_work_for_test_public_community
        assert get_work['private'] == work_for_test_public.private
        dict_work_for_test_public_user = dict(work_for_test_public.user)
        dict_work_for_test_public_user['created_at'] = dict_work_for_test_public_user['created_at'].isoformat(sep='T')
        dict_work_for_test_public_user['updated_at'] = dict_work_for_test_public_user['updated_at'].isoformat(sep='T')
        assert get_work['user'] == dict_work_for_test_public_user

        token = user_token_factory_for_test()
        res_with_auth = client.get(f'/api/v1/works', headers={
            "Authorization": f"Bearer { token.access_token }"
        })

        assert res_with_auth.status_code == 200, 'サインイン有りでWorkListの取得に成功する'
        
        res_with_auth_json = res_with_auth.json()
        assert len(res_with_auth_json) == 2