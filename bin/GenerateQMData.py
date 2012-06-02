#!/usr/bin/env python

""" @package GenerateQMData

Executable script for generating QM data for force, energy, electrostatic potential, and
other ab initio-based fitting simulations. """

import os, sys, glob
from forcebalance.forcefield import FF
from forcebalance.simtab import SimTab
from forcebalance.parser import parse_inputs
from forcebalance.nifty import *
from forcebalance.molecule import Molecule, format_xyz_coord
import numpy as np
import numpy.oldnumeric as nu
import work_queue
import random

# The default VdW radii from Chmiera, taken from AMBER.
# See http://www.cgl.ucsf.edu/chimera/1.5/docs/UsersGuide/midas/vdwtables.html
VdW99 = {'H' : 1.00, 'C' : 1.70, 'N' : 1.625, 'O' : 1.49, 'F' : 1.56, 'P' : 1.871, 'S' : 1.782, 'I' : 2.094, 'Cl' : 1.735, 'Br': 1.978}

def even_list(totlen, splitsize):
    """ Creates a list of number sequences divided as easily as possible.  
    
    Intended for even distribution of QM calculations.  However, this might
    become unnecessary if we always create one directory per calculation 
    (we need it to be this way for Q-Chem anyhow.) """
    joblens = np.zeros(splitsize,dtype=int)
    subsets = []
    for i in range(totlen):
        joblens[i%splitsize] += 1
    jobnow = 0
    for i in range(splitsize):
        subsets.append(range(jobnow, jobnow + joblens[i]))
        jobnow += joblens[i]
    return subsets

def generate_snapshots():
    print "I haven't implemented this yet"
    sys.exit(1)

def create_esp_surfaces(Molecule):
    from forcebalance.mslib import MSMS
    Rads = [VdW99[i] for i in Molecule.elem]
    #xyz = Molecule.xyzs[0]
    na = Molecule.na
    Mol_ESP = []
    printxyz=0
    for i, xyz in enumerate(Molecule.xyzs):
        print "Generating grid points for snapshot %i\r" % i,
        esp_pts = []
        for j in [1.4, 1.6, 1.8, 2.0]:
            MS = MSMS(coords = list(xyz), radii = list(np.array(Rads)*j))
            MS.compute()
            vfloat, vint, tri = MS.getTriangles()
            a = range(len(vfloat))
            random.shuffle(a)
            if len(vfloat) < na:
                warn_press_key("I generated less ESP points than atoms!")
            for idx in a[:na]:
                esp_pts.append(vfloat[idx][:3])
        if printxyz:
            Out = []
            Out.append("%i" % (len(xyz) + len(esp_pts)))
            Out.append("Molecule plus ESP points")
            for j, x in enumerate(xyz):
                Out.append(format_xyz_coord(Molecule.elem[j], x))
            for esp_pt in esp_pts:
                Out.append(format_xyz_coord('chg',esp_pt))
            fout = open('Mao.xyz','w')
            for line in Out:
                print >> fout, line
            fout.close()
            sys.exit(1)
        Mol_ESP.append(esp_pts)
    return Mol_ESP

