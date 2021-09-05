import functools
import html.parser
import json
import time
import urllib.error
import urllib.parse
import urllib.request

user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36"


def urlopen_fakeua(url):
    time.sleep(2)
    print("Now crawl url: " + url)
    return urllib.request.urlopen(
        urllib.request.Request(url, headers={"User-Agent": user_agent})
    )


server_list = set()

# SPARROW


class SPARROWParser(html.parser.HTMLParser):
    def __init__(self):
        super().__init__()
        self.is5ch = False
        self.isPink = False

    def handle_starttag(self, tag, attrs):
        for attr in attrs:
            if attr[1] == "srv_2ch":
                self.is5ch = True
            elif attr[1] == "srv_pnk":
                self.isPink = True

    def handle_data(self, data):
        if self.is5ch:
            server_list.add(data.strip() + ".5ch.net")
            self.is5ch = False
        elif self.isPink:
            server_list.add(data.strip() + ".bbspink.com")
            self.isPink = False


with urlopen_fakeua("https://stat.5ch.net/SPARROW/") as response:
    SPARROWParser().feed(response.read().decode())

# bbsmenu.json

with urlopen_fakeua("https://menu.5ch.net/bbsmenu.json") as response:
    bbsmenu_json = json.loads(response.read())

for category in bbsmenu_json["menu_list"]:
    for content in category["category_content"]:
        server_list.add(urllib.parse.urlparse(content["url"]).hostname)

# Remove non-server URLs

for server in list(server_list):
    bbslist_url = "https://" + server + "/_service/bbslist.txt"
    try:
        with urlopen_fakeua(bbslist_url) as response:
            if response.url == bbslist_url:
                server_list.add(
                    (server, response.read().decode().strip().count("\n") + 1)
                )
    except urllib.error.HTTPError:
        pass
    server_list.remove(server)

# Print server list

server_list = list(server_list)
server_list.sort(key=lambda k: k[0])

print(",".join(map(lambda i: i[0], server_list)))
print(
    functools.reduce(
        lambda t, c: t + "|" + c[0] + "|" + str(c[1]) + "|\n", server_list, ""
    )
)
print("All board num: " + str(functools.reduce(lambda t, c: t + c[1], server_list, 0)))
