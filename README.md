# ntfy-qbit-docker
docker compose for sending nfty notification and automatic download from qbitorrent

Prequisites:
* ntfy
* qbittorrent


--------------------------------------------
Give a json file containing one or more entries like this

```json
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
  ```

  This program will parse the json file and send notifications to the ntfy channel.
  When the notification is received, clicking download will then cause qbittorrent to download the magnet link.

  Please update the following variables in the python file before use.
  
  * Folder where the json file is located - OUTPUT_DIR = Path("/output")
  * Name of the json file - JSON_FILE = OUTPUT_DIR / "results.json"
  * Set environment variables in .env file or update variables for the following in the python code
    * NTFY_SERVER=os.environ.get("NTFY_SERVER", "your-dummy-value")
    * NOTIFY_TOPIC = os.environ.get("NOTIFY_TOPIC", "your-dummy-value")
    * COMMAND_TOPIC = os.environ.get("COMMAND_TOPIC", "your-dummy-value")
    * NTFY_TOKEN = os.environ.get("NTFY_TOKEN", "your-dummy-value")
    * QBIT_API_KEY = os.environ.get("QBIT_API_KEY", "your-dummy-value")
    * QBIT_URL=os.environ.get("QBIT_URL", "your-dummy-value")
  * The program runs and exits.
  * So create a cron job to run it on schedule.
  * Note: check the repository [1tamilmv-rss-parser](https://github.com/0x004ad3E/1tamilmv-rss-parser) for code to get json file

To run

    pip install --no-cache-dir -r requirements.txt

    python notifier.py

or use with the Dockerfile

    docker compose up --build
