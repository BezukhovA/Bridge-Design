# -*- coding: utf-8 -*-
"""
Created on Mon Mar 27 09:19:08 2023

@author: wenxuli
"""

import numpy as np


def dv(d,D):
    # dv is the internal level arm
    # d is the distance from the extreme compressive fibre to the centroid of the 
    # area of the reinforcement steel in the tensile half of the session.
    return max([0.9*d,0.72*D])



def epsilonx(M,dv,V,Pv,N,fpo,Es,Ast,Ep,Apt,Ec,Act):
    # N* is positive for tension and negative for compression
    # Ast is the area of the reinforcing bars in the half depth of the section containing
    # the flexural tension zone (in the zone defined by a depth of D/2 from the 
    # extreme tensile fibre). For reinforcing bars not fully developed, the area of these bars
    # should be reduced by the ratio of their developed stress to the bar's yield stress
    # dv: in mm
    # M: in kNm
    # V: in kN
    M = abs(M)
    V = abs(V)
    if M<(V-Pv)*dv/1000:
        raise ValueError("Design Shear Strength Calculation, Epsilonx, \
                         M* must be at least (V-Pv)*dv")
    tmp = 1e3*(1e3*M/dv+V-Pv+0.5*N)-Apt*fpo
    if tmp>=0:
        # tensile, epsilonx>0
        Area = 2*(Es*Ast+Ep*Apt)
        return min([tmp/Area,3e-3])
    else:
        Area = 2*(Es*Ast+Ep*Apt+Ec*Act)
        return max([tmp/Area,-0.2e-3])
    
def thetav(epsilonx):
    # angle of the compressive strut relative to the longitudinal axis of the member
    return 29+7000*epsilonx
    
def epsilonx_TorsionShear(M,dv,V,Pv,T,N,fpo,A0,Es,Ast,Ep,Apt,Ec,Act,uh):
    # N* is positive for tension and negative for compression
    # Ast is the area of the reinforcing bars in the half depth of the section containing
    # the flexural tension zone (in the zone defined by a depth of D/2 from the 
    # extreme tensile fibre). For reinforcing bars not fully developed, the area of these bars
    # should be reduced by the ratio of their developed stress to the bar's yield stress
    # uh: the perimeter of the centerline of the hoop reinforcement
    M = abs(M)
    V = abs(V)
    # print(M,dv*((V-Pv)**2+(0.9*T*1e3*uh/2/A0)**2)**0.5/1000)
    if M<dv*((V-Pv)**2+(0.9*T*1e3*uh/2/A0)**2)**0.5/1000:        
        raise ValueError("Design Shear Strength Calculation, Epsilonx, \
                         M* must be greater than dv*((V-Pv)**2+(0.9*T*uh/a/A0)**2)**0.5")
    tmp = 1e3*(1e3*M/dv+((V-Pv)**2+(0.9*T*1e3*uh/2/A0)**2)**0.5+0.5*N)-Apt*fpo
    if tmp>=0:
        # tensile, epsilonx>0
        Area = 2*(Es*Ast+Ep*Apt)
        return min([tmp/Area,3e-3])
    else:
        Area = 2*(Es*Ast+Ep*Apt+Ec*Act)
        return max([tmp/Area,-0.2e-3])
 
def kv(fc,dg,Asv,Asvmin,epsilonx):
    # the parameter indicating the capability of the web resisting the aggregate
    # interlocking stresses and provide concrete contribution to the shear strength
    # Asv: cross section area of the reinforcement
    # s: spacing of the reinforcement
    if Asv<Asvmin:
        if fc <=65:
            kdg = max([32/(16+dg),0.8])
        else:
            kdg = 2.0
        return 0.4/(1+1500*epsilonx)*(1300/(1000+kdg*dv))
    else:
        return 0.4/(1+1500*epsilonx)

def Vumax(fc,bv,dv,thetav):
    #shear strength limited by web crushing due to shear only
    thetav = thetav/180*np.pi
    return 0.55*0.9*fc*bv*dv*np.sin(thetav)*np.cos(thetav)
def tauw(V,Vumax,Pv,T,bv,dv,tw,uh,Aoh,opt,phi):
    # web crushing due to combined shear force and torsion
    # opt: 0, for box sections; 1, for solid sections
    # Section 8.2.4.5 of AS5100.5:2017
    tauwmax = phi*Vumax/bv/dv
    if opt ==0:
        if tw>Aoh/uh:
            tauw = (V-Pv)/bv/dv+T*uh/1.7/Aoh**2
        else:
            tauw = (V-Pv)/bv/dv+T/1.7/tw/Aoh
    else:
        tauw = (((V-Pv)/bv/dv)**2+(T*uh/1.7/Aoh**2)**2)**0.5
        
    if tauw<=tauwmax:
        return 0
    else:
        return 1

def Vuc(fc,bv,dv,kv):
    # shear strength contribution from the concrete 
    return kv*min([fc**0.5,8])*bv*dv/1000
def Vus(Asv,s,dv,thetav,fsyf):
    # shear strength conbution of the stirrups and the concrete in inclinded compression 
    # in the web of the beam
    return Asv/s*fsyf*dv/np.tan(thetav/180*np.pi)/1000


def Vu(Vuc,Vus,Pv):
    # design shear strength
    return Vuc+Vus+Pv

