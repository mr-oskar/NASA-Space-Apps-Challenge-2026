from pathlib import Path
import sys, json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
sys.path.insert(0,str(Path(__file__).parent))
from pipeline import ROOT, PROC, REF, OUT, FIG

sns.set_theme(style='whitegrid', context='talk')

def save(fig, path):
    path.parent.mkdir(parents=True, exist_ok=True); fig.tight_layout(); fig.savefig(path,dpi=180,bbox_inches='tight'); plt.close(fig)

def run():
    gale=np.load(REF/'gale_mola_elevation_m.npy'); atac=np.load(REF/'atacama_nasadem_elevation_m.npy')
    slope=np.load(PROC/'atacama_slope_normalized.npy'); rough=np.load(PROC/'atacama_roughness_normalized.npy')
    # Raw and harmonized maps
    fig,ax=plt.subplots(1,2,figsize=(15,6)); im=ax[0].imshow(gale,cmap='terrain'); ax[0].set_title('Mars reference: Gale / MOLA raw elevation (m)'); plt.colorbar(im,ax=ax[0],shrink=.8)
    im=ax[1].imshow(atac,cmap='terrain'); ax[1].set_title('Earth search domain: Atacama / NASADEM raw elevation (m)'); plt.colorbar(im,ax=ax[1],shrink=.8); save(fig,FIG/'processing/01_raw_elevation_maps.png')
    fig,ax=plt.subplots(1,3,figsize=(18,5));
    for a,arr,title in zip(ax,[np.load(PROC/'gale_elevation_normalized.npy'),np.load(PROC/'atacama_elevation_normalized.npy'),slope],['Gale normalized elevation','Atacama normalized elevation','Atacama normalized slope']):
        im=a.imshow(arr,cmap='viridis',vmin=0,vmax=1); a.set_title(title); plt.colorbar(im,ax=a,shrink=.8)
    save(fig,FIG/'processing/02_harmonized_normalized_maps.png')
    # distributions
    fig,ax=plt.subplots(1,2,figsize=(14,5)); ax[0].hist(gale[np.isfinite(gale)].ravel(),bins=50,color='#c45b34'); ax[0].set_title('MOLA elevation distribution'); ax[0].set_xlabel('m'); ax[1].hist(atac[np.isfinite(atac)].ravel(),bins=70,color='#2a7f62'); ax[1].set_title('NASADEM elevation distribution'); ax[1].set_xlabel('m'); save(fig,FIG/'processing/03_distributions_after_qc.png')
    # rankings
    df=pd.read_csv(OUT/'candidate_rankings.csv').head(20).sort_values('confidence_score'); fig,ax=plt.subplots(figsize=(12,8)); colors=df['class'].map({'high':'#1b9e77','neutral':'#d95f02','low':'#7570b3'}); ax.barh(df['cell_id'],df['confidence_score'],color=colors); ax.set_xlim(0,1); ax.set_xlabel('Prototype confidence score (not calibrated probability)'); ax.set_title('Top candidate ranking for Gale-to-Atacama search'); save(fig,FIG/'algorithm/01_candidate_ranking.png')
    fig,ax=plt.subplots(figsize=(8,6)); counts=pd.read_csv(OUT/'candidate_rankings.csv')['class'].value_counts().reindex(['high','neutral','low'],fill_value=0); ax.bar(counts.index,counts.values,color=['#1b9e77','#d95f02','#7570b3']); ax.set_title('Candidate confidence classes'); ax.set_ylabel('cells'); save(fig,FIG/'algorithm/02_confidence_classes.png')
    fig,ax=plt.subplots(figsize=(10,7)); d=pd.read_csv(OUT/'candidate_rankings.csv'); sc=ax.scatter(d['elevation_mean'],d['slope_mean'],c=d['confidence_score'],cmap='plasma',vmin=0,vmax=1,s=35); ax.set_xlabel('Earth cell mean elevation (m)'); ax.set_ylabel('Earth cell mean slope (deg)'); ax.set_title('Evidence-aware candidate space'); plt.colorbar(sc,label='confidence score'); save(fig,FIG/'algorithm/03_candidate_feature_space.png')

if __name__=='__main__': run()
