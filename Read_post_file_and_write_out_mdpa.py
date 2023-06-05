#/////////////////////////////////////////////////
#// Main author: Chengshun Shang (CIMNE)
#// Email: chengshun.shang1996@gmail.com
#// Date: May 2023
#/////////////////////////////////////////////////

import os

class read_and_clone():

    def __init__(self) -> None:
        
        self.p_pram_list = []

    def getParticleDataFromPost(self, aim_mdpa_file_name):
        
        self.p_id = 1
        self.p_record_nodes = False
        self.p_record_elements = False
        self.p_record_radius = False

        if os.path.isfile(aim_mdpa_file_name):
            
            with open(aim_mdpa_file_name, 'r') as mdpa_data:

                for line in mdpa_data:

                    self.p_pram_dict = {
                    "id" : 0,
                    "p_x" : 0.0,
                    "p_y" : 0.0,
                    "p_z" : 0.0,
                    "radius" : 0.0,
                    "p_v_x" : 0.0,
                    "p_v_y" : 0.0,
                    "p_v_z" : 0.0,
                    "p_ele_id": 0,
                    "p_group_id": 0
                    }
                            
                    values = [str(s) for s in line.split()]

                    if len(values) > 1:
                        if values[0] == 'Begin' and values[1] == 'Nodes':
                            self.p_record_nodes = True
                            continue
                        elif values[0] == 'End' and values[1] == 'Nodes':
                            self.p_record_nodes = False

                        if values[0] == 'Begin' and values[1] == 'Elements':
                            self.p_record_elements = True
                            continue
                        elif values[0] == 'End' and values[1] == 'Elements':
                            self.p_record_elements = False

                    if len(values) > 2:
                        if values[0] == 'Begin' and values[2] == 'RADIUS':
                            self.p_record_radius = True
                            continue
                    if len(values) > 1:
                        if values[0] == 'End' and values[1] == 'NodalData' and self.p_record_radius == True:
                            self.p_record_radius = False

                    if self.p_record_nodes:
                        self.p_pram_dict["id"] = int(values[0])
                        self.p_pram_dict["p_x"] = float(values[1])
                        self.p_pram_dict["p_y"] = float(values[2])
                        self.p_pram_dict["p_z"] = float(values[3])

                    if self.p_record_elements:
                        #only modify the values, not add new one
                        temp_p_pram_dict = next(old_p_pram_dict for old_p_pram_dict in self.p_pram_list if old_p_pram_dict['id'] == int(values[2]))
                        temp_p_pram_dict["p_ele_id"] = int(values[0])

                    if self.p_record_radius:
                        #only modify the values, not add new one
                        temp_p_pram_dict = next(old_p_pram_dict for old_p_pram_dict in self.p_pram_list if old_p_pram_dict['id'] == int(values[0]))
                        temp_p_pram_dict["radius"] = float(values[2])

                    if not (self.p_record_elements and self.p_record_radius):
                        if self.p_record_nodes:
                            self.p_pram_list.append(self.p_pram_dict)
                            self.p_id = self.p_id + 1

        self.p_pram_list = sorted(self.p_pram_list, key=lambda d: d['id'])

        self.max_particle_id = max(self.p_pram_list,key=lambda x: x['id'])['id']
        self.max_element_id = max(self.p_pram_list,key=lambda x: x['p_ele_id'])['p_ele_id']

        print("Read mdpa file finished!\t")
            

    def WriteOutGIDData(self):
    
        outName = './inletPG3DEM_OUT_from_Post.mdpa'

        # clean the exsisted file first
        if os.path.isfile(outName):
            os.remove(outName)
        
        with open(outName,'a') as f:
            # write the particle information
            f.write("Begin ModelPartData \n //  VARIABLE_NAME value \n End ModelPartData \n \n Begin Properties 0 \n End Properties \n \n")
            f.write("Begin Nodes\n")
            for p_pram_dict in self.p_pram_list:
                f.write(str(p_pram_dict["id"]) + ' ' + str(p_pram_dict["p_x"]) + ' ' + str(p_pram_dict["p_y"]) + ' ' + str(p_pram_dict["p_z"]) + '\n')
            f.write("End Nodes \n \n")

            f.write("Begin Elements SphericParticle3D// GUI group identifier: Body \n")
            for p_pram_dict in self.p_pram_list:
                f.write(str(p_pram_dict["p_ele_id"]) + ' ' + ' 0 ' + str(p_pram_dict["id"]) + '\n')
            f.write("End Elements \n \n")

            f.write("Begin NodalData RADIUS // GUI group identifier: Body \n")
            for p_pram_dict in self.p_pram_list:
                f.write(str(p_pram_dict["id"]) + ' ' + ' 0 ' + str(p_pram_dict["radius"]) + '\n')
            f.write("End NodalData \n \n")

            ''' only works for continuum DEM calculation
            f.write("Begin NodalData COHESIVE_GROUP // GUI group identifier: Body \n")
            for p_pram_dict in self.p_pram_list:
                f.write(str(p_pram_dict["id"]) + ' ' + ' 0 ' + " 1 " + '\n')
            f.write("End NodalData \n \n")

            f.write("Begin NodalData SKIN_SPHERE \n End NodalData \n \n")
            '''

            f.write("Begin SubModelPart DEMParts_Body // Group Body // Subtree DEMParts \n Begin SubModelPartNodes \n")
            for p_pram_dict in self.p_pram_list:
                if p_pram_dict["p_group_id"] == 0:
                    f.write(str(p_pram_dict["id"]) + '\n')
            f.write("End SubModelPartNodes \n Begin SubModelPartElements \n ")
            for p_pram_dict in self.p_pram_list:
                if p_pram_dict["p_group_id"] == 0:
                    f.write(str(p_pram_dict["p_ele_id"]) + '\n')
            f.write("End SubModelPartElements \n")
            f.write("Begin SubModelPartConditions \n End SubModelPartConditions \n End SubModelPart \n \n")

            #write out joint group
            joint_exist = False
            for p_pram_dict in self.p_pram_list:
                if p_pram_dict["p_group_id"] == 1:
                    joint_exist = True

            if joint_exist:
                f.write("Begin SubModelPart DEMParts_Joint // Group Joint // Subtree DEMParts \n Begin SubModelPartNodes \n")
                for p_pram_dict in self.p_pram_list:
                    if p_pram_dict["p_group_id"] == 1:
                        f.write(str(p_pram_dict["id"]) + '\n')
                f.write("End SubModelPartNodes \n Begin SubModelPartElements \n ")
                for p_pram_dict in self.p_pram_list:
                    if p_pram_dict["p_group_id"] == 1:
                        f.write(str(p_pram_dict["p_ele_id"]) + '\n')
                f.write("End SubModelPartElements \n")
                f.write("Begin SubModelPartConditions \n End SubModelPartConditions \n End SubModelPart \n")

            f.close()

        print("Successfully write out GID DEM.mdpa file!")


if __name__ == "__main__":

    TestDEM = read_and_clone()
    TestDEM.getParticleDataFromPost('G-TriaxialDEM_after_cut.mdpa')
    TestDEM.WriteOutGIDData()