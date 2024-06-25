process VEGETATION_INDEX {
    input:
    output:
    script:
    """
    gdal_calc.py --quiet -A {input} --A_band 5 -B {input} --B_band 4 --calc='(A - B)/(A + B)' \
        --type Float32 --outfile={output} --creation-option 'COMPRESS=DEFLATE' --creation-option 'PREDICTOR=3'
    """
}

process STM {
    input:
    output:
    script:
    """
    gdal_calc.py -A {input}/*_NDVI.tif --outfile={output} --calc='max(A, axis=0)' --creation-option 'COMPRESS=DEFLATE' --creation-option 'PREDICTOR=3'
    """
}

workflow higher_level {
    take:
    main:
    emit:
}
