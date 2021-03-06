# ipython2 SLmain.py

class mockSimulation:
        ## public
        def __init__(self):
                self.theta_mean = [0, 0]
                self.theta_std = [0, 0]
                self.r = 1#number of rounds
                self.s = 1# length of simulations
                self.N = 1# number of parallel simulations
                self.tp = None
                self.mapping = None
                self.x = None
                self.y = None
                
        def run_multipleSim(self):
                return True
        def runNxtRound(self):
                return True
                
        
        ## private
        def PreAll(self, trj):
                """
                Pre-Sampling:
                        choose states with minimum counts or newly discovered states
                output:
                        trj with shape of [[Xs][Ys]]
                """
                import numpy as np
                comb_trj = np.concatenate(trj)
                return trj

                
        def map(self, trj_Ps):
                """

                output:
                      n_ec x n_frames
                """
                # map coordinate space to reaction coorinates space
                import numpy as np
                trj_x = []
                trj_y = []
                x = self.x
                y = self.y
                map = self.mapping

                for MacroFrame in trj_Ps:
                    microFrame = map[int(MacroFrame)]
                    """
                    trj_x.append(x[microFrame])
                    trj_y.append(y[microFrame])
                    """
                    if microFrame==0:
                        x000 = np.load('../state0-200.npy')
                        x00 = np.random.choice(range(len(x000)), 1)
                        x0 = x000[x00][0]
                        #print(x0)
                        trj_x.append(x0[0])
                        trj_y.append(x0[1])
                    else:
                        trj_x.append(x[microFrame])
                        trj_y.append(y[microFrame])
                

                return trj_x, trj_y

        def PreSamp_MC(self, trj, N = 20):
                """
                Pre-Sampling for Monte Carlo simulations:
                        choose states with minimum counts or newly discovered states
                        
                output:
                        trj with shape of 
                """
                import numpy as np
                cl_trjs = trj             
                unique, counts = np.unique(cl_trjs, return_counts=True)
                leastPop = counts.argsort()[:N]
                init_cl = [int(unique[i]) for i in leastPop]
                return init_cl

        
        def run(self, inits, nstepmax = 10):
                """
                Parameters
                ----------
                initi : 
                        initial state (singe state)
                msm :
                        reference MSM
                s :
                        lenght (number of steps) of each simulation	
                
                output :
                        final trajectory
                """
                import numpy as np
                import msmbuilder as msmb
		
                #msm = self.msm
                tp = self.tp
                N = len(inits)
                trjs = np.empty([N, nstepmax])
                for n in range(N):
                        init = np.int(inits[n])
                        trj = msmb.msm_analysis.sample(tp, init, nstepmax)
                        #trj = msm.sample_discrete(state=init, n_steps=nstepmax, random_state=None)
                        trjs[n] = trj
                return trjs
                

        def pltPoints(self, x, y):
            import matplotlib.pyplot as plt
            import numpy as np

            plt.rcParams.update({'font.size':20})
            plt.rc('xtick', labelsize=20)
            plt.rc('ytick', labelsize=20)

            figName = 'fig.png'

            fig = plt.figure()
            ax = fig.add_subplot(111)
            
            
            ax.scatter(x , y, color='darkorange', s=10, alpha=0.4)
            #ax.scatter(x + np.random.normal(0, 0.06/4, len(x)), y+np.random.normal(0, 0.06, len(y)), color='darkorange', s=10, alpha=0.5)
            plt.xlabel('RMSD of A-loop (nm)')
            plt.ylabel('K-E distances (nm)')
            #plt.ylabel('K295-E310 distances (nm)')
            plt.yticks([0, 1, 2])
            plt.xticks([0, 0.5, 1])
            #plt.ylabel(r'$d_{E310-R409}-d_{K295-E310}$')
            plt.ylim([0, 2])
            plt.xlim([0, 1])
