import os
import glob
import pandas as pd
import numpy as np
import ezdxf
import tkinter
import tkinter.filedialog
from tkinter import messagebox
from tkinter.filedialog import askopenfilename

os.remove("file.py")


def description():

    os.chdir(dir_path)

    sag_inlets = [
        "DI-2C",
        "DI-2CC",
        "DI-3C",
        "DI=3CC",
        "DI-4C",
        "DI-4CC",
        "DI-10I",
        "DI-10L",
    ]
    grate_inlets = [
        "DI-1",
        "DI-7",
        "DI-5",
        "DI-10H",
        "DI-10K",
        "DI-10G",
        "DI-10J",
        "DI-10L",
        "DI-10I",
    ]

    grade_inlets = [
        "DI-2B",
        "DI-2BB",
        "DI-3B",
        "DI=3BB",
        "DI-4B",
        "DI-4BB",
        "DI-10H",
        "DI-10K",
    ]

    outlet_strs = ["ES-1", "EW-1", "EW-2"]

    fixed_inlets = [
        "DI-2A",
        "DI-2AA",
        "DI-3A",
        "DI-3AA",
        "DI-4A",
        "DI-4AA",
        "DI-1",
        "DI-5",
        "DI-7",
        "DI-10J",
        "DI-10G",
    ]

    Str_list = [
        "DI-2C",
        "DI-2CC",
        "DI-3C",
        "DI=3CC",
        "DI-4C",
        "DI-4CC",
        "DI-10I",
        "DI-10L",
        "DI-2B",
        "DI-2BB",
        "DI-3B",
        "DI=3BB",
        "DI-4B",
        "DI-4BB",
        "DI-10H",
        "DI-10K",
        "ES-1",
        "EW-2",
        "EW-1",
        "MH-12",
        "DI-2A",
        "DI-2AA",
        "DI-3A",
        "DI-3AA",
        "DI-4A",
        "DI-4AA",
        "DI-1",
        "DI-5",
        "DI-7",
        "DI-10J",
        "DI-10G",
    ]

    df = pd.read_csv(f, sep="\t")

    # cleaning file for dataframe

    df = df.replace("<None>", "")
    df.columns = df.columns.str.replace("ft", "")
    df.columns = df.columns.str.replace("(", "")
    df.columns = df.columns.str.replace(")", "")
    df.columns = df.columns.str.replace("/", "")
    df.columns = df.columns.str.replace("in", "")
    df.columns = df.columns.str.replace("\\n", "")

    idx = df[df["NBT"] == "Outlet"].index[0]
    df_1 = df.iloc[: idx + 1, :]
    df_2 = df.iloc[idx + 1 :, :]
    df_1 = df_1.loc[:, :"NBT"]
    df_2.reset_index(drop=True, inplace=True)
    df_2 = df_2.loc[:, "Start Node":]

    df = pd.merge(df_1, df_2, left_on="Label", right_on="Start Node", how="left").drop(
        "Start Node", axis=1
    )

    df["Str Desc."] = (
        df["ES Desc."].astype(str)
        + df["Inlet Desc."].astype(str)
        + df["MH Desc."].astype(str)
    )

    df["Str Desc."] = df["Str Desc."].str.replace("nan", "")

    df = df.drop(columns=["ES Desc.", "Inlet Desc.", "MH Desc."])

    df = df.rename({"Label": "Start Node"}, axis=1)

    cols = list(df)

    cols.insert(1, cols.pop(cols.index("Stop Node")))

    df = df.loc[:, cols]

    df["Cover"] = df[["Cover Start", "Cover Stop"]].max(axis=1)

    df = df.drop(columns=["Cover Start", "Cover Stop"])

    df["Str."] = [
        " ".join(y for y in x.split() if y in Str_list) for x in df["Str Desc."]
    ]

    df = df.drop(columns=["Str Desc."])

    # Sorting in ascending order and converting to numbers

    df["Ground Elev"] = pd.to_numeric(df["Ground Elev"], errors="coerce")

    df["Invert In"] = pd.to_numeric(df["Invert In"], errors="coerce")

    df["Invert Out"] = pd.to_numeric(df["Invert Out"], errors="coerce")

    df["Slot Length"] = pd.to_numeric(df["Slot Length"], errors="coerce")

    df["Pipe Length"] = pd.to_numeric(df["Pipe Length"], errors="coerce")

    # calculations

    df = df.sort_values(["Start Node"], ascending=[True])

    df.reset_index(drop=True, inplace=True)

    m = len(df.index)

    for i in range(0, m, 1):

        if df.at[i, "Str."] in grate_inlets:

            df.at[i, "Top Elev"] = df.at[i, "Ground Elev"]

        else:

            df.at[i, "Top Elev"] = df.at[i, "Ground Elev"] + 0.5

    for i in range(0, m, 1):

        if df.at[i, "Str."] == "MH-12":

            df.at[i, "Str."] = "MH"

    df["Height"] = df["Top Elev"] - df["Invert In"]

    df["MH Height"] = df["Height"] - 8 / 12

    # writing in dxf file

    dwg = ezdxf.new(dxfversion="R2013", setup=True)

    msp = dwg.modelspace()

    dwg.layers.new(name="Text", dxfattribs={"color": 130})

    dwg.layers.new(name="Structure", dxfattribs={"color": 130})

    for i in range(0, m, 1):

        if df.at[i, "Str."] in fixed_inlets:

            secondline = (
                "H="
                + "%.1f" % df.at[i, "Height"]
                + "'"
                + " INV="
                + "%.2f" % df.at[i, "Invert In"]
            )

        elif df.at[i, "Str."] in outlet_strs:

            for j in range(0, m, 1):

                if df.at[i, "Start Node"] == df.at[j, "Stop Node"]:

                    df.at[i, "Invert In"] = df.at[j, "Invert Out"]

                    df.at[i, "Size"] = df.at[j, "Size"]

            secondline = "INV=" + "%.2f" % df.at[i, "Invert In"]

        else:

            secondline = (
                "H="
                + "%.1f" % df.at[i, "Height"]
                + "'"
                + " L="
                + "%.0f" % df.at[i, "Slot Length"]
                + "'"
                + " INV="
                + "%.2f" % df.at[i, "Invert In"]
            )

        if df.at[i, "Inlet Shp"] == "Full":

            thirdline = "ST'D IS-1 REQ'D"

            if df.at[i, "Str."] in sag_inlets:

                secondline = (
                    "H="
                    + "%.1f" % df.at[i, "Height"]
                    + "'"
                    + " L="
                    + "%.0f" % ((df.at[i, "Slot Length"]) * 2)
                    + "'"
                    + " INV="
                    + "%.2f" % df.at[i, "Invert In"]
                )

                fourthline = "CONNECT UD-4 & CD-2 TO STRUCTURE"

            else:

                fourthline = "CONNECT UD-4 TO STRUCTURE"

        else:

            if df.at[i, "Str."] in sag_inlets:

                secondline = (
                    "H="
                    + "%.1f" % df.at[i, "Height"]
                    + "'"
                    + " L="
                    + "%.0f" % ((df.at[i, "Slot Length"]) * 2)
                    + "'"
                    + " INV="
                    + "%.2f" % df.at[i, "Invert In"]
                )

                thirdline = "CONNECT UD-4 & CD-2 TO STRUCTURE"

            else:

                thirdline = "CONNECT UD-4 TO STRUCTURE"

            fourthline = ""

        if i == 0:

            n = 35

        else:

            n = n

        # writing in dxf file

        msp.add_ellipse(
            (-5, -i * n - 2),
            major_axis=(8, 0),
            ratio=0.45,
            dxfattribs={"layer": "Structure"},
        )

        # INLET STRUCTURE

        msp.add_text(
            df.at[i, "Start Node"], dxfattribs={"layer": "Text", "style": "OpenSans"}
        ).set_pos((-5, -i * n - 2), align="MIDDLE_CENTER")

        # inlet structure writeup

        if df.at[i, "Height"] < 12:

            if df.at[i, "Inlet Shp"] == "Full":

                if df.at[i, "Str."] == "MH":

                    msp.add_mtext(
                        "%.1f" % (df.at[i, "MH Height"])
                        + " L.F OF ST'D "
                        + format(df.at[i, "Str."])
                        + " REQ'D\P"
                        + "1 ST'D FRAME & COVER REQ'D"
                        + "\P"
                        + "INV="
                        + "%.2f" % df.at[i, "Invert In"]
                        + "\P"
                        + thirdline
                        + "\P"
                        + fourthline,
                        dxfattribs={"layer": "Text", "style": "OpenSans"},
                    ).set_location((5, -i * n))

                    k = 25

                elif df.at[i, "Str."] == "DI-5":

                    msp.add_mtext(
                        "1 ST'D "
                        + format(df.at[i, "Str."])
                        + " REQ'D\P"
                        + "Str. A2 COVER REQ'D"
                        + "\P"
                        + "Str. III GRATE  REQ'D"
                        + "\P"
                        + secondline
                        + "\P"
                        + thirdline,
                        dxfattribs={"layer": "Text", "style": "OpenSans"},
                    ).set_location((5, -i * n))

                    k = 25

                else:

                    msp.add_mtext(
                        "1 ST'D "
                        + format(df.at[i, "Str."])
                        + " REQ'D\P"
                        + secondline
                        + "\P"
                        + thirdline
                        + "\P"
                        + fourthline,
                        dxfattribs={"layer": "Text", "style": "OpenSans"},
                    ).set_location((5, -i * n))

                    k = 20

            else:

                if df.at[i, "Str."] == "MH":

                    msp.add_mtext(
                        "%.1f" % (df.at[i, "MH Height"])
                        + " L.F OF ST'D "
                        + format(df.at[i, "Str."])
                        + " REQ'D\P"
                        + "1 ST'D FRAME & COVER REQ'D"
                        + "\P"
                        + "INV="
                        + "%.2f" % df.at[i, "Invert In"]
                        + "\P"
                        + thirdline,
                        dxfattribs={"layer": "Text", "style": "OpenSans"},
                    ).set_location((5, -i * n))

                    k = 20

                elif df.at[i, "Str."] == "DI-5":

                    msp.add_mtext(
                        "1 ST'D "
                        + format(df.at[i, "Str."])
                        + " REQ'D\P"
                        + "Str. A2 COVER REQ'D"
                        + "\P"
                        + "Str. III GRATE  REQ'D"
                        + "\P"
                        + secondline
                        + "\P"
                        + thirdline,
                        dxfattribs={"layer": "Text", "style": "OpenSans"},
                    ).set_location((5, -i * n))

                    k = 25

                elif df.at[i, "Str."] in outlet_strs:

                    msp.add_mtext(
                        "1 ST'D "
                        + format(df.at[i, "size"])
                        + " "
                        + format(df.at[i, "Str."])
                        + " REQ'D\P"
                        + secondline
                        + "\P",
                        dxfattribs={"layer": "Text", "style": "OpenSans"},
                    ).set_location((5, -i * n))

                    k = 15

                else:

                    msp.add_mtext(
                        "1 ST'D "
                        + format(df.at[i, "Str."])
                        + " REQ'D\P"
                        + secondline
                        + "\P"
                        + thirdline,
                        dxfattribs={"layer": "Text", "style": "OpenSans"},
                    ).set_location((5, -i * n))

                    k = 15

        else:

            if df.at[i, "Inlet Shp"] == "Full":

                # value SWAP
                fifthline = "1 ST'D SL-1 REQ'D"
                swap = fourthline
                fourthline = fifthline
                fifthline = swap

                if df.at[i, "Str."] == "MH":

                    msp.add_mtext(
                        "%.1f" % (df.at[i, "MH Height"])
                        + " L.F OF ST'D "
                        + format(df.at[i, "Str."])
                        + " REQ'D\P"
                        + "1 ST'D FRAME & COVER REQ'D"
                        + "\P"
                        + "INV="
                        + "%.2f" % df.at[i, "Invert In"]
                        + "\P"
                        + thirdline
                        + "\P"
                        + fourthline
                        + "\P"
                        + fifthline,
                        dxfattribs={"layer": "Text", "style": "OpenSans"},
                    ).set_location((5, -i * n))

                    k = 30

                elif df.at[i, "Str."] == "DI-5":

                    msp.add_mtext(
                        "1 ST'D "
                        + format(df.at[i, "Str."])
                        + " REQ'D\P"
                        + "Str. A2 COVER REQ'D"
                        + "\P"
                        + "Str. III GRATE  REQ'D"
                        + "\P"
                        + secondline
                        + "\P"
                        + thirdline
                        + "\P"
                        + fourthline
                        + "\P"
                        + fifthline,
                        dxfattribs={"layer": "Text", "style": "OpenSans"},
                    ).set_location((5, -i * n))

                    k = 35

                else:

                    msp.add_mtext(
                        "1 ST'D "
                        + format(df.at[i, "Str."])
                        + " REQ'D\P"
                        + secondline
                        + "\P"
                        + thirdline
                        + "\P"
                        + fourthline
                        + "\P"
                        + fifthline,
                        dxfattribs={"layer": "Text", "style": "OpenSans"},
                    ).set_location((5, -i * n))

                    k = 25

            else:

                # values swap
                fourthline = "1 ST'D SL-1 REQ'D"
                swap = thirdline
                thirdline = fourthline
                fourthline = swap

                if df.at[i, "Str."] == "MH":

                    msp.add_mtext(
                        "%.1f" % (df.at[i, "MH Height"])
                        + " L.F OF ST'D "
                        + format(df.at[i, "Str."])
                        + " REQ'D\P"
                        + "1 ST'D FRAME & COVER REQ'D"
                        + "\P"
                        + "INV="
                        + "%.2f" % df.at[i, "Invert In"]
                        + "\P"
                        + thirdline
                        + "\P"
                        + fourthline,
                        dxfattribs={"layer": "Text", "style": "OpenSans"},
                    ).set_location((5, -i * n))

                    k = 25

                elif df.at[i, "Str."] == "DI-5":

                    msp.add_mtext(
                        "1 ST'D "
                        + format(df.at[i, "Str."])
                        + " REQ'D\P"
                        + "Str. A2 COVER REQ'D"
                        + "\P"
                        + "Str. III GRATE  REQ'D"
                        + "\P"
                        + secondline
                        + "\P"
                        + thirdline
                        + "\P"
                        + fourthline,
                        dxfattribs={"layer": "Text", "style": "OpenSans"},
                    ).set_location((5, -i * n))

                    k = 30

                elif df.at[i, "Str."] in outlet_strs:

                    msp.add_mtext(
                        "1 ST'D "
                        + format(df.at[i, "Size"])
                        + " "
                        + format(df.at[i, "Str."])
                        + " REQ'D\P"
                        + secondline
                        + "\P",
                        dxfattribs={"layer": "Text", "style": "OpenSans"},
                    ).set_location((5, -i * n))

                    k = 15

                else:

                    msp.add_mtext(
                        "1 ST'D "
                        + format(df.at[i, "Str."])
                        + " REQ'D\P"
                        + secondline
                        + "\P"
                        + thirdline
                        + "\P"
                        + fourthline,
                        dxfattribs={"layer": "Text", "style": "OpenSans"},
                    ).set_location((5, -i * n))

                    k = 20

        # calculating n value based upon k

        omax = n

        if k == 15:

            o = 31

        elif k == 20:

            o = 35

        elif k == 25:

            o = 39

        elif k == 30:

            o = 43

        elif k == 35:

            o = 47

        else:

            o = 35

        n = o

        if omax > o:

            n = omax

        else:

            n = o

        # END of inlet structure description

        # 2 ELLIPSE

        msp.add_ellipse(
            (-5, -i * n - k - 2),
            major_axis=(8, 0),
            ratio=0.45,
            dxfattribs={"layer": "Structure"},
        )

        msp.add_line(
            (-17, -i * n - k - 2),
            (-13, -i * n - k - 2),
            dxfattribs={"layer": "Structure"},
        )

        msp.add_ellipse(
            (-25, -i * n - k - 2),
            major_axis=(8, 0),
            ratio=0.45,
            dxfattribs={"layer": "Structure"},
        )

        # PIPE TEXT

        msp.add_text(
            df.at[i, "Start Node"], dxfattribs={"layer": "Text", "style": "OpenSans"}
        ).set_pos((-25, -i * n - k - 2), align="MIDDLE_CENTER")

        msp.add_text(
            df.at[i, "Stop Node"], dxfattribs={"layer": "Text", "style": "OpenSans"}
        ).set_pos((-5, -i * n - k - 2), align="MIDDLE_CENTER")

        msp.add_mtext(
            "%.0f" % df.at[i, "Pipe Length"]
            + "\'-"
            + format(df.at[i, "Size"])
            + " CONC. SSP CLASS III REQ'D ("
            + "%.0f" % df.at[i, "Cover"]
            + "' COVER)\P"
            + "INV(IN)="
            + "%.2f" % df.at[i, "Invert In"]
            + " INV(OUT)="
            + "%.2f" % df.at[i, "Invert Out"],
            dxfattribs={"layer": "Text", "style": "OpenSans"},
        ).set_location((5, -i * n - k))

    # save dxf file

    dwg.saveas(f.split(".")[0] + "_desc.dxf")


