import numpy as np
from import_data import unpack_data_dict


def grouping(data_dict, GroupingValue=0.5):
    """
    This function lets the program know if grouping of the departments is desired. This function should be called before running the optimization
    Input parameters: 
        - data_dict: dictionary containing:
            - Departments: DataFrame containing all Departments' name, width, and height
            - Facility: DataFrame containing facility's name, width, and height.
            - DepartmentsDependencies: transport costs between the departments, using a matrix. Currently unused, but this may change in the future. Originally intended to indicate the dependencies among the departments (with lines or the like).
    Output:
        data_dict_grouped: updated data_dict with updated DepartmentsDependencies
    """

    Departments, Facility, DepartmentsDependencies = unpack_data_dict(data_dict)

    # c_hat:  weight to be added to dependencies
    c_hat = GroupingValue*np.max(DepartmentsDependencies)

    # n:  number of departments
    n = Departments.shape[0]

    # groups: array of group numbers
    groups = Departments["group"]


    # maxgroup:  max index of a group
    maxgroup = np.max(groups)


    # Updating the DepartmentsDependencies according to the groups by adding a set weight c_hat
    for i in range(n):
        # loop to put departments with no group number into their own group
        if np.isnan(groups[i]) == True:
            groups[i] = maxgroup + 1
            maxgroup += 1
        for j in range(i+1,n):
            if groups[i] == groups[j]:
                DepartmentsDependencies[i,j] = DepartmentsDependencies[i,j] + c_hat 
    
    
    
    #update Departments with updated group column for consistency
    Departments["group"] = groups.astype(int)

    data_dict_grouped = {
        "Departments": Departments,
        "Facility": Facility,
        "DepartmentsDependencies": DepartmentsDependencies,
    }
    
    return data_dict_grouped
