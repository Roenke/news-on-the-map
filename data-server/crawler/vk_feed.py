import vk
from datetime import datetime

VK_POST_URL = "https://vk.com/wall-{}_{}"

session = vk.Session()
api = vk.API(session)


def get_posts(group_id, offset):
    try:
        return api.wall.get(owner_id=-group_id, offset=offset, count=100)[1:]
    except Exception as e:
        print 'Error happened: ', e, str(type(e))


def load(url):
    group_name = url.rsplit('/')[-1]
    group = api.groups.getById(group_id=group_name)[0]

    gid = group["gid"]
    offset = 0
    posts = get_posts(gid, offset)
    while len(posts) > 0:
        offset += len(posts)
        for post in posts:
            date = datetime.fromtimestamp(post["date"])
            yield post["text"], date, VK_POST_URL.format(gid, post["id"])

        posts = get_posts(gid, offset)