def profile():

    os.chdir(dir_path)

    sag_inlets = [
        "DI-2C",
        "DI-2CC",
        "DI-3C",
        "DI=3CC",
        "DI-4C",
        "DI-4CC",
        "DI-10I",
        "DI-10L",
    ]

    grade_inlets = [
        "DI-2B",
        "DI-2BB",
        "DI-3B",
        "DI=3BB",
        "DI-4B",
        "DI-4BB",
        "DI-10H",
        "DI-10K",
    ]

    outlet_strs = ["ES-1", "EW-1", "JB-1", "EW-2"]

    fixed_inlets = [
        "DI-2A",
        "DI-2AA",
        "DI-3A",
        "DI-3AA",
        "DI-4A",
        "DI-4AA",
        "DI-1",
        "DI-5",
        "DI-7",
        "DI-10J",
        "DI-10G",
    ]

    grate_inlets = [
        "DI-1",
        "DI-7",
        "DI-5",
        "DI-10H",
        "DI-10K",
        "DI-10G",
        "DI-10J",
        "DI-10L",
        "DI-10I",
    ]

    Str_list = [
        "DI-2C",
        "DI-2CC",
        "DI-3C",
        "DI=3CC",
        "DI-4C",
        "DI-4CC",
        "DI-10I",
        "DI-10L",
        "DI-2B",
        "DI-2BB",
        "DI-3B",
        "DI=3BB",
        "DI-4B",
        "DI-4BB",
        "DI-10H",
        "DI-10K",
        "ES-1",
        "EW-2",
        "EW-1",
        "MH-12",
        "DI-2A",
        "DI-2AA",
        "DI-3A",
        "DI-3AA",
        "DI-4A",
        "DI-4AA",
        "DI-1",
        "DI-5",
        "DI-7",
        "DI-10J",
        "DI-10G",
    ]

    dwg = ezdxf.new(dxfversion="R2013", setup=True)

    msp = dwg.modelspace()

    dwg.layers.new(name="Structure", dxfattribs={"color": 130})

    dwg.layers.new(name="Text", dxfattribs={"color": 1})

    dwg.layers.new(name="Pipe", dxfattribs={"color": 2})

    dwg.layers.new(name="hgl", dxfattribs={"color": 3})

    dwg.layers.new(name="labeline", dxfattribs={"color": 1})

    dwg.layers.new(name="grid", dxfattribs={"color": 0})

    dwg.layers.new(name="boarder", dxfattribs={"color": 0})

    dwg.layers.new(name="leader", dxfattribs={"color": 1})

    df = pd.read_csv(f, sep="\t")

    # cleaning file for dataframe

    df = df.replace("<None>", "")
    df.columns = df.columns.str.replace("ft/s", "")
    df.columns = df.columns.str.replace("ft", "")
    df.columns = df.columns.str.replace("cfs", "")
    df.columns = df.columns.str.replace("degrees", "")
    df.columns = df.columns.str.replace("None", "")
    df.columns = df.columns.str.replace("(", "")
    df.columns = df.columns.str.replace(")", "")
    df.columns = df.columns.str.replace("/", "")
    df.columns = df.columns.str.replace("in", "")
    df.columns = df.columns.str.replace("\\n", "")

    idx = df[df["NBT"] == "Outlet"].index[0]
    df_1 = df.iloc[: idx + 1, :]
    df_2 = df.iloc[idx + 1 :, :]
    df_1 = df_1.loc[:, :"NBT"]
    df_2.reset_index(drop=True, inplace=True)
    df_2 = df_2.loc[:, "Start Node":]

    df = pd.merge(df_1, df_2, left_on="Label", right_on="Start Node", how="left").drop(
        "Start Node", axis=1
    )

    df["Str Desc."] = (
        df["ES Desc."].astype(str)
        + df["Inlet Desc."].astype(str)
        + df["MH Desc."].astype(str)
    )

    df["Str Desc."] = df["Str Desc."].str.replace("nan", "")

    df = df.drop(columns=["ES Desc.", "Inlet Desc.", "MH Desc."])

    df = df.rename({"Label": "Start Node"}, axis=1)

    cols = list(df)

    cols.insert(1, cols.pop(cols.index("Stop Node")))

    df = df.loc[:, cols]

    df["Cover"] = df[["Cover Start", "Cover Stop"]].max(axis=1)

    df = df.drop(columns=["Cover Start", "Cover Stop"])

    df["Str."] = [
        " ".join(y for y in x.split() if y in Str_list) for x in df["Str Desc."]
    ]

    df = df.drop(columns=["Str Desc."])

    # Sorting in ascending order and converting to numbers

    df["Ground Elev"] = pd.to_numeric(df["Ground Elev"], errors="coerce")

    df["Invert In"] = pd.to_numeric(df["Invert In"], errors="coerce")

    df["Invert Out"] = pd.to_numeric(df["Invert Out"], errors="coerce")

    df["Slot Length"] = pd.to_numeric(df["Slot Length"], errors="coerce")

    df["Pipe Length"] = pd.to_numeric(df["Pipe Length"], errors="coerce")

    df["Slope"] = pd.to_numeric(df["Slope"], errors="coerce")

    # calculations

    df["Size"] = df["Size"].astype(str)

    df["TSIZE"] = df["Size"]

    n = len(df)

    for i in range(0, n, 1):

        if df.at[i, "Str."] in grate_inlets or df.at[i, "Str."] == "MH-12":

            df.at[i, "Top Elev"] = df.at[i, "Ground Elev"]

        else:

            df.at[i, "Top Elev"] = df.at[i, "Ground Elev"] + 0.5

    for i in range(0, n, 1):

        if df.at[i, "Str."] == "MH-12":

            df.at[i, "Str."] = "MH"

    df["Height"] = df["Top Elev"] - df["Invert In"]

    df["MH Height"] = df["Height"] - 8 / 12

    for i in range(0, n, 1):

        if "x" in df.at[i, "Size"]:

            df.at[i, "Size"] = df.at[i, "Size"].split("x", 1)[1]
        df.at[i, "Size"] = df.at[i, "Size"].split('"', 1)[0]

        if "Outlet" in df.at[i, "NBT"]:

            for j in range(0, n, 1):

                if df.at[i, "Start Node"] == df.at[j, "Stop Node"]:

                    df.at[i, "Size"] = df.at[j, "Size"]
                    df.at[i, "HGL In"] = df.at[j, "HGL Out"]
                    df.at[i, "Invert In"] = df.at[j, "Invert Out"]
                    df.at[i, "TSIZE"] = df.at[j, "Size"] + '"'
                    df.at[i, "Top Elev"] = (
                        df.at[i, "Invert In"]
                        + float(df.at[j, "Size"]) / 12
                        + (float(df.at[j, "Size"]) / 12 + 1) / 12
                    )
                    df.at[i, "Height"] = df.at[i, "Top Elev"] - df.at[i, "Invert In"]

        if str(df.at[i, "Section Type"]) == "Circle":

            df.at[i, "Section Type"] = "CIRCULAR"

        if str(df.at[i, "Section Type"]) == "Ellipse":

            df.at[i, "Section Type"] = "ELLIPTICAL"

    df["Size"] = pd.to_numeric(df["Size"], errors="coerce")

    #df.to_excel('main.xlsx')

    # creating submetwork

    def get_start_nodes(nodes):
        start_nodes = []
        for node1 in nodes:
            node_is_present = False
            for node2 in nodes:
                if node1[0] == node2[1]:
                    node_is_present = True

            if not node_is_present:
                start_nodes.append(node1[0])

        # print(start_nodes)

        return start_nodes

    def get_seperated_nodes_with_length(nodes, startNodes):
        separatedNodes = []
        for index, sNode in enumerate(startNodes):
            pathLength = 0
            pathNodes = []
            nodePathExist = True
            foundNodePath = []

            foundNodePath = list(filter((lambda n: n[0] == sNode), nodes))
            if not len(foundNodePath):
                nodePathExist = False

            while nodePathExist:
                pathToCheck = foundNodePath[0]
                pathLength += pathToCheck[2]
                pathNodes.append(pathToCheck)

                foundNodePath = list(filter((lambda n: n[0] == pathToCheck[1]), nodes))

                if not len(foundNodePath):
                    nodePathExist = False

            separatedNodes.append(
                {"id": index + 1, "pathLength": pathLength, "nodes": pathNodes}
            )

        return separatedNodes

    def is_array_in_array(array, item):
        contains = list(filter((lambda n: n == item), array))
        if len(contains):
            return True
        return False

    def get_longest_path(seperatedNodes):
        greatestLength = 0

        for n in seperatedNodes:
            if greatestLength < n["pathLength"]:
                greatestLength = n["pathLength"]

        longestPath = list(
            filter((lambda n: n["pathLength"] == greatestLength), seperatedNodes)
        )
        return longestPath[0]

    def get_new_seperated_nodes(seperatedNodes):
        longestPath = get_longest_path(seperatedNodes)
        newSeperatedNodes = []

        otherNodes = list(
            filter((lambda n: n["id"] != longestPath["id"]), seperatedNodes)
        )

        for sn in otherNodes:
            pathLength = 0
            uniqueNodes = list(
                filter(
                    (lambda n: not is_array_in_array(longestPath["nodes"], n)),
                    sn["nodes"],
                )
            )

            for un in uniqueNodes:
                pathLength += un[2]

            newSeperatedNodes.append(
                {"id": sn["id"], "pathLength": pathLength, "nodes": uniqueNodes}
            )

        return {"longest": longestPath, "other": newSeperatedNodes}

    def group_node_by_common_end_point(seperatedNodes):
        groupedNodes = []

        for sn in seperatedNodes:
            lastNode1 = sn["nodes"][-1][1]
            addedNodes = list(filter((lambda n: n["id"] == lastNode1), groupedNodes))

            if len(addedNodes) < 1:
                groupedNodes.append({"id": lastNode1, "nodes": sn["nodes"]})

            if len(addedNodes) == 1:
                newNodes = list(
                    filter(
                        (lambda n: not is_array_in_array(addedNodes[0]["nodes"], n)),
                        sn["nodes"],
                    )
                )
                for nn in newNodes:
                    addedNodes[0]["nodes"].append(nn)

        return groupedNodes

    def getNodes():
        data = df
        # print("df_names", data)

        nodes = []
        for index, row in data.iterrows():
            startNode = str(row["Start Node"])
            stopNode = str(row["Stop Node"])
            pipeLength = row["Pipe Length"]
            station = str(row["Station"])
            offset = str(row["Offset"])
            inletShp = str(row["Inlet Shp"])
            SlotLength = str(row["Slot Length"])
            inletLocation = str(row["Inlet Location"])
            topElev = row["Top Elev"]
            nbt = str(row["NBT"])
            slope = str(row["Slope"])
            invertIn = row["Invert In"]
            invertOut = row["Invert Out"]
            hglIn = row["HGL In"]
            hglOut = row["HGL Out"]
            sectionType = row["Section Type"]
            size = row["Size"]
            cover = row["Cover"]
            Struc = str(row["Str."])
            height = row["Height"]
            mheight = row["MH Height"]
            tSize = row["TSIZE"]
            OInvert = row["Outgog Invert"]
            flow = (row["Flow Total Out"])
            velocity = row["Velocity"]
            CLoss = (row["Contraction Loss AASHTO"])
            ELPVel = (row["Expansion Loss Pipe Velocity AASHTO"])
            ELPFlow = (row["Expansion Loss Pipe Flow AASHTO"])
            qIvI = (row["QIVI"])
            ELoss = (row["Expansion Loss AASHTO"])
            BLPAngle = (row["Bend Loss Pipe Angle AASHTO"])
            BLCoef = (row["Bend Loss Coefficient AASHTO"])
            BLoss = (row["Bend Loss AASHTO"])
            adjHLoss=(row["Adjusted Headloss AASHTO"])
            flowSurface=(row["Flow Local Surface"])
            fSlope=(row["Friction Slope"])
            hLoss=(row["Headloss"])
            vOut=(row["Velocity Out"])
            hglINORD=(row["HGL.IN.ORD"])
            hglOUTORD=(row["HGL.OUT.ORD"])

            if startNode == "nan":
                startNode = 0

            if stopNode == "nan":
                stopNode = 0

            if str(pipeLength) == "nan":
                pipeLength = 0


            item = [
                startNode,
                stopNode,
                pipeLength,
                station,
                offset,
                inletShp,
                SlotLength,
                inletLocation,
                topElev,
                nbt,
                slope,
                invertIn,
                invertOut,
                hglIn,
                hglOut,
                sectionType,
                size,
                cover,
                Struc,
                height,
                mheight,
                tSize,
                OInvert,
                flow,
                velocity,
                CLoss,
                ELPVel,
                ELPFlow,
                qIvI,
                ELoss,
                BLPAngle,
                BLCoef,
                BLoss,
                adjHLoss,
                flowSurface,
                fSlope,
                hLoss,
                vOut,
                hglINORD,
                hglOUTORD,
            ]

            nodes.append(item)

        return nodes

    def convertArrayToDataFrame(theFinalNodes):

        spacing = 0

        loop = 1

        df_347 = pd.DataFrame()

        for finalNode in theFinalNodes:

            spacing = spacing + 100

            df_frame = pd.DataFrame(
                finalNode["nodes"],
                columns=[
                    "Start Node",
                    "Stop Node",
                    "Pipe Length",
                    "Station",
                    "Offset",
                    "Inlet Shp",
                    "Slot Length",
                    "Inlet Location",
                    "Top Elev",
                    "NBT",
                    "Slope",
                    "Invert In",
                    "Invert Out",
                    "HGL In",
                    "HGL Out",
                    "Section Type",
                    "Size",
                    "Cover",
                    "Str.",
                    "Height",
                    "MH Height",
                    "TSIZE",
                    "Outgog Invert",
                    "Flow Total Out",
                    "Velocity",
                    "Contraction Loss AASHTO",
                    "Expansion Loss Pipe Velocity AASHTO",
                    "Expansion Loss Pipe Flow AASHTO",
                    "QIVI",
                    "Expansion Loss AASHTO",
                    "Bend Loss Pipe Angle AASHTO",
                    "Bend Loss Coefficient AASHTO",
                    "Bend Loss AASHTO",
                    "Adjusted Headloss AASHTO",
                    "Flow Local Surface",
                    "Friction Slope",
                    "Headloss",
                    "Velocity Out",
                    "HGL.IN.ORD",
                    "HGL.OUT.ORD",
                ],
            )
            
            df_frame_347=df_frame

            df_frame_347['JunLossTot']=df_frame_347['Contraction Loss AASHTO'].astype(float)+df_frame_347['Expansion Loss AASHTO'].astype(float)+df_frame_347['Bend Loss AASHTO'].astype(float)

            df_frame_347['finalHLOSS']=df_frame_347['Adjusted Headloss AASHTO'].astype(float)+df_frame_347['Headloss'].astype(float)
            
            df_frame_347 = pd.DataFrame([[np.nan] * len(df_frame_347.columns)], columns=df_frame_347.columns).append(df_frame_347, ignore_index=True)
            
            #df_frame_347['HGL Out'].shift(-1)

            df_347 = df_347.append(
                df_frame_347[
                    [
                        "Start Node",
                        "Station",
                        "Outgog Invert",
                        "Size",
                        "Flow Total Out",
                        "Pipe Length",
                        "Friction Slope",
                        "Headloss",
                        "Velocity Out",
                        "Contraction Loss AASHTO",
                        "Expansion Loss Pipe Velocity AASHTO",
                        "Expansion Loss AASHTO",
                        "Bend Loss Pipe Angle AASHTO",
                        "Bend Loss Coefficient AASHTO",
                        "Bend Loss AASHTO",
                        "JunLossTot",
                        "Flow Local Surface",
                        "Adjusted Headloss AASHTO",
                        "Inlet Shp",
                        "finalHLOSS",
                        "HGL.IN.ORD",
                        "HGL.OUT.ORD",
                        "Top Elev",
                    ]
                ].iloc[::-1],
                ignore_index=False,
            )

            df_347.to_excel(f.split(".")[0] + "LD-347.xlsx")

            sub = len(df_frame)

            outfall = df_frame["Invert Out"].min()
            minout = outfall + spacing

            for i in range(0, n, 1):

                if df_frame.at[sub - 1, "Stop Node"] == df.at[i, "Start Node"]:

                    df_frame = df_frame.append(
                        df[df["Start Node"] == df_frame.at[sub - 1, "Stop Node"]],
                        ignore_index=True,
                    )

            sub = len(df_frame)

            def round_down(num, divisor):

                return num - (num % divisor)

            df_frame["RYD"] = (df_frame["Invert In"] - minout) * 5

            df_frame["RYDD"] = (df_frame["Invert Out"] - minout) * 5

            df_frame["HGLD"] = (df_frame["HGL In"] - minout) * 5
            
            df_frame["HGLD2"] = (df_frame["HGL Out"] - minout) * 5

            # Calculating Y

            df_frame["RY1"] = minout + df_frame["RYD"]

            df_frame["RY_grid"] = minout + df_frame["RYD"]

            df_frame["RY2"] = df_frame["RY1"]

            df_frame["RY3"] = df_frame["RY1"] + df_frame["Height"] * 5

            df_frame["RY4"] = df_frame["RY3"]

            df_frame["LY2"] = minout + df_frame["RYDD"]

            df_frame["HY2"] = minout + df_frame["HGLD"]
            
            df_frame["HY3"] = minout + df_frame["HGLD2"]

            df_frame["L4"] = df_frame["Pipe Length"] + 4

            df_frame["CS"] = df_frame["L4"].cumsum()

            df_frame["CS"] = df_frame["CS"].shift(1)

            df_frame["POUT"] = df_frame["Invert Out"].shift(1)

            df_frame["CS"] = df_frame["CS"] * -1

            df_frame["RX1"] = df_frame["CS"] - 2

            df_frame["RX2"] = df_frame["CS"] + 2

            df_frame["RX3"] = df_frame["RX1"]

            df_frame["RX4"] = df_frame["RX2"]

            df_frame.at[(0), "RX1"] = -2

            df_frame.at[(0), "RX2"] = 2

            df_frame.at[(0), "RX3"] = -2

            df_frame.at[(0), "RX4"] = 2

            # print(df_frame)
            low_x = int(round_down(df_frame["RX2"].min(), 25) - 25)

            low_y = int(round_down(df_frame["RY_grid"].min(), 25) - 50)

            high_x = int(round_down(df_frame["RX2"].max(), 25) + 25)

            high_y = int(round_down(df_frame["RY4"].max(), 25) + 50)

            y_st = round(round_down(outfall - 10, 5), 0)

            def count_zeros(number):

                return str(number).count("0")

            if df_frame["Invert In"].min() < 25:

                PL = 25 + df_frame["Invert In"].min()

                DIF = (df_frame["Invert In"].min() - (y_st + 5)) * 5

                T = PL - DIF

            else:

                PL = (
                    df_frame["Invert In"].min()
                    - int(round_down(df_frame["Invert In"].min(), 25))
                    + 25
                )

                DIF = (df_frame["Invert In"].min() - (y_st + 5)) * 5

                T = PL - DIF

            for y in range(low_y + 25, high_y + 25, 25):

                if y == low_y + 25 or y == high_y:

                    msp.add_line(
                        (low_x, y + T), (high_x, y + T), dxfattribs={"layer": "boarder"}
                    )

                else:

                    msp.add_line(
                        (low_x, y + T), (high_x, y + T), dxfattribs={"layer": "grid"}
                    )

                msp.add_mtext(
                    "%.0f" % (y_st + 5),
                    dxfattribs={"layer": "Text", "style": "OpenSans", "char_height": 3},
                ).set_location((low_x - 10, y + 2 + T))

                msp.add_mtext(
                    "%.0f" % (y_st + 5),
                    dxfattribs={"layer": "Text", "style": "OpenSans", "char_height": 3},
                ).set_location((high_x + 5, y + 2 + T))

                y_st = y_st + 5

            x_st = 0

            for x in range(low_x, high_x + 25, 25):

                if x == low_x or x == high_x:

                    msp.add_line(
                        (x, low_y + 25 + T),
                        (x, high_y + T),
                        dxfattribs={"layer": "boarder"},
                    )

                else:

                    msp.add_line(
                        (x, low_y + 25 + T),
                        (x, high_y + T),
                        dxfattribs={"layer": "grid"},
                    )

                x = x - 4

                if x_st != 1050:

                    if count_zeros(x_st) >= 2:

                        check_st = "%.0f" % (x_st / 100)

                        msp.add_mtext(
                            format(check_st) + "+00",
                            dxfattribs={
                                "layer": "Text",
                                "style": "OpenSans",
                                "char_height": 3,
                            },
                        ).set_location((x, low_y + 20 + T))

                if x_st == 0:

                    msp.add_mtext(
                        "0+00",
                        dxfattribs={
                            "layer": "Text",
                            "style": "OpenSans",
                            "char_height": 3,
                        },
                    ).set_location((x, low_y + 20 + T))

                x_st = x_st + 25

            for i in range(0, sub, 1):

                # drawing structures

                msp.add_line(
                    (df_frame.at[i, "RX1"], df_frame.at[i, "RY1"]),
                    (df_frame.at[i, "RX2"], df_frame.at[i, "RY2"]),
                    dxfattribs={"layer": "Structure"},
                )

                msp.add_line(
                    (df_frame.at[i, "RX1"], df_frame.at[i, "RY1"]),
                    (df_frame.at[i, "RX3"], df_frame.at[i, "RY3"]),
                    dxfattribs={"layer": "Structure"},
                )

                msp.add_line(
                    (df_frame.at[i, "RX2"], df_frame.at[i, "RY2"]),
                    (df_frame.at[i, "RX4"], df_frame.at[i, "RY4"]),
                    dxfattribs={"layer": "Structure"},
                )

                msp.add_line(
                    (df_frame.at[i, "RX3"], df_frame.at[i, "RY3"]),
                    (df_frame.at[i, "RX4"], df_frame.at[i, "RY4"]),
                    dxfattribs={"layer": "Structure"},
                )

                # adding text to profile

                msp.add_ellipse(
                    (df_frame.at[i, "RX3"] + 6.5, df_frame.at[i, "RY3"] + 31),
                    major_axis=(8.5, 0),
                    ratio=0.45,
                    dxfattribs={"layer": "Structure"},
                )

                msp.add_text(
                    df_frame.at[i, "Start Node"],
                    dxfattribs={"layer": "Text", "style": "OpenSans", "height": 3},
                ).set_pos(
                    (df_frame.at[i, "RX3"] + 6.5, df_frame.at[i, "RY3"] + 31),
                    align="MIDDLE_CENTER",
                )

                if (
                    df_frame.at[i, "Str."] == "ES-1"
                    or df_frame.at[i, "Str."] == "MH"
                    or df_frame.at[i, "Str."] == "EW-1"
                ):

                    msp.add_mtext(
                        format(df_frame.at[i, "Str."])
                        + "\P"
                        + format(df_frame.at[i, "Station"])
                        + "\P"
                        + "TOP="
                        + "%.2f" % df_frame.at[i, "Top Elev"],
                        dxfattribs={
                            "layer": "Text",
                            "style": "OpenSans",
                            "char_height": 3,
                        },
                    ).set_location((df_frame.at[i, "RX3"], df_frame.at[i, "RY3"] + 25))

                elif df_frame.at[i, "Str."] in sag_inlets:
                    msp.add_mtext(
                        format(df_frame.at[i, "Str."])
                        + "\P"
                        + format(df_frame.at[i, "Station"])
                        + "\P"
                        + "L="
                        + "%.0f" % (float(df_frame.at[i, "Slot Length"]) * 2)
                        + "'"
                        + "\P"
                        + "TOP="
                        + "%.2f" % df_frame.at[i, "Top Elev"],
                        dxfattribs={
                            "layer": "Text",
                            "style": "OpenSans",
                            "char_height": 3,
                        },
                    ).set_location((df_frame.at[i, "RX3"], df_frame.at[i, "RY3"] + 25))

                else:

                    msp.add_mtext(
                        format(df_frame.at[i, "Str."])
                        + "\P"
                        + format(df_frame.at[i, "Station"])
                        + "\P"
                        + "L="
                        + "%.0f" % float(df_frame.at[i, "Slot Length"])
                        + "'"
                        + "\P"
                        + "TOP="
                        + "%.2f" % float(df_frame.at[i, "Top Elev"]),
                        dxfattribs={
                            "layer": "Text",
                            "style": "OpenSans",
                            "char_height": 3,
                        },
                    ).set_location((df_frame.at[i, "RX3"], df_frame.at[i, "RY3"] + 25))

                if df_frame.at[i, "Pipe Length"] <= 200:

                    msp.add_text(
                        "INV.=" + "%.2f" % df_frame.at[i, "Invert In"],
                        dxfattribs={"layer": "Text", "style": "OpenSans", "height": 3},
                    ).set_pos(
                        (df_frame.at[i, "RX1"] + 8, df_frame.at[i, "RY2"] - 13.5),
                        align="TOP_LEFT",
                    )

                    msp.add_text(
                        "INV.=" + "%.2f" % df_frame.at[i, "POUT"],
                        dxfattribs={"layer": "Text", "style": "OpenSans", "height": 3},
                    ).set_pos(
                        (df_frame.at[i, "RX2"] + 8, df_frame.at[i, "RY2"] - 7.5),
                        align="TOP_LEFT",
                    )

                    pt = [
                        (df_frame.at[i, "RX1"], df_frame.at[i, "RY1"]),
                        (df_frame.at[i, "RX1"] + 5, df_frame.at[i, "RY1"] - 14.5),
                        (df_frame.at[i, "RX1"] + 7, df_frame.at[i, "RY2"] - 14.5),
                    ]

                    leader = msp.add_leader(
                        vertices=pt,
                        override={"dimscale": 20.0, "dimldrblk": "EZ_ARROW_FILLED"},
                        dxfattribs={"layer": "leader"},
                    )

                else:

                    msp.add_text(
                        "INV.=" + "%.2f" % df_frame.at[i, "Invert In"],
                        dxfattribs={"layer": "Text", "style": "OpenSans", "height": 3},
                    ).set_pos(
                        (df_frame.at[i, "RX2"] - 12, df_frame.at[i, "RY2"] - 7.5),
                        align="TOP_RIGHT",
                    )

                    msp.add_text(
                        "INV.=" + "%.2f" % df_frame.at[i, "POUT"],
                        dxfattribs={"layer": "Text", "style": "OpenSans", "height": 3},
                    ).set_pos(
                        (df_frame.at[i, "RX2"] + 8, df_frame.at[i, "RY2"] - 7.5),
                        align="TOP_LEFT",
                    )

                    pt = [
                        (df_frame.at[i, "RX1"], df_frame.at[i, "RY1"]),
                        (df_frame.at[i, "RX1"] - 5, df_frame.at[i, "RY1"] - 8.5),
                        (df_frame.at[i, "RX2"] - 11, df_frame.at[i, "RY2"] - 8.5),
                    ]

                    leader = msp.add_leader(
                        vertices=pt,
                        override={"dimscale": 20.0, "dimldrblk": "EZ_ARROW_FILLED"},
                        dxfattribs={"layer": "leader"},
                    )

            for i in range(0, sub - 1, 1):

                lb_x = (df_frame.at[i, "RX1"] + df_frame.at[i + 1, "RX2"]) / 2

                lb_y = (
                    (df_frame.at[i, "RY1"] + (df_frame.at[i, "Size"]) / 12 * 5)
                    + (df_frame.at[i, "LY2"] + (df_frame.at[i, "Size"]) / 12 * 5)
                ) / 2

                if (
                    df_frame.at[i, "Pipe Length"] >= 0
                    and df_frame.at[i, "Pipe Length"] <= 50
                ):

                    msp.add_mtext(
                        "%.0f" % df_frame.at[i, "Pipe Length"]
                        + "\'-"
                        + format(df_frame.at[i, "TSIZE"])
                        + " CONC. SSP"
                        + "\P"                        
                        + " CLASS III @ "
                        + "%.2f" % (float(df_frame.at[i, "Slope"]) * 100)
                        + "%",
                        dxfattribs={
                            "layer": "Text",
                            "style": "OpenSans",
                            "char_height": 3,
                        },
                    ).set_location(
                        (lb_x, lb_y + 10), 
                        attachment_point=5,
                    )

                elif (
                    df_frame.at[i, "Pipe Length"] >= 51
                    and df_frame.at[i, "Pipe Length"] <= 80
                ):

                    msp.add_mtext(
                        "%.0f" % df_frame.at[i, "Pipe Length"]
                        + "\'-"
                        + format(df_frame.at[i, "TSIZE"])
                        + " CONC. SSP"
                        + "\P"                        
                        + " CLASS III @ "
                        + "%.2f" % (float(df_frame.at[i, "Slope"]) * 100)
                        + "%",
                        dxfattribs={
                            "layer": "Text",
                            "style": "OpenSans",
                            "char_height": 3,
                        },
                    ).set_location(
                        (lb_x, lb_y + 10), 
                        attachment_point=5, 
                        rotation=float(df_frame.at[i, "Slope"]) * 290,
                    )
                else:

                    msp.add_mtext(
                        "%.0f" % df_frame.at[i, "Pipe Length"]
                        + "\'-"
                        + format(df_frame.at[i, "TSIZE"])
                        + " CONC. SSP CLASS III @ "
                        + "%.2f" % (float(df_frame.at[i, "Slope"]) * 100)
                        + "%",
                        dxfattribs={
                            "layer": "Text",
                            "style": "OpenSans",
                            "char_height": 3,
                        },
                    ).set_location(
                        (lb_x, lb_y + 4),
                        attachment_point=5,
                        rotation=float(df_frame.at[i, "Slope"]) * 290,
                    )

                # HGL text

                msp.add_text(
                    "HGL",
                    dxfattribs={"layer": "Text", "style": "OpenSans", "height": 3},
                ).set_pos(
                    (df_frame.at[i, "RX1"] - 15, df_frame.at[i, "HY2"] + 15),
                    align="TOP_LEFT",
                )

            # drawing pipe

            sub = len(df_frame)

            for i in range(0, sub - 1, 1):

                msp.add_line(
                    (df_frame.at[i, "RX1"], df_frame.at[i, "RY1"]),
                    (df_frame.at[i + 1, "RX2"], df_frame.at[i, "LY2"]),
                    dxfattribs={"layer": "Pipe"},
                )

                msp.add_line(
                    (
                        df_frame.at[i, "RX1"],
                        df_frame.at[i, "RY1"] + (df_frame.at[i, "Size"]) / 12 * 5,
                    ),
                    (
                        df_frame.at[i + 1, "RX2"],
                        df_frame.at[i, "LY2"] + (df_frame.at[i, "Size"]) / 12 * 5,
                    ),
                    dxfattribs={"layer": "Pipe"},
                )

                msp.add_line(
                    (df_frame.at[i, "RX1"], df_frame.at[i, "HY2"]),
                    (df_frame.at[i + 1, "RX2"], df_frame.at[i, "HY3"]),
                    dxfattribs={"layer": "hgl"},
                )

                if df_frame.at[i, "Pipe Length"] <= 200:

                    pt = [
                        (df_frame.at[i + 1, "RX2"], df_frame.at[i, "LY2"]),
                        (
                            df_frame.at[i + 1, "RX2"] + 5,
                            df_frame.at[i + 1, "RY2"] - 8.5,
                        ),
                        (
                            df_frame.at[i + 1, "RX2"] + 7,
                            df_frame.at[i + 1, "RY2"] - 8.5,
                        ),
                    ]

                    leader = msp.add_leader(
                        vertices=pt,
                        override={"dimscale": 20.0, "dimldrblk": "EZ_ARROW_FILLED"},
                        dxfattribs={"layer": "leader"},
                    )

                else:

                    pt = [
                        (df_frame.at[i + 1, "RX2"], df_frame.at[i, "LY2"]),
                        (
                            df_frame.at[i + 1, "RX2"] + 5,
                            df_frame.at[i + 1, "RY2"] - 8.5,
                        ),
                        (
                            df_frame.at[i + 1, "RX2"] + 7,
                            df_frame.at[i + 1, "RY2"] - 8.5,
                        ),
                    ]

                    leader = msp.add_leader(
                        vertices=pt,
                        override={"dimscale": 20.0, "dimldrblk": "EZ_ARROW_FILLED"},
                        dxfattribs={"layer": "leader"},
                    )

            loop = loop + 1

        dwg.saveas(f.split(".")[0] + "_prof.dxf")

    def mainFunc():
        nodes = getNodes()
        theFinalNodes = []

        def checkUntilFinished(nodes):
            start_nodes = get_start_nodes(nodes)
            # print("start_nodes", start_nodes)

            seperatedNodes = get_seperated_nodes_with_length(nodes, start_nodes)
            # print("seperatedNodes", seperatedNodes)

            newSeperatedNodes = get_new_seperated_nodes(seperatedNodes)
            # print("newSeperatedNodes", newSeperatedNodes)

            theFinalNodes.append(newSeperatedNodes["longest"])

            if len(newSeperatedNodes["other"]) > 0:
                finalNodes = group_node_by_common_end_point(newSeperatedNodes["other"])
                # print("finalNodes", finalNodes)

                for finalNode in finalNodes:
                    checkUntilFinished(finalNode["nodes"])

        checkUntilFinished(nodes)

        # print('theFinalNodes', theFinalNodes)

        convertArrayToDataFrame(theFinalNodes)
        return theFinalNodes

    mainFunc()

    messagebox.showinfo("Thank you!", "Successfuly Created description & Profile")

    return ()


