from first_stage_scipy_minimize import first_stage_scipy_minimize
from first_stage_nonlinear import first_stage_nonlinear


def first_stage(data_dict, Alpha, method="gradient_descent"):
    """
    This function executes the first stage. with the "method" option you can specify what method this function will use.
    Call the function like this:
        - To use the gradient descent function we implemented ourselves, call:
            first_stage(data_dict, Alpha, method="gradient_descent")
          or
            first_stage(data_dict, Alpha)

        - To use the minimize function of scipy.optimize, call:
            first_stage(data_dict, Alpha, method="scipy_minimize")
    """
    
    
    if method == "gradient_descent":
        #print("Using default method Gradient descent ...")
        return first_stage_nonlinear(data_dict, Alpha)
    elif method == "scipy_minimize":
        #print("Using method scipy.optimize.minimize ...")
        return first_stage_scipy_minimize(data_dict, Alpha)
    else:
        raise ValueError('Wrong usage of "method". Set it to "gradient_descent", "scipy_minimize", or leave it blank.')
