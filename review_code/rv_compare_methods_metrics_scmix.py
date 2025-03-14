
import statsmodels.api as sm
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

#import ssl; ssl._create_default_https_context = ssl._create_unverified_context
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.decomposition import NMF
from sklearn.decomposition import FastICA
from sklearn.pipeline import Pipeline

from sciRED import ensembleFCA as efca
from sciRED import glm
from sciRED import rotations as rot
from sciRED import metrics as met

from sciRED.utils import preprocess as proc
from sciRED.utils import visualize as vis
from sciRED.utils import corr
from sciRED.examples import ex_preprocess as exproc
from sciRED.examples import ex_visualize as exvis

import re

np.random.seed(10)
NUM_COMPONENTS = 30
NUM_GENES = 2000
NUM_COMP_TO_VIS = 5


### metrics to compare the methods
# Quality
#Number of covariates missing a factor
#Number of entangled covariates 
#Factor split across multiple factors

############ pca #############
file_name = '/home/delaram/sciRED//review_analysis/benchmark_methods/pca_scores_scMix_numcomp_'+str(NUM_COMPONENTS)+'.csv'
pca_scores = pd.read_csv(file_name, index_col=0)
## select columns with names as F* from pca_scores
pattern_cols = [col for col in pca_scores.columns if 'F' in col]
pca_scores_factor = pca_scores[pattern_cols]

#Time taken - 10F:  12.612469673156738
#time taken (min) - 10F:  0.21020782788594564

#Time taken - 30 F:  11.745956420898438
#time taken (min) - 30 F:  0.1957659403483073


############ nmf ############
file_name = '/home/delaram/sciRED//review_analysis/benchmark_methods/nmf_scores_scMix_numcomp_'+str(NUM_COMPONENTS)+'.csv'
nmf_scores = pd.read_csv(file_name, index_col=0)
## select columns with names as F* from nmf_scores
pattern_cols = [col for col in nmf_scores.columns if 'F' in col]
nmf_scores_factor = nmf_scores[pattern_cols]


#Time to fit NMF - F 10 :  0.334092378616333
#Time to fit NMF (min) - F 10 :  0.005568206310272217

#Time to fit NMF - F 30 :  0.977346658706665
#Time to fit NMF (min) - F 30 :  0.016289110978444418

############ ica ############
file_name = '/home/delaram/sciRED//review_analysis/benchmark_methods/ica_scores_scMix_numcomp_'+str(NUM_COMPONENTS)+'.csv'
ica_scores = pd.read_csv(file_name, index_col=0)
pattern_cols = [col for col in ica_scores.columns if 'F' in col]
ica_scores_factor = ica_scores[pattern_cols]

#Time to fit ica - numcomp 10 :  0.40137553215026855
#Time to fit ica (min) - numcomp 10 :  0.006689592202504476

#Time to fit ica - numcomp 30 :  0.5132331848144531
#Time to fit ica (min) - numcomp 30 :  0.008553886413574218

############ cnmf ############
file_name = '/home/delaram/sciRED/review_analysis/benchmark_methods/cNMF/scMix_cNMF_v2_numcomp_'+str(NUM_COMPONENTS)+'_usage.csv'
cnmf_scores = pd.read_csv(file_name, index_col=0)
pattern_cols = [col for col in cnmf_scores.columns if 'F' in col]
cnmf_scores_factor = cnmf_scores[pattern_cols]

#Time taken (min) - numcomp 30 :  100.98875205119451
#Time taken (second) - numcomp 30 :  6059.3251230716705


############ zinbwave ############ 
file_name = '/home/delaram/sciRED//review_analysis/benchmark_methods/zinbwave_scores_scMix_numcomp_'+str(NUM_COMPONENTS)+'.csv'
zinbwave_scores = pd.read_csv(file_name, index_col=0)
pattern_cols = [col for col in zinbwave_scores.columns if 'W' in col]
zinbwave_scores_factor = zinbwave_scores[pattern_cols]
#"run time for zinbwave - scMix - #F: 30 is: 127485.687"

############ scvi ############

file_name = '/home/delaram/sciRED//review_analysis/benchmark_methods/scvi_scores_scMix_numcomp_'+str(NUM_COMPONENTS)+'.csv'
scvi_scores = pd.read_csv(file_name, index_col=0)
pattern_cols = [col for col in scvi_scores.columns if re.match(r'^F\d+', col)]
scvi_scores_factor = scvi_scores[pattern_cols]

#Time to fit scVI - numcomp 10 :  72.26717019081116
#Time to fit scVI (min) - numcomp 10 :  1.2044528365135192

#Time to fit scVI - numcomp 30 :  74.121915102005
#Time to fit scVI (min) - numcomp 30 :  1.2353652517000835

