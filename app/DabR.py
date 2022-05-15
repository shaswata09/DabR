import csv
import pickle
import random

import gensim
import numpy as np
import requests

# Data files are not added due to confidentiality reasons.
# goodIP_file_path = "/home/shaswata/Desktop/DabR/data/good_IP_data.csv"
# badIP_file_path = "/home/shaswata/Desktop/DabR/data/bad_IP_data.csv"

badIpOriginPath = "./badIpOrigin.pkl"
ipAttributeDictPath = "./ipAttributes.pkl"


def read_data():
    with open(goodIP_file_path, encoding="ISO-8859-1", newline="") as f:
        reader = csv.reader(f)
        goodIpList = list(reader)
    with open(badIP_file_path, encoding="ISO-8859-1", newline="") as f:
        reader = csv.reader(f)
        badIpList = list(reader)
    ipAttributeList = goodIpList[
        0
    ]  # ['ip_address', 'city.names.en', 'subdivisions.names.en', 'country.iso_code', 'registered_country.iso_code', 'traits.user_type', 'traits.asn', 'traits.isp']
    goodIpList = goodIpList[1:]
    badIpList = badIpList[1:]
    return goodIpList, badIpList


def list_splitter(list_to_split, ratio):
    elements = len(list_to_split)
    middle = int(elements * ratio)
    return [list_to_split[:middle], list_to_split[middle:]]


def generate_dataset(goodIpList, badIpList):
    goodIpTrainList, goodIpTestList = list_splitter(goodIpList, 0.75)
    badIpTrainList, badIpTestList = list_splitter(badIpList, 0.75)
    return goodIpTrainList, goodIpTestList, badIpTrainList, badIpTestList


def process_data(goodIpTrainList, badIpTrainList):

    attributeDict = [{}, {}, {}, {}, {}, {}, {}]

    for i in goodIpList:
        for j in range(1, 8):
            if i[j] not in attributeDict[j - 1].keys():
                attributeDict[j - 1][i[j]] = 0

    for i in badIpList:
        for j in range(1, 8):
            if i[j] not in attributeDict[j - 1].keys():
                attributeDict[j - 1][i[j]] = 1 / (len(goodIpList) + len(badIpList))
            else:
                attributeDict[j - 1][i[j]] = attributeDict[j - 1][i[j]] + 1 / (
                    len(goodIpList) + len(badIpList)
                )

    return attributeDict


def get_bad_ip_origin(attributeDict):
    maxBadIpVector = [0, 0, 0, 0, 0, 0, 0]
    indx = 0

    for i in attributeDict:
        maxBadIpVector[indx] = max(i.values())
        indx += 1

    return maxBadIpVector


def getIpVector(ipAttrubute, attributeDict):
    ipVector = [0, 0, 0, 0, 0, 0, 0]
    indx = 0
    for i in ipAttrubute:
        try:
            ipVector[indx] = attributeDict[indx][i]
        except:
            ipVector[indx] = 0
        indx += 1
    return ipVector


def getReputationScore(ipAttrubute, maxBadIpVector, attributeDict):
    ed = np.linalg.norm(
        np.array(getIpVector(ipAttrubute, attributeDict))
        - np.array([0, 0, 0, 0, 0, 0, 0])
    )
    # print(ed)

    edMax = np.linalg.norm(np.array(maxBadIpVector) - np.array([0, 0, 0, 0, 0, 0, 0]))
    # print(edMax)

    dabrScore = (1 - (ed / edMax)) * 10

    return dabrScore


def check_accuracy(goodIpTestList, badIpTestList, maxBadIpVector):
    ipClassifyResult = []

    for i in goodIpTestList:
        score = getReputationScore(i[1:], maxBadIpVector)
        if score > 6:
            ipClassifyResult.append(1)
        else:
            ipClassifyResult.append(0)

    for i in badIpTestList:
        score = getReputationScore(i[1:], maxBadIpVector)
        if score > 6:
            ipClassifyResult.append(0)
        else:
            ipClassifyResult.append(1)

    return sum(ipClassifyResult) / len(ipClassifyResult)


def saveBadIpOrigin(maxBadIpVector):
    with open(badIpOriginPath, "wb") as f:
        pickle.dump(maxBadIpVector, f)


def saveAttributeDict(attributeDict):
    with open(ipAttributeDictPath, "wb") as f:
        pickle.dump(attributeDict, f)


def readBadIpOrigin():
    with open(badIpOriginPath, "rb") as f:
        maxBadIpVector = pickle.load(f)
    return maxBadIpVector


def readIpAttributes():
    with open(ipAttributeDictPath, "rb") as f:
        attributeDict = pickle.load(f)
    return attributeDict


def getAsnValue(asn):
    asn = asn.split()[0][2:]
    return asn


def getIpAttributes(ip):
    ipAttribute = ["", "", "", "", "", "", "", ""]
    ipAttribute[0] = ip

    # Paste ipinfo token in the below url
    ipAsnUrl = f"https://ipinfo.io/{ip}/?token=<ipinfo token>"
    ipAsnResponse = requests.get(ipAsnUrl).json()

    ipAttribute[1] = ipAsnResponse["city"]
    ipAttribute[2] = ipAsnResponse["region"]
    ipAttribute[3] = ipAsnResponse["country"]
    ipAttribute[4] = ipAsnResponse["country"]

    # All IP are considered as residential. It can be explicitly obtained and changed.
    ipAttribute[5] = "residential"
    ipAttribute[6] = getAsnValue(ipAsnResponse["org"])
    ipAttribute[7] = ipAsnResponse["org"].split(" ", 1)[1]

    return ipAttribute


def getIpReputation(ip):
    maxBadIpVector = readBadIpOrigin()
    attributeDict = readIpAttributes()

    # print(maxBadIpVector)
    ipAttrubute = getIpAttributes(ip)
    # print(ipAttrubute)
    repScore = getReputationScore(ipAttrubute[1:], maxBadIpVector, attributeDict)
    # print(repScore)
    return repScore


if __name__ == "__main__":
    # goodIpList, badIpList = read_data()
    # goodIpTrainList, goodIpTestList, badIpTrainList, badIpTestList = generate_dataset(
    #     goodIpList, badIpList
    # )
    # attributeDict = process_data(goodIpTrainList, badIpTrainList)
    # maxBadIpVector = get_bad_ip_origin(attributeDict)
    # saveBadIpOrigin(maxBadIpVector)
    # saveAttributeDict(attributeDict)
    # print(maxBadIpVector)
    # print(readBadIpOrigin())
    # print(check_accuracy(goodIpTestList, badIpTestList, maxBadIpVector))

    # maxBadIpVector = readBadIpOrigin()
    # attributesDict = readIpAttributes()

    print(getIpReputation("39.40.195.174"))
