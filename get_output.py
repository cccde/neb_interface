import numpy as np
import os
import sys
sys.path.append(os.path.abspath("/lustre/lwork/yclee/python_practice/cneb"))
from get_input import *

tri = tot * 3
img = image

####################################
def get_all_log(directory):
    all_log = []
    for i in os.listdir(directory):
        if os.path.isfile(directory + os.sep +i) and i[-4:]== ".log":
            all_log.append(i)
    return sorted(all_log)
####################################
def str_list2float_list(str_l):
    return_list = []
    for x in str_l:
        return_list.append(float(x))
    return return_list
#######################################

def get_coord(file_target):
    coord_1 = []

    with open(file_target, "r") as p:
        find = False
        first_time = True
        for i, line in enumerate(p):
            if first_time:
                if "orientation" in line:
                    number = i + 4
                    find = True
                    first_time = False
            if find:
                if (number + (tot+1) > i)and (i > number):
                    b = str_list2float_list(line.split()[3:6])
                    coord_1 += b

    all_coord_1 = np.array(coord_1)
    coord = all_coord_1.reshape(tot,3)
    return coord

######################################

def get_coord_foroutput(file_target):
    str1 = ""

    with open(file_target, "r") as p:
        find = False
        first_time = True
        for i, line in enumerate(p):
            if first_time:
                if "orientation" in line:
                    number = i
                    find = True
                    first_time = False
            if find:
                if (number + (tot+6) > i)and (i > number):
                    str1+=line

    return str1
#######################################
def get_scf(the_file):
    return_list = []
    with open(the_file, "r") as p:
        find = False
        first_time = True
        for i, line in enumerate(p):
            if first_time:
                if "SCF" in line:
                    number = i
                    find = True
                    first_time = False
            if find:
                if i == number:
                    b = str_list2float_list(line.split()[4:5])

                    return_list += b
    energy = 0
    for i in return_list:
        energy += float(i)
    return energy
#######################################
def get_all_scf(the_log):
    return_list = [1] * len(the_log)
    for i in range(0, len(the_log)):
        return_list[i] = get_scf((the_log)[i])
    return return_list
######################################
def get_max_image(return_list):
    result = return_list.index(max(return_list))
    return result
#######################################
def get_local_ta(file1, file2, file3):
   # the_vec = [1] * tri
   # the_coord = np.array(the_vec).reshape(tot,3)
    e1 = get_scf(file1)
    e2 = get_scf(file2)
    e3 = get_scf(file3)
    if (e3 > e2) and (e2 > e1):
        the_coord = (get_coord(file3) - get_coord(file2))
    elif (e3 < e2) and (e2 < e1):
        the_coord = (get_coord(file2) - get_coord(file1))
    elif (e3 > e2) and (e2 < e1):
        the_coord = (e3-e2)*(get_coord(file3) - get_coord(file2)) + (e1-e2)*(get_coord(file2) - get_coord(file1))
    elif (e3 < e2) and (e2 > e1):
        the_coord = (e2-e1)*(get_coord(file3) - get_coord(file2)) + (e2-e3)*(get_coord(file2) - get_coord(file1))
    return the_coord

######################################
def get_all_tangent_list(the_log):
    return_list = [1] * img
    for i in range(0, img):
        return_list[i] = get_local_ta(the_log[i],the_log[i+1],the_log[i+2]).tolist()
    return return_list
#####################################
def get_vector(file1, file2):
    vec1 = get_coord(file1)
    vec2 = get_coord(file2)
    vec12 = vec2 - vec1
    return vec12
#####################################
def get_para_force(ori_force, file1, file2, file3):

    my_force = ori_force.reshape(tri, 1)

    vector_13 = get_local_ta(file1, file2, file3)

    c = vector_13.reshape(tri,1)

    ab_2 = np.power(c, 2)

    total_dist = np.sum(ab_2, axis=0)

    abc = my_force * c

    sum_inner_product = np.sum(abc, axis=0)

    k = sum_inner_product / total_dist

    para_vector = k * c

    return para_vector
####################################
def find_force2(file2, file1, file3):

    force=[]


    with open(file2, "r") as o:
        find = False
        first_time = True
        for i, line in enumerate(o):
            if first_time:
                if "Axes" in line:
                    number = i + 4
                    find = True
                    first_time = False

            if find:
                if (number + (tot+1) > i)and (i > number):
                   a = str_list2float_list(line.split()[2:5])
                   force += a

    full_real_force = np.array(force)

    my_force = full_real_force.reshape(tri,1)

    para_force = get_para_force(full_real_force, file1, file2, file3)

    normal_force = my_force - para_force

    the_force = normal_force.reshape(tot,3)

    full = (np.sum(np.power(my_force,2),axis=0)) ** 0.5
    para = (np.sum(np.power(para_force,2),axis=0)) ** 0.5
    normal = (np.sum(np.power(normal_force,2),axis=0)) ** 0.5

    return float(full),float(para),float(normal)
