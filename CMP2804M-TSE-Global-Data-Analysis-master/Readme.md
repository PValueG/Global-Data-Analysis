# TSE Global Data Analyis Tool (GDAT)
----------------------------------
**GDAT licensed under the GPLv3, example datasets sourced from the World bank under the Creative Commons Attribution 4.0 (CC-BY 4.0) licence**

---------------------------------

## About GDAT
GDAT is a Python platform for building interactive dashboards, for uni or bivariate analysis of global datasets.
With GDAT you can create various visualisations such as histograms, scatter plots and choropleths of your chosen variables,
as well as compute various descriptive statistical measures.
## Downloading & Running locally
To Download and Run GDAT locally on your machine:
### Requirements
* A valid installation of Python 3.x.x, with Pip for package management
* Optional: Virtualenv installation
### Steps (Assumes a Linux/Unix system)

1. Clone this repository to your machine
2. CD into the root directory, and if desired configure a virtual enviroment for package installation
3. Run Pip install -r ./requirements.txt, to install the required packages
4. Run, Python index.py and navigate to 0.0.0.0:8050 in your browser of choice to access the application


## Using GDAT

Upload or select an existing dataset


[Populate menu]

Select the X and Y variables you wish to analyse 
* Optional: Select normalisation or transformation of variables
* Optional: Select a country column 'Country code' if you wish to  compare global statistics
* Optional: Select a colourscheme for the world map and graphs to be generated  to


[Create dashboard]

Breakdown statistics and a Correlation/Variance graph will be generated alongside a
global heatmap is generated if selected.
Various graphs can then be created based upon the variables selected.


[Graph Selection]


Select the graph
*Optional: Select additonal graph features (such as using colour scheme)

[Create Graph]

That specific graph will then be created based upon the variable selected.
Additonal graphs can be created in the same way.
Datasets are also available for preview as well as to download locally if chosen.



## Transformations

Min-max normalisation.
* An operation which rescales a set of data, and is useful when comparing data from two different scales or converting to a new scale, data is normalised to fit a target range of [0,1]

Z score normalisation.
* An operation which normalises a set of data using z scores and the normal distribution curve, similar to Min-max but handles outliers better at the cost of not producing data with the exact same scale.

Power transform Non-Gaussian variables.
* A way to convert data which cannot be normally distributed into one that can through the use of Power transformations. Allows advanced analysis and statistical breakdowns on datasets contain non-normal data.

Scatter plot OLS Linear regression
* Plots a line of regression on the scatter plot based on the 'Ordinary least squares' method to estimate unknown parameters in a linear regression model.

Scatter plot LOWESS regression
* Plots a smooth curve between the variables on the scatter plot based on the 'Locally Weighted Scatter-plot Smoother', giving an indication of how well the model fits the summary data.


## Example Scenario:
worldBank2011.csv is selected.


[Populate Menu]
Population, total is selected for the X-Axis variable.


Population growth (annual %) is selected for the Y-Axis Variable.


No normalisation is selected.


Transform Non-Gaussian variables is selected.


Country code is selected.


blues is selected.


[Create dashboard]


Scatter Plot is selected.


None is selected.


Use default colours is selected.


[Graph Selection]


[Create Box Plot]


## Direct contributors
* Thomas Burrows
* Eden Benson
* Joseph Brentnall
* Patrick Goodall
* Ethan Henderson
* Christopher Lovesey
* Thomas Sarno

