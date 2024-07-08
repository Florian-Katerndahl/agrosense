include { preprocess } from './module/preprocess.nf'
include { higher_level } from './module/higher_level.nf'
include { cropland_detection } from './module/cropland_detection.nf'

/* An unnamed workflow is the main entry point by default for Nextflow workflows.
 * Named workflows, like the ones below, are subworkflows similar to how they exist in Snakemake
 * Comments reagarding Nextflow are added mainly in the preprocess workflow
*/
workflow {
    cube_channel = preprocess()

    // create spectral temporal metrics; since we only look at yearly aggregates, no additional config is needed here
    higher_level(cube_channel)

    // circle detection, accuaracy assessment
    cropland_detection(higher_level.out.stm_chips, params.validation_data)
}

