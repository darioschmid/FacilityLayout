import time
import copy
import warnings
import sys
import os
import numpy as np


# Importing all the other functions needed
from import_data import import_data
from grouping import grouping
from change_facility_rot import change_facility_rot
from visualize import visualize
from evaluate_solution import evaluate_solution
from first_stage import first_stage
from triangulation import triangulation
from second_stage import second_stage
from heuristic_relpos_loop import heuristic_relpos_loop
from export_data import export_data
from rotate_facility import rotate_facility




def main_function(ExcelFileInformation, ExcelFileTransportFlow, ExcelFileTransportMeans, ExcelFilesOutputPath, Alpha=0.5, Grouping=False, GroupingValue=0.5, Method="gradient_descent", Min="cost", Iterations=10, VisualizationFirstStagePath="visualization_first_stage.png", VisualizationPath="visualization.png", drawLabels=True):

    """This function executes the entire problem.

        Input:
            - ExcelFilesPath: Path to the directory where the Excel files with the input data is saved.
            - ExcelFilesOutputPath: Path to where the Excel Files with the output data should be saved.
            - Alpha: Constant controlling the repulsion of the departments in the first stage. 0 < Alpha <= 1.
            - Grouping: Specify whether grouping will be active or not
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

    # Record how much time the script takes
    startSeconds = time.time()
    
    # Validate that all input parameters have the correct type and are defined correctly
    validateInput(ExcelFileInformation, ExcelFileTransportFlow, ExcelFileTransportMeans, ExcelFilesOutputPath, Alpha, Grouping, GroupingValue, Method, Min, Iterations, VisualizationFirstStagePath, VisualizationPath, drawLabels)
    
    srcDir = os.path.dirname(__file__)
    # Prepare for gurobi Logs Folder
    if not os.path.exists(srcDir + "/gurobiLogs/"):
        os.makedirs(srcDir + "/gurobiLogs/")





    print("""
###########################
######  Import Data  ######
###########################
    """)
    """Here we import the data from the excel files to DataFrames and a numpy matrix."""

    # Import all relevant data from excel files into DataFrames
    data_dict = import_data(ExcelFileInformation, ExcelFileTransportFlow, ExcelFileTransportMeans)
    print("Successfully imported the necessary data from the Excel files.")





    print("""
########################
######  Grouping  ######
########################
    """)
    """Here we modify the imported data to implement grouping of departments;
    We increase the dependencies between departments in the same group. This means that they will be closer together in the end."""

    # Evaluate whether grouping should be active in the first place.
    # If Grouping is active, but all grouping variables are not set, we set Grouping to False.
    # If Grouping is not active, nothing happens.
    Grouping = Grouping and not np.all(np.isnan(data_dict["Departments"]["group"].to_numpy()))

    # Grouping if needed
    if Grouping:
        data_dict = grouping(data_dict, GroupingValue)
        print("The Departments are grouped.")
    else:
        print("The Departments are not grouped.") 





    print("""
###############################
######  Iteration Start  ######
###############################
    """)
    """We execute our optimization steps multiple times, because we get different solutions (or sometimes even no solutions at all) in every execution. For that purpose we must keep track of the solutions and their objective values, whose setup we do here."""

    # Save the original data_dict to use it in every iteration
    data_dict_original = copy.deepcopy(data_dict)

    # initialize list for the variables which need to be saved
    DepartmentsXYrelative_list = []
    DepartmentsAlpha_list = []
    DepartmentsBeta_list = []
    DepartmentsXYoptimal_list = []
    obj_val_list = []
    area_list = []
    data_dict_list = []
    success_list = []

    # unnecessary since the programm stops if no solution is found
    #success = False  # Initialize success variable. After the loop we will know if we ever had success executing the second stage.
    print("Trying to solve the optimization problem...")
    for i in range(Iterations):
        # Preprocessing data dict
        data_dict = copy.deepcopy(data_dict_original)  # Start with the original data dict





        """
###############################
######  Rotate Facility  ######
###############################
        """
        """Here we rotate the facility in every other iteration. We do this because it can change the objective value."""
        if i%2:
            data_dict = change_facility_rot(data_dict)





        f"""
#################################################
######  Executing First Stage Iteration {i+1}  ######
#################################################
        """
        """Here we execute the first step of the optimization. TODO: Mehr Details"""

        DepartmentsXYrelative = first_stage(data_dict, Alpha, method=Method)
        #print("")  # Empty print statement for spacing
        if DepartmentsXYrelative is None:
            raise ValueError("First stage failed, DepartmentsXYrelative is empty.")
        #print("Successfully solved the first stage. Following relative positions were calculated:")
        #print(DepartmentsXYrelative)


        # adjust list
        DepartmentsXYrelative_list.append(copy.deepcopy(DepartmentsXYrelative))





        f"""
