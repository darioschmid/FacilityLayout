import os
from heuristic_relpos import heuristic_relpos
from second_stage import second_stage

def heuristic_relpos_loop(Alpha, data_dict, DepartmentsXYoptimal, DepartmentsAlpha, DepartmentsBeta, best_obj_val, iterations=5, dir=""):

    """
    This function uses a heuristic to close gaps between departments. It changes some parameters of the relative positions and runs the second stage again.
    Input parameters:
        - Alpha: in (0,1], Parameter for
        - data_dict: dictionary containing:
            - Departments: DataFrame containing all Departments' name, width, and height
            - Facility: DataFrame containing facility's name, width, and height.
            - DepartmentsDependencies: transport costs between the departments, using a matrix. Currently unused, but this may change in the future. Originally intended to indicate the dependencies among the departments (with lines or the like).
        - DepartmentsXYoptimal: DataFrame with the output of the second stage (X- and Y- Coordinates of the departments)
        - DepartmentsAlpha: Binary Dataframe for the relative positions
        - DepartmentsBeta: Binary Dataframe for the relative positions
        - best_obj_val: Integer, best objective value so far
        - iterations: Integer to set the number of iterations
            default: 5
    Output:
        - best_DepartmentsAlpha: Binary Dataframe for the updated relative positions
        - best_DepartmentsBeta: Binary Dataframe for the updated relative positions
        - best_DepartmentsXY:  DataFrame with the updated output of the second stage after changing some relative positions (X- and Y- Coordinates of the departments). Corresponds to the best objective value
        - best_data_dict: dictionary that contains the updated DataFrames corresponding to the best objective value
        - best_obj_value: (updated) best objective value so far 
    """
    
    best_obj_value = best_obj_val
    best_DepartmentsXY = DepartmentsXYoptimal.copy()
    best_data_dict = {key: value.copy() for key, value in data_dict.items()}
    best_DepartmentsAlpha = DepartmentsAlpha.copy()
    best_DepartmentsBeta = DepartmentsBeta.copy()

    for k in range(iterations):
        
        DepartmentsAlpha, DepartmentsBeta, changed = heuristic_relpos(DepartmentsXYoptimal, data_dict, DepartmentsAlpha, DepartmentsBeta)
        if not changed:
            # No Alphas or Betas were changed, skip to next iteration
            break
        print(f"Heuristic modified Alphas or Betas in iteration {k}, optimizing again...")

        DepartmentsXYoptimal, data_dict, obj_val = second_stage(DepartmentsAlpha, DepartmentsBeta, data_dict, output=dir+f"GurobiLogsHeuristicIteration{k}.log")
        
        # update variables with best solution if calculated solution is better
        if obj_val < best_obj_val:
            best_obj_value = obj_val
            best_DepartmentsXY = DepartmentsXYoptimal.copy()
            best_data_dict = {key: value.copy() for key, value in data_dict.items()}
            best_DepartmentsAlpha = DepartmentsAlpha.copy()
            best_DepartmentsBeta = DepartmentsBeta.copy()

    return best_DepartmentsAlpha, best_DepartmentsBeta, best_DepartmentsXY, best_data_dict, best_obj_value
