import pandas as pd
import xarray as xr
import zarr
import dask.array as da
from zarr.errors import PathNotFoundError
import logging

logging.basicConfig()


def get_best_item_for_year(
    catalog, year, bbox, collection="sentinel-2-l2a", max_cloud_cover=30
):
    """
    Return the least cloudy Sentinel-2 item for a given year and bbox.
    """
    results = catalog.search(
        collections=[collection],
        bbox=bbox,
        datetime=[f"{year}-03-01", f"{year}-10-30"],
        query={"eo:cloud_cover": {"lt": max_cloud_cover}},
    )
    items = results.item_collection()
    if not items:
        return None
    best_item = min(items, key=lambda x: x.properties.get("eo:cloud_cover", 999))
    logging.debug(
        f"{year}: selected item with cloud cover = {best_item.properties.get('eo:cloud_cover', 'unknown')}%"
    )
    return best_item


def load_sentinel_data(
    catalog,
    years,
    bbox,
    collection="sentinel-2-l2a",
    asset="SR_10m",
    max_cloud_cover=30,
    chunks={},
):
    """
    Load Sentinel-2 data for a given bounding box and years.
    """
    items = [
        item
        for year in years
        if (
            item := get_best_item_for_year(
                catalog, year, bbox, collection, max_cloud_cover
            )
        )
        is not None
    ]
    datasets = []
    for item in items:
        try:
            ds = xr.open_dataset(
                item.assets[asset].href,
                engine="eopf-zarr",
                chunks=chunks,
            )
        except (FileNotFoundError, OSError) as e:
            logging.warning(f"Skipping missing file: {item.assets[asset].href}")
            continue

        time_coord = pd.to_datetime([item.datetime]).tz_localize(None)  # always naive
        ds = ds.expand_dims(time=time_coord)
        datasets.append(ds)
    return xr.concat(datasets, dim="time", join="outer") if datasets else None


def load_sentinel_scl(
    catalog,
    years,
    bbox,
    collection="sentinel-2-l2a",
    asset="SCL_20m",
    max_cloud_cover=30,
):
    """
    Load Sentinel-2 SCL datasets as a separate xarray Dataset stacked along time.
    """
    items = [
        item
        for year in years
        if (
            item := get_best_item_for_year(
                catalog, year, bbox, collection, max_cloud_cover
            )
        )
        is not None
    ]

    scl_datasets = []
    for item in items:
        try:
            href = item.assets[asset].href

            # Guard against empty or None paths early
            if not href:
                raise PathNotFoundError("Empty asset href")

            scl_z = zarr.open(href, mode="r")

            scl_da = xr.DataArray(
                da.from_array(scl_z, chunks=scl_z.chunks),
                dims=("y", "x"),
                name="scl",
            )

        except (PathNotFoundError, FileNotFoundError, OSError, ValueError):
            logging.warning(f"Skipping missing SCL asset: {href}")
            continue
        ds_scl = xr.Dataset({"scl": scl_da})
        time_coord = pd.to_datetime([item.datetime]).tz_localize(None)
        ds_scl = ds_scl.expand_dims(time=time_coord)
        scl_datasets.append(ds_scl)

    return xr.concat(scl_datasets, dim="time", join="outer") if scl_datasets else None


def get_epsg_from_first_band(ds):
    for var in ds.data_vars:
        attrs = ds[var].attrs
        if "proj:epsg" in attrs:
            return int(attrs["proj:epsg"])
    raise ValueError("No proj:epsg found in any data variable")


def validate_scl(scl):
    """
    Create a boolean mask for valid pixels based on the Scene Classification Layer (SCL).

    Returns
    -------
    valid_mask : xarray.DataArray (bool)
        True for pixels considered valid for analysis, False for invalid pixels.
    """

    # Sentinel-2 SCL classes
    scl_classes = {
        0: "No data",  # No observation
        1: "Saturated / defective",  # Sensor issues
        2: "Dark area pixels",  # Very low reflectance (shadowed)
        3: "Cloud shadows",  # Pixels in shadow of clouds
        4: "Vegetation",  # Green vegetation
        5: "Bare soil",  # Soil / sand / non-vegetated areas
        6: "Water",  # Lakes, rivers, ocean
        7: "Unclassified",  # Could not classify
        8: "Cloud medium probability",  # Clouds detected with medium confidence
        9: "Cloud high probability",  # Clouds detected with high confidence
        10: "Thin cirrus",  # High altitude thin clouds
        11: "Snow / ice",  # Snow or ice cover
    }

    # Define which SCL classes are considered invalid for analysis
    # (common for NDVI / vegetation analysis)
    invalid_classes = [0, 1, 2, 3, 7, 8, 9, 10, 11]

    # Create boolean mask: True = valid, False = invalid
    valid_mask = ~scl.isin(invalid_classes)

    return valid_mask
