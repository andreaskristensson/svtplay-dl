# ex:ts=4:sw=4:sts=4:et
# -*- tab-width: 4; c-basic-offset: 4; indent-tabs-mode: nil -*-
from __future__ import absolute_import
import sys
import re
import json

from svtplay.utils import get_http_data, select_quality
from svtplay.log import log
from svtplay.rtmp import download_rtmp

class Kanal5():
    def handle(self, url):
        return ("kanal5play.se" in url) or ('kanal9play.se' in url)

    def get(self, options, url):
        match = re.search(".*video/([0-9]+)", url)
        if not match:
            log.error("Can't find video file")
            sys.exit(2)
        url = "http://www.kanal5play.se/api/getVideo?format=FLASH&videoId=%s" % match.group(1)
        data = json.loads(get_http_data(url))
        options.live = data["isLive"]
        steambaseurl = data["streamBaseUrl"]
        if data["hasSubtitle"]:
            subtitle = "http://www.kanal5play.se/api/subtitles/%s" % match.group(1)
        streams = {}

        for i in data["streams"]:
            stream = {}
            stream["source"] = i["source"]
            streams[int(i["bitrate"])] = stream

        test = select_quality(options, streams)

        filename = test["source"]
        match = re.search("^(.*):", filename)
        options.output  = "%s.%s" % (options.output, match.group(1))
        options.other = "-W %s -y %s " % ("http://www.kanal5play.se/flash/StandardPlayer.swf", filename)
        download_rtmp(options, steambaseurl)
        if options.subtitle:
            if options.output != "-":
                data = get_http_data(subtitle)
                subtitle_json(options, data)
