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


from data_processing.pre_processing import creat_fem_and_inlet_mesh_files

class GravitationalDepositionMethod():

    def __init__(self) -> None:

        pass

    def Initialization(self, parameters, ini_path):

        self.parameters = parameters
        self.ini_path = ini_path

    def CreatInitialCases(self):
        CreatIniCases = creat_fem_and_inlet_mesh_files.CreatFemAndInletMeshFiles()
        RVE_size = [self.parameters["domain_length_x"], self.parameters["domain_length_y"], self.parameters["domain_length_z"]]
        CreatIniCases.Initialize(RVE_size, self.parameters["particle_radius_max"], self.parameters["packing_num"], self.ini_path)
        problem_name = self.parameters["problem_name"]
        CreatIniCases.CreatFemMeshFile(problem_name)
        CreatIniCases.CreatInletMeshFile(problem_name, self.parameters["inlet_properties"])
        CreatIniCases.CreatDemMeshFile(problem_name)

    def RunDEM(self):

        pass

    def Run(self, parameters, ini_path):

        self.Initialization(parameters, ini_path)
        self.CreatInitialCases()
        self.RunDEM()