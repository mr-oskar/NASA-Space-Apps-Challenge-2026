"""Download reproducible study inputs.

NASA Earthdata protected links require an Earthdata Login. For unattended local
reproduction, the public Planetary Computer STAC mirror is used for NASADEM COGs.
MOLA is downloaded from the PDS Geosciences Node.
"""
from pathlib import Path
import requests, json
ROOT=Path(__file__).resolve().parents[1]; MARS=ROOT/'data/raw/mars'; EARTH=ROOT/'data/raw/earth'; META=ROOT/'data/raw/metadata'

def get(url,path):
    path.parent.mkdir(parents=True,exist_ok=True)
    r=requests.get(url,timeout=300); r.raise_for_status(); path.write_bytes(r.content)

def main():
    base='https://pds-geosciences.wustl.edu/mgs/urn-nasa-pds-mgs_mola_topography_derived/meg016'
    for fn in ['megt90n000eb.img','megt90n000eb.xml','megt90n000eb.hdr']: get(f'{base}/{fn}',MARS/fn)
    tiles=['s22w070','s23w070','s24w070','s22w069','s23w069','s24w069']
    records=[]
    for tile in tiles:
        unsigned=f'https://nasademeuwest.blob.core.windows.net/nasadem-cog/v001/NASADEM_HGT_{tile}.tif'
        signed=requests.get('https://planetarycomputer.microsoft.com/api/sas/v1/sign',params={'href':unsigned},timeout=30).json()['href']
        get(signed,EARTH/f'NASADEM_HGT_{tile}.tif'); records.append({'tile':tile,'asset':unsigned})
    (META/'sources.json').write_text(json.dumps({'mola_base':base,'nasadem_collection':'https://planetarycomputer.microsoft.com/api/stac/v1/collections/nasadem','nasadem_assets':records},indent=2))
if __name__=='__main__': main()
