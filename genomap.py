#!/usr/bin/env python3

import os
import pandas as pd
import pyBigWig as pbw
import numpy as np
import argparse as ap
import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib.colors import BoundaryNorm, Normalize, LinearSegmentedColormap
from matplotlib.cm import ScalarMappable
    

def get_cbar_outfile(cbarfile, outputfile):
    if not cbarfile:
        basedir = os.path.dirname(outputfile)
        cbarfile = os.path.join(
            basedir,
            'colorbar.pdf'
        )
    
    return cbarfile


def get_colormap(cmapstring):
    if len(cmapstring.split(',')) > 1:
        colors = cmapstring.split(',')
        cmap = LinearSegmentedColormap.from_list(
            'custom_cmap',
            colors,
            256
        )
    
    else:
        cmap = plt.get_cmap(cmapstring)
    
    return cmap


def bw_to_df(bwfile, binsize):
    bw = pbw.open(bwfile)
    df = pd.DataFrame(
        columns = ['chrom', 'start', 'end', 'counts']
    )
    for chrom in bw.chroms().keys():
        intervals = []
        for start, end, value in bw.intervals(chrom):
            if (end - start) > binsize:
                intervals.extend(
                    [(chrom, pos, pos + binsize, value)
                    if pos + binsize <= end
                    else (chrom, pos, end, value)
                    for pos in range(start, end, binsize)]
                )
            
            else:
                intervals.append((chrom, start, end, value))
            
        chrom_df = pd.DataFrame(
            intervals,
            columns = ['chrom', 'start', 'end', 'counts']
        )
        df = pd.concat(
            [df, chrom_df]
        )
    bw.close()
    return df


def get_vminmax(values, vminarg, vmaxarg):
    bounds = []
    for arg in [vminarg, vmaxarg]:
        if arg.startswith('p'):
            bounds.append(
                np.nanpercentile(values, float(arg[1:]))
            )
        else:
            bounds.append(float(arg[1:]))
    
    return bounds
    
    
parser = ap.ArgumentParser(
    description = 'genomap is an easy to use script to transform you BigWig files into'
    'bedGraphs files with RGB encoded colors for use as heatmap in the UCSC Genome Brower'
)
parser.add_argument(
    '-i',
    '--input',
    required = True,
    help = 'BigWig file to convert to bedGraph. Has to be generated with equal sized bins'
)
parser.add_argument(
    '-bs',
    '--binsize',
    required = True,
    type = int,
    help = 'size of the bins used to generate the BigWig file'
)
parser.add_argument(
    '--vmin',
    default = 'p5',
    help = 'Minimum value to use for the colormap. If prepended by a "p" the value will be interpreted as percentile (has to be in range 0-100)'
)
parser.add_argument(
    '--vmax',
    default = 'p75',
    help = 'Maximum value to use for the colormap. If prepended by a "p" the value will be interpreted as percentile (has to be in range 0-100)'
)
parser.add_argument(
    '--colormap',
    default = 'coolwarm',
    help = 'Either a named matplotlib colormap or a sequence of comma-separated colors to use as colormap'
)
parser.add_argument(
    '-co',
    '--colorbarFile',
    default = None,
    help = 'name of the file to where the colorbar should be saved. If not given will be saved as colorbar.pdf in the basedir of the output file'
)
parser.add_argument(
    '-o',
    '--outputFile',
    required = True
)
args = parser.parse_args()

cmap = get_colormap(args.colormap)
df = bw_to_df(
    args.input,
    args.binsize
)
counts = df.loc[:, 'counts'].copy()
counts[counts == 0] = np.nan
vmin, vmax = get_vminmax(
    counts,
    args.vmin,
    args.vmax
)
bounds = BoundaryNorm(
    np.linspace(vmin, vmax, 10), 
    9, 
    clip = True
)
norm = Normalize(0, 8)
df['rgb'] = df['counts'].apply(
    lambda x: ','.join(
        str(int(round(i*255))) for i in cmap(norm(bounds(x)))[:-1]
    )
)
df[['score', 'name', 'strand']] = [0, '.', '.']
df[['thickStart', 'thickEnd']] = df[['start', 'end']]
columns = ['chrom', 'start', 'end', 'name', 'score', 'strand', 'thickStart', 'thickEnd', 'rgb']
df[columns].to_csv(
    args.outputFile, 
    sep = '\t',
    header = False,
    index = False
)

cbarfile = get_cbar_outfile(
    args.colorbarFile,
    args.outputFile
)
fig = plt.figure()
ax = fig.add_axes([0.5, 0.1, 0.04, 0.8])
cb = mpl.colorbar.ColorbarBase(
    ax,
    cmap = cmap,
    boundaries = bounds.boundaries
)
fig.set_figheight(5)
fig.set_figwidth(5)
fig.savefig(cbarfile)
