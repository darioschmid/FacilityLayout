import gurobipy as gp
from gurobipy import GRB
import pandas as pd
import numpy as np
from import_data import unpack_data_dict
import os
import parser
from import_data import import_data
from visualize import visualize
import time

def first_model(data_dict):
    """
    This function solves the whole optimization problem formulated for the first model using Gurobi. In particular, this linear program includes the unmodified, more difficult non-overlap constraints mentioned in the technical documentation and therefore has a significantly longer running time compared to the two-stage-approach.
    """

    Departments, Facility, DepartmentsDependencies = unpack_data_dict(data_dict)

    model = gp.Model('first_model') #Initiating the model

    ##############  Initilizing the data  ##############

    #width: always in x-direction
    #height: always in y -direction
    
    n = len(Departments)   #number of departments
    c = DepartmentsDependencies #Dataframe with the Dependencies between the departments, n rows and n columns
    w = Departments["w"].to_numpy()  #converting the width of the departments into an numpy array of length n
    h = Departments["h"].to_numpy()  #converting the height of the departments into an numpy array of length n
    w_F = float(Facility.iloc[0]['w']) #width of facility 
    h_F = float(Facility.iloc[0]['h']) #height of facility 


    ##############  Variables  ##############


    # Two distance variables; size: n x n matrices; d_x[i][j]= distance between facilities i and j in x-direction, d_y accordingly
    d_x = model.addVars(n, n, vtype=GRB.CONTINUOUS, name="d_x")
    d_y = model.addVars(n, n, vtype=GRB.CONTINUOUS, name="d_y")
    
    #Two variables; size: n x 1; x-, y-coordinates of the departments
    x = model.addVars(n, lb=-GRB.INFINITY, vtype=GRB.CONTINUOUS, name="x")
    y = model.addVars(n, lb=-GRB.INFINITY, vtype=GRB.CONTINUOUS, name="y")

    #Alphas and Betas for relative arrangement
    alpha = model.addVars(n, n, vtype=GRB.BINARY, name="alpha")  #matrix/array of the alphas (relative locations); size: n x n; alpha[i][j]= 1 if department i is on the left of j, 0 else
    beta = model.addVars(n, n, vtype=GRB.BINARY, name="beta")  #matrix/array of the betas (relative locations); size: n x n; beta[i][j]= 1 if department i is on the below of j. 0 else

    
    ##############  Constraints  ##############
    

    #Constraints for the linearization of the objective function
    constr0 = model.addConstrs(d_x[i,j] >= x[i] - x[j] for i in range(n) for j in range(n) if i < j)
    constr1 = model.addConstrs(d_x[i,j] >= x[j] - x[i] for i in range(n) for j in range(n) if i < j)
    constr2 = model.addConstrs(d_y[i,j] >= y[i] - y[j] for i in range(n) for j in range(n) if i < j)
    constr3 = model.addConstrs(d_y[i,j] >= y[j] - y[i] for i in range(n) for j in range(n) if i < j)


    #Constraints to make sure the departments are inside the facility
    constr4 = model.addConstrs(1/2 * (float(w[i]) - w_F) <= x[i] for i in range(n))
    constr5 = model.addConstrs(1/2 * (w_F - float(w[i])) >= x[i] for i in range(n))
    constr6 = model.addConstrs(1/2 * (float(h[i]) - h_F) <= y[i] for i in range(n))
    constr7 = model.addConstrs(1/2 * (h_F - float(h[i])) >= y[i] for i in range(n))

   
    #non-overlap constraints
    constr8 = model.addConstrs(x[i] + 1/2 * float(w[i]) <= x[j] - 1/2 * float(w[j]) + w_F * (1 - alpha[i,j]) for i in range(n) for j in range(n) if i != j)
    constr9 = model.addConstrs(y[i] + 1/2 * float(h[i]) <= y[j] - 1/2 * float(h[j]) + h_F * (1 - beta[i,j]) for i in range(n) for j in range(n) if i != j)

    #Alpha Beta constraints
    constr10 = model.addConstrs(alpha[i,j] + alpha[j,i] + beta[i,j] + beta[j,i] == 1 for i in range(n) for j in range(n) if i < j)
    

    ##############  Objective function  ##############
    

    model.setObjective(sum(c[i,j] * (d_x[i,j] + d_y[i,j]) for i in range(n) for j in range(i+1, n)), GRB.MINIMIZE)

    #Optimizing
    model.optimize()

    ansX = []
    ansY = []
    
    for i in range(n):
        ansX.append(x[i].x)
        ansY.append(y[i].x)


    DepartmentsXYDict = {
        "x": ansX,
        "y": ansY
    }

    DepartmentsXY = pd.DataFrame(data=DepartmentsXYDict)

    DepartmentsXY = pd.merge(Departments["name"], DepartmentsXY, left_index=True, right_index=True)
    
    data_dict = {
        "Departments": Departments,
        "Facility": Facility,
        "DepartmentsDependencies": DepartmentsDependencies,
    }
    
    return DepartmentsXY, data_dict




# Record how much time the script takes
startSeconds = time.time()


rootDir = os.path.dirname(__file__) + "/../"  # Root directory of this repo (i.e., where files like README.md and requirements.txt are located)
constants = parser.parseIni(rootDir + "settings.ini")  # Parse all constants in .ini file to single dictionary

ExcelFilesInputPath = rootDir + constants["ExcelFilesInputPath"]
ExcelFileInformation = ExcelFilesInputPath + "/Information.xlsx"
ExcelFileTransportFlow = ExcelFilesInputPath + "/Transportflow.xlsx"
ExcelFileTransportMeans = ExcelFilesInputPath + "/Transportmean.xlsx"

print("""
###########################
######  Import Data  ######
###########################
""")
"""Here we import the data from the excel files to DataFrames and a numpy matrix."""

# Import all relevant data from excel files into DataFrames
data_dict = import_data(ExcelFileInformation, ExcelFileTransportFlow, ExcelFileTransportMeans)
# TODO Implement checks of Ecxel files
print("Successfully imported the necessary data from the Excel files.")


DepartmentsXY, data_dict = first_model(data_dict) 

visualize(data_dict, DepartmentsXY, FileName="facility_layout/second_model/visualization_first_stage_10_departments.png", useFacility=True, Grouping=False, drawLabels=False)


    
# Record how much time the script takes
endSeconds = time.time()



# Print how much time the script took
deltaSeconds = int(endSeconds - startSeconds) + 1
print("This script took", time.strftime("%Hh %Mm %Ss", time.gmtime(deltaSeconds)))