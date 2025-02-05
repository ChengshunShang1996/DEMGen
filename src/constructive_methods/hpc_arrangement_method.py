#/////////////////////////////////////////////////
__author__      = "Chengshun Shang (CIMNE)"
__copyright__   = "Copyright (C) 2023-present by Chengshun Shang"
__version__     = "0.0.1"
__maintainer__  = "Chengshun Shang"
__email__       = "cshang@cimne.upc.edu"
__status__      = "development"
__date__        = "June 21, 2024"
__license__     = "BSD 2-Clause License"
#/////////////////////////////////////////////////

from constructive_methods.constructive_method import ConstructiveMethod

class HpcArrangementMethod(ConstructiveMethod):

    def __init__(self) -> None:

        pass
    
    def CreateInitialPackings(self):

        p_id = 1
        i_row = 1
        i_col = 1
        i_thick = 1
        domain_length_x = self.parameters["domain_length_x"]
        domain_length_y = self.parameters["domain_length_y"]
        domain_length_z = self.parameters["domain_length_z"]
        r = self.parameters["particle_radius_max"]
        is_round = self.parameters["is_round_option"]
        ini_point_x = -0.5 * domain_length_x
        ini_point_y = -0.5 * domain_length_y
        ini_point_z = -0.5 * domain_length_z
        while i_row <= domain_length_x / ( 2.0 * r):
            while i_col <= domain_length_y / ((6**0.5 * 2 /3) * r):
                while i_thick <= domain_length_z / ( 3**0.5 * r):
                    if is_round:
                        if i_col % 2 != 0 :
                            if i_thick % 2 == 0:
                                p_x = (2.0 * i_row) * r + ini_point_x
                            else:
                                p_x = (2.0 * i_row - 1.0) * r + ini_point_x
                        else:
                            if i_thick % 2 == 0:
                                p_x = (2.0 * i_row - 1.0) * r + ini_point_x
                            else:
                                p_x = (2.0 * i_row) * r + ini_point_x
                        
                        p_y = r + (i_col - 1.0) * ((6**0.5 * 2 /3) * r) + ini_point_y

                        if i_col % 2 == 0 :
                            p_z = (3**0.5 / 3 + 1) * r + (i_thick - 1) * (3**0.5 * r) + ini_point_z
                        else:
                            p_z = r + (i_thick - 1) * (3**0.5 * r) + ini_point_z

                        p_x = round(p_x, 5)
                        p_y = round(p_y, 5)
                        p_z = round(p_z, 5)
                        
                    else:
                        if i_col % 2 != 0 :
                            if i_thick % 2 == 0:
                                p_x = (2.0 * i_row) * r + ini_point_x
                            else:
                                p_x = (2.0 * i_row - 1.0) * r + ini_point_x
                        else:
                            if i_thick % 2 == 0:
                                p_x = (2.0 * i_row - 1.0) * r + ini_point_x
                            else:
                                p_x = (2.0 * i_row) * r + ini_point_x
                        
                        p_y = r + (i_col - 1.0) * ((6**0.5 * 2 /3) * r) + ini_point_y

                        if i_col % 2 == 0 :
                            p_z = (3**0.5 / 3 + 1) * r + (i_thick - 1) * (3**0.5 * r) + ini_point_z
                        else:
                            p_z = r + (i_thick - 1) * (3**0.5 * r) + ini_point_z

                    p_parameter_dict = {
                        "id" : p_id,
                        "p_x" : p_x,
                        "p_y" : p_y,
                        "p_z" : p_z,
                        "radius" : r,
                        "p_v_x" : 0.0,
                        "p_v_y" : 0.0,
                        "p_v_z" : 0.0,
                        "p_ele_id": p_id,
                        "p_group_id": 0
                        }
                    self.particle_list.append(p_parameter_dict)
                    p_id = p_id + 1
                    i_thick += 1
                i_col += 1
                i_thick = 1
            i_row += 1
            i_col = 1
        print("Create HPC spheres finished!\t")