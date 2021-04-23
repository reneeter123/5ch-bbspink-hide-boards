from functools import reduce
from html.parser import HTMLParser
from time import sleep
from urllib.error import HTTPError
from urllib.request import Request, urlopen

sparrow_url = "https://stat.5ch.net/SPARROW/"
user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36"
sleep_time = 2
result_file = "tatesugi_list.txt"

server_url_list = []

board_url_list = []

tatesugi_list = []

error_board_url_list = []


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

print("All SETTING.TXT crawling…")

for board_url in board_url_list:
    append_tatesugi = {"tatesugi": "", "name": "", "url": board_url}
    try:
        with urlopen_fakeua(board_url + "SETTING.TXT") as response:
            for setting_line in response.read().decode("shift_jis").split("\n"):
                if setting_line.startswith("BBS_TITLE="):
                    append_tatesugi["name"] = setting_line.removeprefix("BBS_TITLE=")
                elif setting_line.startswith("BBS_THREAD_TATESUGI="):
                    append_tatesugi["tatesugi"] = setting_line.removeprefix(
                        "BBS_THREAD_TATESUGI="
                    )
    except HTTPError as error:
        print(
            "ERROR : Could not get SETTING.TXT. Error code : "
            + str(error.code)
            + " Skip this board."
        )
        error_board_url_list.append(board_url)
    tatesugi_list.append(append_tatesugi)

print("Finish all SETTING.TXT crawl!")

print("Writing result…")


def sort_list(x):
    try:
        sort_value = int(x["tatesugi"])
    except ValueError:
        sort_value = 99999
    return sort_value


tatesugi_list.sort(key=sort_list)
result = reduce(
    lambda total, current: total
    + "|"
    + current["tatesugi"]
    + "|"
    + current["name"]
    + "|<"
    + current["url"]
    + ">|\n",
    tatesugi_list,
    "",
)
result += "\nError board url list : " + str(error_board_url_list)
with open(result_file, "w") as file:
    file.write(result)

print("Finish write result!")

print("All finish!")
