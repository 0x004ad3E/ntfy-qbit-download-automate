# ntfy-qbit-docker
docker compose for sending nfty notification and automatic download from qbitorrent

Prequisites:
* ntfy account or self hosting
* qbittorrent running on local network

Give a json file containing one or more entries like this
  {
    "feed": "http://example.com",
    "title": "Example video",
    "published": "Thu, 08 Oct 2026 21:04:56 +0000",
    "date": "2026-10-08",
    "topic_url": "http://someurl.com",
    "first_image": "http://someimage.com/file.jpg",
    "magnet_links": [
      "magnet:?xt=urn:whatever"
    ],
    "tags": "movies"
  }

  This program will parse the json file and send notifications to the ntfy channel.
  When the notification is received, clicking download will then cause qbittorrent to download the magnet link.

  Please update the following variables in the python file before use.
  
  * Folder where the json file is located - OUTPUT_DIR = Path("/output")
  * Name of the json file - JSON_FILE = OUTPUT_DIR / "results.json"
  * URL of the ntfy server - NTFY_SERVER = "https://ntfy.sh"
  * NTFY Channel - COMMAND_TOPIC = "scraper-command"
  * Authentication token for the ntfy server - NTFY_TOKEN = "tk_wkerjwekrjwer"
  * qbittorrent api key - QBIT_API_KEY = "qbt_434534srwerwer"
  * qbittorrent url - QBIT_URL="192.168.50.93:6520"
  * The program runs and exits.
  * So create a cron job to run it on schedule.
  * Note check the repository [1tamilmv](https://github.com/0x004ad3E/1tamilmv-rss-parser) for code to get json file

To run

    pip install --no-cache-dir -r requirements.txt

    python notifier.py

or use with the Dockerfile

    docker compose up --build
