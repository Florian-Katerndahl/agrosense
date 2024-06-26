process DOWNLOAD {
    input:
    tuple path(aoi), val(start_date), val(end_date)
    
    output:
    
    script:
    """
    
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
    ls $stack_dir
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

workflow preprocess {
    take:
    // aoi
    // begin
    // end
    
    main:
    cube_channel = CUBE_INIT(params.cube_origin, params.cube_projection)

    // transformed_channel = Channel.of([aoi, begin, end])
    //     | DOWNLOAD
    transformed_channel = Channel.fromPath("/home/florian/git-repos/agrosense/resources/landsat/*.tar")
        | flatten
        | UNPACK
        | STACK
        | TRANSFORM
    
    preprocessed_channel = transformed_channel
        | combine(cube_channel)
        | CUBE
        | flatten
        // put into funtion? is tile id, platform, wrs, date, year, file
        | map{ it -> [it[-2].toString(),
                      it[-1].toString().tokenize('.')[0].tokenize('_')[0],
                      it[-1].toString().tokenize('.')[0].tokenize('_')[1],
                      it[-1].toString().tokenize('.')[0].tokenize('_')[2],
                      it[-1].toString().tokenize('.')[0].tokenize('_')[2][0..3],
                      it]}
        // | collect(flat: false)
    
    emit:
    preprocessed_channel
}