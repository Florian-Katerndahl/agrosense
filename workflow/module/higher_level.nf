process NDVI {
    // this can be implemented dynamically to allow for arbitrary spectral indices, see geoflow for a how-to
    label 'gdal'

    input:
    tuple val(tileId), val(platform), val(wrs), val(date), val(year), path(scene)
    
    output:
    tuple val(tileId), val(platform), val(wrs), val(date), val(year), path("${platform}_${wrs}_${date}_NDVI.tif")
    
    script:
    """
    gdal_calc.py --quiet -A $scene --A_band 5 -B $scene --B_band 4 --calc='(A - B)/(A + B)' \
        --type Float32 --outfile=${platform}_${wrs}_${date}_NDVI.tif \
        --creation-option 'COMPRESS=DEFLATE' --creation-option 'PREDICTOR=3'
    """
}

process STM {
    // TODO make this a parameter as well
    publishDir "/home/eouser/git-repos/agrosense/ndvi/${year}/tifs", mode: 'copy', overwrite: true
    label 'gdal'

    input:
    tuple val(tileId), val(platform), val(wrs), val(date), val(year), path(ndvis)

    output:
    tuple val(tileId), val(year), path("${tileId}_${year}_max_NDVI.tif")

    script:
    // Groovy can be mixed in; values created here can also be used in the output directive above
    // WARN value range hard coded for NDVI
    if (!(ndvis instanceof List)) {
    """
    gdal_calc.py -A ${ndvis[0]} \
        --calc='numpy.where((A >= -1) & (A <= 1), A, -2)' \
        --hideNoData --NoDataValue=-2 --outfile ${tileId}_${year}_max_NDVI.tif

    """
    } else {
    """
    gdal_calc.py -A ${ndvis.join(' ')} \
        --calc='numpy.max(numpy.where((A >= -1) & (A <= 1), A, -2), axis=0)' \
        --hideNoData --NoDataValue=-2 \
        --outfile=${tileId}_${year}_max_NDVI.tif \
        --creation-option 'COMPRESS=DEFLATE' --creation-option 'PREDICTOR=3'
    """
    }    
}

process VRT {
    // TODO make this a parameter as well
    // meh, not the nicest file structure, but whatever
    publishDir "/home/eouser/git-repos/agrosense/ndvi/${year}", mode: 'copy', overwrite: true
    label 'gdal'

    input:
    tuple val(tileId), val(year), path(ndvis)

    output:
    tuple val(year), path("output.vrt")

    script:
    // WARN has dependency on STM for file structure
    """
    mkdir tifs
    mv ${ndvis.join(' ')} tifs
    gdalbuildvrt output.vrt tifs/*.tif
    """

}

workflow higher_level {
    take:
    preprocessed_images
    
    main:
    aggregated_ndvi = preprocessed_images
        | NDVI
        | groupTuple(by: [0, 4]) // if no group size is given, calls to groupTuple are blocking
        | STM
        | groupTuple(by: 1)
        | VRT 

    emit:
    aggregated_ndvi
}
