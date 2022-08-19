import numpy as np
import pandas as pd

# consists of two function:
# import_data: input is path of excel files output is dictionary of information 
# unpack_data_dict: input data dict from import data output are components of the datadict

def import_data(ExcelFileInformation, ExcelFileTransportFlow, ExcelFileTransportMeans):
    """
    Import the three Excel files 'imformation.xlsx', 'transportmeans.xlsx' and 'transportflow.xlsm'
      - 'information.xlsx': Two sheets 'Departments', 'Facility'
        - 'Departments': name, width, height, group
        - 'Facility': name, width, height
      - 'transportmeans.xlsx': One sheet 'transport means'
        - 'transport means': name, direkte Transportkosten, fixe Transportkosten
      - 'transportflow.xlsx': Two sheets 'transport matrix', 'transport means matrix'
        - 'Transportmatrix': columns are department names, frequency between departments
        - 'transport means matrix:' columns are department names, transport mean between departments
    
    Return dictionary with entries:
      - 'Departments': Dataframe same shape as the sheet 'Departments' of 'information.xlsx'
      - 'Facility': Dataframe same shape as the sheet 'Facility' of 'information.xlsx'
      - 'DepartmentsDependencies': numpy array of entries in the sheet 'Transportmatrix' of 'transportflow.xlsx' together with direct cost of the assigned transport mean
    """



    # import excelfiles
    Departments = pd.read_excel(ExcelFileInformation, sheet_name='Departments')
    Facility = pd.read_excel(ExcelFileInformation, sheet_name='Facility')
    DepartmentsDependencies = pd.read_excel(ExcelFileTransportFlow, sheet_name='Flow matrix')
    DepartmentsTransportDirect = pd.read_excel(ExcelFileTransportFlow, sheet_name='Mean matrix')
    Transportmittel = pd.read_excel(ExcelFileTransportMeans, sheet_name='Transportmean')

    # rename columns of Departments
    Departments.rename(columns = {'w[mm]':'w', 'h[mm]':'h'}, inplace = True)

    # rename columns of Facility
    Facility.rename(columns = {'w[mm]':'w', 'h[mm]':'h'}, inplace = True)

    # transform DepartmentsDependencies to numpy array
    DepartmentsDependencies = DepartmentsDependencies.to_numpy()
    # eliminate first row
    DepartmentsDependencies = DepartmentsDependencies[:,1:]
    # transform to float
    DepartmentsDependencies = DepartmentsDependencies.astype(np.float)

    # create DepartmentsTransportDirect
    
    # get names of transport means
    transport_names = Transportmittel["name"].to_numpy()
    direct_cost = Transportmittel["variable cost"].to_numpy()
    

    number_transportmeans = len(transport_names)

    # replace NaN in DepartmentsTransportDirect
    DepartmentsTransportDirect = DepartmentsTransportDirect.fillna(0)

    # transform to numpy and remove first column
    DepartmentsTransportDirect = DepartmentsTransportDirect.to_numpy()
    DepartmentsTransportDirect = DepartmentsTransportDirect[:,1:]

    # iterate over both arrays and replace names of transport mean with corresponding direct
    number_departments = len(DepartmentsTransportDirect)
    for i in range(number_departments):
        for j in range(number_departments):
            for k in range(number_transportmeans):
                if DepartmentsTransportDirect[i,j] == transport_names[k]:
                    DepartmentsTransportDirect[i,j] = direct_cost[k]

    # multiplicate dependencies and direct costs of transport
    DepartmentsTransportDirect = DepartmentsTransportDirect.astype(np.float)
    DepartmentsTransportDirect = DepartmentsTransportDirect*DepartmentsDependencies

    # make DepartmentsTransportDirect upper triangular
    DepartmentsTransportDirect_upper = np.triu(DepartmentsTransportDirect, k=0)
    DepartmentsTransportDirect_lower = np.tril(DepartmentsTransportDirect, k=-1)
    DepartmentsTransportDirect_lower = np.transpose(DepartmentsTransportDirect_lower)
    DepartmentsDependencies = DepartmentsTransportDirect_upper + DepartmentsTransportDirect_lower

    # Create outputdict
    data_dict = {
        "Departments": Departments,
        "Facility": Facility,
        "DepartmentsDependencies": DepartmentsDependencies,
    }

    return data_dict

def unpack_data_dict(data_dict):
    """ Unpacks the data_dict into Departments, Facility, DepartmentsDependencies.
    """

    Departments = data_dict["Departments"]
    Facility = data_dict["Facility"]
    DepartmentsDependencies = data_dict["DepartmentsDependencies"]

    # copy the following line if you want to use this method
    # Departments, Facility, DepartmentsDependencies = unpack_data_dict(data_dict)

    return Departments, Facility, DepartmentsDependencies