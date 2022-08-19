import pandas as pd
import numpy as np
from import_data import unpack_data_dict

def rotate_facility(DepartmentsXY, data_dict, data_dict_original):
    '''
    If optimal solution chose a rotated facility, the whole Layout is flipped back;
    This is done by exchanging width and hight of each department,
    as well as mirroring the positions along the diagonal.
    '''
    Departments, Facility, DepartmentsDependencies = unpack_data_dict(data_dict)
    _, Facility_original, _ = unpack_data_dict(data_dict_original)
    w_F = Facility["w"].to_numpy()
    w_F_o = Facility_original["w"].to_numpy()
    h_F_o = Facility_original["h"].to_numpy()


    # rotate everything back if facility was rotated
    if (w_F != w_F_o):
        Facility["w"] = w_F_o
        Facility["h"] = h_F_o
        x = DepartmentsXY["x"].to_numpy()
        y = DepartmentsXY["y"].to_numpy()
        DepartmentsXY["x"] = y
        DepartmentsXY["y"] = x
        w = Departments["w"].to_numpy()
        h = Departments["h"].to_numpy()
        Departments["w"] = h
        Departments["h"] = w

    # Create outputdict
    data_dict = {
        "Departments": Departments,
        "Facility": Facility,
        "DepartmentsDependencies": DepartmentsDependencies,
    }
    return DepartmentsXY, data_dict