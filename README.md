# `autoplius.lt` car price devaluation dashboard

Website demo: https://autoplius-deval.herokuapp.com/

## Description

This repository is made out of 2 parts:

* dash app,
* iJupyter notebooks.

## Project stucture

Dash app:

* `app.py` main python file for running dashboard,
* `utils.py` helper functions to select specific data for graphs,
* `Procfile` file is needed to host website on `heroku.com`.

Notebooks `/Notebooks`:

* `data_scraping_explained.ipynb` describes how data was scraped from autoplius.lt,
* `data_analysis.ipynb` prototypes plotly graphs and creates simple model for estimating car's price devaluation,
* `/images` sub-folder for storing images for notebooks locally.

## Project requirements

`requirements.txt` file contains list of required libraries to run app on local machine or host on Heroku website.