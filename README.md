# harz-deforestation-eopf

## Summary

Motivation: 
In the area of the "Harz Naturschutzgebiet" there was a lot of monoculture of certain tree species, particularly vulnurable to insect disease, which in turn lead to a huge deforestation of the area starting around 2018. As this is within the timeframe of Sentinel-2, it would be interesting to see how the deforestation affected the area. 

The goal is to see the effects of the dying monoculture of trees, aswell as trying to see the new growth for a more sustainable forest, which is currently growing. The question is, how easy it is to see, especially as the new trees are still in the initial growth phase. 

In terms of the working environment, we would like to generate thematic files, which we can then use to come together and integrate them to a fully fledged report. The standard procedure should be defined together, then we split into (mostly) solo work and then we come together to integrate the results. 

Links for Research:
Dying of the trees
https://www.harzinfo.de/naturlandschaft-harz/initiative-der-wald-ruft/hintergruende

New vegetation growth
https://www.ndr.de/nachrichten/niedersachsen/braunschweig_harz_goettingen/Nach-Waldsterben-Junger-Mischwald-im-Harz-entwickelt-sich-2025-gut,mischwald100.html

Nagendra, H. (2001). Using remote sensing to assess biodiversity. International Journal of Remote Sensing, 22(12), 2377–2400. https://doi.org/10.1080/01431160117096

Turner, W., Spector, S., Gardiner, N., Fladeland, M., Sterling, E., & Steininger, M. (2003). Remote sensing for biodiversity science and conservation. Trends in Ecology & Evolution, 18(6), 306–314. doi:10.1016/S0169-5347(03)00070-3

Siebert C, Brauns M, Remmler P, Geyer S, Sauke F, Musolff A, Lechtenfeld O, Herzsprung P, Cheng M, Schmidt S, Rode M, Friese K (2025) The Harz Mountain Observatory: a hydro-ecological observatory for long-term effects of large-scale forest change. ARPHA Conference Abstracts 8: e155870. https://doi.org/10.3897/aca.8.e155870

Seidl, R., Müller, J., Hothorn, T., Bässler, C., Heurich, M. and Kautz, M. (2016), Small beetle, large-scale drivers: how regional and landscape factors affect outbreaks of the European spruce bark beetle. J Appl Ecol, 53: 530-540. https://doi.org/10.1111/1365-2664.12540 


Interesting topics: 
- Deforestation
- Influence on air quality
- Influence on heat retention
- Influence on land slides frequency
  - Newspaper-Database to enrich dataset 
- Influence on Biodiversity
- Temporal-spatial analysis of respective areas
- Spread of bark beetle?
  - Maybe: Other dataset containing exactly that --> Trees dying = beetle is there
  - Compare areas that are not affected, even though it is still forest (maybe even monoculture) 

Roles: 

- Current selection of topics:

Phil: deforestation, air quality, land slides

Aarya: Heat retention

Randy: Biodiversity

## Conda Env Installation

Run the following commands to create the conda environment:  
```
conda env create -n eopf -f environment_eopf.yml
```
Then activate the environment and create the kernel for use in jupyter notebook.
```
python -m ipykernel install --user --name eopf --display-name "Python (eopf)"
```
Then, select the kernel in a jupyter notebook. Kernel -> Change Kernel -> Python (eopf)  
When you are using the xarray-eopf or xcube-eopf modules, you must run this shim:
```
try:
    from xcube_resampling.constants import AggMethods  # if it exists, fine
except Exception:
    from xcube_resampling.constants import AGG_METHODS as AggMethods
```