def do_quantum():
    wq_port = 5813
    M = Molecule('shots.gro')
    M += Molecule(os.path.abspath('../settings/qchem.in'))
    digits = len(str(len(M)-1))
    formstr = '\"%%0%ii\"' % digits

    def read_quantum():
        Result = None
        os.chdir('calcs')
        for i in range(M.ns):
     'B%�$��r��F�&V7F�'�V�"R����b�2�F��W��7G2�F�ғ���2�6�F�"�F�Ґ��b�2�F��W��7G2�w6�V���WBr����WGWB����V7V�R�w6�V���WBr���b�2�F��W��7G2�w��B�W7r����WGWB�����V7V�R�w��B�W7r���b&W7V�B�����S��&W7V�B��WGW@�V�6S��&W7V�B���WGW@�V�6S��&�6RW�6WF���%F�R�WGWBf��RW2F�W6�wBW��7B�"R�2�F��'7F��w6�V���WBr����2�6�F�"�r��r��V�6S��&�6RW�6WF���%F�R7V&F�&V7F�'�W2F�W6�wBW��7B�"R�2�F��'7F��F�Ғ���2�6�F�"�r��r��&WGW&�&W7V�@� �FVb'V��V�GV҂���U5�7&VFU�W7�7W&f6W2�Ґ�v�&��VWVR�6WE�FV'Vu�f�r�v��r��w�v�&��VWVR�v�&�VWVR�w��'B�W�6�W6�fS�f�6R�6�WFF�v��f�6R��w�7V6�g����R�vf�&6V&��6Rr���2���VF�'2�v6�72r���2�6�F�"�v6�72r��f�"���&�vR����2���F���Wff�&�7G"R����2���VF�'2�F�Ґ��2�6�F�"�F�Ґ���VF�E�7&V�2��v�vFW7s��V�U5��җҐ���w&�FR�'6�V���"�6V�V7C֒��U5&��"���'&��U5��Ғ�&��&�p���6fWG�B�tU5w&�Br�U5&��"��&��B%VWVV��rW��""�F�ТVWVU�W�w�6����B�w6�V�C���6�V���6�V���WBr� ���WE�f��W2��'6�V���"�$U5w&�B%����WGWE�f��W2��'6�V���WB"�'��B�W7"�&Vf�V�B�FB%��fW&&�6S�f�6R���2�6�F�"�r��r��f�"���&�vR����2���w�v�B�w���2�6�F�"�r��r���b�2�F��W��7G2�v6�72r���&��B&6�72F�&V7F�'�W��7G2�&VF��r6�7V�F���&W7V�G2� �&W7V�B�&VE�V�GV҂��V�6S��&��B&6�72F�&V7F�'�F�W6�wBW��7B�6WGF��rW�B'V���r6�7V�F���2� �'V��V�GV҂��&��B$��r&VF��r6�7V�F���&W7V�G2� �&W7V�B�&VE�V�GV҂��&��B%w&�F��r&W7V�G2F�FF�G�B� �&W7V�B�w&�FR�wFF�G�Br��&WGW&�&W7V�@��FVbvV�W&FR�6����B���&��B6����E�v��RuТ6��F�"��2�F�����w6��V�F���2r�6����E�v��RuҐ��b��B�2�F��W��7G2�6��F�"���v&��&W75��W��"W2F�W6�wBW��7B"R6��F�"���2�6�F�"�6��F�"��tF�'2�v��"�v��"�&vV���ӕճӕճӕ�"���b�V�tF�'2�����&��B$��vV�2W��7B� �7�2�W��B���f�'7B�G'VP�w&�FT���f�6P�f�"B��tF�'3��&��B$��r6�V6���r"�@��2�6�F�"�B���b�2�F��W��7G2�w6��G2�w&�r��B�2�F��W��7G2�wFF�G�Br���&��B$&�F�6��G2�w&��BFF�G�BW��7B �6��G2����V7V�R�w6��G2�w&�r��FF����V7V�R�wFF�G�Br�����'&��6��G2燗�2��"���'&��FF燗�2���b�6�R�"�6�S��&�6RW�6WF���w6��G2�w&��BFF�G�BV"F�6��F��F�ffW&V�BFFr��VƖb�������'2�aise Exception('shots.gro and qdata.txt appear to contain different xyz coordinates')
            shots.qm_energies = qdata.qm_energies
            shots.qm_forces   = qdata.qm_forces
            shots.qm_espxyzs     = qdata.qm_espxyzs
            shots.qm_espvals     = qdata.qm_espvals
            if First:
                All = shots
            else:
                All += shots
            WriteAll = True
        elif os.path.exists('shots.gro'):
            print "shots.gro exists"
            print "I need to GENERATE qdata.txt now."
            do_quantum()
        elif os.path.exists('qdata.txt'):
            warn_press_key('qdata.txt exists.')
        else:
            print "I need to GENERATE shots.gro now."
            generate_snapshots()
            run_quantum()
        os.chdir('..')
    All.write('all.gro')
    All.write('qdata.txt')
    os.chdir('..')
        

def main():
    options, sim_opts = parse_inputs(sys.argv[1])

    # ## The list of fitting simulations
    # self.Simulations = [SimTab[opts['simtype']](self.options,opts,self.FF) for opts in self.sim_opts]
    # ## The optimizer component of the project
    # self.Optimizer   = Optimizer(self.options,self.Objective,self.FF,self.Simulations)
    
    print "\x1b[1;97m Welcome to ForceBalance version 0.12! =D\x1b[0m"
    if len(sys.argv) != 2:
        print "Please call this program with only one argument - the name of the input file."
        sys.exit(1)

    for S in sim_opts:
        Generate(S)
    
    # P = Project(sys.argv[1])
    # P.Optimizer.Run()

if __name__ == "__main__":
    main()
