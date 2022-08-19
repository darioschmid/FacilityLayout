import numpy as np
from first_stage_nonlinear_gradient import first_stage_nonlinear_gradient
from first_stage_nonlinear_gradient import first_stage_nonlinear_objective

def first_stage_nonlinear_gradient_descent(StartPositions,theta_squared, data_dict,Alpha):
    """ Executes the gradient descent of the first stage
         Input:
             - StartPositions: nx2 array [x,y]
             - DepartmentsWidthHeight: nx2 array [w,h]
             - DepartmentsDependencies: nxn array upper triangular
             - Alpha to specify param K

    """
    # input: - StartPositions: nx2 array [x,y]
    #        - DepartmentsWidthHeight: nx2 array [w,h]
    #        - DepartmentsDependencies: nxn array upper triangular
    #        - Alpha to specify param K

    
    # params for gradient descent
    max_iters = 10000
    tolerance = 0.00000000000001 # for difference of gradient
    iters = 0
    alpha0 = 1 # Startvalue for ArmijoLineSearch, standard value for this in literature

    ActualPositions = StartPositions.flatten('F') # transform matrix of positions into vector
    # form: [x_1, x_2, x_3,..., x_n, y_1, y_2, y_3,...., y_n]

    function_evaluated = first_stage_nonlinear_objective(ActualPositions, theta_squared, data_dict, Alpha)
    gradient_evaluated = first_stage_nonlinear_gradient(ActualPositions, theta_squared, data_dict, Alpha)
    gradient_evaluated_norm = np.linalg.norm(gradient_evaluated)
    gradient_difference = gradient_evaluated_norm

    print('Initial condition: y = {:.4f}, x = {} \n'.format(function_evaluated, ActualPositions))

    while gradient_difference > tolerance and iters < max_iters:
        old_function_evaluated = gradient_evaluated_norm
        SearchDirection = -gradient_evaluated
        rate, function_evaluated = ArmijoLineSearch(ActualPositions,SearchDirection,gradient_evaluated,function_evaluated,alpha0,theta_squared,data_dict,Alpha,rho=0.5,c1=1e-4)
        ActualPositions = ActualPositions + rate*SearchDirection # Gradientstep
        gradient_evaluated = first_stage_nonlinear_gradient(ActualPositions, theta_squared, data_dict, Alpha)
        gradient_evaluated_norm = np.linalg.norm(gradient_evaluated)
        gradient_difference = np.abs(old_function_evaluated-gradient_evaluated_norm)
        iters = iters + 1
        #print('Iteration: {} \t y = {:.4f}, x = {}, gradient = {:.4f}'.
        #      format(iters, function_evaluated, ActualPositions, gradient_evaluated_norm))

    if iters == max_iters:
            print('\nGradient descent does not converge.')
    else:
        print('\nSolution: \t Iteration: {}, y = {:.4f}, x = {}'.format(iters, function_evaluated, ActualPositions))

    opt_positions = ActualPositions

    return opt_positions

def ArmijoLineSearch(ActualPositions,SearchDirection,ActualGradient,ActualFunction,alpha0,theta_squared,data_dict,Alpha,rho=0.5,c1=1e-4):
    """ Executes the Armijo LineSearch Algorithm for generating the step length of the gradient descent method
    """

    derphi0 = np.dot(ActualGradient, SearchDirection) # intermediate step
    NewPositions = ActualPositions + alpha0*SearchDirection # intermediate step
    phi_a0 = first_stage_nonlinear_objective(NewPositions,theta_squared,data_dict,Alpha) # function value when going with length alpha0 in Searchdirection

    while not phi_a0 <= ActualFunction + c1*alpha0*derphi0:
        alpha0 = alpha0 * rho # shrink step length
        NewPositions = ActualPositions + alpha0*SearchDirection
        phi_a0 = first_stage_nonlinear_objective(NewPositions,theta_squared,data_dict,Alpha) # function value when going with new length alpha0 in Searchdirection

    steplength = alpha0
    function_evaluated = phi_a0

    return steplength, function_evaluated