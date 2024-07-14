process DETECT_CIRCLES {
    input:
    tuple val(tileId), val(year), path(stm)

    output:
    tuple val(tileId), val(year), path(stm), path("${tileId}_${year}_circles.json")

    script:
    """
    detectcircle --input $stm --output ${tileId}_${year}_circles.json
    """
}

process TRANSFORM_COORDINATES {
    input:
    tuple val(tileId), val(year), path(stm), path(circles)

    output:
    tuple val(tileId), val(year), path("${tileId}_${year}_circles.gpkg")
    script:
    """
    GEOTRANSFORM=\$(gdalinfo $stm -json | jq '.geoTransform[]')
    OFFSET=\$(echo \$GEOTRANSFORM | cut -d ' ' -f 1,4)     # first X, second Y
    PIXELSIZE=\$(echo \$GEOTRANSFORM | cut -d ' ' -f 2,6)  # first X, second Y

    transformcoordinates --input-file $circles --output-file "${tileId}_${year}_circles.gpkg" \
        --origins \$OFFSET --pixel-sizes \$PIXELSIZE --crs '${params.cube_projection}'
    """
}

process MERGE_CIRCLES {
    publishDir "${params.cropland_directory}", mode: 'copy', pattern: "${year}_circles.gpkg", enabled: params.store_cropland
    label 'gdal'

    input:
    tuple val(tileId), val(year), path(circles)

    output:
    tuple val(year), path("${year}_circles.gpkg")

    script:
    """
    ogrmerge.py -o ${year}_circles.gpkg $circles -single -nln $year -src_layer_field_name tile
    """
}

process ACCURACY_ASSESSMENT {
    publishDir "${params.cropland_directory}", mode: 'copy', enabled: params.store_cropland

    input:
    tuple val(year), path(prediction), path(validation_data)

    output:
    tuple path("accuracy_summary_${year}.csv"), path("${year}_accuracy_assessment.gpkg")

    when:
    validation_data.exists()

    script:
    """
    accuracy_assessment --predicted-file $prediction --validation-file $validation_data \
        --validation-layer validation_data_${year} \
        --output-file accuracy_summary_${year}.csv \
        --tp-output-file ${year}_accuracy_assessment.gpkg 
    """
}


workflow cropland_detection {
    take:
    stm_chips
    validation_db

    main:
    DETECT_CIRCLES(stm_chips)
        | TRANSFORM_COORDINATES
        | groupTuple(by: 1)  // group by year
        | MERGE_CIRCLES
        | combine( Channel.fromPath(validation_db) )
        | ACCURACY_ASSESSMENT

    emit:
    detected_acres = MERGE_CIRCLES.out
    accuaracy_acres = ACCURACY_ASSESSMENT.out
}