####################################
def find_force1(file2):

    force=[]


    with open(file2, "r") as o:
        find = False
        first_time = True
        for i, line in enumerate(o):
            if first_time:
                if "Axes" in line:
                    number = i + 4
                    find = True
                    first_time = False

            if find:
                if (number + (tot+1) > i)and (i > number):
                   a = str_list2float_list(line.split()[2:5])
                   force += a

    full_real_force = np.array(force)

    my_force = full_real_force.reshape(tri,1)

    full = (np.sum(np.power(my_force,2),axis=0)) ** 0.5

    return float(full)

##########################################################
def get_force_list(the_list):
    return_list = []
    for i in range(1, len(the_list)-1):
        full,para,normal = find_force2(the_list[i],the_list[i-1],the_list[i+1])
        return_list.append(full)
        return_list.append(normal)
        return_list.append(para)
    return return_list
#######################################
#print (get_force_list(get_all_log(".")))
log_list = get_all_log(".")
scf_list = get_all_scf(log_list)
the_force_list = get_force_list(log_list)
with open("decision","r") as d:
    for i,line in enumerate(d):
        if i == 0:
            status = line.split()[0]
        if i == 1:
            decision = int(line.split()[0])-1
with open("OUTPUT",'a') as o:
    if decision == 0:
        o.write("--------------------------------------------------------------------------------------------------------------- "+ "\n")
        o.write("This CNEB program follows the idea of G. Henkelman, J. Chem. Phys. 113, 9901 (2000) and G. Henkelman, H. Jonsson, J. Chem. Phys. 113, 9978(2000)\n")
        o.write("and this program is written by Yu-Chi Lee and Cheng-Chau Chiu\n")
        o.write("If you use this program, please cite Yu-Chi Lee, Cheng-Chau Chiu and https://github.com/cccde/neb_interface\n") 
        o.write("--------------------------------------------------------------------------------------------------------------- \n\n\n\n\n\n")
    o.write("\nThis is iteration " + str(decision)+"\n\n\n\n")
    for i in range(0,len(log_list)):
        coord = get_coord_foroutput(log_list[i])
        o.write("The coordinates of image " + str(i) + " \n")
        o.write(coord)
        o.write("\n")
    o.write("Iteration " + str(decision) + " result: \n")
    o.write(" --------------------------------------------------------------------------------------------------------------- "+ "\n")
    o.write("\t"+"Image".ljust(18)+"Energy".ljust(22)+"Total Force".ljust(22)+"Perpendicular Force".ljust(24)+"Parallel Force".ljust(22)+ "\n")
    o.write("\t"+"".ljust(18)+"(Hartrees)".ljust(22)+"(Hartrees/Bohr)".ljust(22)+"(Hartrees/Bohr)".ljust(24)+"(Hartrees/Bohr)".ljust(22)+ "\n")
    o.write(" --------------------------------------------------------------------------------------------------------------- "+ "\n")
    for i in range(0,img+2):
        if i == 0:
            o.write("\t" +("Image "+ str(i)).ljust(18) + str(scf_list[i])[:9].ljust(22) + str(find_force1(log_list[0]))[:9].ljust(22) + "X".ljust(24) + "X".ljust(22) + "\n")
        elif i == img+1:
            o.write("\t" +("Image "+ str(i)).ljust(18) + str(scf_list[i])[:9].ljust(22) + str(find_force1(log_list[-1]))[:9].ljust(22) + "X".ljust(24) + "X".ljust(22) + "\n")
        else:
            o.write("\t" +("Image "+ str(i)).ljust(18) + str(scf_list[i])[:9].ljust(22) + str(the_force_list[(i-1)*3])[:9].ljust(22) + str(the_force_list[(i-1)*3+1])[:9].ljust(24)+ str(the_force_list[(i-1)*3+2])[:9].ljust(22)+ "\n")
    o.write(" --------------------------------------------------------------------------------------------------------------- "+ "\n")
    if status == "True":
        o.write("No convergency reached after iteration " + str(decision) + " \n\n\n\n")
    if (status == "False") and (decision == nsw):
        o.write("No convergency reached after iteration " + str(decision) +"\n")
        o.write("CNEB stops because it has reached the maximum steps(nsw) "+"\n\n\n\n")
    if (status == "False") and (decision != nsw):
        o.write("CENB converges after iteration " + str(decision) + " \n")
        o.write("CNEB stops because the maximum force is lower than the convergence condition \n\n\n\n")
