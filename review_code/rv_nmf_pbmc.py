import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import statsmodels.api as sm

from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.decomposition import NMF
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


np.random.seed(10)
NUM_COMPONENTS = 30
NUM_GENES = 2000
NUM_COMP_TO_VIS = 5

data_file_path = '/home/delaram/sciFA/Data/PBMC_Lupus_Kang8vs8_data.h5ad'
data = exproc.import_AnnData(data_file_path)
data, gene_idx = proc.get_sub_data(data, num_genes=NUM_GENES) # subset the data to num_genes HVGs
y, genes, num_cells, num_genes = proc.get_data_array(data)
y_sample, y_stim, y_cell_type, y_cluster  = exproc.get_metadata_humanPBMC(data)

colors_dict_humanPBMC = exvis.get_colors_dict_humanPBMC(y_sample, y_stim, y_cell_type)
plt_legend_sample = exvis.get_legend_patch(y_sample, colors_dict_humanPBMC['sample'] )
plt_legend_stim = exvis.get_legend_patch(y_stim, colors_dict_humanPBMC['stim'] )
plt_legend_cell_type = exvis.get_legend_patch(y_cell_type, colors_dict_humanPBMC['cell_type'] )


#### design matrix - library size only
x = proc.get_library_design_mat(data, lib_size='nCount_originalexp')

####################################
#### Running NMF on the count data ######
####################################
nmf = NMF(n_components=NUM_COMPONENTS, init='nndsvd', random_state=0)
nmf_scores = nmf.fit_transform(y)
nmf_loading = nmf.components_
nmf_loading.shape

factor_loading = nmf_loading
factor_scores = nmf_scores

NUM_COMP_TO_VIS = 10
### make a dictionary of colors for each sample in y_sample
vis.plot_pca(factor_scores, NUM_COMP_TO_VIS, 
             cell_color_vec= colors_dict_humanPBMC['cell_type'],
               legend_handles=True,
               title='NMF factors on count data',
               plt_legend_list=plt_legend_cell_type)

vis.plot_pca(factor_scores, NUM_COMP_TO_VIS, 
             cell_color_vec= colors_dict_humanPBMC['stim'],
               legend_handles=True,
               title='NMF factors on count data',
               plt_legend_list=plt_legend_stim)

vis.plot_pca(factor_scores, NUM_COMP_TO_VIS, 
             cell_color_vec= colors_dict_humanPBMC['sample'],
               legend_handles=True,
               title='NMF factors on count data',
               plt_legend_list=plt_legend_sample)

#### plot the loadings of the factors
vis.plot_factor_loading(nmf_loading.T, genes, 0, 1, fontsize=10, 
                    num_gene_labels=2,
                    title='Scatter plot of the loading vectors', 
                    label_x=True, label_y=True)



####################################
#### Matching between factors and covariates ######
####################################
######## NMF factors
factor_loading = nmf_loading
factor_scores = nmf_scores
covariate_vec = y_stim
covariate_level = np.unique(covariate_vec)[1]


nmf_loading_df = pd.DataFrame(nmf_loading)
nmf_loading_df = nmf_loading_df.T
nmf_loading_df.columns = ['F'+str(i) for i in range(1, nmf_loading_df.shape[1]+1)]
nmf_loading_df.index = genes


### save to csv file
nmf_scores_df = pd.DataFrame(nmf_scores)
nmf_scores_df.columns = ['F'+str(i) for i in range(1, nmf_scores_df.shape[1]+1)]
nmf_scores_df.index = data.obs.index.values
nmf_scores_df_merged = pd.concat([data.obs, nmf_scores_df], axis=1)
nmf_scores_df_merged.to_csv('/home/delaram/sciRED/review_analysis/NMF_scores_df_merged_lupusPBMC.csv')
nmf_loading_df.to_csv('/home/delaram/sciRED/review_analysis/NMF_loading_df_lupusPBMC.csv')



####################################
#### FCAT score calculation ######
####################################

### FCAT needs to be calculated for each covariate separately
fcat_sample = efca.FCAT(y_sample, factor_scores, scale='standard', mean='arithmatic')
fcat_stim = efca.FCAT(y_stim, factor_scores, scale='standard', mean='arithmatic')
fcat_cell_type = efca.FCAT(y_cell_type, factor_scores, scale='standard', mean='arithmatic')


### concatenate FCAT table for protocol and cell line
fcat = pd.concat([fcat_sample, fcat_stim, fcat_cell_type], axis=0)

fcat = pd.concat([fcat_stim, fcat_cell_type], axis=0)
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


### select the factors that are matched with any covariate level
matched_factor_index = np.where(matched_factor_dist>0)[0] 
fcat_matched = fcat.iloc[:,matched_factor_index] 
x_labels_matched = fcat_matched.columns.values
vis.plot_FCAT(fcat_matched, x_axis_label=x_labels_matched, title='', color='coolwarm',
                                 x_axis_fontsize=40, y_axis_fontsize=39, title_fontsize=40,
                                 x_axis_tick_fontsize=36, y_axis_tick_fontsize=38, 
                                 save=False, save_path='../Plots/mean_importance_df_matched_PBMC.pdf')

factor_libsize_correlation = corr.get_factor_libsize_correlation(factor_scores, library_size = data.obs.nCount_originalexp)
vis.plot_factor_cor_barplot(factor_libsize_correlation, 
             title='Correlation of factors with library size', 
             y_label='Correlation', x_label='Factors')


### concatenate FCAT table for protocol and cell line
fcat = pd.concat([fcat_stim, fcat_cell_type], axis=0)
fcat = fcat[fcat.index != 'NA'] ### remove the rownames called NA from table

vis.plot_FCAT(fcat, title='', color='coolwarm',
              x_axis_fontsize=40, y_axis_fontsize=39, title_fontsize=40,
              x_axis_tick_fontsize=36, y_axis_tick_fontsize=40, 
              save=False, save_path='../Plots/mean_importance_df_matched_PBMC.pdf')


stim_fcat_sorted_scores, stim_factors_sorted = vis.plot_sorted_factor_FCA_scores(fcat, 'stim')


####################################
#### Bimodality scores
#silhouette_score = met.kmeans_bimodal_score(factor_scores, time_eff=True)
bimodality_index = met.bimodality_index(factor_scores)
#bimodality_score = np.mean([silhouette_score, bimodality_index], axis=0)
bimodality_score = bimodality_index
#### Effect size
factor_variance = met.factor_variance(factor_scores)

## Specificity
simpson_fcat = met.simpson_diversity_index(fcat)

### label dependent factor metrics
asv_cell_type = met.average_scaled_var(factor_scores, covariate_vector=y_cell_type, mean_type='arithmetic')
asv_stim = met.average_scaled_var(factor_scores, covariate_vector=y_stim, mean_type='arithmetic')
asv_sample = met.average_scaled_var(factor_scores, y_sample, mean_type='arithmetic')


########### create factor-interpretibility score table (FIST) ######
metrics_dict = {'Bimodality':bimodality_score, 
                    'Specificity':simpson_fcat,
                    'Effect size': factor_variance,
                    'Homogeneity (cell type)':asv_cell_type,
                    "Homogeneity (stimulated)":asv_stim,
                    'Homogeneity (sample)':asv_sample}

fist = met.FIST(metrics_dict)
vis.plot_FIST(fist, title='Scaled metrics for all the factors')
### subset the first 15 factors of fist dataframe
vis.plot_FIST(fist.iloc[0:15,:])
vis.plot_FIST(fist.iloc[matched_factor_index,:])
