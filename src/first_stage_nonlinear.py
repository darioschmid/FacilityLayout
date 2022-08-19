import pandas as pd
import numpy as np
from first_stage_nonlinear_gradient_descent import first_stage_nonlinear_gradient_descent
from import_data import unpack_data_dict

def first_stage_nonlinear(data_dict, Alpha):
    """ Executes the first stage with gradient descent by preprocessing the data and calling the actual gradient descent method.
         Input: - data_dict: extract information about departments and facility
                - Alpha: for calculating param K
         Output: - DepartmentsXYrelative: coordinates of the relative positions of the departments
    """

    Departments, Facility, DepartmentsDependencies = unpack_data_dict(data_dict)

    # Define Start positions, maybe many startpositions and call grad_descent for every position
    # to not get stuck in local optimum
    n = len(Departments)   #number of departments
    w_F = float(Facility.iloc[0]['w']) #width of facility 
    h_F = float(Facility.iloc[0]['h']) #height of facility
    # np.random.seed(42) # to reproduce solution
    x_Dep = np.random.uniform(low=-1/2 * w_F, high=1/2 * w_F, size=(n,)).astype(float) # random positions in range of facility width
    y_Dep = np.random.uniform(low=-1/2 * h_F, high=1/2 * h_F, size=(n,)).astype(float) # random positions in range of facility height
    x_Dep = x_Dep.tolist()
    y_Dep = y_Dep.tolist()
    DepartmentsStartDict = {
        "x": x_Dep,
        "y": y_Dep
    }
    StartPositions = pd.DataFrame(data=DepartmentsStartDict)
    StartPositions = pd.merge(Departments["name"], StartPositions, left_index=True, right_index=True)

    # Transform StartPositions to array
    StartPositions = StartPositions[["x","y"]].to_numpy()
    # Transform DepartmentsWidthHeight to array
    w = Departments["w"].to_numpy()  #converting the width of the departments into an numpy array of length n
    h = Departments["h"].to_numpy()  #converting the height of the departments into an numpy array of length n

    # Calculate teta_squared
    theta_squared = np.zeros(shape=(n,n))
    for i in range(n):
        for j in range(n):
            theta_squared[i,j] = 1/4 * ((w[i]+w[j])**2 + (h[i]+h[j])**2)

    # Calculate Optimal positions
    DepartmentsXYrelative = first_stage_nonlinear_gradient_descent(StartPositions,theta_squared, data_dict,Alpha)

    # Extract x and y coordinates
    x = DepartmentsXYrelative[range(0,n)]
    y = DepartmentsXYrelative[range(n,2*n)]

    # Transform to list
    x = x.tolist()
    y = y.tolist()

    # Transform to Dataframe
    DepartmentsOptPosDict = {
        "x": x,
        "y": y
    }
    OptPos = pd.DataFrame(data=DepartmentsOptPosDict)
    DepartmentsXYrelative = pd.merge(Departments["name"], OptPos, left_index=True, right_index=True)

    return DepartmentsXYrelative