############ scCoGAPs ############
file_name = '/home/delaram/sciRED//review_analysis/benchmark_methods/scCoGAPS_scores_scMix.csv'
scCoGAPs_scores = pd.read_csv(file_name, index_col=0)
pattern_cols = [col for col in scCoGAPs_scores.columns if 'Pattern' in col]
scCoGAPs_scores_factor = scCoGAPs_scores[pattern_cols]

#time taken: ~38 hours = 136800 seconds

############ sciRED ############
file_name = '/home/delaram/sciRED//review_analysis/benchmark_methods/sciRED_scores_scMix_numcomp_'+str(NUM_COMPONENTS)+'.csv'
sciRED_scores = pd.read_csv(file_name, index_col=0)
pattern_cols = [col for col in sciRED_scores.columns if re.match(r'^F\d+', col)]
sciRED_scores_factor = sciRED_scores[pattern_cols]

#Time taken - 10 F:  14.09949016571045 
#Time taken (min) - 10 F:  0.23499150276184083

#Time taken - 30 F:  12.847084999084473
#Time taken (min) - 30 F:  0.21411808331807455


y_sample = pca_scores['sample'].reset_index(drop=True)
y_cell_line = pca_scores['cell_line'].reset_index(drop=True)

### create a dictonrary for FA run times in seconds  
fa_time_dict = {}
fa_time_dict['sciRED'] = 12.847084999084473
fa_time_dict['pca'] = 11.745956420898438
fa_time_dict['ica'] = 0.5132331848144531
fa_time_dict['nmf'] = 0.977346658706665
fa_time_dict['scvi'] = 74.121915102005 
fa_time_dict['zinbwave'] = 127485.687 
fa_time_dict['cnmf'] = 6059.3251230716705
fa_time_dict['scCoGAPs'] = 136800 # needs to be updated


### create a dictoinary of scores for each method in a loop
fa_dict = {}
fa_dict['sciRED'] = sciRED_scores_factor.to_numpy()
fa_dict['pca'] = pca_scores_factor.to_numpy()
fa_dict['ica'] = ica_scores_factor.to_numpy()
fa_dict['nmf'] = nmf_scores_factor.to_numpy()
fa_dict['scvi'] = scvi_scores_factor.to_numpy()
fa_dict['zinbwave'] = zinbwave_scores_factor.to_numpy()
fa_dict['cnmf'] = cnmf_scores_factor.to_numpy()
fa_dict['scCoGAPs'] = scCoGAPs_scores_factor.to_numpy()


### create a dictoinary of y_sample for each method in a loop
### run FCAT on each method in a loop and save the results in a dictionary
fcat_dict_sample = {}
fcat_dict_cell_line = {}
### make dictionaries for threshold, matched factors and covariates
threshold_dict = {}
matched_factor_dict = {}
matched_covariate_dict = {}


for method, fa_scores in fa_dict.items():
    
    fcat_sample = efca.FCAT(y_sample, fa_scores, scale='standard', mean='arithmatic')
    fcat_cell_line = efca.FCAT(y_cell_line, fa_scores, scale='standard', mean='arithmatic')
    
    fcat_dict_sample[method] = fcat_sample
    fcat_dict_cell_line[method] = fcat_cell_line

    ### plot the FCAT scores
    fcat = pd.concat([fcat_sample, fcat_cell_line], axis=0)
    fcat = fcat[fcat.index != 'NA'] ### remove the rownames called NA from table

    vis.plot_FCAT(fcat, title='', color='coolwarm',
                x_axis_fontsize=20, y_axis_fontsize=20, title_fontsize=22,
                x_axis_tick_fontsize=32, y_axis_tick_fontsize=34)
    

    ### using Otsu's method to calculate the threshold
    threshold = efca.get_otsu_threshold(fcat.values.flatten())

    vis.plot_histogram(fcat.values.flatten(),
                    xlabel='Factor-Covariate Association scores',
                    title='FCAT score distribution',
                    threshold=threshold)


    ## rownames of the FCAT table
    all_covariate_levels = fcat.index.values
    matched_factor_dist, percent_matched_fact = efca.get_percent_matched_factors(fcat, threshold)
    matched_covariate_dist, percent_matched_cov = efca.get_percent_matched_covariates(fcat, threshold=threshold)
    print('percent_matched_fact: ', percent_matched_fact)
    print('percent_matched_cov: ', percent_matched_cov)
    vis.plot_matched_factor_dist(matched_factor_dist)
    vis.plot_matched_covariate_dist(matched_covariate_dist, 
                                    covariate_levels=all_covariate_levels)
    
    threshold_dict[method] = threshold
    matched_factor_dict[method] = matched_factor_dist
    matched_covariate_dict[method] = matched_covariate_dist

    


### make dictionarues for saving the results for number of covariates missing a factor, entangled covariates, factors split across multiple covariates
missing_factor_dict = {}
entangled_covariate_dict = {}
split_factor_dict = {}


