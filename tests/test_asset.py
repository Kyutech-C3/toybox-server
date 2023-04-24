import json
import pytest
from .fixtures import (
    client,
    use_test_db_fixture,
    user_token_factory_for_test,
    image_asset_for_test,
    session_for_test,
    user_factory_for_test,
    user_for_test,
)


@pytest.mark.usefixtures("use_test_db_fixture")
class TestAsset:
    def test_post_asset_without_auth(use_test_db_fixture):
        """
        認証無しでAssetを投稿する
        """
        image = open("tests/test_data/test_image.png", "rb")
        asset_type = "image"

        res = client.post(
            "/api/v1/assets",
            files={"file": ("test_image.png", image, "image/png")},
            data={"asset_type": asset_type},
        )

        print(res.request)

        assert res.status_code == 403, "Assetの投稿に失敗する"

    def test_post_correct_image_asset(use_test_db_fixture, user_token_factory_for_test):
        """
        画像のAssetを投稿する
        """
        token = user_token_factory_for_test()
        image = open("tests/test_data/test_image.png", "rb")
        asset_type = "image"

        res = client.post(
            "/api/v1/assets",
            headers={"Authorization": f"Bearer { token.access_token }"},
            files={"file": ("test_image.png", image, "image/png")},
            data={"asset_type": asset_type},
        )

        assert res.status_code == 200, "Assetの投稿に成功する"

    def test_post_incorrect_type_asset(
        use_test_db_fixture, user_token_factory_for_test
    ):
        """
        タイプを間違えて画像のAssetを投稿する
        """
        token = user_token_factory_for_test()
        image = open("tests/test_data/test_image.png", "rb")
        asset_type = "video"

        res = client.post(
            "/api/v1/assets",
            headers={"Authorization": f"Bearer { token.access_token }"},
            files={"file": ("test_image.png", image, "image/png")},
            data={"asset_type": asset_type},
        )

        assert res.status_code == 400, "Assetの投稿に失敗する"

    def test_post_not_exist_type_asset(
        use_test_db_fixture, user_token_factory_for_test
    ):
        """
        存在しないタイプを指定して画像のAssetを投稿する
        """
        token = user_token_factory_for_test()
        image = open("tests/test_data/test_image.png", "rb")
        asset_type = "gazou"

        res = client.post(
            "/api/v1/assets",
            headers={"Authorization": f"Bearer { token.access_token }"},
            files={"file": ("test_image.png", image, "image/png")},
            data={"asset_type": asset_type},
        )

        assert res.status_code == 422, "Assetの投稿に失敗する"
