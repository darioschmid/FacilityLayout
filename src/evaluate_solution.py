import pandas as pd
from import_data import unpack_data_dict

def evaluate_solution(DepartmentsXYoptimal, data_dict):
    """ This function evaluates the solution
         Input: 
             - DepartmentsXYoptimal: optimal coordinates of the centers of the departments
             - data_dict: optimal data_dict
         Output:
             - width of rectangular area occupied by the layout
             - height of the rectangular area occupied by the layout
             - rectangular area occupied by the layout
    """

    Departments, Facility, DepartmentsDependencies = unpack_data_dict(data_dict)

    df = pd.merge(DepartmentsXYoptimal,Departments,on='name')

    # calculate most left point
    df['left_end'] = df['x'] - 0.5*df['w']
    # calculate most right point
    df['right_end'] = df['x'] + 0.5*df['w']
    # calculate most upper point
    df['upper_end'] = df['y'] + 0.5*df['h']
    # calculate most lower point
    df['lower_end'] = df['y'] - 0.5*df['h']

    # columns of df to calculate min and max values
    min_df = df[['left_end','lower_end']]
    max_df = df[['right_end','upper_end']]

    # calculate min and max values (directly transformed to numpy array)
    min_val = min_df.min().values
    max_val = max_df.max().values

    # calculate lenght and height of generatet solution
    val = max_val - min_val
    Area = val[0]*val[1]

    # Define Dataframe
    dict = {'w': [val[0]], 'h': [val[1]], 'Area': [Area]}
    solution_eval = pd.DataFrame(data=dict)
    
    

    return val[0], val[1], Area