### for each method - print hte number of covariates missing a factor
for method in matched_covariate_dict.keys():
    print('method: ', method)
    matched_covariate_dist = matched_covariate_dict[method]
    matched_covariate_dist = matched_covariate_dist[matched_covariate_dist == 0]
    #print(matched_covariate_dist)
    print('number of covariates missing a factor: ', matched_covariate_dist.shape[0])
    print('')
    missing_factor_dict[method] = matched_covariate_dist.shape[0]

### for each method - print hte number of covariates matched with more than one factor (entangled covariates)
for method in matched_covariate_dict.keys():
    print('method: ', method)
    matched_covariate_dist = matched_covariate_dict[method]
    matched_covariate_dist = matched_covariate_dist[matched_covariate_dist > 1]
    print('#covariates matched with more than one factor: ', matched_covariate_dist.shape[0])
    print('')
    entangled_covariate_dict[method] = matched_covariate_dist.shape[0]


### for each method - print the number of factors split across multiple covariates
for method in matched_factor_dict.keys():
    print('method: ', method)
    matched_factor_dist = matched_factor_dict[method]
    matched_factor_dist = matched_factor_dist[matched_factor_dist > 1]
    print('#factors split across multiple covariates: ', matched_factor_dist.shape[0])
    print('')
    split_factor_dict[method] = matched_factor_dist.shape[0]



### save teh results in a csv file
file_name = '/home/delaram/sciRED//review_analysis/benchmark_methods/metrics_scmix.csv'
df = pd.DataFrame([missing_factor_dict, entangled_covariate_dict, split_factor_dict])
df = df.T
## add run time to the dataframe
df['run_time'] = df.index.map(fa_time_dict)
## add column names 
df.columns = ['missing_factor', 'entangled_covariate', 'split_factor', 'run_time']
## print the dataframe
print(df)
#df.to_csv(file_name)



#### plot each metric for each method in a bar plot - four separate plots

### calculate total number of unique covariates levels based on the matched_covariate_dict
unique_covariate_levels = set()
for method in matched_covariate_dict.keys():
    matched_covariate_dist = matched_covariate_dict[method]
    unique_covariate_levels.update(matched_covariate_dist.index.values)
print('total number of unique covariate levels: ', len(unique_covariate_levels))
num_unique_covariate_levels = len(unique_covariate_levels)

#### plot each metric for each method in a bar plot - four separate plots

# Figure 1: Number of covariates missing a factor
fig = plt.figure(figsize=(10, 6))
methods = list(missing_factor_dict.keys())
missing_factors = [missing_factor_dict[method] for method in methods]
plt.bar(methods, missing_factors, color='#4C72B0', edgecolor='black')  # Slate blue
## set y axis limit based on the number of unique covariate levels
plt.ylim(0, num_unique_covariate_levels)
plt.title('Number of covariates missing a factor', fontsize=20)
plt.ylabel('Number of covariates', fontsize=20)
plt.xlabel('Methods', fontsize=20)
plt.xticks(fontsize=19, rotation=45)
plt.yticks(fontsize=19)
plt.show()


# Figure 2: Number of entangled covariates
fig = plt.figure(figsize=(10, 6))
methods = list(entangled_covariate_dict.keys())
entangled_covariates = [entangled_covariate_dict[method] for method in methods]
plt.bar(methods, entangled_covariates, color='#55A868', edgecolor='black')  # Medium green
plt.title('Number of entangled covariates', fontsize=20)
plt.ylim(0, num_unique_covariate_levels)
plt.ylabel('Number of covariates', fontsize=20)
plt.xlabel('Methods', fontsize=20)
plt.xticks(fontsize=19, rotation=45)
plt.yticks(fontsize=19)
plt.show()

# Figure 3: Number of factors split across multiple covariates
fig = plt.figure(figsize=(10, 6))
methods = list(split_factor_dict.keys())
split_factors = [split_factor_dict[method] for method in methods]
plt.bar(methods, split_factors, color='#C44E52', edgecolor='black')  # Reddish pink
plt.title('Number of factors split across multiple covariates', fontsize=20)
plt.ylabel('Number of factors', fontsize=20)
plt.xlabel('Methods', fontsize=20)
plt.xticks(fontsize=19, rotation=45)
plt.yticks(fontsize=19)
plt.show()

# Figure 4: Run time (seconds)
fig = plt.figure(figsize=(10, 6))
methods = list(fa_time_dict.keys())
run_times = [fa_time_dict[method] for method in methods]
plt.bar(methods, run_times, color='#8172B2', edgecolor='black')  # Purple
### make it log scale
plt.yscale('log')
plt.title('Run time (log scaled)', fontsize=20)
plt.ylabel('Time (seconds)', fontsize=20)
plt.xlabel('Methods', fontsize=20)
plt.xticks(fontsize=19, rotation=45)
plt.yticks(fontsize=19)
plt.show()