###################################################
######  Executing Triangulation Iteration {i+1}  ######
###################################################
        """
        """Here we determine the alpha and beta matrices which encode the relative positions of the departments. If department i is on the left of department j, alpha[i,j] = 1, otherwise alpha[i,j] = 0. Similarly beta[i,j] = 1 if i is below j, otherwise beta[i,j] = 0. Note that between two departments only the bigger relation of left/right or up/down is considered, i.e., two departments can only lay left/right OR above/below each other. This means we have alpha[i,j] + alpha[j,i] + beta[i,j] + beta[j,i] = 1, for all 1 <= i < j <= n."""

        # Do Comparison/Triangulation to get the relative positions of the departments
        DepartmentsAlpha, DepartmentsBeta = triangulation(DepartmentsXYrelative)
        if DepartmentsAlpha is None or DepartmentsBeta is None:
            raise ValueError("Triangulation step failed, DepartmentsAlpha or DepartmentsBeta is empty.")
        #print("Successfully executed Triangulation step. Following Alphas and Betas were calculated:")
        #print("Alpha = ", DepartmentsAlpha, sep="\n")
        #print("Beta = ", DepartmentsBeta, sep="\n")


        # adjust list
        DepartmentsAlpha_list.append(copy.deepcopy(DepartmentsAlpha))
        DepartmentsBeta_list.append(copy.deepcopy(DepartmentsBeta))





        f"""
##################################################
######  Executing Second Stage Iteration {i+1}  ######
##################################################
        """
        """Here we execute the second step of the optimization. We use Gurobi to solve the rest of the optimization problem, but with easier to solve non-overlap constraints, thanks to the alpha and beta matrices."""

        # Trying to solve second stage
        try:
            DepartmentsXYoptimal, data_dict, obj_val = second_stage(DepartmentsAlpha, DepartmentsBeta, data_dict_original, output=srcDir + "/gurobiLogs/" + f"GurobiLogsHeuristicIteration{i}.log")
            success = True
            # Adjust lists by deepcopy of the new generated variables
            DepartmentsXYoptimal_list.append(copy.deepcopy(DepartmentsXYoptimal))
            obj_val_list.append(copy.deepcopy(obj_val))
            width, height, area = evaluate_solution(DepartmentsXYoptimal, data_dict)
            area_list.append(copy.deepcopy(area))
            data_dict_list.append(copy.deepcopy(data_dict))
            success_list.append(True)
            print(f"Iteration {i+1}/{Iterations}: Success ✅")
        except ValueError:
            # Generate Dummy entries for the lists such that it is possible to get optimal layout
            DepartmentsXYoptimal_list.append(0)
            obj_val_list.append(0)
            area_list.append(0)
            data_dict_list.append(0)
            success_list.append(False)
            print(f"Iteration {i+1}/{Iterations}: Failure ❌")





    """
######################################
######  Iteration Verification  ######
######################################
    """
    # check if everything is correct in previous step
    correct = False
    lengths_list = [len(DepartmentsXYrelative_list),len(DepartmentsAlpha_list),len(DepartmentsBeta_list),len(DepartmentsXYoptimal_list),len(obj_val_list),len(area_list),len(data_dict_list),len(success_list)]
    if all(v == Iterations for v in lengths_list):
        correct = True
    if not correct:
        print("There is a problem with storing the information during the iterations.")
        return


    opt_index = find_best_solution(Min, obj_val_list, area_list)





    """
####################################
######  Iteration Management  ######
####################################
    """
    # reassign optimal layout for later heuristic
    DepartmentsXYrelative = DepartmentsXYrelative_list[opt_index]
    DepartmentsAlpha = DepartmentsAlpha_list[opt_index]
    DepartmentsBeta = DepartmentsBeta_list[opt_index]
    DepartmentsXYoptimal = DepartmentsXYoptimal_list[opt_index]
    obj_val = obj_val_list[opt_index]
    data_dict = data_dict_list[opt_index]





    print("""
###################################################
######  Executing Postprocessing Heuristics  ######
###################################################
    """)
    """Here we execute postprocessing heuristics trying to improve the solution. For that purpose we modify some entries of the alpha and beta matrices."""

    # Alpha-Beta Heuristic (change relative positions) to close some gaps
    heuristic_iterations = 5
    DepartmentsAlpha, DepartmentsBeta, DepartmentsXYoptimal, data_dict, obj_value = heuristic_relpos_loop(Alpha, data_dict, DepartmentsXYoptimal, DepartmentsAlpha, DepartmentsBeta, obj_val, iterations=heuristic_iterations, dir=srcDir + "/gurobiLogs/")





    print("""
#######################################
######  Generate Visualizations  ######
#######################################
    """)

    # rotate Facility Layout back to original format of facility
    DepartmentsXYoptimal, data_dict = rotate_facility(DepartmentsXYoptimal, data_dict, data_dict_original)

    # Visualize the solution 
    visualize(data_dict, DepartmentsXYrelative, VisualizationFirstStagePath, Grouping=Grouping, useFacility=False, drawLabels=drawLabels)
    visualize(data_dict, DepartmentsXYoptimal, VisualizationPath, Grouping=Grouping, drawLabels=drawLabels)





    print("""
