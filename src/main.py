##################################################
## Facility Layout
##################################################
# This project was created in 2022 by Sarah Gräßle, Julia Schmalzbauer, Dario Schmid, and Andreas Seger
# as part of a case study in discrete optimization at Technical University Munich, Germany. This project aims to 
# solve the mathematical facility layout problem using a two-stage approach with nonlinear and linear
# optimization. For this purpose, we use scipy.optimize.minimize and our own implementation of
# gradient descent for the nonlinear part, and Gurobi for the integer program.
# This project was completed with the help of our supervisor at Technical University Munich, Dr. Michael Ritter, and Constantin
# Radzio at Voith Turbo GmbH, Garching bei München.
__author__ = "Sarah Gräßle, Julia Schmalzbauer, Dario Schmid, Andreas Seger"
__credits__ = ["Sarah Gräßle", "Julia Schmalzbauer", "Dario Schmid", "Andreas Seger"]
__emails__ = ["sarah.graessle@tum.de", "julia.schmalzbauer@tum.de", "da.schmid@tum.de", "andreas.seger@tum.de"]
##################################################




from main_function import main_function
import os
import sys
import logger
import parser

# IMPORTANT!!!
# Please install Python 3 and all packages used in this project. See README.md for more details.



"""This script executes the entire problem.

    Input (defined in "settings.ini"):
        - ExcelFilesPath: Path to the directory where the Excel files with the input data is saved.
        - ExcelFilesOutputPath: Path to where the Excel Files with the output data should be saved.
        - Alpha: Constant controlling the repulsion of the departments in the first stage. 0 < Alpha <= 1.
        - Grouping: Defines whether grouping will be active or not. Must be True or False.
        - Method:
            - "gradient_descent" to use the gradient descent function we implemented ourselves to solve the first stage
            - "scipy_minimize" to use the minimize function of scipy.optimize to solve the first stage 
        - Min: Defines after which criterion the solution will be chosen from all available iteration solutions. Note that this does NOT change the optimization objective, which will always be to minimize the total cost, not the total area.
            - "cost" opt solution with respect to cost
            - "area" opt solution with respect ro area
        - Iterations: Number of iterations of first and second stage
        - NameVisualizationFirstStage: Name of the file that stores the image of the visualization of the first stage (e.g. "visualization_main_first_stage.png")
        - NameVisualization: Name of the file that stores the image of the visualization of the solution (e.g."visualization_main.png")
    
    Output:
        - Console log logs the result of the various preparation and optimization steps. We took special care to make this function especially easy to read, so please take the time to read it. It explains what every step does, see the individual function definitions for more details.
        - Visualizations: This program generates two visualizations (of first and second optimization step). It can be used as an intermediate step to inspect the output of this program without having to import it into visTable.
        - Excel Output File: Excel File with the determined x- and y-coordinates of the departments. Can be directly imported into visTable.
"""


# Start logging console output to log file
logFileName = "FacilityLayout.log"
sys.stdout = logger.Logger(logFileName)


rootDir = os.path.dirname(__file__) + "/../"  # Root directory of this repo (i.e., where files like README.md and requirements.txt are located)
constants = parser.parseIni(rootDir + "settings.ini")  # Parse all constants in .ini file to single dictionary


# Set all constants from constants dictionary
ExcelFilesInputPath = rootDir + constants["ExcelFilesInputPath"]
ExcelFileInformation = ExcelFilesInputPath + "/" + constants["ExcelFileInformation"]
ExcelFileTransportFlow = ExcelFilesInputPath + "/" + constants["ExcelFileTransportFlow"]
ExcelFileTransportMeans = ExcelFilesInputPath + "/" + constants["ExcelFileTransportMeans"]
ExcelFilesOutputPath = rootDir + constants["ExcelFilesOutputPath"]
Alpha = constants["Alpha"]
Grouping = constants["Grouping"]
GroupingValue = constants["GroupingValue"]
Method = constants["Method"]
Min = constants["Min"]
Iterations = constants["Iterations"]
VisualizationFirstStagePath = rootDir + constants["VisualizationFirstStagePath"]
VisualizationPath = rootDir + constants["VisualizationPath"]
drawLabels = constants["drawLabels"]


main_function(ExcelFileInformation, ExcelFileTransportFlow, ExcelFileTransportMeans, ExcelFilesOutputPath, Alpha=Alpha, Grouping=Grouping, GroupingValue=GroupingValue, Method=Method, Min=Min, Iterations=Iterations, VisualizationFirstStagePath=VisualizationFirstStagePath, VisualizationPath=VisualizationPath, drawLabels=drawLabels)


# Stop logging to "FacilityLayout.log"
sys.stdout.close()
