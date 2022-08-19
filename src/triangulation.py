#from facility_layout.first_model.main import DepartmentsAlpha
import numpy as np

def triangulation(DepartmentsXYrelative):
    """ Calculates Alpha and Beta matrices to determine the relative postions. The input is the output of the first stage.
    """

    # input: Dataframe 
    #   +---+----------+----+----+
    #   |   |   name   |  x |  y |
    #   +---+----------+----+----+
    #   | 0 | Lager    | -5 |  0 |
    #   | 1 | Versand  |  3 |  3 |
    #   | 2 | Drechsel |  3 | -2 |
    #   +---+----------+----+----+
    # output: two 2-dim arrays with values for alpha_ij and ß_ij

    # get number of departments
    num_departments = DepartmentsXYrelative.shape[0]

    DepartmentsAlpha = np.zeros((num_departments,num_departments))
    DepartmentsBeta = np.zeros((num_departments,num_departments))

    # transform DepartmentsXYrelative to numpy 
    DepartmentsXYrelative = DepartmentsXYrelative.to_numpy()
    # form x coordinates
    x = DepartmentsXYrelative[:,1]
    # form y coordinates
    y = DepartmentsXYrelative[:,2]

    for i in range(num_departments):
        for j in range(i+1,num_departments):
            if abs(x[i]-x[j]) >= abs(y[i]-y[j]):
                if x[i] >= x[j]:
                    # i right of j
                    DepartmentsAlpha[i,j] = 0
                    DepartmentsAlpha[j,i] = 1
                else:
                    # i left of j
                    DepartmentsAlpha[i,j] = 1
                    DepartmentsAlpha[j,i] = 0
            elif y[i] >= y[j]:
                # i above j
                DepartmentsBeta[i,j] = 0
                DepartmentsBeta[j,i] = 1
            else:
                # i below j
                DepartmentsBeta[i,j] = 1
                DepartmentsBeta[j,i] = 0


    return DepartmentsAlpha, DepartmentsBeta