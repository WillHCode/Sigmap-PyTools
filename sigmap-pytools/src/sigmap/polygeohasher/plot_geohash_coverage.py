import warnings
from typing import Optional, Literal, Tuple

import geopandas as gpd
import matplotlib.cm as cm
import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from geopandas import GeoDataFrame
from shapely import MultiPolygon
from shapely.geometry import box

from .logger import logging
from .utils.geohash import geohashes_to_gdf
from .utils.gadm_download import download_gadm_country
from .utils.polygons import build_single_multipolygon
from .adaptative_geohash_coverage import adaptive_geohash_coverage, geohash_coverage

logger = logging.getLogger(__name__)

def plot_geohash_coverage(
    country_geom: MultiPolygon,
    geohash_dict: dict,
    tiles_gdf: Optional[gpd.GeoDataFrame] = None,
    style: Literal['adaptive', 'single'] = 'adaptive',
    figsize: Tuple[float, float] = (12, 14),
    save_path: Optional[str] = None,
    dpi: int = 200,
    draw_bbox: bool = True,
    draw_country: bool = True,
    label_tiles: bool = False,
    color_by_level: bool = True,
    cmap: str = 'viridis',
    title: Optional[str] = None,
    show_stats: bool = True,
    alpha: float = 0.6,
    edge_color: str = 'navy',
    edge_width: float = 0.7,
    country_color: str = 'crimson',
    country_width: float = 2.5,
    show_legend: bool = True
):
    """
    Universal plotting function for geohash coverage results.
    
    Works with both adaptive_geohash_coverage and geohash_coverage outputs.
    
    Parameters
    ----------
    country_geom : shapely.geometry
        Country boundary geometry (MultiPolygon or Polygon)
    geohash_dict : dict
        Dictionary with level as keys and list of geohashes as values
        Output from adaptive_geohash_coverage or geohash_coverage
    tiles_gdf : gpd.GeoDataFrame, optional
        GeoDataFrame with 'level' column. If None, will be created from geohash_dict
    style : {'adaptive', 'simple', 'heatmap'}
        Visualization style:
        - 'adaptive': Color by level with legend (best for adaptive coverage)
        - 'simple': Single color (good for single-level coverage)
        - 'heatmap': Density-based coloring
    figsize : tuple, default (12, 14)
        Figure size in inches
    save_path : str, optional
        Path to save the figure
    dpi : int, default 200
        Resolution for saved figure
    draw_bbox : bool, default True
        Draw bounding box around country
    draw_country : bool, default True
        Draw country boundary
    label_tiles : bool, default False
        Add geohash labels to tiles (only for ≤100 tiles)
    color_by_level : bool, default True
        Color tiles by geohash level (ignored if style='simple')
    cmap : str, default 'viridis'
        Matplotlib colormap name
    title : str, optional
        Custom title. If None, auto-generates title with stats
    show_stats : bool, default True
        Show statistics in title
    alpha : float, default 0.6
        Tile transparency (0-1)
    edge_color : str, default 'navy'
        Tile edge color
    edge_width : float, default 0.7
        Tile edge width
    country_color : str, default 'crimson'
        Country boundary color
    country_width : float, default 2.5
        Country boundary width
    show_legend : bool, default True
        Show legend for level colors
    
    Returns
    -------
    fig : matplotlib.figure.Figure
        Figure object
    ax : matplotlib.axes.Axes
        Axes object
    """
    
    # Create GeoDataFrame if not provided
    if tiles_gdf is None:
        all_geohashes = []
        all_levels = []
        for level, tiles in geohash_dict.items():
            all_geohashes.extend(tiles)
            all_levels.extend([level] * len(tiles))
        
        if not all_geohashes:
            raise ValueError("No geohashes found in geohash_dict")
        
        tiles_gdf = geohashes_to_gdf(all_geohashes)
        tiles_gdf['level'] = all_levels

    fig, ax = plt.subplots(1, 1, figsize=figsize)
    ax.set_aspect('equal')

    lon_min, lat_min, lon_max, lat_max = country_geom.bounds

    if draw_bbox:
        bbox_geom = box(lon_min, lat_min, lon_max, lat_max)
        bbox_gdf = gpd.GeoDataFrame({'geometry': [bbox_geom]}, crs='EPSG:4326')
        bbox_gdf.plot(
            ax=ax, 
            facecolor='none', 
            edgecolor='orange',
            linewidth=2, 
            linestyle='--', 
            alpha=0.8, 
            zorder=0.5,
            label='Bounding Box'
        )
    
    # Plot tiles based on style
    if style == 'adaptive' and color_by_level and 'level' in tiles_gdf.columns:
        _plot_adaptive_style(ax, tiles_gdf, cmap, alpha, edge_color, edge_width, show_legend)

    else:
        tiles_gdf.plot(
            ax=ax, 
            facecolor='lightblue', 
            edgecolor=edge_color,
            linewidth=edge_width, 
            alpha=alpha, 
            zorder=1,
            label='Geohash Tiles'
        )
    
    # Draw country boundary
    if draw_country:
        country_gdf = gpd.GeoDataFrame({'geometry': [country_geom]}, crs='EPSG:4326')
        country_gdf.plot(
            ax=ax, 
            facecolor='none', 
            edgecolor=country_color,
            linewidth=country_width, 
            zorder=2,
            label='Country Boundary'
        )

    if label_tiles and len(tiles_gdf) <= 100:
        _add_tile_labels(ax, tiles_gdf)
    elif label_tiles and len(tiles_gdf) > 100:
        warnings.warn(f"Too many tiles ({len(tiles_gdf)}) to label. Skipping labels.")

    if title is None and show_stats:
        title = _generate_title(tiles_gdf, geohash_dict)
    
    if title:
        ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
    
    ax.set_axis_off()
    plt.tight_layout()
    
    # Save if path provided
    if save_path:
        fig.savefig(save_path, dpi=dpi, bbox_inches='tight')
        logger.info(f"Saved plot to: {save_path}")
    
    return fig, ax


