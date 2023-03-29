# -*- coding: utf-8 -*-
"""
Created on Sun Feb  5 21:42:19 2023

@author: wenxuli
"""





class Object:
    pass 

'''load factors for ULS, SLS and Fatigue limit state design loads'''
def LoadactorsV():
    '''for 300LA rail traffic load'''
    return {'ULS':1.6,'SLS':1.0,'FLS':1.0}
def LoadactorsH():
    '''load factors for longitudinal and traction forces and nosing forces are considered
    here'''
    return {'ULS':1.6,'SLS':1.0}


class LoadFactors:
    def __init__(self):
        '''According to Appendix D of AS5100.2'''
        self.ULS = Object()
        self.SLS = Object()
        self.FDL = Object()
    def PermanentLoad(self):        
        self.ULS.conc = 1.2
        self.ULS.blsttrk = 1.7
        self.ULS.concslab=2.0
        self.ULS.shrinkcreep = 1.2
        self.ULS.prestress = 1.0
        
        self.SLS.conc = 1.0
        self.SLS.blsttrk = 1.3
              
        
    def TransientLoad(self):
        self.ULS.M300LA  = 1.6
        self.ULS.braketraction = 1.6
        self.ULS.derailment = 1.0
        self.ULS.prestress2nd = 1.0
        self.ULS.prestresstransfer = 1.0
        self.ULS.derailmentCaseA = 1.2 
        self.ULS.derailmentCaseB = 1.0
        self.SLS.M300LA = 1.0
        self.SLS.braketraction = 1.0
class DLA:
    def __init__(self,L):
        """dynamic load allowance, applies to both ULS and SLS, section 9.5.1 of AS5100.2
        L: characteristic length of a component in meters """
        self.L = L
    def DynBending(self):
        '''Dynamic load allowance for bending effects, Section 9.5.3 of AS5100.2        
        alpha: the dynamic load factor. alpha*deadload=dynamic load'''
        alpha = 2.16/(self.L**0.5-0.2)-0.27
        if alpha>0.67:
            alpha = 0.67
        if alpha < 0.2:
            alpha = 0.2 
        self.alpha_bending = alpha
    def DynOthers(self):
        '''Dynamic load allowance for other load effects, Section 9.5.5 of AS5100.2
        L: characteristic length of a component in meters;
        Dynamic load effct for torsion, shear and reactions'''
        self.alpha_others = 0.67*self.DynBending()
        
    def DesignAction(self,load_factor,loads):
        #=================================not finished=========================
        #=================================not finished=========================
        #=================================not finished=========================
        '''Section 9.5.1 of AS5100.2
        Design action is the design loads in various directions.
        alpha: the dynamic load factor, determined by DynaBending(L) or DhnOthers(L), depending on the type of the loading;
        load_factor: load factors, determined by LoadactorsV() and LoadFactors_Horizontal(), for ULS and SLS it has 
        different values;
        loads: M300LA(span), BrakeForce(LLF,n), TractionForce(LLF,n) and NosingLoad(rail_type,*args)
        '''
        '''the effect is from bending''' 
        self.designaction_bending = (self.alpha_bending+1)*load_factor*loads
        '''the effect is from other loading'''
        self.designaction_others = (self.alpha_others+1)*load_factor*loads
        


#%% ULS and SLS design loads

from Bridge_design_lib.Input_Data import InputData
from Bridge_design_lib.Load_Distribution import LoadDist
loadfactors = LoadFactors()
loadfactors.PermanentLoad()
loadfactors.TransientLoad()
Inputs = InputData()
Inputs.Blst()


def ULSLoadComb(bf,trk_no,dpth_slab,dst_trks=0,x_shift=0,y_shift=0):
    
    LdDistCase1 = LoadDist(1,trk_no,dpth_slab,Inputs.blst.h,
                                             Inputs.l_slp,dst_trks=0)
    
    LdDistCase1.DerailmentLoadonBr(Inputs.Lv,Inputs.L,bf,Inputs.gauge,x_shift,y_shift)
    
    LdDistCase1.FatigueLoadsOnBr(Inputs.Lv,Inputs.L,x_shift)
    
    FatigueLdsFinal = LdDistCase1.FatigueLoads
    
    
    BlstTrkULS = {'DeadLoad':loadfactors.ULS.blsttrk*Inputs.blst.wt,
        'FatigueLoad':[(i[0],i[1],loadfactors.ULS.M300LA*i[2]) for i in FatigueLdsFinal],
        'DerailmentLoadCaseA1':[(i[0],i[1],loadfactors.ULS.derailmentCaseA*i[2]) 
                                for i in LdDistCase1.DerailmentLoads.blst.CaseA1],
        'DerailmentLoadCaseA2':{'load':loadfactors.ULS.derailmentCaseA*LdDistCase1.DerailmentLoads.blst.CaseA2['load'],
                                'xshift':x_shift,'yshift':y_shift},
        'DerailmentLoadCaseB':LdDistCase1.DerailmentLoads.blst.CaseB # the ULS load factor or caseB is 1.0
            }
    # print('BlstTrk ULS is: ',BlsttrkULS)
    return BlstTrkULS
    
    # Slabtrk = {'DeadLoad':[loadfactors.ULS.blsttrk*loadfactors.blst.wt],
    #     'FatigueLoad':[(i[0],i[1],loadfactors.ULS.M300LA*i[3]) for i in FatigueLoadsFinal],
    #     'DerailmentLoad':[CaseA(Lv,x,gauge,x_shift)]}

    

def SLSLoadComb(bf,trk_no,dpth_slab,dst_trks=0,x_shift=0,y_shift=0):
    
    LdDistCase1 = LoadDist(1,trk_no,dpth_slab,Inputs.blst.h,
                                             Inputs.l_slp,dst_trks=0)
    LdDistCase1.FatigueLoadsOnBr(Inputs.Lv,Inputs.L,x_shift)
    
    FatigueLoadsFinal = LdDistCase1.FatigueLoads
    BlstTrkSLS = {'DeadLoad':[loadfactors.SLS.blsttrk*Inputs.blst.wt],
        'FatigueLoad': FatigueLoadsFinal # the load factor for fatigue load in SLS is 1.0
        }
    # print('BlstTrk SLS is: ',BlstTrkSLS)
    return BlstTrkSLS
         
        