from datetime import timedelta

import pytest

from .fixtures import (
    client,
    session_for_test,
    use_test_db_fixture,
    user_factory_for_test,
    user_for_test,
    user_token_factory_for_test,
    users_factory_for_test,
)


@pytest.mark.usefixtures("use_test_db_fixture")
class TestUser:
    def test_get_me(
        use_test_db_fixture, user_factory_for_test, user_token_factory_for_test
    ):
        """
        自分の情報を取得
        """
        token = user_token_factory_for_test()
        print("Token", token)
        res = client.get(
            "/api/v1/users/@me",
            headers={"Authorization": f"Bearer { token.access_token }"},
        )
        assert res.status_code == 200, "自分の情報の取得に成功する"

    def test_get_me_unauthorized(user_factory_for_test, user_token_factory_for_test):
        """
        アクセストークンなしで自分の情報の取得に失敗する
        """
        user_token_factory_for_test()
        res = client.get(
            "/api/v1/users/@me",
            headers={
                # Without Authorization header...
            },
        )
        assert res.status_code == 403, "アクセストークンなしで自分の情報の取得に失敗する"

    def test_get_me_with_expired_access_token(
        use_test_db_fixture, user_factory_for_test, user_token_factory_for_test
    ):
        """
        期限切れのアクセストークンを用いて自分の情報の取得をしようとし、失敗する
        """
        # Create access_token which is expired before 10s
        token = user_token_factory_for_test(
            access_token_expires_delta=timedelta(seconds=-10)
        )

        res = client.get(
            "/api/v1/users/@me",
            headers={"Authorization": f"Bearer { token.access_token }"},
        )
        assert res.status_code == 403, "有効期限切れのアクセストークンを使った自分の情報の取得に失敗する"

    def test_get_user_by_id(use_test_db_fixture, users_factory_for_test):
        print("test_get_user_by_id :::::::: ユーザーの情報を取得")
        """
        ユーザーの情報を取得
        """
        count = 0
        users_info = users_factory_for_test()
        for user_info in users_info:
            count += 1
            user_id: str = user_info.id
            name: str = user_info.name
            display_name: str = user_info.display_name

            res = client.get(f"/api/v1/users/{user_id}")
            assert res.status_code == 200, "ユーザーの情報の取得に成功する"
            assert res.json()["id"] == user_id
            assert res.json()["name"] == name
            assert res.json()["display_name"] == display_name

    def test_get_user_by_not_correct_id(use_test_db_fixture, users_factory_for_test):
        print("test_get_user_by_not_correct_id :::::::: 間違ったユーザーIDでユーザーの情報を取得")
        """
        間違ったユーザーIDでユーザーの情報を取得
        """
        count = 0
        users_info = users_factory_for_test()
        for user_info in users_info:
            count += 1
            user_id: str = user_info.id + "hoge"

            res = client.get(f"/api/v1/users/{user_id}")
            assert res.status_code == 404, "ユーザーの情報の取得に失敗する"

    def test_get_users(use_test_db_fixture, users_factory_for_test):
        """
        ユーザー一覧を取得
        """
        users_info = users_factory_for_test()
        res = client.get("/api/v1/users")
        assert res.status_code == 200, "ユーザー一覧の取得に成功する"
        for index, user_info in enumerate(users_info):
            print(user_info)
            print(res.json())
            user_id: str = user_info.id

            assert res.json()[-index - 1]["id"] == user_id

    def test_get_users_with_limit(use_test_db_fixture, users_factory_for_test):
        print("test_get_users_with_limit :::::::: 取得するユーザー数を制限してユーザー一覧を取得")
        """
        取得するユーザー数を制限してユーザー一覧を取得
        """
        limit = 3
        users_factory_for_test()
        res = client.get(f"/api/v1/users?limit={limit}")

        print(res.json())

        assert res.status_code == 200, "取得するユーザー数を制限してユーザー一覧の取得に成功する"
        assert len(res.json()) == limit

    def test_get_users_with_offset_id(use_test_db_fixture, users_factory_for_test):
        print("test_get_users_with_offset_id :::::::: オフセットを指定してユーザー一覧を取得")
        """
        オフセットを指定してユーザー一覧を取得
        """
        users_info = users_factory_for_test()
        offset_id = users_info[2].id
        user_id = users_info[3].id
        res = client.get(f"/api/v1/users?oldest_user_id={offset_id}")

        assert res.status_code == 200, "オフセットを指定してユーザー一覧の取得に成功する"
        assert res.json()[-1]["id"] == user_id

    def test_get_users_with_not_exit_offset_id(
        use_test_db_fixture, users_factory_for_test
    ):
        print(
            "test_get_users_with_not_exit_offset_id :::::::: 存在しないオフセットIDを指定してユーザー一覧を取得"
        )
        """
        存在しないオフセットIDを指定してユーザー一覧を取得
        """
        users_info = users_factory_for_test()
        offset_id = users_info[2].id + "hoge"
        res = client.get(f"/api/v1/users?oldest_user_id={offset_id}")

        assert res.status_code == 400, "存在しないオフセットIDを指定してユーザー一覧の取得に失敗する"

    def test_put_all_info_of_user_me(
        use_test_db_fixture,
        user_factory_for_test,
        user_token_factory_for_test,
        session_for_test,
    ):
        print("test_put_all_info_of_user_me :::::::: ユーザーの情報をすべて編集")
        """
        ユーザーの情報をすべて編集
        """
        user_info = user_factory_for_test(
            session_for_test, "testuser1@test.com", "testuser1", "testuser1"
        )
        token = user_token_factory_for_test()

        display_name: str = user_info.display_name
        profile: str = user_info.profile

        new_display_name: str = "new_display_name"
        new_profile: str = "new_profile"
        new_twitter_id: str = "new_twitter_id"
        new_github_id: str = "new_github_id"

        print("Token", token)
        res = client.put(
            "/api/v1/users/@me",
            headers={"Authorization": f"Bearer { token.access_token }"},
            json={
                "display_name": new_display_name,
                "profile": new_profile,
                "twitter_id": new_twitter_id,
                "github_id": new_github_id,
            },
        )

        assert res.status_code == 200, "ユーザーのすべての情報の編集に成功する"
        assert res.json()["display_name"] == new_display_name
        assert res.json()["profile"] == new_profile
        assert res.json()["twitter_id"] == new_twitter_id
        assert res.json()["github_id"] == new_github_id
        assert res.json()["display_name"] != display_name
        assert res.json()["profile"] != profile

    def test_put_a_info_of_user_me(
        use_test_db_fixture,
        user_factory_for_test,
        user_token_factory_for_test,
        session_for_test,
    ):
        print("test_put_a_info_of_user_me :::::::: ユーザーの情報を1つ編集")
        """
        ユーザーの情報を1つ編集
        """
        user_info = user_factory_for_test(
            session_for_test, "testuser2@test.com", "testuser2", "testuser2"
        )
        token = user_token_factory_for_test()

        display_name: str = user_info.display_name
        profile: str = user_info.profile

        new_display_name: str = "new_display_name"

        print("Token", token)
        res = client.put(
            "/api/v1/users/@me",
            headers={"Authorization": f"Bearer { token.access_token }"},
            json={"display_name": new_display_name},
        )

        assert res.status_code == 200, "ユーザーの1つの情報の編集に成功する"
        assert res.json()["display_name"] == new_display_name
        assert res.json()["display_name"] != display_name
        assert res.json()["profile"] == profile

    def test_put_unauthorized(use_test_db_fixture):
        print("test_put_unauthorized :::::::: アクセストークンなしで自分の情報を変更する")
        """
        アクセストークンなしで自分の情報を変更する
        """
        new_display_name: str = "new_display_name"
        new_profile: str = "new_profile"

        res = client.put(
            "/api/v1/users/@me",
            headers={
                # Without Authorization header...
            },
            json={
                "display_name": new_display_name,
                "profile": new_profile,
            },
        )

        assert res.status_code == 403, "アクセストークンなしで自分の情報の変更に失敗する"

    def test_put_with_expired_access_token(
        use_test_db_fixture, user_token_factory_for_test
    ):
        print("test_put_with_expired_access_token :::::::: 期限切れのアクセストークンを用いて自分の情報を変更する")
        """
        期限切れのアクセストークンを用いて自分の情報を変更する
        """
        # Create access_token which is expired before 10s
        token = user_token_factory_for_test(
            access_token_expires_delta=timedelta(seconds=-10)
        )

        new_display_name: str = "new_display_name"
        new_profile: str = "new_profile"

        print("Token", token)
        res = client.put(
            "/api/v1/users/@me",
            headers={"Authorization": f"Bearer { token.access_token }"},
            json={
                "display_name": new_display_name,
                "profile": new_profile,
            },
        )

        assert res.status_code == 403, "期限切れのアクセストークンを用いて自分の情報の変更に失敗する"

    def test_update_avatar(
        use_test_db_fixture, user_for_test, user_token_factory_for_test
    ):
        """
        ユーザーのアバターを更新する
        """
        image = open("tests/test_data/test_image.png", "rb")
        token = user_token_factory_for_test()
        res = client.put(
            "/api/v1/users/@me/avatar",
            headers={"Authorization": f"Bearer { token.access_token }"},
            files={"file": ("test_image.png", image, "image/png")},
        )
        assert res.status_code == 200, "自分の情報の取得に成功する"
        res_json = res.json()
        assert res_json["avatar_url"] != user_for_test.avatar_url

    def test_update_avatar(use_test_db_fixture, user_token_factory_for_test):
        """
        ユーザーのアバターの更新に失敗する
        """
        video = open("tests/test_data/test_video.mp4", "rb")
        token = user_token_factory_for_test()
        res = client.put(
            "/api/v1/users/@me/avatar",
            headers={"Authorization": f"Bearer { token.access_token }"},
            files={"file": ("test_video.mp4", video, "video/mp4")},
        )
        assert res.status_code == 422, "ファイルの型が異なるため失敗する"

    def test_delete_avatar(use_test_db_fixture, user_token_factory_for_test):
        """
        ユーザーのアバターを削除する
        """
        image = open("tests/test_data/test_image.png", "rb")
        token = user_token_factory_for_test()
        res = client.put(
            "/api/v1/users/@me/avatar",
            headers={"Authorization": f"Bearer { token.access_token }"},
            files={"file": ("test_image.png", image, "image/png")},
        )
        old_avatar = res.json()["avatar_url"]
        res = client.delete(
            "/api/v1/users/@me/avatar",
            headers={"Authorization": f"Bearer { token.access_token }"},
        )
        assert res.status_code == 200, "アバターの削除に成功する"
        assert res.json()["avatar_url"] != old_avatar
