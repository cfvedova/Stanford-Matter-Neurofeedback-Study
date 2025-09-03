import numpy as np
from bvbabel.prt import read_prt



def create_prt():

    """Create TurboBrainVoyager PRT file with default values."""

    header = dict()
    # -------------------------------------------------------------------------
    # PRT Header (Version 2)
    # -------------------------------------------------------------------------

    header['FileVersion'] = '2'
    header['ResolutionOfTime'] = 'Volumes'
    header['Experiment'] = ''
    header['BackgroundColor'] = '0 0 0'
    header['TextColor'] = '255 255 255'
    header['TimeCourseColor'] = '255 255 255'
    header['TimeCourseThick'] = '3'
    header['ReferenceFuncColor'] = '0 0 80'
    header['ReferenceFuncThick'] = '3'
    header['NrOfConditions'] = 1

    # -------------------------------------------------------------------------
    # PRT Condition Info
    # -------------------------------------------------------------------------

    data_prt = list()

    for i in range(header['NrOfConditions']):

        data_prt.append(dict())

        # Add condition name
        data_prt[i]["NameOfCondition"] = 'Rest'

        # Add condition occurances
        data_prt[i]["NrOfOccurances"] = 1

        # Add timings
        data_prt[i]["Time start"] = int(1)
        data_prt[i]["Time stop"] = int(2)

        # Add color
        data_prt[i]["Color"] = np.asarray([64, 64, 64])


    return header, data_prt


def write_prt(filename, header, data_prt):

    """Protocol to write TurboBrainVoyager PRT file.

    Parameters
    ----------
    filename : string
        Path to file.
    header : dictionary
        Protocol (PRT) header.
    data_prt : list of dictionaries


    """

    with open(filename, 'w') as f:
        f.write("\n")

        data = header["FileVersion"]
        f.write("FileVersion:        {}\n".format(data))
        f.write("\n")

        data = header["ResolutionOfTime"]
        f.write("ResolutionOfTime:   {}\n".format(data))
        f.write("\n")

        data = header["Experiment"]
        f.write("Experiment:         {}\n".format(data))
        f.write("\n")

        data = header["BackgroundColor"]
        f.write("BackgroundColor:    {}\n".format(data))
        data = header["TextColor"]
        f.write("TextColor:          {}\n".format(data))
        data = header["TimeCourseColor"]
        f.write("TimeCourseColor:    {}\n".format(data))
        data = header["TimeCourseThick"]
        f.write("TimeCourseThick:    {}\n".format(data))
        data = header["ReferenceFuncColor"]
        f.write("ReferenceFuncColor: {}\n".format(data))
        data = header["ReferenceFuncThick"]
        f.write("ReferenceFuncThick: {}\n".format(data))
        f.write("\n")

        data = header["NrOfConditions"]
        f.write("NrOfConditions: {}\n".format(data))

        for i in range(len(data_prt)):
            f.write("\n")
            data = data_prt[i]["NameOfCondition"]
            f.write("{}\n".format(data))
            data = data_prt[i]["NrOfOccurances"]
            f.write("{}\n".format(data))

            for j in range(data_prt[i]["NrOfOccurances"]):
                value1 = data_prt[i]["Time start"][j]
                value2 = data_prt[i]["Time stop"][j]
                if header["ResolutionOfTime"].lower() == "volumes":
                    value1 = int(value1)
                    value2 = int(value2)


                f.write(f"{value1:>4} {value2:>4}\n")

            data = data_prt[i]["Color"]
            f.write("Color: {} {} {}\n".format(data[0], data[1], data[2]))


