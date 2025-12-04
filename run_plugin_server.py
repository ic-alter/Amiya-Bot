import time
import json
import hashlib
import aiohttp

from amiya import run_amiya
from amiyabot.util import argv
from pluginsServer.src import server, api

AFDIAN_USER = argv('afdian-user')
AFDIAN_TOKEN = argv('afdian-token')


@server.server.app.get('/get_sponsors')
async def get_sponsors():
    if not AFDIAN_TOKEN or not AFDIAN_USER:
        return []

    curr_page = 1
    total_page = 1
    sponsor_list = []

    while curr_page <= total_page:
        sec = int(time.time())
        params = json.dumps({'page': curr_page})
        data = {
            'user_id': AFDIAN_USER,
            'params': params,
            'ts': sec,
            'sign': hashlib.md5(
                f'{AFDIAN_TOKEN}params{params}ts{sec}user_id{AFDIAN_USER}'.encode(encoding='utf-8')
            ).hexdigest(),
        }
        headers = {'Content-Type': 'application/json'}
        url = 'https://afdian.com/api/open/query-sponsor'

        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=json.dumps(data), headers=headers) as res:
                res_content = await res.json()
                if res_content['ec'] == 200:
                    total_page = res_content['data']['total_page']
                    sponsor_list += res_content['data']['list']
                else:
                    break

        curr_page += 1

    return json.dumps(sponsor_list, ensure_ascii=False)


if __name__ == '__main__':
    run_amiya(server.server.serve())
