import pytest
from .fixtures import (
    client,
    use_test_db_fixture,
    session_for_test,
    user_token_factory_for_test,
    user_factory_for_test,
    tag_for_test,
    user_for_test,
    tags_for_test,
)


@pytest.mark.usefixtures("use_test_db_fixture")
class TestTag:
    def test_post_tag(use_test_db_fixture, user_token_factory_for_test):
        """
        タグを作成する
        """
        name: str = "hoge"
        color: str = "#FFFFFFFF"
        token = user_token_factory_for_test()

        res = client.post(
            "/api/v1/tags",
            headers={"Authorization": f"Bearer { token.access_token }"},
            json={"name": name, "color": color},
        )

        assert res.status_code == 200, "tagの作成に成功する"

        res_json = res.json()
        print(res_json)
        assert res_json["name"] == name
        assert res_json["color"] == color

    def test_post_tag(use_test_db_fixture, user_token_factory_for_test):
        """
        カラーコードを間違えたタグを作成する
        """
        name: str = "hoge"
        color: str = "あいうえお"
        token = user_token_factory_for_test()

        res = client.post(
            "/api/v1/tags",
            headers={"Authorization": f"Bearer { token.access_token }"},
            json={"name": name, "color": color},
        )

        assert res.status_code == 422, "tagの作成に失敗する"

    def test_get_tags(use_test_db_fixture, tags_for_test):
        """
        タグ一覧を取得する
        """
        res = client.get("/api/v1/tags")

        assert res.status_code == 200, "タグ一覧の取得に成功する"

        res_json = res.json()

        assert res_json == tags_for_test

    def test_get_tags_forword_match_search(use_test_db_fixture, tags_for_test):
        """
        前方一致検索タグ一覧を取得する
        """
        tags = tags_for_test
        tags1 = [tag for tag in tags if tag.name.startswith("test1")]
        tags2 = [tag for tag in tags if tag.name.startswith("test2")]
        tags3 = [tag for tag in tags if tag.name.startswith("test1_tag1")]

        res = client.get("/api/v1/tags?w=test1")
        assert res.status_code == 200, "タグ一覧の取得に成功する"
        res_json = res.json()
        assert res_json == tags1

        res = client.get("/api/v1/tags?w=test2")
        assert res.status_code == 200, "タグ一覧の取得に成功する"
        res_json = res.json()
        assert res_json == tags2

        res = client.get("/api/v1/tags?w=test1_tag1")
        assert res.status_code == 200, "タグ一覧の取得に成功する"
        res_json = res.json()
        assert res_json == tags3

    def test_get_tags_forword_match_search_by_nothing_tag_name(
        use_test_db_fixture, tags_for_test
    ):
        """
        存在しないタグネームで前方一致検索タグ一覧を取得する
        """
        res = client.get("/api/v1/tags?w=test3")
        assert res.status_code == 200, "タグ一覧の取得に成功する"
        res_json = res.json()
        assert res_json == []

    def test_get_tag_by_tag_id(
        use_test_db_fixture, tag_for_test, user_token_factory_for_test
    ):
        """
        タグid指定でタグ情報を取得する
        """
        tag_id: str = tag_for_test.id
        name: str = tag_for_test.name
        color: str = tag_for_test.color
        token = user_token_factory_for_test()

        res = client.get(
            f"/api/v1/tags/{tag_id}",
            headers={"Authorization": f"Bearer { token.access_token }"},
        )

        assert res.status_code == 200, "タグid指定でタグ情報の取得に成功する"

        res_json = res.json()

        print(res_json)
        assert res_json["id"] == tag_id
        assert res_json["name"] == name
        assert res_json["color"] == color

    def test_put_tag(use_test_db_fixture, tag_for_test, user_token_factory_for_test):
        """
        タグを編集する
        """
        tag_id: str = tag_for_test.id
        name: str = "hogehoge"
        color: str = "#00000000"
        token = user_token_factory_for_test()

        res = client.put(
            f"/api/v1/tags/{tag_id}",
            headers={"Authorization": f"Bearer { token.access_token }"},
            json={"name": name, "color": color},
        )

        assert res.status_code == 200, "タグの編集に成功する"

        res_json = res.json()
        print(res_json)
        assert res_json["id"] == tag_id
        assert res_json["name"] == name
        assert res_json["color"] == color

    def test_put_tag(use_test_db_fixture, tag_for_test, user_token_factory_for_test):
        """
        タグを削除する
        """
        tag_id: str = tag_for_test.id
        name: str = "hogehoge"
        color: str = "#00000000"
        token = user_token_factory_for_test()

        res = client.delete(
            f"/api/v1/tags/{tag_id}",
            headers={"Authorization": f"Bearer { token.access_token }"},
        )

        assert res.status_code == 200, "タグの削除に成功する"

        res_json = res.json()
        print(res_json)
        assert res_json == {"status": "OK"}