def combo():

    description()

    profile()


root = tkinter.Tk()

root.title("Water Resources")

screen_width = root.winfo_screenwidth()

screen_height = root.winfo_screenheight()


x = int((screen_width / 2) - 200)

y = int((screen_height / 2) - 75)

# You can set the geometry attribute to change the root windows size

root.geometry(
    "{}x{}+{}+{}".format(800, 150, x - 250, y - 300)
)  # You want the size of the app to be 500x500

root.resizable(0, 0)  # Don't allow resizing in the x or y direction


def print_path():

    global f, dir_path

    f = askopenfilename()

    dir_path = os.path.dirname(os.path.realpath(f))

    label_3 = tkinter.Label(root, text=f, fg="green")

    label_3.place(relx=0.5, rely=0.60, anchor="c")

    return ()


# print(f)

label_1 = tkinter.Label(
    root, text="GENERATE DRAINAGE DESCRIPTION & STORM SEWER PROFILE", fg="blue"
)

label_1.place(relx=0.5, rely=0.1, anchor="c")

label_2 = tkinter.Label(root, text="\u00a9 Kabin R. Luitel", fg="red")

label_2.place(relx=0.07, rely=0.85, anchor="c")

label_3 = tkinter.Label(root, text="Contact: kabinluitel@gmail.com", fg="red")

label_3.place(relx=0.88, rely=0.85, anchor="c")

b1 = tkinter.Button(
    root, text="CHOOSE FILE:", bg="grey", fg="black", command=print_path
)

b1.place(relx=0.5, rely=0.35, anchor="c")

b2 = tkinter.Button(root, text="RUN", bg="green", fg="black", command=combo)

b2.place(relx=0.5, rely=0.80, anchor="c")

root.mainloop()