def _plot_adaptive_style(ax, tiles_gdf, cmap, alpha, edge_color, edge_width, show_legend):
    """
    Plot tiles with color-coded levels (adaptive style).

    Parameters
    ----------
    ax : matplotlib.axes.Axes
        Axes to plot on
    tiles_gdf : gpd.GeoDataFrame
        GeoDataFrame with 'level' column
    cmap : str
        Colormap name
    alpha : float
        Transparency level
    edge_color : str
        Edge color for tiles
    edge_width : float
        Edge width for tiles
    show_legend : bool
        Whether to show legend
    """
    unique_levels = sorted(tiles_gdf['level'].unique())

    colors = cm.get_cmap(cmap, len(unique_levels))
    norm = mcolors.BoundaryNorm(
        boundaries=[l - 0.5 for l in unique_levels] + [unique_levels[-1] + 0.5],
        ncolors=len(unique_levels)
    )

    tiles_gdf.plot(
        ax=ax, 
        column='level', 
        cmap=colors, 
        norm=norm,
        edgecolor=edge_color, 
        linewidth=edge_width, 
        alpha=alpha, 
        zorder=1,
        legend=show_legend,
        legend_kwds={
            'label': 'Geohash Level',
            'orientation': 'vertical',
            'shrink': 0.8
        }
    )

def _add_tile_labels(ax, tiles_gdf):
    """
    Add geohash labels to tiles.

    Parameters
    ----------
    ax : matplotlib.axes.Axes
        Axes to plot on
    tiles_gdf : gpd.GeoDataFrame
        GeoDataFrame with geohash geometries
    """
    for _, row in tiles_gdf.iterrows():
        with warnings.catch_warnings():
            warnings.filterwarnings('ignore', category=UserWarning)
            centroid = row.geometry.centroid
        
        ax.text(
            centroid.x, centroid.y, 
            row['geohash'],
            ha='center', 
            va='center', 
            fontsize=7, 
            fontweight='bold',
            zorder=3,
            bbox=dict(
                boxstyle='round,pad=0.3',
                facecolor='white',
                alpha=0.7,
                edgecolor='gray',
                linewidth=0.5
            )
        )


