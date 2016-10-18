import vk
from datetime import datetime


VK_POST_URL = "https://vk.com/wall-{}_{}"

session = vk.Session()
api = vk.API(session)


def load(url):
    group_name = url.rsplit('/')[-1]
    group = api.groups.getById(group_id=group_name)[0]

    gid = group["gid"]
    for post in api.wall.get(owner_id=-gid)[1:]:
        date = datetime.fromtimestamp(post["date"])
        yield post["text"], date, VK_POST_URL.format(gid, post["id"])
