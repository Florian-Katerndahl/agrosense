process DOWNLOAD {
    secret 'USGS_USERNAME'
    secret 'USGS_PASSWORD'
    
    output:
    path("*.tar")
    
    script:
    """
    downloadlandsat --username \$USGS_USERNAME -- password \$USGS_PASSWORD \
        --coordinates ${params.coordinates.join(' ')} --start-date ${params.date_range["start"]} \
        --end-date ${params.date_range["end"]} --max-results ${params.max_results} \
        --max-cloud-cover ${params.max_cloud_cover} --output-dir .
    """
}

process UNPACK {
    input:
    path(tar)
    
    output:
    tuple val(scene_identifier), path(scene_identifier, type: 'dir')
    
    script:
    scene_identifier = tar[-1].toString().tokenize('.')[0]
    """
    mkdir $scene_identifier
    tar -xf $tar -C $scene_identifier
    rm $scene_identifier/*_ST*
    rm $scene_identifier/*.txt
    """
}

process STACK {
    label 'largeMemory'
    label 'gdal'

    input:
    tuple val(scene_identifier), path(unpacked)
    
    output:
    tuple val(scene_identifier), path('stack')
    
    script:
    """
    mkdir stack
    gdal_merge.py -q -separate -o ${scene_identifier}_stacked.tif $unpacked/*SR_B*.TIF
    mv ${scene_identifier}_stacked.tif stack
    cp $unpacked/*_QA*.TIF $unpacked/*.xml stack
    """
}

process TRANSFORM {
    // publishDir "${params.raw_directory}/${scene_identifier}", mode: 'symlink', overwrite: true, enabled: params.store_raw, pattern: "${scene_identifier}.tif"
    label 'largeMemory'
    input:
    tuple val(scene_identifier), path(stack_dir)
    
    output:
    tuple val(scene_identifier), path("${scene_identifier}.tif")
    
    script:
    """
    PLATFORM=\$(basename $stack_dir/${scene_identifier}_stacked.tif | cut -d '_' -f1)
    if [[ "\$PLATFORM" == 'LC09' || "\$PLATFORM" == 'LC08' ]];
    then
        SENSOR=OLI
    else
        SENSOR=TM
    fi
    preprocess --platform \$SENSOR -o ${scene_identifier}.tif ${scene_identifier}_stacked.tif $stack_dir
    """
}

process CUBE_INIT {
    publishDir params.cube_directory, mode: 'copy', overwrite: true, enabled: params.store_cube
    label 'force'

    input:
    val(cube_origin)
    val(cube_projection)
    
    output:
    path('datacube-definition.prj')
    
    script:
    """
    force-cube-init -d . -o ${cube_origin.join(',')} '${cube_projection}'
    """
}


/* This process takes as input a single channel, each entry comprising of a tuple with three entries
 * The process outputs files according to the specified glob pattern.
 * The script body is executed inside the docker image (or locally, when container support is turned off)
 * or the underlying execution environment requires images (e.g. K8s), similar to Snakemake, any file content
 * that starts with a Shebang could also be supplied; bash is simply assumed by default.
 * The process output usually never leaves a working directory whih is assumed to be non-persistent in the
 * sense that it can be deleted at any point. It's used for caching processing steps. Using the publishDir
 * directive, outputs are saved to a pre-defined folder outside of the working directory.
*/
process CUBE {
    publishDir params.cube_directory, mode: 'copy', overwrite: true, enabled: params.store_cube
    label 'force'

    input:
    tuple val(scene_identifier), path(stacked), path(projection)
    
    output:
    path('**/*.tif', includeInputs: false)
    
    script:
    // TODO we need a tile-allow list, if we're using a bounding box to disregard unneeded data?
    """
    force-cube -s ${params.cube_resolution} -o . -j ${params.force_threads} -t ${params.cube_dtype} $stacked
    rename -e 's/(LC0[89])_L2SP_(\\d{6})_(\\d{8})_.*/\$1_\$2_\$3.tif/' **/*.tif
    """
}


/* A subworkflow can take arguments (values, channels, etc.); the actual work is done in the
 * main section and any output of a subworkflow is defined in the emit section
*/
workflow preprocess {
    take:
    
    main:
    // call a process with the expected number of inputs; a process always outputs a channel
    cube_channel = CUBE_INIT(params.cube_origin, params.cube_projection)

    // | is the pipe oprator and offers (I'd say) a readable way of connecting processes with channels
    //transformed_channel = DOWNLOAD 
    //     | DOWNLOAD
    transformed_channel = Channel.fromPath("${params.output_directory}/resources/landsat/*.tar")
        | flatten
        | UNPACK
        | STACK
        | TRANSFORM
    /* combine, flatten and map are channel operators. that is, they do not do any computational work
     * but are used to transform either all channel elements at once (combine, flatten) or
     * individually (map).
     * In case of the map operator, an additional closure is passed
    */
    preprocessed_channel = transformed_channel
        | combine(cube_channel)
        | CUBE
        | flatten
        // tile id, platform, wrs, date, year, file
        | map{ it -> [it[-2].toString(),
                      it[-1].toString().tokenize('.')[0].tokenize('_')[0],
                      it[-1].toString().tokenize('.')[0].tokenize('_')[1],
                      it[-1].toString().tokenize('.')[0].tokenize('_')[2],
                      it[-1].toString().tokenize('.')[0].tokenize('_')[2][0..3],
                      it]}
    
    emit:
    preprocessed_channel
}
