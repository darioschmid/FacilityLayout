import pandas as pd
import numpy as np
from scipy.optimize import minimize
from import_data import unpack_data_dict



def first_stage_scipy_minimize(data_dict, Alpha):
    """Iteratively calls the first stage nonlinear optimization problem and chooses the best solution."""

    n = 1  # Number of iterations
    ObjValues = []  # Array in which we record the objective values of the iterations
    ObjValue = -1

    for i in range(n):
        prevObjValue = ObjValue
        DepartmentsXYrelativeTemp, ObjValue = first_stage_iteration(data_dict, Alpha)
        if(ObjValue < prevObjValue or prevObjValue == -1):
            DepartmentsXYrelative = DepartmentsXYrelativeTemp
        ObjValues.append(ObjValue)

    # Messages for debugging purposes
    #print("Objective values are", ObjValues)
    if n > 1:
        print(f"Mean is {np.mean(ObjValues)} with standard derivation {np.std(ObjValues)} resulting in a gap of {round(100 * np.std(ObjValues) / np.mean(ObjValues), 2)}%")

    return DepartmentsXYrelative



def first_stage_iteration(data_dict, Alpha):
    """Actually solves the nonlinear attractor-repeller optimization problem (without non-overlap constraints) using scipy.optimize.minimize."""

    ##############  Import constants  ##############

    Departments, Facility, DepartmentsDependencies = unpack_data_dict(data_dict)

    n = len(Departments)   #number of departments
    w_F = float(Facility.iloc[0]['w']) #width of facility 
    h_F = float(Facility.iloc[0]['h']) #height of facility 
    w = Departments["w"].to_numpy()  #converting the width of the departments into an numpy array of length n
    h = Departments["h"].to_numpy()  #converting the height of the departments into an numpy array of length n
    c = DepartmentsDependencies #numpy-Array with the Dependencies between the departments, n rows and n columns



    ##############  Preprocessing for the objective function  ##############

    #calculating the thetas; size: n x n array
    theta_squared = np.zeros(shape=(n,n))
    for i in range(n):
        for j in range(n):
            theta_squared[i,j] = 1/4 * ((w[i]+w[j])**2 + (h[i]+h[j])**2)

    #calculating K; size: 1 x 1 Array
    K = np.zeros(shape=(1)) 
    K = Alpha * sum(c[i,j] for i in range(n) for j in range(n) if i<j)



    ##############  Objective function  ##############

    def objective(params):
        params = params.reshape(2, n)
        x = params[0]
        y = params[1]
        # Calculate matrix D
        D = np.zeros((n, n))
        for i in range(n):
            for j in range(n):
                D[i,j] = np.sqrt((x[i] - x[j])**2 + (y[i] - y[j])**2)

        return sum([c[i,j] * D[i,j] + K * (theta_squared[i,j]/D[i,j] - 1) for i in range(n) for j in range(n) if i<j])



    ##############  Constraints  ##############

    cons = []

    for i in range(n):
        #def f1(params, i=i):
        def f1(params):
            params = params.reshape(2, n)
            x = params[0]
            y = params[1]
            return 1/2 * (float(w[i]) - w_F) - x[i]
        cons.append({'type': 'ineq', 'fun': f1})
        #def f2(params, i=i):
        def f2(params):
            params = params.reshape(2, n)
            x = params[0]
            y = params[1]
            return x[i] - 1/2 * (w_F - float(w[i]))
        cons.append({'type': 'ineq', 'fun': f2})
        #def f3(params, i=i):
        def f3(params):
            params = params.reshape(2, n)
            x = params[0]
            y = params[1]
            return 1/2 * (float(h[i]) - h_F) - y[i]
        cons.append({'type': 'ineq', 'fun': f3})
        #def f4(params, i=i):
        def f4(params):
            params = params.reshape(2, n)
            x = params[0]
            y = params[1]
            return y[i] - 1/2 * (h_F - float(h[i]))
        cons.append({'type': 'ineq', 'fun': f4})



    ##############  Output  ##############

    #np.random.seed(17)
    x0 = np.random.uniform(low=-1/2 * w_F, high=1/2 * w_F , size=(n,)).astype(float)
    y0 = np.random.uniform(low=-1/2 * h_F, high=1/2 * h_F , size=(n,)).astype(float)

    params = np.concatenate((x0, y0))

    options = {
        "maxiter": 10**2,
        "disp": False
    }

    sol = minimize(objective, params, method='SLSQP', constraints=cons, options=options)
    #print(sol)

    output = sol["x"]
    output = np.array(output).reshape(2, n)
    x = output[0]
    y = output[1]
    #print("x =", x)
    #print("y =", y)


    # Create DataFrames for Output

    DepartmentsXYrelativeDict = {
        "x": x,
        "y": y
    }

    DepartmentsXYrelative = pd.DataFrame(data=DepartmentsXYrelativeDict)
    DepartmentsXYrelative = pd.merge(Departments["name"], DepartmentsXYrelative, left_index=True, right_index=True)
    ObjValue = sol["fun"]

    return DepartmentsXYrelative, ObjValue