#            plt.show()
            fig.savefig('fig.png', dpi=1000, bbox_inches='tight')

            return 

        def reward_state(self, S, theta_mean, theta_std, W_):
                
                r_s = 0
                for k in range(len(W_)):
                    if theta_std[k]==0:
                        print(theta_std[k])
                        theta_std[k]=1

                    #r_s = r_s + W_[k]*(abs(S[k] - theta_mean[k])/theta_std[k]) #No direction
                    if (S[k] - theta_mean[k]) < 0:  # direstional
                        r_s = r_s + W_[k][0]*(abs(S[k] - theta_mean[k])/theta_std[k]) # W_[k][0] is weight for W_ negetive direction
                    else:
                        r_s = r_s + W_[k][1]*(abs(S[k] - theta_mean[k])/theta_std[k]) # W_[k][1] is weight for W_ positive direction
                    
                return r_s


        def updateStat(self, trj_Sp_theta):      
                import numpy as np
                theta_mean = []
                theta_std = []
                for theta in range(len(trj_Sp_theta)):
                        theta_mean.append(np.mean(trj_Sp_theta[theta]))
                        theta_std.append(np.std(trj_Sp_theta[theta]))
                self.theta_std = theta_std
                self.theta_mean = theta_mean
        

        def reward_trj(self, trj_Sp_theta, W_):
                """
                
                """
                import numpy as np
                #theta_mean = []
                #theta_std = []
                #for theta in range(len(W_)):
                #        theta_mean.append(np.mean(trj_Sp_theta[theta]))
                #        theta_std.append(np.std(trj_Sp_theta[theta]))
                

                r = []
                # for over all dicovered states
                trj_Sp_theta = np.array(trj_Sp_theta)
                for state_index in range(len(trj_Sp_theta[0])):
                        #print('trj_Sp_theta', trj_Sp_theta)
                        state_theta = trj_Sp_theta[:, state_index]
                        r_s = self.reward_state(state_theta, self.theta_mean, self.theta_std, W_)
                        
                        r.append(r_s)
                        
                R = np.sum(np.array(r))
                return R
                
        
        
        def updateW(self, trj_Sp_theta, W_0):
                """
                update weigths 
                prior_weigths = W_0
                """
                def fun(x):
                        global trj_Sp_theta_z
                        W_0 = [[x[0], x[1]],[x[2], x[3]]]
                        #W_0 = x
                        r_0 = self.reward_trj(trj_Sp_theta, W_0)
                        return -1*r_0                        
                import numpy as np
                from scipy.optimize import minimize
                
                global trj_Sp_theta_z 
                trj_Sp_theta_z = trj_Sp_theta
                delta = 0.1
                cons = ({'type': 'eq',
                          'fun' : lambda x: np.array([np.sum(x)-1])},
                         {'type': 'ineq',
                          'fun' : lambda x: np.array([np.min(x)])}, # greater than zero
                         {'type': 'ineq',
                          'fun' : lambda x: np.array([-np.abs(x[0]-x0[0])+delta])}, # greater than zero
                         {'type': 'ineq',
                          'fun' : lambda x: np.array([-np.abs(x[1]-x0[1])+delta])}, # greater than zero
                          {'type': 'ineq',
                          'fun' : lambda x: np.array([-np.abs(x[2]-x0[2])+delta])}, # greater than zero
                         {'type': 'ineq',
                          'fun' : lambda x: np.array([-np.abs(x[3]-x0[3])+delta])}) # greater than zero

                x0 = [W_0[0][0], W_0[0][1], W_0[1][0], W_0[1][1]]   # with dir 
                #x0 = W_0 # no dir
                res = minimize(fun, x0, constraints=cons)
                x = res.x
                W = [[x[0], x[1]],[x[2], x[3]]] # with dir
                #W = x
                return W
                
        def findStarting(self, trj_Ps_theta, trj_Ps, W_1, starting_n=10 , method = 'RL'):
                """
                trj_Ps_theta: 
                         size n_theta x n_frames
                trj_Ps:
                """
                # get new starting points (in theta domain) using new reward function based on updated weigths (W_1)
                import numpy as np               
                theta_mean = []
                theta_std = []
                for theta in range(len(W_1)):
                    theta_mean.append(np.mean(trj_Ps_theta[theta]))
                    theta_std.append(np.std(trj_Ps_theta[theta]))
                        
                ranks = {}
                trj_Ps_theta = np.array(trj_Ps_theta)
                for state_index in range(len(trj_Ps_theta[0])):
                        state_theta = trj_Ps_theta[:,state_index]
                        
                        r = self.reward_state(state_theta, theta_mean, theta_std, W_1)
                        
                        ranks[state_index] = r

                newPoints_index0 = sorted(ranks.items(), key=lambda x: x[1], reverse=True)[0:starting_n] 
                newPoints_index = np.array(newPoints_index0)[:,0]   
                
                #n_coord = len(trj_Ps)
                n_coord = 1                     
                #newPoints = []
                newPoints = [trj_Ps[int(i)] for i in newPoints_index]
                #for coord in range(n_coord):
                #          newPoints.append([trj_Ps[coord][int(i)] for i in newPoints_index])                                   
                return newPoints
        
 

	

