import functools
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

servers = sys.argv[1].split(",")
user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36"


def urlopen_fakeua(url):
    time.sleep(2)
    print("Now crawl url: " + url)
    return urllib.request.urlopen(
        urllib.request.Request(url, headers={"User-Agent": user_agent})
    )


# bbslist.txt

board_url_list = set()

for server in servers:
    with urlopen_fakeua("https://" + server + "/_service/bbslist.txt") as response:
        for board_dir in response.read().decode().strip().split("\n"):
            board_url_list.add("https://" + server + "/" + board_dir + "/")

# bbsmenu.json

bbsmenu_board_url_list = set()

with urlopen_fakeua("https://menu.5ch.net/bbsmenu.json") as response:
    bbsmenu_json = json.loads(response.read())

for category in bbsmenu_json["menu_list"]:
    for content in category["category_content"]:
        if urllib.parse.urlparse(content["url"]).hostname in servers:
            bbsmenu_board_url_list.add(content["url"])

# Print hide boards

hide_boards = []

for hide_board in board_url_list - bbsmenu_board_url_list:
    try:
        with urlopen_fakeua(hide_board + "SETTING.TXT") as response:
            hide_boards.append(
                (
                    re.search(
                        r"BBS_TITLE=(.*)", response.read().decode("shift_jis")
                    ).groups()[0],
                    hide_board,
                )
            )
    except urllib.error.HTTPError:
        hide_boards.append(("SETTING.TXT error", hide_board))

hide_boards.sort(key=lambda k: k[1])

print(
    functools.reduce(
        lambda t, c: t + "|" + c[0] + "|<" + c[1] + ">|\n", hide_boards, ""
    )
)
