#!/usr/bin/env python3
# Plotting comparisons of temerature from Gardens Meso2 and KCLL airport for AMS 2022
# Created 12 Janurary 2022 by Sam Gardner <stgardner4@tamu.edu>

import pandas as pd
from datetime import datetime as dt, timedelta
from matplotlib import pyplot as plt
from matplotlib.gridspec import GridSpec
from matplotlib import image as mpimage
from matplotlib import dates as mpdates
from metpy.units import units as mpunits

if __name__ == "__main__":
    kcll = pd.read_csv("KCLL.csv", comment="#")[1:]
    kcll["pydatetimes"] = [datetimestring[:-4] for datetimestring in kcll["Date_Time"]]
    kcll["pydatetimes"] = pd.to_datetime(kcll["pydatetimes"], format="%m/%d/%Y %H:%M")
    kcll = kcll.set_index(["pydatetimes"])
    kcll["air_temp_set_1"] = kcll["air_temp_set_1"].astype(float) * mpunits.degF
    kcll["firstCloudLayer"] = [cloudStr[-1] for cloudStr in kcll["cloud_layer_1_code_set_1"].fillna(1).astype(float).astype(int).astype(str)]
    kcll["firstCloudLayer"] = kcll["firstCloudLayer"].astype(int).replace(0, -.1).replace(1, 0).replace(2, .375).replace(3, .75).replace(4, 1).replace(5, -.1).replace(6, 0).replace(7, .375).replace(8, .75).replace(9, -1)
    kcll["secondCloudLayer"] = [cloudStr[-1] for cloudStr in kcll["cloud_layer_2_code_set_1"].fillna(1).astype(float).astype(int).astype(str)]
    kcll["secondCloudLayer"] = kcll["secondCloudLayer"].astype(int).replace(0, -.1).replace(1, 0).replace(2, .375).replace(3, .75).replace(4, 1).replace(5, -.1).replace(6, 0).replace(7, .375).replace(8, .75).replace(9, -1)
    kcll["thirdCloudLayer"] = [cloudStr[-1] for cloudStr in kcll["cloud_layer_3_code_set_1"].fillna(1).astype(float).astype(int).astype(str)]
    kcll["thirdCloudLayer"] = kcll["thirdCloudLayer"].astype(int).replace(0, -.1).replace(1, 0).replace(2, .375).replace(3, .75).replace(4, 1).replace(5, -.1).replace(6, 0).replace(7, .375).replace(8, .75).replace(9, -1)
    kcll["cloud_coverage"] = [max(kcll["firstCloudLayer"].iloc[i], kcll["secondCloudLayer"].iloc[i], kcll["thirdCloudLayer"].iloc[i]) for i in range(0, len(kcll.index))]
    startDate = kcll.index[0]
    startDate = dt(startDate.year, startDate.month, startDate.day, 0, 0, 0)
    endDate = kcll.index[-1]
    workingDate = dt(startDate.year, startDate.month, startDate.day, 17, 0, 0)

    gardens = pd.read_csv("Gardens Meso_Table10.dat", skiprows=1).dropna().iloc[1:].reset_index(drop=True)
    gardens["pydatetimes"] = pd.to_datetime(gardens["TIMESTAMP"], format="%Y-%m-%d %H:%M:%S", errors="coerce")
    gardens = gardens.set_index(["pydatetimes"])
    gardens["AvgAT"] = gardens["AvgAT"].astype(float)
    gardens["AvgAT"] = gardens["AvgAT"] * 1.8 * mpunits.degF + 32

    while (workingDate + timedelta(hours=14)) < endDate:
        dateStr = workingDate.strftime("%Y-%m-%d")
        print(dateStr)
        if workingDate > gardens.index[0] and workingDate < gardens.index[-1]:
            workingKcllData = kcll[workingDate:(workingDate + timedelta(hours=14))]
            workingGardensData = gardens[gardens.index > workingDate]
            workingGardensData = workingGardensData[workingGardensData.index < workingDate + timedelta(hours=14)]
            fig = plt.figure()
            gs = GridSpec(2, 1, figure=fig, height_ratios=[1,10])
            cloudAx = fig.add_subplot(gs[0,0])
            cloudAx.plot(workingKcllData.index, workingKcllData["cloud_coverage"])
            cloudAx.fill_between(workingKcllData.index, workingKcllData["cloud_coverage"])
            cloudAx.xaxis.set_major_formatter(mpdates.DateFormatter("%H:%M"))
            cloudAx.set_yticks([-0.1, 0, .375, .75, 1])
            cloudAx.set_yticklabels(["Missing", "Clear", "Scattered", "Broken", "Overcast"])
            cloudAx.set_ylim(-0.1, 1.01)
            cloudAx.set_ylabel("Cloud Coverage")
            cloudAx.set_position([cloudAx.get_position().x0, .98-cloudAx.get_position().height, cloudAx.get_position().width, cloudAx.get_position().height])
            ax = fig.add_subplot(gs[1,0])
            ax.plot(workingKcllData.index, workingKcllData["air_temp_set_1"], "red", label="KCLL")
            ax.scatter(workingKcllData.index, workingKcllData["air_temp_set_1"], s=1, c="red")
            ax.plot(workingGardensData.index, workingGardensData["AvgAT"], "blue", label="Meso2")
            ax.set_xlabel("Temperature (°F)")
            ax.scatter(workingGardensData.index, workingGardensData["AvgAT"], s=1, c="blue")
            ax.xaxis.set_major_formatter(mpdates.DateFormatter("%H:%M"))
            ax.set_yticks(range(25, 90, 5))
            ax.set_ylim([25, 90])
            ax.legend()
            ax.set_position([ax.get_position().x0, .90-(cloudAx.get_position().height+ax.get_position().height), ax.get_position().width, ax.get_position().height])
            tax = fig.add_axes([0,0,(ax.get_position().width/3),.05])
            tax.text(0.5, 0.5, "TAMU Mesonet Gardens and KCLL Temperature and Cloud Cover\nNight of "+dateStr, horizontalalignment="center", verticalalignment="center", fontsize=16)
            tax.axis("off")
            tax.set_position([(ax.get_position().width/2)-(tax.get_position().width/2)+ax.get_position().x0, ax.get_position().y0-.05-tax.get_position().height, tax.get_position().width, tax.get_position().height], which="both")
            lax = fig.add_axes([0,0,(ax.get_position().width/3),1])
            # The logo axes must have the same aspect ratio as the image we're trying to display or else the image will be stretched/compressed
            lax.set_aspect(2821/11071)
            # turn off the axis
            lax.axis("off")
            # turn off axis spines
            plt.setp(lax.spines.values(), visible=False)
            # read in the image
            atmoLogo = mpimage.imread("assets/atmoLogo.png")
            # show the image
            lax.imshow(atmoLogo)
            # We want the logo axes to be all the way to the right, and as low as possible without cutting anything off
            lax.set_position([.95-lax.get_position().width, ax.get_position().y0-.05-lax.get_position().height, lax.get_position().width, lax.get_position().height], which="both")            
            px = 1/plt.rcParams["figure.dpi"]
            fig.set_size_inches(1920*px, 1080*px)
            fig.savefig("output/"+dateStr.replace("-", "")+".png")
        workingDate = workingDate + timedelta(days=1)