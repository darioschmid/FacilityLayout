from import_data import unpack_data_dict

def change_facility_rot(data_dict):
    """
    This function rotates the facility, i.e., swaps the width and height of it.
    Input parameters:
        data_dict: dictionary containing:
            - Departments: DataFrame containing all Departments' name, width, and height
            - Facility: DataFrame containing facility's name, width, and height.
            - DepartmentsDependencies: transport costs between the departments, using a matrix. Currently unused, but this may change in the future. Originally intended to indicate the dependencies among the departments (with lines or the like).
    Output: 
        - data_dict_rot: dictionary with rotated facility dimensions
    """

    Departments, Facility, DepartmentsDependencies = unpack_data_dict(data_dict)

    w = Facility["w"]
    h = Facility["h"]
    # rotate the facility
    w_new = h
    h_new = w
    # save in dataframe Facility
    Facility["w"] = w_new
    Facility["h"] = h_new

    # saving as new dictionary
    data_dict_rot = {
        "Departments": Departments,
        "Facility": Facility,
        "DepartmentsDependencies": DepartmentsDependencies,
    }
    return data_dict_rot