def _generate_title(tiles_gdf, geohash_dict):
    """
    Generate informative title with statistics.

    Parameters
    ----------
    tiles_gdf : gpd.GeoDataFrame
        GeoDataFrame of tiles
    geohash_dict : dict
        Dictionary with level as keys and geohashes as values

    Returns
    -------
    str
        Formatted title string
    """
    total_tiles = len(tiles_gdf)
    
    if 'level' in tiles_gdf.columns:
        levels = tiles_gdf['level'].values
        min_level = int(levels.min())
        max_level = int(levels.max())
        
        if min_level == max_level:
            level_info = f"Level {min_level}"
        else:
            level_info = f"Levels {min_level}–{max_level}"
        
        # Level distribution
        level_dist = " | ".join([
            f"L{level}: {len(tiles)}" 
            for level, tiles in sorted(geohash_dict.items())
        ])
        
        return f"Geohash Coverage: {level_info}\nTotal: {total_tiles:,} tiles ({level_dist})"
    else:
        return f"Geohash Coverage\nTotal: {total_tiles:,} tiles"


def plot_geohash_comparison(
    country_geom: MultiPolygon,
    results_list: list,
    labels: list,
    figsize: Tuple[float, float] = (18, 6),
    save_path: Optional[str] = None
):
    """
    Plot multiple geohash coverage results side-by-side for comparison.
    
    Parameters
    ----------
    country_geom : shapely.geometry
        Country boundary geometry
    results_list : list of tuple
        List of (geohash_dict, tiles_gdf) tuples to compare
    labels : list of str
        Labels for each result (e.g., ['L3', 'L4', 'L5'])
    figsize : tuple
        Figure size
    save_path : str, optional
        Path to save comparison figure

    Returns
    -------
    fig : matplotlib.figure.Figure
    axes : list of matplotlib.axes.Axes
    """
    n_plots = len(results_list)
    fig, axes = plt.subplots(1, n_plots, figsize=figsize)
    
    if n_plots == 1:
        axes = [axes]
    
    for ax, (geohash_dict, tiles_gdf), label in zip(axes, results_list, labels):
        # Create temporary figure for each subplot
        temp_fig, temp_ax = plt.subplots(1, 1)
        
        # Plot on temporary axis
        plot_geohash_coverage(
            country_geom,
            geohash_dict,
            tiles_gdf,
            title=label,
            show_legend=False
        )
        plt.close(temp_fig)
        
        # Recreate on actual subplot
        if tiles_gdf is None:
            all_geohashes = []
            all_levels = []
            for level, tiles in geohash_dict.items():
                all_geohashes.extend(tiles)
                all_levels.extend([level] * len(tiles))
            tiles_gdf = geohashes_to_gdf(all_geohashes)
            tiles_gdf['level'] = all_levels
        
        tiles_gdf.plot(ax=ax, facecolor='lightblue', edgecolor='navy', 
                      linewidth=0.5, alpha=0.6)
        
        country_gdf = gpd.GeoDataFrame({'geometry': [country_geom]}, crs='EPSG:4326')
        country_gdf.plot(ax=ax, facecolor='none', edgecolor='crimson', linewidth=2)
        
        ax.set_title(f"{label}\n{len(tiles_gdf)} tiles", fontsize=12, fontweight='bold')
        ax.set_axis_off()
    
    plt.tight_layout()
    
    if save_path:
        fig.savefig(save_path, dpi=200, bbox_inches='tight')
        logger.info(f"Saved comparison to: {save_path}")
    
    return fig, axes


