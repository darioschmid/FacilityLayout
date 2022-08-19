from import_data import unpack_data_dict
import pandas as pd
import numpy as np

 # output as excel files:
 # Dependencies as Transportflow.xlsx with Names in first coloum and line
 # Departments, DepartmentsXY as Information.xlsx coloumns: name, x[mm], y[mm], z[mm], rotation[°], w[mm], h[mm]
     
def export_data(ExcelFilesOutputPath, ExcelFileTransportFlow, DepartmentsXY, data_dict):
    """
    This function exports the solution data to Excel sheets.
    -'Information.xlsx' contains two sheets, 'Departments': information of the optimal positions of the departments, 'Facility': size of the facility
    -'Transportflow.xlsx' contains the information concerning the product flow, not the costs of transportation
    """
    Departments, Facility, _ = unpack_data_dict(data_dict)
    n = len(Departments)
    names = Departments["name"].to_numpy()
    x = DepartmentsXY["x"].to_numpy()
    y = DepartmentsXY["y"].to_numpy()
    z = np.zeros(n)
    rotation = np.zeros(n)
    w = Departments["w"].to_numpy()
    h = Departments["h"].to_numpy()
    w_F = Facility["w"].to_numpy()
    h_F = Facility["h"].to_numpy()
    name_F = Facility["name"].to_numpy()

    blocksExcelFileName = "Blöcke.xlsx"
    TransportMatrixExcelFileName = "Transportmatrix.xlsx"

    # move Departments so that (0,0) is bottom left corner of facility and not center
    for i in range(n):
        x[i] = x[i] + 0.5*w_F
        y[i] = y[i] + 0.5*h_F

    # get directed dependencies without costs of transport
    DepartmentsDependencies = pd.read_excel(ExcelFileTransportFlow, sheet_name='Flow matrix')
    DepartmentsDependencies = DepartmentsDependencies.to_numpy()
    DepartmentsDependencies = DepartmentsDependencies[:,1:]
    DepartmentsDependencies = DepartmentsDependencies.astype(np.float)
    
    # add names to Dependencies
    transportmatrix = np.c_[names, DepartmentsDependencies]
    names_long = np.append("", names)

    # create blocks matrix
    blocks = np.c_[names, x, y, z, rotation, w, h]
    column_names = ["name", "x[mm]", "y[mm]", "z[mm]", "rotation[°]", "w[mm]", "h[mm]"]

    # create Facility matrix
    facility_exp = np.c_[name_F, w_F, h_F]
    column_facility = ["name", "w[mm]", "h[mm]"]

    # export to excel files
    transportmatrix_df = pd.DataFrame(transportmatrix)
    transportmatrix_df.to_excel(ExcelFilesOutputPath+'/Transportflow.xlsx', sheet_name = 'Transportflow', header = names_long, index = False)

    blocks_df = pd.DataFrame(blocks)
    facility_df = pd.DataFrame(facility_exp)
    writer = pd.ExcelWriter(ExcelFilesOutputPath + '/Information.xlsx')
    blocks_df.to_excel(writer, sheet_name = 'Departments', header = column_names, index = False)
    facility_df.to_excel(writer, sheet_name = 'Facility', header = column_facility, index = False)
    writer.save()

    # Print location of generated exports
    print("Successfully generated export excel sheet 'Transportflow' and saved at", ExcelFilesOutputPath + '/Transportflow.xlsx')
    print("Successfully generated export excel sheet 'Information' and saved at", ExcelFilesOutputPath + '/Information.xlsx')
    
    return