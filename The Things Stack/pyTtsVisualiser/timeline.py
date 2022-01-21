# %%
from os import sep
import sys
import datetime
import argparse
import matplotlib.pyplot as plt
import numpy as np
import json
import pandas as pd
import requests
import secrets

from requests.exceptions import HTTPError

inputPath = None
mmToGround = 2190
# argparser = argparse.ArgumentParser(description="Graph snow measurements.")
# argparser.add_argument("--file", nargs='?', type=str, help="path to file containing json list of measurements")
# args = argparser.parse_args()
# inputPath = args.file

if inputPath is not None:
    snowmonitorDataFrame = pd.read_json(inputPath)
else:
    # Call api
    try:
        secrets = secrets.Secrets()
        response = requests.get(secrets.dataApiUrl,
            headers={'Accept': 'text/event-stream', 'Authorization': secrets.authorizationKey}, 
            params={'last': '48h'})
        response.raise_for_status()
        measurementsAsJsonList = []
        ndjson = response.content.decode().split("\n\n")
    except HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')
        exit()

    # Initialise a figure. subplots() with no args gives one plot.
    fig, axs = plt.subplots(sharex="all", sharey="all")

    for jsonObj in ndjson:
            if jsonObj:
                measurementsAsJsonList.append(json.loads(jsonObj))

    snowmonitorDataFrame = pd.json_normalize(measurementsAsJsonList, sep='_')
    # print(snowmonitorDataFrame.head())
    distanceDf = snowmonitorDataFrame[snowmonitorDataFrame.result_uplink_message_decoded_payload_distance > 1000][snowmonitorDataFrame.result_uplink_message_decoded_payload_distance < mmToGround+100]
    distanceDf["snowdepth"] = mmToGround - distanceDf["result_uplink_message_decoded_payload_distance"]
    distanceDf["datetime"] = pd.to_datetime(distanceDf["result_received_at"])
    #print(distanceDf.head())

    groupedByDeviceIdDf = distanceDf[["result_end_device_ids_device_id", "snowdepth", "result_uplink_message_decoded_payload_temperaturec", "datetime"]].groupby("result_end_device_ids_device_id")
    # print(groupedByDeviceIdDf.head())

    for name, group in groupedByDeviceIdDf:
        group.plot(x="datetime", y="snowdepth", ax=axs, label=str("%s: Distance" % (name)))
        #group.plot(x="datetime", y="tempc2", ax=axs, label=str("%s: Temp 2" % (name)))

    timespan = distanceDf["datetime"].max() - distanceDf["datetime"].min()
    # print(timespan)

    hours, remainder = divmod(timespan.total_seconds(), 3600)
    minutes, seconds = divmod(remainder, 60)

    axs.set_title(str("Snow last %dH, %dM" % (hours, minutes)))
    plt.xlabel("Hour of day")
    plt.ylabel("Distance to surface")
    plt.legend()

    # Ask Matplotlib to show the plot
    plt.show()
    # %%
