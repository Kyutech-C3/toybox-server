import pytest
from .fixtures import use_test_db_fixture

@pytest.mark.usefixtures('use_test_db_fixture')
class TestWork:

    def test_post_work_without_auth(use_test_db_fixture):
        """
        Workを認証なしで投稿する
        """

    def test_post_work_about_visibillity(use_test_db_fixture):
        """
        公開設定のそれぞれを投稿する
        """

    def test_post_work_about_thumbnail(use_test_db_fixture):
        """
        サムネイルのあるものないものをそれぞれ投稿する
        """

    def test_post_work_about_assets(use_test_db_fixture):
        """
        アセットのあるものないものをそれぞれ投稿する
        """

    def test_post_work_about_url(use_test_db_fixture):
        """
        関連URLのあるものないものをそれぞれ投稿する
        """

    def test_post_work_about_tag(use_test_db_fixture):
        """
        タグのあるものないものをそれぞれ投稿する
        """

    def test_post_work_without_title(use_test_db_fixture):
        """
        Workのタイトル無しで投稿する
        """

    def test_post_work_without_description(use_test_db_fixture):
        """
        Workの説明文なしで投稿する
        """

    def test_post_work_incorrect_community(use_test_db_fixture):
        """
        存在しないコミュニティのIDを指定して投稿する
        """

    def test_post_work_incorrect_visibbility(use_test_db_fixture):
        """
        間違った公開設定を指定して投稿する
        """

    def test_post_work_incorrect_asset(use_test_db_fixture):
        """
        存在しないアセットのIDを指定して投稿する
        """

    def test_post_work_incorrect_thumbnail_asset(use_test_db_fixture):
        """
        存在しないアセットのIDをサムネイルに指定して投稿する
        """

    def test_post_work_incorrect_url(use_test_db_fixture):
        """
        間違ったURLを指定して投稿する
        """

    def test_post_work_incorrect_tag(use_test_db_fixture):
        """
        存在しないタグのIDを指定して投稿する
        """

    def test_get_work_by_correct_id(use_test_db_fixture):
        """
        IDを指定してWorkを取得する
        """

    def test_get_work_by_incorrect_id(use_test_db_fixture):
        """
        存在しないIDを指定してWorkを取得する
        """

    def test_get_works(use_test_db_fixture):
        """
        複数のWorkを取得する
        """

    def test_get_works_pagenation(use_test_db_fixture):
        """
        Work取得のページネーションを確認する
        """

    def test_put_work(use_test_db_fixture):
        """
        Workの情報を変更する
        """

    def test_delete_correct_work(use_test_db_fixture):
        """
        Workを削除する
        """

    def test_delete_incorrect_work(use_test_db_fixture):
        """
        存在しないWorkを削除する
        """
