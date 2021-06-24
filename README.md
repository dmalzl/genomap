# genomap
An easy to use tool to generate heatmap like tracks for the UCSC Genome Browser

## Generating a bigWig file from your BAMs
The easiest way to generate a bigWig file from your alignments is to use the [deepTools](https://deeptools.readthedocs.io/en/develop/index.html) suites [`bamCoverage`](https://deeptools.readthedocs.io/en/develop/content/tools/bamCoverage.html)
```bash
bamCoverage -b <inputBAM> \
            -o <outputFileName> \
            -of bigwig \
            -bs 5000 \
            -p 16 \
            --ignoreDuplicates \
            --normalizeUsing CPM \
            --exactScaling
```
This will generate a coverage track with a 5kb tiling normalized to counts per million over the genome from your input BAM file.

## Converting bigWig file to bedGraph with UCSC suitable RGB column
Now that we have our bigWig file, the next step is to generate a UCSC compatible bedGraph with an itemRGB column. This is done using the `genomap.py` script and is invoked as follows:
```bash
./genomap.py -i <bigwigFile> \
           -bs 5000 \
           --vmin 0 \
           --vmax p75 \
           --colormap coolwarm \
           -o <outputBedGraph>
```
This will turn the bigwig into a bedGraph containing 9 columns including the itemRGB column which encodes the bigWig values as RGB colors for the UCSC genome browser.

## Converting bedGraph to bigBed
The last step is to convert the bedGraph to it's binary twin the bigBed. This is done using the [UCSC kentUtils](https://github.com/ENCODE-DCC/kentUtils) suite. Note that you need
```bash
cat <bedGraphFile> | sort -k1,1 -k2,2n > <sortedBedGraph>
bedToBigBed <sortedBedGraph> chrom.sizes <outputBigBed>
```
The chrom.sizes file is a generic tab-separated file containing two columns describing the name and the size of the chromosomes contained in the bedGraph file.

## Add to TrackHub on UCSC
The last step is to add the generated bigBed to you UCSC TrackHub using the following directives
```
track <trackName>
shortLabel      <trackShortLabel>
longLabel       <trackLongLabel>
bigDataUrl      <path/to/bigBed>
itemRgb         on
type    bigBed 9 .
```

# General comment on usage
The UCSC Genome Browser is an online tool to display sequencing an other related data. The versatility also brings some caveats such as a requirement for restriction of colorspace in cases of the itemRGB column of bigBed files as well as the number of regions that can simultaneously be displayed, which seems to be restricted to 1000 regions. Thus, a general point for consideration is the size of the regions one wants to view on the browser, since the heatmap will turn black for regions that span more than 1000 bigBed bins. An example would be as follows:

Consider viewing a 10Mb region on would need at least a binsize of 10,000,000 / 1,000 = 10,000 in order to be able to enjoy the colored version of the bigBed.
