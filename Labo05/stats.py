def fdr_correction(pval,qval=0.05):
    
    import numpy as np
    
    # Sort p-values
    pval_S = list(pval)
    pval_S.sort()

    # Number of observations
    N = len(pval)

    # Order (indices), in the same size as the p-values
    idx = np.array(range(1,N+1),dtype=float)

    # Line to be used as cutoff
    cV = np.sum(1/idx)
    thrline = idx*qval/float(N*cV)

    # Find the largest pval, still under the line
    thr = max([p for i,p in enumerate(pval_S) if p<=thrline[i]])
    
    return thr

def SAM(X,y,N_shuffle=2):
# X has N_genes rows and N_cond colums
# y refers to the classes    

    from scipy import stats
    import numpy as np
    import matplotlib.pyplot as plt
    from scipy.stats import t
    
    N_genes = np.shape(X)[0]
    N_cond = np.shape(X)[1]

    idx0 = [i for i,yi in enumerate(y) if yi==0]    
    idx1 = [i for i,yi in enumerate(y) if yi==1]    
    
    X = np.array(X,dtype=float)
    
    # t-test for each gene (also randomized)
    tt = []
    pval = []
    tt_random = []
    for i in range(N_genes):
        ttest = stats.ttest_ind(X[i,idx0],X[i,idx1],equal_var=False)
        t.append(ttest[0])
        pval.append(ttest[1])
        # compute N_shuffle permutations to calculate wx_random
        tt_tmp = []
        for j in range(0,N_shuffle):
            X_random = shuffle_data(X)
            tt_tmp.append(stats.ttest_ind(X_random[i,idx0],X_random[i,idx1],equal_var=False)[0])
        tt_random.append(np.mean(tt_tmp))
        
    # Sort
    tt.sort()
    tt_random.sort()
       
    # Plot
    plt.figure()
    plt.plot(tt_random,t,'k.')
    plt.xlabel('Expected Correlation (if random)')
    plt.ylabel('Observed Correlation')
    plt.grid()
    plt.title('SAM')
    
    # significance levels
    fdr_pval = fdr_correction(pval)
    corr_fdr = t.ppf(1-fdr_pval/2.0,N_cond-1) 
    xx = np.linspace(np.min(tt_random),np.max(tt_random),10)
    plt.plot(xx,xx+corr_fdr,'k--')
    plt.plot(xx,xx-corr_fdr,'k--')
    plt.show()
    
def volcano_plot(X,y,pval=[],idx=[]):
    
    import scipy.stats as ss
    import numpy as np    
    import matplotlib.pyplot as plt
    
    N_genes = np.shape(X)[0]    
    
    idx0 = [i for i,yi in enumerate(y) if yi==0]    
    idx1 = [i for i,yi in enumerate(y) if yi==1]    
    
    X = np.array(X,dtype=float)
    
    p = [] # p-value
    fc = [] # fold change
    for i in range(N_genes):
        corr = ss.pearsonr(X[i,:],y)
        if len(pval)==0:
            p.append(corr[1])
        else:
            p.append(pval[i])
        fc.append(np.mean(X[i,idx1])/np.mean(X[i,idx0]))
        
    significance_pval = fdr_correction(p)
    
    plt.figure()
    plt.plot(-np.log2(fc),-np.log10(p),'b.',zorder=0)
    plt.xlabel('-log2(fold change)')
    plt.ylabel('-log10(p-value)')
    minix = min(-np.log2(fc))
    maxix = max(-np.log2(fc))
    mm = max(np.abs(minix),maxix)+0.1
    fc = np.array(fc)
    p = np.array(p)
    plt.plot(-np.log2(fc[idx]),-np.log10(p[idx]),'r.',zorder=1)
    plt.hlines(-np.log10(significance_pval),-mm,mm,'k',linestyles='dotted',lw=4,zorder=2)
    plt.xlim([-mm,mm])
    plt.title('Volcano plot')
    plt.show()
        
def shuffle_data(X):
    
    from random import shuffle
    import numpy as np
    
    # get shuffled columns indexes
    shuffled_idx = range(0,np.shape(X)[1]) 
    shuffle(shuffled_idx) 

    # use shuffled_idx to randomize the columns of data
    X_random = X[:,shuffled_idx]

    return X_random
    
