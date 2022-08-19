import numpy as np
from import_data import unpack_data_dict

def first_stage_nonlinear_gradient(ActualPositions,theta_squared, data_dict,Alpha):
    """ Calculates the evaluated Gradient at the current position
    """
    
    Departments, Facility, DepartmentsDependencies = unpack_data_dict(data_dict)

    n = len(DepartmentsDependencies)
    x = ActualPositions[range(0,n)] # Extract x coordinates of actual positions
    y = ActualPositions[range(n,2*n)] # Extract y coordinates of actual positions
    x_grad = np.zeros((n,))
    y_grad = np.zeros((n,))

    # Calculate distance matrix
    D_ij = np.zeros((n,n))
    for i in range(n):
        for j in range(i+1,n):
            D_ij[i,j] = (x[i]-x[j])**2 + (y[i]-y[j])**2
    
    #calculating K; size: 1 x 1 Array
    K = np.zeros(shape=(1)) 
    K = Alpha * sum(DepartmentsDependencies[i,j] for i in range(n) for j in range(n) if i<j)


    # calculate gradient
    for t in range(n):
        # gradient for x_t
        x_first_sum = sum((-2*DepartmentsDependencies[j,t]*(x[j]-x[t]) + K*(2*theta_squared[j,t]/(((x[j]-x[t])**2+(y[j]-y[t])**2)**2))*(x[j]-x[t])) for j in range(t) if j != t)
        x_second_sum = sum((2*DepartmentsDependencies[t,j]*(x[t]-x[j]) + K*(-2*theta_squared[t,j]/(((x[t]-x[j])**2+(y[t]-y[j])**2)**2))*(x[t]-x[j])) for j in range(t,n) if j != t)
        x_grad[t] = x_first_sum + x_second_sum
        # gradient for y_t
        y_first_sum = sum((-2*DepartmentsDependencies[j,t]*(y[j]-y[t]) + K*(2*theta_squared[j,t]/(((x[j]-x[t])**2+(y[j]-y[t])**2)**2))*(y[j]-y[t])) for j in range(t) if j != t)
        y_second_sum = sum((2*DepartmentsDependencies[t,j]*(y[t]-y[j]) + K*(-2*theta_squared[t,j]/(((x[t]-x[j])**2+(y[t]-y[j])**2)**2))*(y[t]-y[j])) for j in range(t,n) if j != t)
        y_grad[t] = y_first_sum + y_second_sum


    gradient_evaluated = np.concatenate((x_grad, y_grad), axis=None) # transform to combined vector

    
    return gradient_evaluated

def first_stage_nonlinear_objective(ActualPositions,theta_squared,data_dict,Alpha):
    """Calculates the objective value at the current position
    """

    Departments, Facility, DepartmentsDependencies = unpack_data_dict(data_dict)

    # preparation of objective
    n = len(DepartmentsDependencies)
    x = ActualPositions[range(0,n)] # Extract x coordinates of actual positions
    y = ActualPositions[range(n,2*n)] # Extract y coordinates of actual positions
    
    # Calculate distance matrix
    D_ij = np.zeros((n,n))
    for i in range(n):
        for j in range(i+1,n):
            D_ij[i,j] = (x[i]-x[j])**2 + (y[i]-y[j])**2
    
    #calculating K; size: 1 x 1 Array
    K = np.zeros(shape=(1)) 
    K = Alpha * sum(DepartmentsDependencies[i,j] for i in range(n) for j in range(n) if i<j)


    function_value = sum((DepartmentsDependencies[i,j]*D_ij[i,j] + K*(theta_squared[i,j]/D_ij[i,j] - 1)) for i in range(n) for j in range(n) if i<j)
    
    return function_value