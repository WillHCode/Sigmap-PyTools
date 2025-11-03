import fnmatch
import io
import os
import tempfile
import zipfile
from pathlib import Path
from typing import Optional

import geopandas as gpd
import requests

from ..logger import logging

logger = logging.getLogger(__name__)

def clear_gadm_temp_files(
    dirs=None,
    patterns=None,
    dry_run=False,
    verbose=False,
    extra_path_to_check: list=None,
):
    """
    Clear GADM temporary files from specified directories.

    Parameters
    ----------
    dirs : list or None, default None
        Directories to search. If None, uses temp directory
    patterns : list or None, default None
        File patterns to match. If None, uses default GADM patterns
    dry_run : bool, default False
        If True, only report files without deleting
    verbose : bool, default False
        Enable verbose logging
    extra_path_to_check : list or None, default None
        Additional paths to check

    Returns
    -------
    list
        List of file paths (candidates if dry_run, removed if not)
    """
    if dirs is None:
        dirs = [tempfile.gettempdir()]
        if extra_path_to_check is not None:
            dirs.extend(extra_path_to_check)
    dirs = [Path(d) for d in dirs if Path(d).exists()]

    if patterns is None:
        patterns = ['gadm*', 'gadm_*', '*gadm*', 'gadm.*', '*.gdb', '*.shp', '*.shx', '*.dbf', '*.prj', '*.zip', '*.gpkg', '*.sqlite']

    candidates = []
    for d in dirs:
        for root, _, files in os.walk(d):
            for pat in patterns:
                for fname in fnmatch.filter(files, pat):
                    candidates.append(Path(root) / fname)

    candidates = sorted({str(p.resolve()) for p in candidates})

    if verbose:
        if not candidates:
            logger.info("No candidate GADM/temp files found in: " + str([str(d) for d in dirs]))
        else:
            logger.info(f"Candidate files (count = {len(candidates)}):")
            for p in candidates:
                logger.info(f"  {p}")

    removed = []
    if not dry_run:
        for p in candidates:
            try:
                Path(p).unlink()
                removed.append(p)
            except Exception as e:
                logger.error(f"Failed to remove {p}: {e}")

        if verbose:
            logger.info(f"Removed {len(removed)} files.")
    else:
        if verbose:
            logger.info("Dry-run mode: no files were deleted. Set dry_run=False to actually delete them.")

    return candidates if dry_run else removed


def check_already_exist(iso3: str, level: int = 0, cache_dir: Optional[str] = None) -> Optional[str]:
    """
    Check if GADM shapefile already exists in cache directory.

    Parameters:
    -----------
    iso3 : str
        ISO3 country code
    level : int
        Administrative level (0 = country boundary)
    cache_dir : str
        Directory to check for existing files

    Returns:
    --------
    str or None : Path to existing shapefile if found, None otherwise
    """
    if cache_dir is None:
        return None

    if not os.path.exists(cache_dir):
        return None

    iso3 = iso3.upper()

    pattern = f"gadm41_{iso3}_{level}.shp"
    for file in os.listdir(cache_dir):
        if file == pattern:
            shp_path = os.path.join(cache_dir, file)
            logger.info(f"Found cached shapefile: {shp_path}")
            return shp_path

    matching_files = [f for f in os.listdir(cache_dir) if f.startswith(f"gadm41_{iso3}_") and f.endswith(".shp")]

    if matching_files:
        matching_files.sort()
        for file in matching_files:
            if f"_{level}.shp" in file:
                shp_path = os.path.join(cache_dir, file)
                logger.info(f"Found cached shapefile: {shp_path}")
                return shp_path

        shp_path = os.path.join(cache_dir, matching_files[0])
        logger.warning(f"Exact level not found, using: {shp_path}")
        return shp_path

    return None


def load_country_from_path(shp_path: str) -> gpd.GeoDataFrame:
    """
    Load country geometry from shapefile path.

    Parameters:
    -----------
    shp_path : str
        Path to the shapefile

    Returns:
    --------
    gpd.GeoDataFrame : Loaded geodataframe in EPSG:4326
    """
    if not os.path.exists(shp_path):
        raise FileNotFoundError(f"Shapefile not found: {shp_path}")

    logger.info(f"Loading from cache: {shp_path}")
    gdf = gpd.read_file(shp_path)
    return gdf.to_crs("EPSG:4326")


def download_gadm_country(
        iso3: str,
        level: int = 0,
        cache_dir: Optional[str] = None,
        force_download: bool = False
) -> gpd.GeoDataFrame:
    """
    Download or load GADM country boundary data.

    Parameters:
    -----------
    iso3 : str
        ISO3 country code (e.g., 'FRA', 'USA')
    level : int
        Administrative level (0 = country, 1 = states/regions, etc.)
    cache_dir : str, optional
        Directory to cache downloaded files. If None, uses temp directory.
    force_download : bool
        If True, download even if a cached version exists

    Returns:
    --------
    gpd.GeoDataFrame : Country boundary in EPSG:4326
    """
    assert iso3 is not None
    iso3 = iso3.upper()

    # Check if file already exists (unless force_download is True)
    if not force_download and cache_dir is not None:
        existing_path = check_already_exist(iso3, level, cache_dir)
        if existing_path is not None:
            return load_country_from_path(existing_path)

    logger.info(f"Downloading GADM data for {iso3} (level {level})...")

    url = f"https://geodata.ucdavis.edu/gadm/gadm4.1/shp/gadm41_{iso3}_shp.zip"

    try:
        resp = requests.get(url, timeout=60)
        resp.raise_for_status()
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"Failed to download GADM data for {iso3}: {e}")

    z = zipfile.ZipFile(io.BytesIO(resp.content))

    if cache_dir is None:
        dest = tempfile.mkdtemp(prefix=f"gadm_{iso3}_")
        logger.info(f"Temp file created at {dest}")
        use_temp = True
    else:
        os.makedirs(cache_dir, exist_ok=True)
        dest = cache_dir
        logger.info(f"Caching to {dest}")
        use_temp = False

    z.extractall(dest)

    shp_files = [f for f in os.listdir(dest) if f.endswith(f"_{level}.shp")]
    if not shp_files:
        shp_files = [f for f in os.listdir(dest) if f.endswith(".shp")]
        if not shp_files:
            raise RuntimeError(f"No shapefile found in GADM zip for {iso3} (extracted to {dest})")

    shp_path = os.path.join(dest, shp_files[0])
    gdf = gpd.read_file(shp_path)

    if use_temp:
        logger.info("Cleaning up temp files...")
        clear_gadm_temp_files(dirs=[dest], dry_run=False, verbose=False)

    logger.info(f"Successfully loaded {iso3} (level {level})")
    return gdf.to_crs("EPSG:4326")

if __name__ == '__main__':
    clear_gadm_temp_files(dry_run=True, verbose=True)