"""Reproducible prototype pipeline for the Inferential-Node Planetary Analog Algorithm.

This module deliberately separates data harmonization, feature extraction, and
candidate reasoning. It does not claim a calibrated scientific probability.
"""
from pathlib import Path
import json, re, zipfile
import numpy as np
import pandas as pd
import rasterio
from rasterio.merge import merge
from rasterio.transform import from_origin
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data/raw"
PROC = ROOT / "data/processed"
REF = ROOT / "data/reference_region"
OUT = ROOT / "data/algorithm_outputs"
FIG = ROOT / "figures"
for p in [PROC, REF, OUT, FIG/"processing", FIG/"algorithm"]: p.mkdir(parents=True, exist_ok=True)


def read_mola_crop(center_lat=-5.4, center_lon=137.8, half_deg=5.0):
    """Read the PDS MEG016 big-endian int16 global map and crop Gale region."""
    img = RAW / "mars/megt90n000eb.img"
    arr = np.memmap(img, dtype=">i2", mode="r", shape=(2880, 5760))
    row0 = max(0, int((90 - (center_lat + half_deg))*16))
    row1 = min(arr.shape[0], int((90 - (center_lat - half_deg))*16))
    col0 = int(center_lon*16 - half_deg*16)
    col1 = int(center_lon*16 + half_deg*16)
    crop = np.array(arr[row0:row1, col0:col1], dtype="float32")
    crop[crop == 0] = np.nan
    lats = 90 - (np.arange(row0, row1) + 0.5)/16
    lons = (np.arange(col0, col1) + 0.5)/16
    meta = {"source":"MOLA MEGDR 16 pixels/degree", "shape":list(crop.shape), "lat_min":float(lats.min()), "lat_max":float(lats.max()), "lon_min":float(lons.min()), "lon_max":float(lons.max()), "units":"m", "dtype":"int16 big-endian"}
    np.save(REF/"gale_mola_elevation_m.npy", crop)
    (REF/"gale_mola_metadata.json").write_text(json.dumps(meta, indent=2))
    return crop, lats, lons, meta


def mosaic_nasadem():
    paths = sorted((RAW/"earth").glob("NASADEM_HGT_*.tif"))
    if not paths: raise FileNotFoundError("NASADEM COGs not found")
    datasets = [rasterio.open(p) for p in paths]
    data, transform = merge(datasets)
    meta = datasets[0].meta.copy(); meta.update({"height":data.shape[1],"width":data.shape[2],"transform":transform,"count":1,"dtype":"float32","nodata":-32767})
    for ds in datasets: ds.close()
    dem = data[0].astype("float32")
    dem[dem <= -32760] = np.nan
    with rasterio.open(PROC/"atacama_nasadem_mosaic.tif", "w", **meta) as dst: dst.write(np.nan_to_num(dem,nan=-32767).astype("float32"),1)
    np.save(REF/"atacama_nasadem_elevation_m.npy", dem)
    return dem, transform, meta


def terrain_features(elev, pixel_x_m, pixel_y_m):
    """Compute robust, comparable terrain features from an elevation array."""
    fill = np.nanmedian(elev)
    z = np.where(np.isfinite(elev), elev, fill)
    gy, gx = np.gradient(z, pixel_y_m, pixel_x_m)
    slope = np.degrees(np.arctan(np.hypot(gx, gy)))
    rough = np.sqrt(np.maximum(0, (z - _mean_filter(z))**2))
    return {"elevation_m":elev, "slope_deg":slope, "roughness_m":rough}


