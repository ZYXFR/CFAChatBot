import csv
import pandas as pd
from . import prompts, tc_utils
from datetime import datetime, timedelta

def load_patterns() -> list:
    patterns: list = []
    with open("data/classic_patterns.csv", encoding="utf-8") as _file:
        reader = csv.reader(_file, delimiter=",")
        for line in reader:
            patterns.append(line[0].strip().lower())
    return patterns

def load_assets() -> dict:
    assets: dict = {}
    with open('data/assets.csv', 'r') as data:
        for line in csv.DictReader(data):
            assets[line["name"]] = {
                "entity_id": line["entity_id"],
                "instrument_id": line["instrument_id"],
                "description": line["description"],
                "logo": line["logo"]
            }
    assets["General"] = {
        "entity_id": None,
        "instrument_id": None,
        "description": "Hello, I'm your helpful financial assistant. You can ask me general questions about finance and economy.",
        "logo": None,
    }
    return assets

def load_summaries_reports(assets, _api) -> dict:
    summaries: dict = {asset: [] for asset in assets}
    all_summaries = tc_utils.get_summaries(
        [assets[asset]["entity_id"] for asset in assets],
        "en",
        "paraphrase",
        _api
    )
    for sum in all_summaries:
        asset = sum["entity"]["name"]
        summaries[asset] = [info["content"] for info in sum["summaries"]]
    return summaries

def convert_str_to_markdown(text: str) -> str:
    text = text.replace("$", r"\$")
    text = text.replace("\n", "\n\n")
    return text

def split_events(events: list) -> tuple:
    classics, candlesticks, indicators, oscillators = [], [], [], []
    for event in events:
        if event["event class"] == "classic":
            classics.append(event)
        elif event["event class"] == "shortterm":
            candlesticks.append(event)
        elif event["event class"] == "indicator":
            indicators.append(event)
        elif event["event class"] == "oscillator":
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
    if "resistance40" in sup_res and "support40" in sup_res and sup_res["resistance40"] and sup_res["support40"]:
        sup_res_short["resistance40"] = sup_res["resistance40"]
        sup_res_short["support40"] = sup_res["support40"]
    if "resistance250" in sup_res and "support250" in sup_res and sup_res["resistance250"] and sup_res["support250"]:
        sup_res_intermediate["resistance250"] = sup_res["resistance250"]
        sup_res_intermediate["support250"] = sup_res["support250"]
    if "resistance500" in sup_res and "support500" in sup_res and sup_res["resistance500"] and sup_res["support500"]:
        sup_res_long["resistance500"] = sup_res["resistance500"]
        sup_res_long["support500"] = sup_res["support500"]
    return sup_res_short, sup_res_intermediate, sup_res_long
