import os
import s3fs
from datetime import datetime
from pathlib import Path

import geopandas as gpd
import matplotlib.colors as mcolors
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import numpy as np
import requests
import xarray as xr
from shapely import geometry

# Set up a local cluster for distributed computing.
from distributed import LocalCluster

def extract_time(ds):
    date_format = "%Y%m%dT%H%M%S"
    filename = ds.encoding["source"]
    date_str = os.path.basename(filename).split("_")[2]
    time = datetime.strptime(date_str, date_format)
    return ds.assign_coords(time=time)

def to_km2(dataarray, resolution):
    # Calculate forest area
    return dataarray * np.prod(list(resolution)) / 1e6

def plot_rgb_ndvi(dset, x_slice, y_slice):
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))

    # Extract RGB bands
    rgb = dset[["b04", "b03", "b02"]].to_dataarray(dim="bands")

    # 1. Normal RGB (raw or scaled 0-1)
    rgb_normal = rgb # scale to 0-1 if needed
    rgb_normal.plot.imshow(
        ax=axes[0],
        rgb="bands",
        extent=(x_slice.start, x_slice.stop, y_slice.start, y_slice.stop),
    )
    axes[0].set_title("RGB (Normal)")

    # 2. Enhanced RGB (contrast stretch)
    rgb_enhanced = (rgb - 0.02) / (0.35 - 0.02)
    rgb_enhanced = rgb_enhanced.clip(0, 1)
    rgb_enhanced.plot.imshow(
        ax=axes[1],
        rgb="bands",
        extent=(x_slice.start, x_slice.stop, y_slice.start, y_slice.stop),
    )
    axes[1].set_title("RGB (Enhanced)")

    # 3. NDVI
    ndvi_plot = dset["ndvi"].plot(
        ax=axes[2], cmap="Greens", vmin=-1, vmax=1, add_colorbar=False
    )
    axes[2].set_title("NDVI")

    # Add color bar for NDVI
    fig.subplots_adjust(right=0.85)
    cbar_ax = fig.add_axes([0.88, 0.15, 0.03, 0.7])
    fig.colorbar(ndvi_plot, cax=cbar_ax)

    plt.show()