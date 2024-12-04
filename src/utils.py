import csv
import datetime
import os
import time
from typing import Generator

import nltk

nltk.download("punkt_tab")


def load_assets() -> dict:
    assets: dict = {}
    with open("src/data/assets.csv", "r") as data:
        for line in csv.DictReader(data):
            assets[line["name"]] = {
                "entity_id": line["entity_id"],
                "instrument_id": line["instrument_id"],
                "ticker": line["ticker"],
                "description": line["description"],
                "logo": line["logo"],
            }
    return assets


def split_events(events: list, oscillators_value: dict) -> tuple:
    classics, candlesticks, indicators, oscillators = [], [], [], []
    for event in events:
        if event["event class"] == "classic":
            classics.append(event)
        elif event["event class"] == "shortterm":
            candlesticks.append(event)
        elif event["event class"] == "indicator":
            indicators.append(event)
        elif event["event class"] == "oscillator":
            for ov in oscillators_value:
                if ov in event["event"].lower():
                    event[f"value of {event['event']}"] = oscillators_value[ov]
            oscillators.append(event)
    return classics, candlesticks, indicators, oscillators


def split_smas(sma: dict) -> tuple:
    sma_short, sma_intermediate = {}, {}
    if "sma4" in sma and sma["sma4"]:
        sma_short["sma4"] = sma["sma4"]
    if "sma9" in sma and sma["sma9"]:
        sma_short["sma9"] = sma["sma9"]
    if "sma21" in sma and sma["sma21"]:
        sma_short["sma21"] = sma["sma21"]
    if "sma50" in sma and sma["sma50"]:
        sma_intermediate["sma50"] = sma["sma50"]
    if "sma200" in sma and sma["sma200"]:
        sma_intermediate["sma200"] = sma["sma200"]
    return sma_short, sma_intermediate


def split_sup_res(sup_res: dict) -> tuple:
    sup_res_short, sup_res_intermediate, sup_res_long = {}, {}, {}
    if (
        "resistance40" in sup_res
        and "support40" in sup_res
        and sup_res["resistance40"]
        and sup_res["support40"]
    ):
        sup_res_short["resistance40"] = sup_res["resistance40"]
        sup_res_short["support40"] = sup_res["support40"]
    if (
        "resistance250" in sup_res
        and "support250" in sup_res
        and sup_res["resistance250"]
        and sup_res["support250"]
    ):
        sup_res_intermediate["resistance250"] = sup_res["resistance250"]
        sup_res_intermediate["support250"] = sup_res["support250"]
    if (
        "resistance500" in sup_res
        and "support500" in sup_res
        and sup_res["resistance500"]
        and sup_res["support500"]
    ):
        sup_res_long["resistance500"] = sup_res["resistance500"]
        sup_res_long["support500"] = sup_res["support500"]
    return sup_res_short, sup_res_intermediate, sup_res_long


def stream_data(text: str) -> Generator:
    for word in text.split(" "):
        yield word + " "
        time.sleep(0.005)


def save_data(
    _input: str,
    _output: str,
    assistant_type: str,
    analyzer_type: str,
    llm_type: str,
    asset: str,
) -> None:
    day = datetime.datetime.now().strftime("%Y-%m-%d")
    _datetime = datetime.datetime.now().strftime("%Y-%m-%d_%H:%M:%S:%s")
    llm_type = llm_type.split("/")[-1]
    if not os.path.exists(
        f"logs/{day}/{llm_type}/{assistant_type}/{analyzer_type}/inputs"
    ):
        os.makedirs(f"logs/{day}/{llm_type}/{assistant_type}/{analyzer_type}/inputs/")
        os.makedirs(f"logs/{day}/{llm_type}/{assistant_type}/{analyzer_type}/outputs/")
    with open(
        f"logs/{day}/{llm_type}/{assistant_type}/{analyzer_type}/inputs/{llm_type}-{asset}-{_datetime}.input",
        "w",
    ) as _file:
        _file.write(_input)
    with open(
        f"logs/{day}/{llm_type}/{assistant_type}/{analyzer_type}/outputs/{llm_type}-{asset}-{_datetime}.output",
        "w",
    ) as _file:
        _file.write(_output)


def convert_str_to_markdown(text: str) -> str:
    text = text.replace("$", "\$")  # noqa: W605
    return text


def clean_string_to_tts(text: str) -> str:
    char_to_remove: list = ["#", "*"]
    for char in char_to_remove:
        text = text.replace(char, "")
    return text


def normalize_asset_name(asset: str) -> str:
    # Replace special caracter %20 by ' '
    return asset.replace("%20", " ")