def plot_level_statistics(
    geohash_dict: dict,
    figsize: Tuple[float, float] = (10, 6),
    save_path: Optional[str] = None,
    style: Literal['bar', 'pie'] = 'bar'
):
    """
    Plot tile distribution statistics across geohash levels.

    Parameters
    ----------
    geohash_dict : dict
        Dictionary with level as keys and list of geohashes as values
    figsize : tuple, default (10, 6)
        Figure size in inches
    save_path : str, optional
        Path to save the figure
    style : {'bar', 'pie'}, default 'bar'
        Plot style - bar chart or pie chart

    Returns
    -------
    fig : matplotlib.figure.Figure
        Figure object
    ax : matplotlib.axes.Axes
        Axes object
    """
    levels = sorted(geohash_dict.keys())
    counts = [len(geohash_dict[level]) for level in levels]
    total = sum(counts) or 1  # avoid division by zero

    fig, ax = plt.subplots(1, 1, figsize=figsize)

    # Colormap and colors for consistency with map visuals
    cmap = cm.get_cmap('viridis', len(levels))
    colors = [cmap(i) for i in range(len(levels))]

    labels = [f'Level {l}' for l in levels]
    pct = [(count / total) * 100 for count in counts]

    if style == 'bar':
        bars = ax.bar(levels, counts, color=colors, alpha=0.8, edgecolor='navy')
        ax.set_xlabel('Geohash Level', fontsize=12, fontweight='bold')
        ax.set_ylabel('Number of Tiles', fontsize=12, fontweight='bold')
        ax.set_title(f'Tile Distribution by Level\nTotal: {total:,} tiles',
                     fontsize=14, fontweight='bold')
        ax.grid(axis='y', alpha=0.3, linestyle='--')

        # show counts above bars (but percentages only in legend)
        for bar, count in zip(bars, counts):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                    f'{count:,}',
                    ha='center', va='bottom', fontsize=10, fontweight='bold')

        # Build legend entries with colored squares and percentages
        patches = [
            mpatches.Patch(color=colors[i], label=f'{labels[i]} — {pct[i]:.1f}%')
            for i in range(len(levels))
        ]
        # place legend outside the plot to the right
        ax.legend(handles=patches, title='Levels', bbox_to_anchor=(1.02, 1), loc='upper left', borderaxespad=0.)

    else:  # pie chart
        # no labels/autopct on the slices — legend will contain level + %
        wedges, _ = ax.pie(
            counts,
            labels=None,
            colors=colors,
            startangle=90,
            wedgeprops=dict(edgecolor='white')
        )

        ax.set_title(f'Tile Distribution by Level\nTotal: {total:,} tiles',
                     fontsize=14, fontweight='bold')

        # Legend with color square, level and percent (and optional count)
        patches = [
            mpatches.Patch(color=colors[i],
                           label=f'{labels[i]} — {pct[i]:.1f}% ({counts[i]:,})')
            for i in range(len(levels))
        ]
        ax.legend(handles=patches, title='Levels', bbox_to_anchor=(1.02, 0.5), loc='center left', borderaxespad=0.)

    plt.tight_layout()

    if save_path:
        fig.savefig(save_path, dpi=200, bbox_inches='tight')
        logger.info(f"Saved statistics to: {save_path}")

    return fig, ax


def quick_plot(country_geom: MultiPolygon,
               geohash_dict: dict[str, list[str]],
               tiles_gdf: GeoDataFrame=None):
    """
    Quick plot with sensible defaults.

    Parameters
    ----------
    country_geom : shapely.geometry
        Country boundary geometry
    geohash_dict : dict
        Dictionary with level as keys and list of geohashes as values
    tiles_gdf : gpd.GeoDataFrame, optional
        Optional GeoDataFrame with 'level' column

    Returns
    -------
    fig : matplotlib.figure.Figure
        Figure object
    ax : matplotlib.axes.Axes
        Axes object
    """
    fig, ax = plot_geohash_coverage(country_geom, geohash_dict, tiles_gdf)
    plt.show()
    return fig, ax


if __name__ == '__main__':
    # Load country
    country_gdf = download_gadm_country("BEL", cache_dir='./gadm_cache')
    country_geom = build_single_multipolygon(country_gdf)
    
    # Test adaptive coverage
    geohash_dict, tiles_gdf = adaptive_geohash_coverage(country_geom, 2, 8)

    logger.info(f"Generated coverage: {geohash_dict}")
    # Plot with different styles
    fig1, ax1 = plot_geohash_coverage(
        country_geom, geohash_dict, tiles_gdf,
        style='adaptive',
        save_path='adaptive_coverage.png'
    )
    
    fig2, ax2 = plot_level_statistics(
        geohash_dict,
        style='pie',
        save_path='level_stats.png'
    )
    
    plt.show()
