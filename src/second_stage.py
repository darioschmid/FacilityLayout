import gurobipy as gp
from gurobipy import GRB
import pandas as pd
import numpy as np
from import_data import unpack_data_dict

def second_stage(DepartmentsAlpha, DepartmentsBeta, data_dict, output=""):
    """
    This is the second stage of the two-step-approach.
    In this stage we place the departments inside of the facility. In contrast to the first stage, we include the non-overlap constraints, although be it - thanks to the relative positions (matrices alpha and beta) determined by the triangulation - in a more simple form.
    We use Gurobi to solve this Linear Program.
    """
    
    Departments, Facility, DepartmentsDependencies = unpack_data_dict(data_dict)

    model = gp.Model('second_stage')  # Initiating the model
    if output:
        model.setParam('LogToConsole', 0)  # Suppress the console logs if desired
        model.setParam('LogFile', output)  # Enable logging to file

    ##############  Initilizing the data  ##############

    #width: always in x-direction
    #height: always in y -direction
    
    n = len(DepartmentsAlpha)   #number of departments
    c = DepartmentsDependencies #Dataframe with the Dependencies between the departments, n rows and n columns
    w = Departments["w"].to_numpy()  #converting the width of the departments into an numpy array of length n
    h = Departments["h"].to_numpy()  #converting the height of the departments into an numpy array of length n
    alpha = DepartmentsAlpha    #matrix/array of the alphas (relative locations); size: n x n; alpha[i][j]= 1 if department i is on the left of j, 0 else
    beta = DepartmentsBeta  #matrix/array of the betas (relative locations); size: n x n; beta[i][j]= 1 if department i is on the below of j. 0 else
    w_F = float(Facility.iloc[0]['w']) #width of facility 
    h_F = float(Facility.iloc[0]['h']) #height of facility 


    ##############  Variables  ##############


    # Two distance variables; size: n x n matrices; d_x[i][j]= distance between facilities i and j in x-direction, d_y accordingly
    d_x = model.addVars(n, n, vtype=GRB.CONTINUOUS, name="d_x")
    d_y = model.addVars(n, n, vtype=GRB.CONTINUOUS, name="d_y")
    
    # Two variables; size: n x 1; x-, y-coordinates of the departments
   
    x = model.addVars(n, lb=-GRB.INFINITY, vtype=GRB.CONTINUOUS, name="x")
    y = model.addVars(n, lb=-GRB.INFINITY, vtype=GRB.CONTINUOUS, name="y")

    # Indicator variable for rotation of departments, r = 1: not rotated, r = 0: rotated by 90°
    # r_F: \in {0,1}, 1 if no rotation of facility, 0 if facility is rotated
    # w_F_hat, h_F_hat: number, new width and height of facility
    r = model.addVars(n, vtype=GRB.BINARY, name="r")
    r_F = model.addVar(vtype=GRB.BINARY, name="r_F")
    w_F_hat = model.addVar(vtype=GRB.CONTINUOUS, name ="w_F_hat")
    h_F_hat = model.addVar(vtype=GRB.CONTINUOUS, name ="h_F_hat")


    
    ##############  Constraints  ##############

    #Constraints for the linearization of the objective function
    constr0 = model.addConstrs(d_x[i,j] >= x[i] - x[j] for i in range(n) for j in range(n) if i < j)
    constr1 = model.addConstrs(d_x[i,j] >= x[j] - x[i] for i in range(n) for j in range(n) if i < j)
    constr2 = model.addConstrs(d_y[i,j] >= y[i] - y[j] for i in range(n) for j in range(n) if i < j)
    constr3 = model.addConstrs(d_y[i,j] >= y[j] - y[i] for i in range(n) for j in range(n) if i < j)


    #Constraints to make sure the departments are inside the facility
    constr4 = model.addConstrs(1/2 * (r[i]*float(w[i])+(1-r[i])*float(h[i]) - (w_F_hat)) <= x[i] for i in range(n))
    constr5 = model.addConstrs(1/2 * ((w_F_hat) - (r[i]*float(w[i])+(1-r[i])*float(h[i]))) >= x[i] for i in range(n))
    constr6 = model.addConstrs(1/2 * ((1-r[i])*float(w[i])+r[i]*float(h[i]) -  (h_F_hat)) <= y[i] for i in range(n))
    constr7 = model.addConstrs(1/2 * (h_F_hat - ((1-r[i])*float(w[i])+r[i]*float(h[i]))) >= y[i] for i in range(n))

    
    #non-overlap constraints
    constr8 = model.addConstrs(x[i] + 1/2 * (r[i]*float(w[i])+(1-r[i])*float(h[i])) <= x[j] - 1/2 * (r[j]*float(w[j])+(1-r[j])*float(h[j])) + w_F_hat * (1 - alpha[i,j]) for i in range(n) for j in range(n) if i != j)
    constr9 = model.addConstrs(y[i] + 1/2 * ((1-r[i])*float(w[i])+r[i]*float(h[i])) <= y[j] - 1/2 * ((1-r[j])*float(w[j])+r[j]*float(h[j])) + h_F_hat * (1 - beta[i,j]) for i in range(n) for j in range(n) if i != j)
    
    #rotation constraints
    constr10 = model.addConstr(w_F_hat == r_F*w_F + (1-r_F)*h_F)
    constr11 = model.addConstr(h_F_hat == (1-r_F)*w_F + r_F*h_F)

    ##############  Objective function  ##############
    

    model.setObjective(sum(c[i,j] * (d_x[i,j] + d_y[i,j]) for i in range(n) for j in range(i+1, n)), GRB.MINIMIZE)

    #Optimizing
    model.optimize()

    # Raise error if model is infeasible
    if model.status == GRB.INFEASIBLE:
        raise ValueError('Model is infeasible.')
    elif model.status != GRB.OPTIMAL:
        raise ValueError('Model does not have an optimal value.')
    #print("model.status =", model.status)

    ansX = []
    ansY = []
    ansr = []
    ansr_F = r_F.x
    
    for i in range(n):
        ansX.append(x[i].x)
        ansY.append(y[i].x)
        ansr.append(r[i].x)


    DepartmentsXYDict = {
        "x": ansX,
        "y": ansY
    }
    ansr = np.array(ansr)
    ansr_F = np.array(ansr_F)
    
    DepartmentsXY = pd.DataFrame(data=DepartmentsXYDict)

    DepartmentsXY = pd.merge(Departments["name"], DepartmentsXY, left_index=True, right_index=True)

    # setting new widh and hight for departments and facility as rotations might occur
    w_new = (ansr*w) + (1-ansr)*h
    h_new = (1-ansr)*w + ansr*h
    w_F_new = (ansr_F*w_F) + (1-ansr_F)*h_F
    h_F_new = (1-ansr_F)*w_F + ansr_F*h_F

    Departments["w"] = w_new
    Departments["h"] = h_new
    Facility["w"] = w_F_new
    Facility["h"] = h_F_new

    data_dict = {
        "Departments": Departments,
        "Facility": Facility,
        "DepartmentsDependencies": DepartmentsDependencies,
    }
    # saving the objective value for later usage
    obj_val = model.objVal
    
    return DepartmentsXY, data_dict, obj_val
