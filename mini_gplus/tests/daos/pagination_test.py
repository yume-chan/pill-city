from .base_test_case import BaseTestCase
from freezegun import freeze_time
from mini_gplus.models import Post
from mini_gplus.daos.user import sign_up, find_user
from mini_gplus.daos.post import create_post, dangerously_get_post, sees_post
from mini_gplus.daos.pagination import get_page, poll_latest


class PaginationTest(BaseTestCase):
    def test_empty(self):
        self.assertEqual([], get_page(Post, {}, self._post_filter_noop, None, 5))

    @staticmethod
    def _post_filter_noop(_):
        return True

    @staticmethod
    def _post_filter_sees_on_home(self):
        def _func(post):
            return sees_post(self, post, True)
        return _func

    def test_one_page_no_time_collision_no_filter(self):
        self.assertTrue(sign_up('user1', '1234'))
        user1 = find_user('user1')
        all_paged_posts = []
        for i in range(4):
            all_paged_posts.append(dangerously_get_post(create_post(user1, str(i), True, [], False, None, [], [],
                                                                    False).eid))
        all_paged_posts = list(reversed(all_paged_posts))

        self.assertEqual(all_paged_posts, get_page(Post, {}, self._post_filter_noop, None, 5))
        last_post = all_paged_posts[-1]
        self.assertEqual([], get_page(Post, {}, self._post_filter_noop, last_post.eid, 5))

    def test_poll_latest_no_time_collision_no_filter(self):
        self.assertTrue(sign_up('user1', '1234'))
        user1 = find_user('user1')
        all_posts = []
        for i in range(4):
            all_posts.append(dangerously_get_post(create_post(user1, str(i), True, [], False, None, [], [], False).eid))
        all_posts = list(reversed(all_posts))

        self.assertEqual(all_posts[: 2], poll_latest(Post, {}, self._post_filter_noop, all_posts[2].eid))

    def test_one_page_no_time_collision_and_filter(self):
        self.assertTrue(sign_up('user1', '1234'))
        self.assertTrue(sign_up('user2', '1234'))
        user1 = find_user('user1')
        user2 = find_user('user2')
        all_paged_posts = []
        for i in range(8):
            if i % 2 == 0:
                all_paged_posts.append(dangerously_get_post(create_post(user1, str(i), True, [], False, None, [], [],
                                                                        False).eid))
            else:
                create_post(user2, str(i), True, [], False, None, [], [], False)
        all_paged_posts = list(reversed(all_paged_posts))

        self.assertEqual(all_paged_posts, get_page(Post, {}, self._post_filter_sees_on_home(user1), None, 5))
        last_post = all_paged_posts[-1]
        self.assertEqual([], get_page(Post, {}, self._post_filter_sees_on_home(user1), last_post.eid, 5))

    def test_multiple_pages_no_time_collision_no_filter(self):
        self.assertTrue(sign_up('user1', '1234'))
        user1 = find_user('user1')
        all_paged_posts = []
        for i in range(9):
            all_paged_posts.append(dangerously_get_post(create_post(user1, str(i), True, [], False, None, [], [],
                                                                    False).eid))
        all_paged_posts = list(reversed(all_paged_posts))

        self.assertEqual(all_paged_posts[: 5], get_page(Post, {}, self._post_filter_noop, None, 5))
        last_post = all_paged_posts[4]
        self.assertEqual(all_paged_posts[5:], get_page(Post, {}, self._post_filter_noop, last_post.eid, 5))

    def test_multiple_pages_no_time_collision_filter(self):
        self.assertTrue(sign_up('user1', '1234'))
        self.assertTrue(sign_up('user2', '1234'))
        user1 = find_user('user1')
        user2 = find_user('user2')
        all_paged_posts = []
        for i in range(18):
            if i % 2 == 0:
                all_paged_posts.append(dangerously_get_post(create_post(user1, str(i), True, [], False, None, [], [],
                                                                        False).eid))
            else:
                create_post(user2, str(i), True, [], False, None, [], [], False)
        all_paged_posts = list(reversed(all_paged_posts))

        self.assertEqual(all_paged_posts[: 5], get_page(Post, {}, self._post_filter_sees_on_home(user1), None, 5))
        last_post = all_paged_posts[4]
        self.assertEqual(all_paged_posts[5:], get_page(Post, {}, self._post_filter_sees_on_home(user1), last_post.eid,
                                                       5))

    def test_multiple_pages_time_collision_no_filter(self):
        self.assertTrue(sign_up('user1', '1234'))
        user1 = find_user('user1')
        all_paged_posts = []
        with freeze_time():
            for i in range(9):
                all_paged_posts.append(dangerously_get_post(create_post(user1, str(i), True, [], False, None, [], [],
                                                                        False).eid))
        all_paged_posts = list(reversed(all_paged_posts))

        self.assertEqual(all_paged_posts[: 5], get_page(Post, {}, self._post_filter_noop, None, 5))
        last_post = all_paged_posts[4]
        self.assertEqual(all_paged_posts[5:], get_page(Post, {}, self._post_filter_noop, last_post.eid, 5))

    def test_multiple_pages_time_collision_filter(self):
        self.assertTrue(sign_up('user1', '1234'))
        self.assertTrue(sign_up('user2', '1234'))
        user1 = find_user('user1')
        user2 = find_user('user2')
        all_paged_posts = []
        with freeze_time():
            for i in range(18):
                if i % 2 == 0:
                    all_paged_posts.append(dangerously_get_post(create_post(user1, str(i), True, [], False, None, [],
                                                                            [], False).eid))
                else:
                    create_post(user2, str(i), True, [], False, None, [], [], False)
        all_paged_posts = list(reversed(all_paged_posts))

        self.assertEqual(all_paged_posts[: 5], get_page(Post, {}, self._post_filter_sees_on_home(user1), None, 5))
        last_post = all_paged_posts[4]
        self.assertEqual(all_paged_posts[5:], get_page(Post, {}, self._post_filter_sees_on_home(user1), last_post.eid,
                                                       5))
