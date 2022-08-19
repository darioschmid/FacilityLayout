from import_data import unpack_data_dict

def heuristic_relpos(DepartmentsXY, data_dict, DepartmentsAlpha, DepartmentsBeta):

    """
    This function defines a heuristic to close some gaps between departments. 
    Input parameters: 
        - DepartmentsXY: DataFrame containing X- and Y- coordinates of the departments
        - data_dict: dictionary containing:
            - Departments: DataFrame containing all Departments' name, width, and height
            - Facility: DataFrame containing facility's name, width, and height.
            - DepartmentsDependencies: transport costs between the departments, using a matrix. Currently unused, but this may change in the future. Originally intended to indicate the dependencies among the departments (with lines or the like).
        - DepartmentsAlpha: Binary Dataframe for the relative positions
        - DepartmentsBeta: Binary Dataframe for the relative positions
    Output: 
        - DepartmentsAlpha: Binary Dataframe for the updated relative positions
        - DepartmentsBeta: Binary Dataframe for the updated relative positions
        - changed: Boolean variable, 
            - True if the Dataframes DepartmentsAlpha and DepartmentsBeta have been changed
            - False if the Dataframes DepartmentsAlpha and DepartmentsBeta have not been changed
    
    """
    
    Departments, _, _ = unpack_data_dict(data_dict)

    n = DepartmentsXY.shape[0]
    x = DepartmentsXY["x"].to_numpy()
    y = DepartmentsXY["y"].to_numpy()
    w = Departments["w"].to_numpy() 
    h = Departments["h"].to_numpy()
    changed = False
    for i in range(n):
        for j in range(i+1,n):
            if DepartmentsAlpha[i,j]==1 or DepartmentsAlpha[j,i]==1:
                if y[i]+0.5*h[i] <= y[j]-0.5*h[j]:
                    DepartmentsBeta[i,j] = 1
                    DepartmentsAlpha[i,j] = 0
                    DepartmentsAlpha[j,i] = 0
                    changed = True
                elif y[j]+0.5*h[j] <= y[i]-0.5*h[i]:
                    DepartmentsBeta[j,i] = 1 
                    DepartmentsAlpha[i,j] = 0
                    DepartmentsAlpha[j,i] = 0
                    changed = True
            else:
                if x[i]+0.5*w[i] <= x[j]-0.5*w[j]:
                    DepartmentsAlpha[i,j] = 1
                    DepartmentsBeta[i,j] = 0
                    DepartmentsBeta[j,i] = 0
                    changed = True
                elif x[j]+0.5*w[j] <= x[i]-0.5*w[i]:
                    DepartmentsAlpha[j,i] = 1 
                    DepartmentsBeta[i,j] = 0
                    DepartmentsBeta[j,i] = 0
                    changed = True


    return DepartmentsAlpha, DepartmentsBeta, changed