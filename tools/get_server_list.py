from functools import reduce
from html.parser import HTMLParser
from time import sleep
from urllib.request import Request, urlopen

sparrow_url = "https://stat.5ch.net/SPARROW/"
user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36"
sleep_time = 2
result_file = "server_list.txt"

server_list = []


def urlopen_fakeua(url):
    sleep(sleep_time)
    print("Now crawl url : " + url)
    return urlopen(Request(url, headers={"User-Agent": user_agent}))


print("SPARROW crawling…")


class SPARROWParser(HTMLParser):
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
        if self.is5ch or self.isPink:
            append_server = {"name": data.strip(), "url": "", "board_num": 0}
            if self.is5ch:
                append_server["url"] = "https://" + append_server["name"] + ".5ch.net/"
                self.is5ch = False
            elif self.isPink:
                append_server["url"] = (
                    "https://" + append_server["name"] + ".bbspink.com/"
                )
                self.isPink = False
            server_list.append(append_server)


with urlopen_fakeua(sparrow_url) as response:
    SPARROWParser().feed(response.read().decode())

server_list.sort(key=lambda x: x["name"])

print("Finish SPARROW crawl!")

print("All bbslist.txt crawling…")

for index, server in enumerate(server_list):
    with urlopen_fakeua(server["url"] + "_service/bbslist.txt") as response:
        server_list[index]["board_num"] = len(
            list(
                filter(None, [x.strip() for x in response.read().decode().split("\n")])
            )
        )

print("Finish all bbslist.txt crawl!")

print("Writing result…")

result = reduce(
    lambda total, current: total
    + "|"
    + current["name"]
    + "|<"
    + current["url"]
    + ">|"
    + str(current["board_num"])
    + "|\n",
    server_list,
    "",
)
result += "\nAll board num : " + str(
    reduce(lambda total, current: total + current["board_num"], server_list, 0)
)
with open(result_file, "w") as file:
    file.write(result)

print("Finish write result!")

print("All finish!")