##################################
######  Exporting to Excel  ######
##################################
    """)
    # Export data to an Excel files importable by visTable
    export_data(ExcelFilesOutputPath, ExcelFileTransportFlow, DepartmentsXYoptimal, data_dict)





    print("""
#######################
######  Summary  ######
#######################
    """)

    # Print the objective Value
    print('The location of the departments are:', DepartmentsXYoptimal, sep="\n")
    print('The objective value is:', obj_val, "(quality of the solution, less means better)")

    # Get measure for size of created solution
    width, height, area = evaluate_solution(DepartmentsXYoptimal, data_dict)
    print('The rectangular area occupied by the solution is:', area)
    print('The width is:', width, 'and the height is:', height)

    # Print number of successful tries
    number_success = sum(success_list)
    print('The success rate is: ', number_success, '/', Iterations)
    
    # Record how much time the script takes
    endSeconds = time.time()



    # Print how much time the script took
    deltaSeconds = int(endSeconds - startSeconds) + 1
    print("This script took", time.strftime("%Hh %Mm %Ss", time.gmtime(deltaSeconds)))



    return





def validateInput(ExcelFileInformation, ExcelFileTransportFlow, ExcelFileTransportMeans, ExcelFilesOutputPath, Alpha, Grouping, GroupingValue, Method, Min, Iterations, VisualizationFirstStagePath, VisualizationPath, drawText):
    """This function checks for type and value errors in the inputs of the main_function."""


    # Check input for type errors
    
    if not isinstance(ExcelFileInformation, str):
        raise TypeError("The ExcelFileInformation is not a string.")
    
    if not isinstance(ExcelFileTransportFlow, str):
        raise TypeError("The ExcelFileTransportFlow is not a string.")
    
    if not isinstance(ExcelFileTransportMeans, str):
        raise TypeError("The ExcelFileTransportMeans is not a string.")
    
    if not isinstance(ExcelFilesOutputPath, str):
        raise TypeError("The Excelfile output path is not a string.")

    if not isinstance(Alpha, float):
        raise TypeError("The Variable Alpha is not a floating point number.")

    if not isinstance(Grouping, bool):
        raise TypeError("The variable Grouping is not a bool.")

    if not isinstance(Iterations, int):
        raise TypeError("The variable Iterations is not an integer.")

    if not isinstance(VisualizationFirstStagePath, str):
        raise TypeError("The name of the visualization of the first stage is not a string.")

    if not isinstance(VisualizationPath, str):
        raise TypeError("The name of the visualization is not a string.")
    
    if not isinstance(drawText, bool):
        raise TypeError("The variable drawText is not a bool.")


    # Check input for value errors

    if Iterations == 0:
        raise ValueError("There is no Iteration. Increase the number of Iterations to at least 1.")

    if not (Method == "gradient_descent" or Method == "scipy_minimize"):
        raise ValueError('The variable Method is wrongly specified. Available options: "scipy_minimize", "gradient_descent"')
    
    if not (0 <= GroupingValue and GroupingValue <= 1):
        raise ValueError('The variable GroupingValue is not between 0 and 1.')

    if not (Min == "cost" or Min == "area"):
        raise ValueError('The variable Min is wrongly specified. Available options: "cost", "area"')

    if not VisualizationFirstStagePath.endswith(".png"):
        warnings.warn("The name of the visualization of the first stage does not end with '.png'")

    if not VisualizationPath.endswith(".png"):
        warnings.warn("The name of the visualization does not end with '.png'")


    return





def find_best_solution(Min, obj_val_list, area_list):
    """This function chooses the best solution based on obj_val_list or area_list"""

    index_list = []  # Initialize empty index list

    # Check which minimization type we have. A deep copy is not needed here.
    if Min == "cost":
        val_list = obj_val_list
    elif Min == "area":
        val_list = area_list
    else:
        raise Exception('Fatal error: Min is neither "cost" nor "area", which actually should be noticed by validateInput()')


    # Stop method if no solution is found
    if all(b == 0 for b in val_list):
        print(f"""
################################################################################
######  There is no solution to this problem. The facility is too small.  ######
######  Use larger facility or increase number of iterations.             ######
################################################################################
    """)
        sys.exit(0)  # Quit program if we find no solution
    
    # Get indices of unsuccessful tries
    for k in range(len(val_list)):
        if val_list[k] == 0:
            index_list.append(k)
    # Increase entries of unsuccessful tries such that they cannot be optimal
    for kk in range(len(index_list)):
        val_list[index_list[kk]]= max(val_list) + 1
    # Get optimal index
    opt_index = val_list.index(min(val_list))
    
    return opt_index
