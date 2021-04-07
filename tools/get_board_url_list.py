from functools import reduce
from html.parser import HTMLParser
from time import sleep
from urllib.request import Request, urlopen

sparrow_url = "https://stat.5ch.net/SPARROW/"
user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36"
sleep_time = 2
result_file = "board_list.txt"

server_url_list = []

board_url_list = []


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
        if self.is5ch:
            server_url_list.append("https://" + data.strip() + ".5ch.net/")
            self.is5ch = False
        elif self.isPink:
            server_url_list.append("https://" + data.strip() + ".bbspink.com/")
            self.isPink = False


with urlopen_fakeua(sparrow_url) as response:
    SPARROWParser().feed(response.read().decode())

print("Finish SPARROW crawl!")

print("All bbslist.txt crawling…")

for server_url in server_url_list:
    with urlopen_fakeua(server_url + "_service/bbslist.txt") as response:
        for board_dir in list(
            filter(None, [x.strip() for x in response.read().decode().split("\n")])
        ):
            board_url_list.append(server_url + board_dir + "/")

print("Finish all bbslist.txt crawl!")

print("Writing result…")

board_url_list.sort()
with open(result_file, "w") as file:
    file.write(
        reduce(lambda total, current: total + current + "\n", board_url_list, "")
    )

print("Finish write result!")

print("All finish!")
