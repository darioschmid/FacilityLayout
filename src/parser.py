import configparser
import os


def parseIni(iniPath):
    """This function reads from the settings.ini file and turns every entry into a variable and returns these in a dictionary.
    Sections are ignored."""
    config = configparser.ConfigParser()  # Initialize config parser object
    config.optionxform = str  # Ensures upper and lower case is NOT ignored
    config.read(iniPath)  # Read from ini file

    collection = {}  # Initialize output dict

    # Iterate through every key in every section and store its key and value as a new entry in collection dict.
    # The actual section a key + value is in is irrelevant, but there are still three sections in settings.ini for clarity.
    for section in config:
        #print(f"Current section is {section}")
        for key in config[section]:
            #print(f"Current key is {key} with value {config[section][key]=}")
            # Store key and value in collection, where we automatically cast the value to its best fitting type
            collection[key] = convert(config[section][key])



    return collection


def convert(input):
    """This function smartly casts a string to integer, float, bool, or leave it as a string, depending on its content."""

    assert isinstance(input, str), "Input is not a string!"

    # Try to convert to integer
    try:
        casted = int(input)
        return casted
    except ValueError:
        pass

    # Try to convert to float
    try:
        casted = float(input)
        return casted
    except ValueError:
        pass

    # Try to convert to bool
    if input.lower() == "true":
        return True
    elif input.lower() == "false":
        return False

    # No appropriate data type was found, just return string input.
    return input


# DEBUGGING
if __name__ == "__main__":
    """Test all various strings which could be in a .ini file"""
    print("")
    print("Testing convert function...")
    print(f'{convert("Test")=}')
    print(f'{type(convert("Test"))=}')
    print(f'{convert("2")=}')
    print(f'{type(convert("2"))=}')
    print(f'{convert("2.0")=}')
    print(f'{type(convert("2.0"))=}')
    print(f'{convert("True")=}')
    print(f'{type(convert("True"))=}')
    print(f'{convert("False")=}')
    print(f'{type(convert("False"))=}')
    print("\n")

    """Test parseIni function"""
    print("Test parseIni function")
    print(parseIni(os.path.dirname(__file__) + "/../settings.ini"))
