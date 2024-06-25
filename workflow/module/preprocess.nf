process DOWNLOAD {
    input:
    tuple path(aoi), val(start_date), val(end_date), val(sensors)
    
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
    mkdir ${scene_identifier}
    tar -xf {input} -C {scene_identifier}
    rm {scene_identifier}/*_ST*
    rm {scene_identifier}/*.txt
    """
}

process STACK {
    input:
    
    output:
    
    script:
    """
    mkdir {output}
    gdal_merge.py -q -separate -o {wildcards.scene}.tif {input}/*SR_B*.TIF
    mv {wildcards.scene}.tif {output}
    cp {input}/*_QA*.TIF {input}/*.xml {output}
    """
}

process TRANSFORM {
    publishDir "${params.raw_directory}/${scene_identifier}", mode: 'symlink', overwrite: true, enabled: params.store_raw, pattern: "${scene_identifier}.tif"
    input:
    tuple val(scene_identifier), path(raw_dir)
    
    output:
    tuple val(scene_identifier), path("${scene_identifier}.tif")
    
    script:
    // TODO PLATFORM in groovy, not bash? Though, I don't need this information outside of the script body...
    """
    PLATFORM=$(basename {input}/{wildcards.scene}.tif | cut -d '_' -f1)
    if [[ "\$PLATFORM" == 'LC09' || "\$PLATFORM" == 'LC08' ]];
    then
        SENSOR=OLI
    else
        SENSOR=TM
    fi
    preprocess --platform \$SENSOR -o ${scene_identifier}.tif ${scene_identifier}.tif $raw_dir
    """
}

process CUBE_INIT {
    // usually, this is not good practice to modify the input of a process, let's see...
    input:
    tuple path(cube), val(cube_origin), val(cube_projections)
    output:
    path(cube, type: 'dir')
    script:
    """
    mkdir -p cube
    force-cube-init -d ${cube} -o ${cube_origin.join(',')} ${cube_projections}
    """
}
// TODO check what David in Rangeland

process CUBE {
    publishDir params.cube_directory, mode: 'copy', overwrite: true, enabled: params.store_cube

    input:
    tuple path(raw), path(cube)
    
    output:
    // usually, this is not good practice to modify the input of a process, let's see...
    path(cube, type: 'dir')
    
    script:
    // TODO ahh, what were the string interpolation rules for nextflow again?
        // TODO Couldn't I have simply multiple CUBEs, one for each year which all depend on a process called CUBE_INIT (creating the datacube.prj). Actually, if I have a process for initializing the cube directory, I wouldn't need any aggregation and could simply cube each scene indepently
    // TODO we need a tile-allow list, if we're using a bounding box to disregard unneeded data
    """
    force-cube -s ${paras.cube_resolution} ${raw} -o ${cube} -j {params.force_threads} -t ${params.cube_dtype}
    """
}

workflow preprocess {
    take:
    
    main:
    preprocess_channel = Channel.from_...()
        | DOWNLOAD
        | flatten
        | UNPACK
        | STACK
        | TRANSFORM
        | collect
        | CUBE
    
    emit:
    
}