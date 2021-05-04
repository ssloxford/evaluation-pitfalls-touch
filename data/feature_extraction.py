import os
import sys
import csv
import pandas as pd
import numpy as np
import statistics
import math

from pingouin import circ_mean, circ_r
from collections import defaultdict
from pprint import pprint


def output_path(path):
    new_path_array = path.split("/")
    new_path_array[-2] = "features"
    new_path_array.pop()
    new_path_array.pop()
    new_path_array.append("features.csv")
    new_path_array = "/".join(new_path_array)

    return new_path_array


if __name__ == "__main__":
    sorted_folder = "data_files"

    userdata = pd.read_csv("tables/userdata.csv")

    cuuid = ""
    total = len(userdata.index)
    current = 0

    for subdir, dirs, files in os.walk(sorted_folder):
        for file in files:
            path = os.path.join(subdir, file)
            if path.split("/")[-1] == ".DS_Store":
                continue

            export_path = output_path(path)
            uuid = path.split("/")[-6]

            direction = path.split("/")[-4]

            if uuid != cuuid:
                cuuid = uuid
                current += 1
                sys.stdout.write("\rUser (%d/%d)" % (current, total))
                sys.stdout.flush()

            if path.split("/")[-2] != "touch_data":
                continue

            model = userdata.loc[userdata["uuid"] == uuid]["phone_model"].values[0]

            output = [
                [
                    "uuid",
                    "phone_model",
                    "measurement_id",
                    "gametype",
                    "iteration",
                    "swipe_counter",
                    "duration",
                    "startX",
                    "startY",
                    "stopX",
                    "stopY",
                    "distance",
                    "mean_result_len",
                    "pVel20",
                    "pVel50",
                    "pVel80",
                    "pAcc20",
                    "pAcc50",
                    "pAcc80",
                    "maxAbs",
                    "pDev20",
                    "pDev50",
                    "pDev80",
                    "avgDirection",
                    "dirEndToEnd,vdirFlag",
                    "trajectoryLength",
                    "dirLenTrajLenRatio",
                    "avgVelocity",
                    "medAccOver5",
                    "midPressure",
                    "midCover",
                    "direction",
                ]
            ]

            touch_data = []
            with open(path, encoding="utf-8") as touches:
                touchreader = csv.reader(touches, delimiter=",")
                order = next(touchreader)
                cnv = {}

                for i, o in enumerate(order):
                    cnv[o] = i

                single_touch = []

                for touch in touchreader:
                    if touch[cnv["type"]] == "2":
                        single_touch.append(
                            {
                                "pressure": touch[cnv["pressure"]],
                                "timestamp": touch[cnv["timestamp"]],
                                "y": touch[cnv["y"]],
                                "x": touch[cnv["x"]],
                                "area": touch[cnv["area"]],
                            }
                        )

                        touch_data.append(single_touch)
                        single_touch = []
                    else:
                        single_touch.append(
                            {
                                "pressure": touch[cnv["pressure"]],
                                "timestamp": touch[cnv["timestamp"]],
                                "y": touch[cnv["y"]],
                                "x": touch[cnv["x"]],
                                "area": touch[cnv["area"]],
                            }
                        )

            size = width, height = 0, 0
            multiplierX = 1
            multiplierY = 1

            if model in ["iPhone 6s Plus", "iPhone 7 Plus", "iPhone 8 Plus"]:
                multiplierX = 1
                multiplierY = 1
                size = width, height = 1080, 1920
            elif model in ["iPhone 6s", "iPhone 7", "iPhone 8"]:
                size = width, height = 750, 1334
                multiplierX = 1.44
                multiplierY = 1.44
            elif model in ["iPhone X", "iPhone XS"]:
                size = width, height = 1125, 2436
                multiplierX = 0.96
                multiplyerY = 0.7882
            elif model in ["iPhone XS Max"]:
                size = width, height = 1242, 2688
                multiplierX = 0.8696
                multiplyerY = 0.7143
            else:
                print(model)

            swipe_counter = 0

            for touch in touch_data:
                swipeCounts = []
                percentails = [20, 50, 80]
                temp = touch
                swipe_count = len(temp)
                midX = []
                midY = []

                for t in temp:
                    t["x"] = multiplierX * float(t["x"])
                    t["y"] = multiplierY * float(t["y"])

                for t in temp:
                    midX.append(float(t["x"]))
                    midY.append(float(t["y"]))

                if (statistics.stdev(midX) < 5 and statistics.stdev(midY) < 5) or len(
                    touch
                ) < 3:
                    continue
                else:
                    duration = int(
                        float(temp[-1]["timestamp"]) - float(temp[0]["timestamp"])
                    )
                    startX = float(temp[0]["x"])
                    startY = float(temp[0]["y"])
                    stopX = float(temp[-1]["x"])
                    stopY = float(temp[-1]["y"])
                    distance = math.sqrt((startX - stopX) ** 2 + (startY - stopY) ** 2)

                    xDisp = []
                    yDisp = []
                    tDelta = []

                    tPrev = temp[0]
                    for i, t in enumerate(temp):
                        if i != 0:
                            xDisp.append(float(t["x"]) - float(tPrev["x"]))
                            yDisp.append(float(t["y"]) - float(tPrev["y"]))
                            tDelta.append(
                                int(float(t["timestamp"]) - float(tPrev["timestamp"]))
                            )
                            tPrev = t

                    angl = []
                    v = []
                    pairwDist = []

                    for i in range(len(xDisp)):
                        angl.append(math.atan2(yDisp[i], xDisp[i]))
                        pairwDist.append(math.sqrt(xDisp[i] ** 2 + yDisp[i] ** 2))
                        if tDelta[i] == 0:
                            v.append(0)
                        else:
                            v.append(
                                math.sqrt(xDisp[i] ** 2 + yDisp[i] ** 2) / tDelta[i]
                            )

                    pVel = np.percentile(v, percentails, interpolation="midpoint")
                    pVel20 = pVel[0]
                    pVel50 = pVel[1]
                    pVel80 = pVel[2]

                    mean_result_len = circ_r(np.array(angl))

                    a = []
                    vPrev = v[0]
                    for i, vTemp in enumerate(v):
                        if i != 0:
                            if tDelta[i] == 0:
                                a.append(0)
                            else:
                                a.append((vTemp - vPrev) / tDelta[i])
                            vPrev = vTemp

                    pAcc = np.percentile(a, percentails, interpolation="midpoint")
                    pAcc20 = pAcc[0]
                    pAcc50 = pAcc[1]
                    pAcc80 = pAcc[2]

                    medianVel3Points = statistics.median(v[-3:])

                    xVek = []
                    yVek = []

                    xv = float(temp[0]["x"])
                    yv = float(temp[0]["y"])
                    for t in temp:
                        xVek.append(float(t["x"]) - xv)
                        yVek.append(float(t["y"]) - yv)

                    perVek = np.cross([xVek[-1], yVek[-1], 0], [0, 0, 1])

                    for i, p in enumerate(perVek):
                        perVek[i] = perVek[i] / math.sqrt(
                            perVek[0] * perVek[0] + perVek[1] * perVek[1]
                        )

                    projectOnPrepStraight = []

                    for i in range(len(xVek)):
                        projectOnPrepStraight.append(
                            xVek[i] * perVek[0] + yVek[i] * perVek[1]
                        )

                    maxAbs = -1

                    for proj in projectOnPrepStraight:
                        if abs(proj) > maxAbs:
                            maxAbs = abs(proj)

                    pDev = np.percentile(
                        projectOnPrepStraight, percentails, interpolation="midpoint"
                    )
                    pDev20 = pDev[0]
                    pDev50 = pDev[1]
                    pDev80 = pDev[2]

                    avgDirection = circ_mean(angl)
                    dirEndToEnd = math.atan2(stopY - startY, stopX - startX)

                    tmpangle = dirEndToEnd + math.pi
                    # dirFlag = 0

                    if tmpangle <= math.pi / 4:
                        dirFlag = 4
                    elif tmpangle > math.pi / 4 and tmpangle <= 5 * math.pi / 4:
                        if tmpangle < 3 * math.pi / 4:
                            dirFlag = 1
                        else:
                            dirFlag = 2
                    else:
                        if tmpangle < 7 * math.pi / 4:
                            dirFlag = 3
                        else:
                            dirFlag = 4

                    trajectoryLength = sum(pairwDist)

                    dirLenTrajLenRatio = distance / trajectoryLength

                    avgVelocity = trajectoryLength / duration

                    medAccOver5 = statistics.median(a[:5])

                    pressure = []
                    area = []

                    for t in temp:
                        pressure.append(float(t["pressure"]))
                        area.append(float(t["area"]))

                    midPressure = statistics.median(
                        pressure[
                            math.floor(len(pressure) / 2)
                            - 1 : math.ceil(len(pressure) / 2)
                        ]
                    )
                    midCover = statistics.median(
                        area[math.floor(len(area) / 2) - 1 : math.ceil(len(area) / 2)]
                    )

                    dir = ""

                    if direction == "swipe":
                        if startX - stopX > 0:
                            dir = "left"
                        else:
                            dir = "right"
                    elif direction == "scroll":
                        if startY - stopY > 0:
                            dir = "up"
                        else:
                            dir = "down"

                    swipeFeatures = [
                        duration,
                        startX,
                        startY,
                        stopX,
                        stopY,
                        distance,
                        mean_result_len,
                        pVel20,
                        pVel50,
                        pVel80,
                        pAcc20,
                        pAcc50,
                        pAcc80,
                        maxAbs,
                        pDev20,
                        pDev50,
                        pDev80,
                        avgDirection,
                        dirEndToEnd,
                        dirFlag,
                        trajectoryLength,
                        dirLenTrajLenRatio,
                        avgVelocity,
                        medAccOver5,
                        midPressure,
                        midCover,
                        dir,
                    ]
                    swipeFeatures.insert(0, swipe_counter)
                    swipeFeatures.insert(0, path.split("/")[-3])
                    swipeFeatures.insert(0, path.split("/")[-4])
                    swipeFeatures.insert(0, path.split("/")[-5])
                    swipeFeatures.insert(0, model)
                    swipeFeatures.insert(0, path.split("/")[-6])

                    output.append(swipeFeatures)
                    swipe_counter += 1

            os.makedirs(os.path.dirname(export_path), exist_ok=True)
            f = open(export_path, "w+")
            for o in output:
                f.write(",".join(str(e) for e in o) + "\n")

            f.close()

    features_folder = "data_files"
    export_path = "features.csv"

    if os.path.exists(export_path):
        os.remove(export_path)

    f_export = open(export_path, "a+")

    userdata = pd.read_csv("tables/userdata.csv")

    cuuid = ""
    total = len(userdata.index)
    current = 0
    t_first = True

    for subdir, dirs, files in os.walk(features_folder):
        for file in files:
            path = os.path.join(subdir, file)
            if path.split("/")[-1] != "features.csv":
                continue

            uuid = path.split("/")[-5]

            if uuid != cuuid:
                cuuid = uuid
                current += 1
                sys.stdout.write("\rUser (%d/%d)" % (current, total))
                sys.stdout.flush()

            first = True
            with open(path, encoding="utf-8") as f:
                for line in f:
                    if first:
                        first = False
                        if t_first:
                            f_export.write(line)
                            t_first = False
                    else:
                        f_export.write(line)

    f_export.close()
