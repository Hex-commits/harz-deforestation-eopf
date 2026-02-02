import numpy as np

## Functions

### Helper Functions to be a tad bit flexible.


def mean_if_exists(da, dim):
    return da.mean(dim) if dim in da.dims else da


def select_year(ds, year=None):
    """
    If year is None -> keep all years
    If year is int -> select that year
    """
    if year is None:
        return ds
    return ds.sel(year=year)


def nir_red_texture(ds, year=None, window=3):
    if year is not None:
        ds = ds.sel(year=year)

    nir_red = ds.b08 / ds.b04

    return (
        nir_red.mean("year", skipna=True).rolling(x=window, y=window, center=True).var()
    )


def spectral_entropy(ds, bands=("b02", "b03", "b04", "b08"), year=None):
    ds = select_year(ds, year)

    spectral = ds[list(bands)].to_array("band")
    spectral = mean_if_exists(spectral, "year")

    spectral_norm = spectral / spectral.sum("band")

    return -(spectral_norm * np.log(spectral_norm)).sum("band")


def ndvi_texture(ds, year=None, window=3):
    ds = select_year(ds, year)

    ndvi = mean_if_exists(ds.ndvi, "year")

    return ndvi.rolling(x=window, y=window, center=True).std()


def spectral_spatial_std(
    ds,
    bands=("b02", "b03", "b04", "b08"),
    year=None,
    window=3,
):
    ds = select_year(ds, year)

    spectral = ds[list(bands)].to_array("band")

    spectral = mean_if_exists(spectral, "year")

    return spectral.rolling(x=window, y=window, center=True).std().mean("band")


def spectral_texture(
    ds,
    bands=("b02", "b03", "b04", "b08"),
    year=None,
    window=9,
):
    """
    Spatial texture based on multi-band spectral standard deviation.
    """

    if year is not None:
        ds = ds.sel(year=year)

    spectral = ds[list(bands)].to_array("band")

    return spectral.rolling(x=window, y=window, center=True).std().mean("band")


def forest_monoculture_index(
    spectral_std,
    entropy_mean,
    ndvi_texture,
    weights=(0.4, 0.3, 0.3),
):
    w1, w2, w3 = weights

    return (
        (1 - spectral_std / spectral_std.max()) * w1
        + (1 - entropy_mean / entropy_mean.max()) * w2
        + (1 - ndvi_texture / ndvi_texture.max()) * w3
    )
