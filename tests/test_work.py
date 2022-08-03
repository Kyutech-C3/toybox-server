import json
import pytest
from .fixtures import client, use_test_db_fixture, session_for_test, user_factory_for_test, user_token_factory_for_test, asset_factory_for_test, user_for_test, tag_for_test, work_factory_for_test, tag_factory_for_test
from db.models import Visibility

@pytest.mark.usefixtures('use_test_db_fixture')
class TestWork:

    def test_post_work_without_auth(use_test_db_fixture, asset_factory_for_test, tag_for_test):
        """
        Workを認証なしで投稿する
        """
        title = 'testwork'
        description = 'this work is test work!!'
        visibility = 'public'
        asset = asset_factory_for_test()
        thumbnail = asset_factory_for_test()
        urls = [
            {
                "url": "https://github.com/PigeonsHouse/NicoCommeDon",
                "url_type": "github"
            }
        ]

        res = client.post('/api/v1/works', json={
                "title": title,
                "description": description,
                "visibility": visibility,
                "thumbnail_asset_id": thumbnail.id,
                "assets_id": [
                    asset.id
                ],
                "tags_id": [tag_for_test.id],
                "urls": urls
            }
        )

        assert res.status_code == 403, "認証に失敗する"

    def test_post_work_about_visibility(use_test_db_fixture, user_token_factory_for_test, asset_factory_for_test, tag_for_test):
        """
        公開設定のそれぞれを投稿する
        """
        token = user_token_factory_for_test()
        title = 'testwork'
        description = 'this work is test work!!'
        visibility = 'public'
        asset = asset_factory_for_test()
        thumbnail = asset_factory_for_test()
        urls = [
            {
                "url": "https://github.com/PigeonsHouse/NicoCommeDon",
                "url_type": "github"
            }
        ]

        res = client.post('/api/v1/works', headers={
                "Authorization": f"Bearer {token.access_token}"
            },json={
                "title": title,
                "description": description,
                "visibility": visibility,
                "thumbnail_asset_id": thumbnail.id,
                "assets_id": [
                    asset.id
                ],
                "tags_id": [tag_for_test.id],
                "urls": urls
            }
        )

        assert res.status_code == 200, "Workの投稿に成功する"
        res_json = res.json()
        assert res_json['title'] == title
        assert res_json['description'] == description
        assert res_json['visibility'] == visibility

        visibility = 'private'
        res = client.post('/api/v1/works', headers={
                "Authorization": f"Bearer {token.access_token}"
            },json={
                "title": title,
                "description": description,
                "visibility": visibility,
                "thumbnail_asset_id": thumbnail.id,
                "assets_id": [
                    asset.id
                ],
                "tags_id": [tag_for_test.id],
                "urls": urls
            }
        )

        assert res.status_code == 200, "Workの投稿に成功する"
        res_json = res.json()
        assert res_json['title'] == title
        assert res_json['description'] == description
        assert res_json['visibility'] == visibility

        visibility = 'draft'
        res = client.post('/api/v1/works', headers={
                "Authorization": f"Bearer {token.access_token}"
            },json={
                "title": title,
                "description": description,
                "visibility": visibility,
                "thumbnail_asset_id": thumbnail.id,
                "assets_id": [
                    asset.id
                ],
                "tags_id": [tag_for_test.id],
                "urls": urls
            }
        )

        assert res.status_code == 200, "Workの投稿に成功する"
        res_json = res.json()
        assert res_json['title'] == title
        assert res_json['description'] == description
        assert res_json['visibility'] == visibility

    def test_post_work_about_thumbnail(use_test_db_fixture, user_token_factory_for_test, asset_factory_for_test, tag_for_test):
        """
        サムネイルのあるものないものをそれぞれ投稿する
        """
        token = user_token_factory_for_test()
        title = 'testwork'
        description = 'this work is test work!!'
        visibility = 'public'
        asset = asset_factory_for_test()
        urls = [
            {
                "url": "https://github.com/PigeonsHouse/NicoCommeDon",
                "url_type": "github"
            }
        ]

        res = client.post('/api/v1/works', headers={
                "Authorization": f"Bearer {token.access_token}"
            }, json={
                "title": title,
                "description": description,
                "visibility": visibility,
                "assets_id": [
                    asset.id
                ],
                "tags_id": [tag_for_test.id],
                "urls": urls
            }
        )

        assert res.status_code == 200, "Workの投稿に成功する"
        res_json = res.json()
        assert res_json['title'] == title
        assert res_json['description'] == description
        assert res_json['thumbnail'] == None

        thumbnail = asset_factory_for_test()
        res = client.post('/api/v1/works', headers={
                "Authorization": f"Bearer {token.access_token}"
            },json={
                "title": title,
                "description": description,
                "visibility": visibility,
                "thumbnail_asset_id": thumbnail.id,
                "assets_id": [
                    asset.id
                ],
                "tags_id": [tag_for_test.id],
                "urls": urls
            }
        )

        assert res.status_code == 200, "Workの投稿に成功する"
        res_json = res.json()
        assert res_json['title'] == title
        assert res_json['description'] == description
        assert res_json['thumbnail']['id'] == thumbnail.id

    def test_post_work_about_assets(use_test_db_fixture, user_token_factory_for_test, asset_factory_for_test, tag_for_test):
        """
        アセットのあるものないものをそれぞれ投稿する
        """
        token = user_token_factory_for_test()
        title = 'testwork'
        description = 'this work is test work!!'
        visibility = 'public'
        thumbnail = asset_factory_for_test()
        urls = [
            {
                "url": "https://github.com/PigeonsHouse/NicoCommeDon",
                "url_type": "github"
            }
        ]

        res = client.post('/api/v1/works', headers={
                "Authorization": f"Bearer {token.access_token}"
            },json={
                "title": title,
                "description": description,
                "visibility": visibility,
                "thumbnail_asset_id": thumbnail.id,
                "assets_id": [],
                "tags_id": [tag_for_test.id],
                "urls": urls
            }
        )

        assert res.status_code == 200, "Workの投稿に成功する"
        res_json = res.json()
        assert res_json['title'] == title
        assert res_json['description'] == description
        assert res_json['assets'] == []

        asset = asset_factory_for_test()
        res = client.post('/api/v1/works', headers={
                "Authorization": f"Bearer {token.access_token}"
            },json={
                "title": title,
                "description": description,
                "visibility": visibility,
                "thumbnail_asset_id": thumbnail.id,
                "assets_id": [
                    asset.id
                ],
                "tags_id": [tag_for_test.id],
                "urls": urls
            }
        )

        assert res.status_code == 200, "Workの投稿に成功する"
        res_json = res.json()
        assert res_json['title'] == title
        assert res_json['description'] == description
        assert res_json['assets'][0]['id'] == asset.id

    def test_post_work_about_url(use_test_db_fixture, user_token_factory_for_test, asset_factory_for_test, tag_for_test):
        """
        関連URLのあるものないものをそれぞれ投稿する
        """
        token = user_token_factory_for_test()
        title = 'testwork'
        description = 'this work is test work!!'
        visibility = 'public'
        asset = asset_factory_for_test()
        thumbnail = asset_factory_for_test()

        res = client.post('/api/v1/works', headers={
                "Authorization": f"Bearer {token.access_token}"
            },json={
                "title": title,
                "description": description,
                "visibility": visibility,
                "thumbnail_asset_id": thumbnail.id,
                "assets_id": [
                    asset.id
                ],
                "tags_id": [tag_for_test.id],
                "urls": []
            }
        )

        assert res.status_code == 200, "Workの投稿に成功する"
        res_json = res.json()
        assert res_json['title'] == title
        assert res_json['description'] == description
        assert res_json['urls'] == []

        url = "https://github.com/PigeonsHouse/NicoCommeDon"
        url_type = "github"
        urls = [
            {
                "url": url,
                "url_type": url_type
            }
        ]
        res = client.post('/api/v1/works', headers={
                "Authorization": f"Bearer {token.access_token}"
            },json={
                "title": title,
                "description": description,
                "visibility": visibility,
                "thumbnail_asset_id": thumbnail.id,
                "assets_id": [
                    asset.id
                ],
                "tags_id": [tag_for_test.id],
                "urls": urls
            }
        )

        assert res.status_code == 200, "Workの投稿に成功する"
        res_json = res.json()
        assert res_json['title'] == title
        assert res_json['description'] == description
        assert res_json['urls'][0]['url'] == url
        assert res_json['urls'][0]['url_type'] == url_type

    # def test_post_work_about_tag(use_test_db_fixture):
    #     """
    #     タグのあるものないものをそれぞれ投稿する
    #     """

    # def test_post_work_without_title(use_test_db_fixture):
    #     """
    #     Workのタイトル無しで投稿する
    #     """

    # def test_post_work_without_description(use_test_db_fixture):
    #     """
    #     Workの説明文なしで投稿する
    #     """

    # def test_post_work_incorrect_community(use_test_db_fixture):
    #     """
    #     存在しないコミュニティのIDを指定して投稿する
    #     """

    # def test_post_work_incorrect_visibility(use_test_db_fixture):
    #     """
    #     間違った公開設定を指定して投稿する
    #     """

    # def test_post_work_incorrect_asset(use_test_db_fixture):
    #     """
    #     存在しないアセットのIDを指定して投稿する
    #     """

    # def test_post_work_incorrect_thumbnail_asset(use_test_db_fixture):
    #     """
    #     存在しないアセットのIDをサムネイルに指定して投稿する
    #     """

    # def test_post_work_incorrect_url(use_test_db_fixture):
    #     """
    #     間違ったURLを指定して投稿する
    #     """

    # def test_post_work_incorrect_tag(use_test_db_fixture):
    #     """
    #     存在しないタグのIDを指定して投稿する
    #     """

    # def test_post_work_another_asset(use_test_db_fixture):
    #     """
    #     別人のAssetでWorkを投稿する
    #     """

    # def test_get_work_by_correct_id(use_test_db_fixture):
    #     """
    #     IDを指定してWorkを取得する
    #     """

    # def test_get_work_by_incorrect_id(use_test_db_fixture):
    #     """
    #     存在しないIDを指定してWorkを取得する
    #     """

    # def test_get_works(use_test_db_fixture):
    #     """
    #     複数のWorkを取得する
    #     """

    # def test_get_works_pagination(use_test_db_fixture):
    #     """
    #     Work取得のページネーションを確認する
    #     """

    # def test_put_work(use_test_db_fixture):
    #     """
    #     Workの情報を変更する
    #     """

    # def test_delete_correct_work(use_test_db_fixture):
    #     """
    #     Workを削除する
    #     """

    # def test_delete_incorrect_work(use_test_db_fixture):
    #     """
    #     存在しないWorkを削除する
    #     """

    def test_get_my_works(use_test_db_fixture, user_token_factory_for_test, work_factory_for_test):
        """
        自分の作品を取得する
        """
        work = work_factory_for_test()
        token = user_token_factory_for_test()
        res = client.get('/api/v1/users/@me/works', headers={
            "Authorization": f"Bearer { token.access_token }"
        })

        assert res.status_code == 200
        res_json = res.json()
        assert len(res_json) == 1
        assert res_json[0]['id'] == work.id

    def test_get_my_works_without_auth(use_test_db_fixture):
        """
        自分の作品を認証無しで取得する
        """
        res = client.get('/api/v1/users/@me/works')

        assert res.status_code == 403, '作品の取得に失敗する'
        
    def test_get_his_works(use_test_db_fixture, user_token_factory_for_test, work_factory_for_test, user_factory_for_test):
        """
        指定したユーザーの作品を取得する
        """
        target_user = user_factory_for_test(email='hoge@test.jp')
        work = work_factory_for_test(user_id=target_user.id)
        my_token = user_token_factory_for_test()
        res = client.get(f'/api/v1/users/{ target_user.id }/works', headers={
            "Authorization": f"Bearer { my_token.access_token }"
        })

        assert res.status_code == 200
        res_json = res.json()
        assert len(res_json) == 1
        assert res_json[0]['id'] == work.id

    def test_get_not_exist_user_works(use_test_db_fixture, user_token_factory_for_test):
        """
        存在しないユーザーの作品を取得する
        """
        token = user_token_factory_for_test()
        res = client.get(f'/api/v1/users/hogehogeuserid/works', headers={
            "Authorization": f"Bearer { token.access_token }"
        })

        assert res.status_code == 404, '作品の取得に失敗する'

    def test_search_works_by_tag(use_test_db_fixture, user_token_factory_for_test, tag_factory_for_test, work_factory_for_test):
        """
        タグから作品を絞り込んで検索する
        """
        token = user_token_factory_for_test()

        test_tag1 = tag_factory_for_test(name='testtag1', color='#ff3030')
        test_tag2 = tag_factory_for_test(name='testtag2', color='#30ff30')
        test_tag3 = tag_factory_for_test(name='testtag3', color='#3030ff')
        test_tag4 = tag_factory_for_test(name='testtag4', color='#44e099')
        test_tag5 = tag_factory_for_test(name='testtag5', color='#30dda0')

        work1 = work_factory_for_test(title='testwork1', visibility=Visibility.public, tags_id=[test_tag1.id, test_tag2.id, test_tag5.id])
        work2 = work_factory_for_test(title='testwork2', visibility=Visibility.public, tags_id=[test_tag2.id, test_tag3.id, test_tag5.id])
        work3 = work_factory_for_test(title='testwork3', visibility=Visibility.private, tags_id=[test_tag1.id, test_tag4.id, test_tag5.id])

        res = client.get(f'/api/v1/works?tags={test_tag1.id}', headers={
            'Authorization': f'Bearer { token.access_token }'
            }
        )

        assert res.status_code == 200
        res_json = res.json()
        assert len(res_json) == 2
        assert res_json[0].get('title') == work3.title
        assert res_json[1].get('title') == work1.title

        res = client.get(f'/api/v1/works?tags={test_tag5.id}', headers={
            'Authorization': f'Bearer { token.access_token }'
            }
        )

        assert res.status_code == 200
        res_json = res.json()
        assert len(res_json) == 3
        assert res_json[0].get('title') == work3.title
        assert res_json[1].get('title') == work2.title
        assert res_json[2].get('title') == work1.title

    def test_search_works_by_some_tag(use_test_db_fixture, user_token_factory_for_test, tag_factory_for_test, work_factory_for_test):
        """
        複数のタグから作品を絞り込んで検索する
        """
        token = user_token_factory_for_test()

        test_tag1 = tag_factory_for_test(name='testtag1', color='#ff3030')
        test_tag2 = tag_factory_for_test(name='testtag2', color='#30ff30')
        test_tag3 = tag_factory_for_test(name='testtag3', color='#3030ff')
        test_tag4 = tag_factory_for_test(name='testtag4', color='#44e099')
        test_tag5 = tag_factory_for_test(name='testtag5', color='#30dda0')

        work_factory_for_test(title='testwork1', visibility=Visibility.public, tags_id=[test_tag1.id, test_tag2.id, test_tag5.id])
        work_factory_for_test(title='testwork2', visibility=Visibility.public, tags_id=[test_tag2.id, test_tag3.id, test_tag5.id])
        work3 = work_factory_for_test(title='testwork3', visibility=Visibility.private, tags_id=[test_tag1.id, test_tag4.id, test_tag5.id])

        res = client.get(f'/api/v1/works?tags={test_tag1.id},{test_tag4.id}', headers={
            'Authorization': f'Bearer { token.access_token }'
            }
        )

        assert res.status_code == 200
        res_json = res.json()
        assert len(res_json) == 1
        assert res_json[0].get('title') == work3.title

    def test_search_works_by_tag_without_auth(use_test_db_fixture, tag_factory_for_test, work_factory_for_test):
        """
        認証無しでタグから作品を絞り込んで検索する
        """
        test_tag1 = tag_factory_for_test(name='testtag1', color='#ff3030')
        test_tag2 = tag_factory_for_test(name='testtag2', color='#30ff30')
        test_tag3 = tag_factory_for_test(name='testtag3', color='#3030ff')
        test_tag4 = tag_factory_for_test(name='testtag4', color='#44e099')
        test_tag5 = tag_factory_for_test(name='testtag5', color='#30dda0')

        work1 = work_factory_for_test(title='testwork1', visibility=Visibility.public, tags_id=[test_tag1.id, test_tag2.id, test_tag5.id])
        work_factory_for_test(title='testwork2', visibility=Visibility.public, tags_id=[test_tag2.id, test_tag3.id, test_tag5.id])
        work_factory_for_test(title='testwork3', visibility=Visibility.private, tags_id=[test_tag1.id, test_tag4.id, test_tag5.id])

        res = client.get(f'/api/v1/works?tags={test_tag1.id}')

        assert res.status_code == 200
        res_json = res.json()
        assert len(res_json) == 1
        assert res_json[0].get('title') == work1.title

    def test_search_works_by_strict_tag(use_test_db_fixture, user_token_factory_for_test, tag_factory_for_test, work_factory_for_test):
        """
        存在しない条件でタグから作品を絞り込んで検索する
        """
        token = user_token_factory_for_test()

        test_tag1 = tag_factory_for_test(name='testtag1', color='#ff3030')
        test_tag2 = tag_factory_for_test(name='testtag2', color='#30ff30')
        test_tag3 = tag_factory_for_test(name='testtag3', color='#3030ff')
        test_tag4 = tag_factory_for_test(name='testtag4', color='#44e099')
        test_tag5 = tag_factory_for_test(name='testtag5', color='#30dda0')

        work_factory_for_test(title='testwork1', visibility=Visibility.public, tags_id=[test_tag1.id, test_tag2.id, test_tag5.id])
        work_factory_for_test(title='testwork2', visibility=Visibility.public, tags_id=[test_tag2.id, test_tag3.id, test_tag5.id])
        work_factory_for_test(title='testwork3', visibility=Visibility.private, tags_id=[test_tag1.id, test_tag4.id, test_tag5.id])

        res = client.get(f'/api/v1/works?tags={test_tag1.id},{test_tag2.id},{test_tag4.id}', headers={
            'Authorization': f'Bearer { token.access_token }'
        })

        assert res.status_code == 200
        res_json = res.json()
        assert len(res_json) == 0
        assert res_json == []