def _mean_filter(a, k=5):
    pad = np.pad(a, k//2, mode="edge")
    out = np.zeros_like(a, dtype="float32")
    for i in range(k):
        for j in range(k): out += pad[i:i+a.shape[0],j:j+a.shape[1]]
    return out/(k*k)


def robust_normalize(a, low=2, high=98):
    q1,q2=np.nanpercentile(a,[low,high]); return np.clip((a-q1)/(q2-q1+1e-9),0,1).astype("float32"), {"p02":float(q1),"p98":float(q2)}


def cell_features(elev, transform, bbox=(-70,-25,-68,-21), cell_deg=0.25):
    """Aggregate Earth terrain features into cells while preserving cell IDs."""
    west,south,east,north=bbox
    rows=[]
    with rasterio.open(PROC/"atacama_nasadem_mosaic.tif") as ds:
        window=rasterio.windows.from_bounds(west,south,east,north,ds.transform)
        data=ds.read(1,window=window).astype('float32'); data[data<=-32760]=np.nan
        tr=ds.window_transform(window)
    resx,resy=abs(tr.a),abs(tr.e)
    npx=max(1,int(cell_deg/resx)); npy=max(1,int(cell_deg/resy))
    for r in range(0,data.shape[0],npy):
        for c in range(0,data.shape[1],npx):
            x=data[r:min(r+npy,data.shape[0]),c:min(c+npx,data.shape[1])]
            if min(x.shape) < 2 or np.isfinite(x).sum()<0.5*x.size: continue
            gy,gx=np.gradient(np.nan_to_num(x,nan=np.nanmedian(x)),resy*111320,resx*111320)
            slope=np.degrees(np.arctan(np.hypot(gx,gy)))
            rows.append({"cell_id":f"r{r}_c{c}","row":r,"col":c,"lat":tr.f+(r+npy/2)*tr.e,"lon":tr.c+(c+npx/2)*tr.a,"elevation_mean":float(np.nanmean(x),),"elevation_std":float(np.nanstd(x)),"slope_mean":float(np.nanmean(slope)),"slope_std":float(np.nanstd(slope)),"valid_fraction":float(np.isfinite(x).mean())})
    df=pd.DataFrame(rows); df.to_csv(OUT/"earth_candidate_cells.csv",index=False); return df


def summarize(a, pixel_m=3704.46):
    gy,gx=np.gradient(np.nan_to_num(a,nan=np.nanmedian(a)), pixel_m, pixel_m)
    slope=np.degrees(np.arctan(np.hypot(gx,gy)))
    return {"elevation_mean":float(np.nanmean(a)),"elevation_std":float(np.nanstd(a)),"slope_mean":float(np.nanmean(slope)),"slope_std":float(np.nanstd(slope))}


def inferential_node_score(target, candidates):
    """Evidence-aware prototype score; confidence is a ranking score, not probability."""
    cols=["elevation_mean","elevation_std","slope_mean","slope_std"]
    ref=np.array([target[c] for c in cols],dtype=float); mat=candidates[cols].to_numpy(float)
    med=np.nanmedian(mat,axis=0); scale=np.nanpercentile(mat,75,axis=0)-np.nanpercentile(mat,25,axis=0); scale[scale==0]=1
    d=np.sqrt(np.nanmean(((mat-ref)/scale)**2,axis=1)); similarity=np.exp(-d)
    coverage=candidates[cols].notna().mean(axis=1).to_numpy()
    # source independence factor is explicit and conservative in this prototype.
    quality=np.minimum(candidates["valid_fraction"].to_numpy(),1.0)
    confidence=np.clip(0.65*similarity+0.20*coverage+0.15*quality,0,1)
    out=candidates.copy(); out["similarity_score"]=similarity; out["evidence_coverage"]=coverage; out["confidence_score"]=confidence
    out["class"]=np.select([confidence>=0.7,confidence>=0.3],["high","neutral"],default="low")
    out=out.sort_values("confidence_score",ascending=False); out.to_csv(OUT/"candidate_rankings.csv",index=False); return out


def run():
    gale,lats,lons,_=read_mola_crop(); mars=terrain_features(gale,3704.46,3704.46)
    mosaic_nasadem()
    with rasterio.open(PROC/"atacama_nasadem_mosaic.tif") as ds: earth=ds.read(1).astype(float); earth[earth<=-32760]=np.nan; px=abs(ds.transform.a)*111320; py=abs(ds.transform.e)*111320
    ef=terrain_features(earth,px,py)
    for name,arr in [("gale_elevation",gale),("atacama_elevation",earth),("atacama_slope",ef["slope_deg"]),("atacama_roughness",ef["roughness_m"])]:
        norm,stats=robust_normalize(arr); np.save(PROC/f"{name}_normalized.npy",norm); (PROC/f"{name}_normalization.json").write_text(json.dumps(stats,indent=2))
    cells=cell_features(earth,None); target=summarize(gale); rankings=inferential_node_score(target,cells)
    (OUT/"target_summary.json").write_text(json.dumps(target,indent=2))
    return target,rankings

if __name__=='__main__': run()
