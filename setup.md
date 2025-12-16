pyproject.toml --> Fixes Python version and so much more.

This synchronizes the local environment on the state of the requirements.
````sh
uv sync
````

Commands like this make it easy to add packages under the same name, as they are present in pip. 
````sh
uv add xarray
````

Notice: Pip is only installed, because you can easily run JupyterLab-Notebooks in PyCharm. However, their workflow requires pip to be installed.

You need GDAL to be installed on your respective working environment. 
