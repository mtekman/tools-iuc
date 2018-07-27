#!/usr/bin/env R
VERSION = "0.1"

args = commandArgs(trailingOnly = T)
#args=c('/tmp/tmp7xvC2l/job_working_directory/000/2/tmpEWGYM8')
source(args[1])

require(methods)
suppressPackageStartupMessages(
    source(file.path(scripts.dir,"RaceID3_StemID2_class.R"))
)

options(repr.plot.height = 5)

suppressPackageStartupMessages(library(scater))
suppressPackageStartupMessages(require(biomaRt))


## TSV to SCSeq
#input_matrix <- read.table(
#    count.matrix,
#    stringsAsFaactors = F,
#    na.strings=c("NA", "-", "?", "."),
#    header=TRUE,
#    row.names=1
#)
#input_matrix[is.na(input_matrix)] <- 0
#sc <- SCseq(data.frame(input_matrix))
sc <- readRDS(count.matrix)
sc <- SCseq(sc)

## Filtering
new_sc <- filterdata(
    sc,
    mintotal = c.mintotal,
    minexpr  = c.minexpr,
    maxexpr  = c.maxexpr,
    downsample = c.downsample,
    sfn = c.sfn,
    hkn = c.hkn,
    dsn = c.dsn,
    rseed = c.rseed,
    CGenes = c.cgenes,
    FGenes = c.fgenes
)

## Annotation
mart <- useMart(
    biomart = "ENSEMBL_MART_ENSEMBL",
    dataset = ca.dataset
)

k <- getBM(
##    filters = "ensembl_gene_id",
    filters = "external_gene_name",
    attributes = c(
        "ensembl_gene_id",
        "external_gene_name",
        "name_1006"
    ),
    values = rownames(new_sc@fdata),
    mart = mart
)

## Not RaceID3
##sce <- SingleCellExperiment(assays=list(counts = as.matrix(new_sc@fdata)))
##sce <- calculateQCMetrics(sce) 
##hist(sce$total_counts, breaks = 50, main = "Library Size")
##print(plotQC(sce, type = "high"))

if (c.docc){
    vset <- c()
    if (c.docc.custom){
        vset <- c(c.docc.custom.cgenes, c.docc.custom.sgenes)
    }
    else {
        ccg <- unique(k[k$name_1006 == "cell cycle",]$ensembl_gene_id)
        cpg <- unique(k[k$name_1006 == "cell proliferation",]$ensembl_gene_id)
        vset <- unique(c(ccg,cpg))
        message("Number of cell-cycle and cell-proliferation to correct against: ", length(vset))
    }

    x <- CCcorrect(new_sc@fdata,
                   vset=vset,
                   CGenes=NULL, ccor=.4, nComp=NULL, pvalue=.05, quant=.01, mode="pca" )

    new_sc@fdata <- x$xcor
}

if (c.dobatchregression){
    batch_vars <- data.frame(
        row.names = names(new_sc@fdata),
        batch = sub(c.dobatchregression.regexcapture, "\\1", names(new_sc@fdata))
    )
    new_sc@fdata <- varRegression(new_sc@fdata, batch_vars)
}

                                        # K means
zzz <- capture.output(
    new_sc <- clustexp(
        new_sc,
        clustnr = ck.clustnr,
        bootnr = ck.bootnr,
        metric = ck.metric,
        do.gap = ck.dogap,
        sat = TRUE,
        SE.method = ck.semethod,
        SE.factor = ck.sefactor,
        B.gap = ck.bgap,
        cln = ck.cln,
        rseed = ck.rseed,
        FUNcluster = ck.funcluster,
        FSelect = TRUE
    )
)


##rbind(new_sc@clusterpar)
pdf(out.pdf.clusterqc)
par(mfrow=c(2,2), mar=c(4,4,3,3), cex.main = 0.00001, cex=0.9, cex.lab = 0.9)
plotsaturation(new_sc,disp=F)
if (ck.dogap) plotgap(new_sc)
plotjaccard(new_sc)
plotsilhouette(new_sc)
dev.off()

new_sc <- comptsne(
    new_sc,
    rseed = ct.rseed,
    sammonmap = ct.sammonmap,
    fast = ct.fast,
    perplexity = ct.perplexity,
    
    )
## fast = T, use saturation plots as a better guide -- and pick the ones with high values still
## jaccard to see if it makes sense.

new_sc <- findoutliers(
    new_sc,
    outminc = co.outminc,
    outlg = co.outlg,
    probthr = co.probthr,
    outdistquant = co.outdistquant
)

if (co.dorandforest){
    new_sc <- rfcorrect(new_sc)
}

## Computed here, but requires findoutliers to run first, which is why we
## we cannot simply pack this into another tool by itself. At the same time
## The genes fed to analyse these require prior knowledge, so it must be given
## in a seperate tool.
cdiff <- clustdiffgenes(new_sc, pvalue = .01)

pdf(out.pdf.heatmaps)
x <- clustheatmap(new_sc, final=F, hmethod= cm.hmethod)
mtext("Heatmap - Initial Clustering", side=3, outer=F, line=1, col="black")
x <- clustheatmap(new_sc, final=T, hmethod= cm.hmethod)
mtext("Heatmap - Final Clustering", side=3, outer=F, line=1, col="black")
dev.off()

pdf(out.pdf.tsnes)
plottsne(new_sc, final=F)
mtext("tSNE - Initial Clustering", side=3, outer=F, line=1, col="black")
plottsne(new_sc, final=T)
mtext("tSNE - Final Clustering", side=3, outer=F, line=1, col="black")
dev.off()

## return new_sc as the object for:
## --> cdiffgenes tool
## --> plotexptsne tool
## attributes(new_sc)$sce_obj <- sce
attributes(new_sc)$kmart <- k
attributes(new_sc)$cdiffer <- cdiff

saveRDS(new_sc, out.rds)

