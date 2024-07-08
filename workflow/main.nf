include { preprocess } from './module/preprocess.nf'
include { higher_level } from './module/higher_level.nf'

/* An unnamed workflow is the main entry point by default for Nextflow workflows.
 * Named workflows, like the ones below, are subworkflows similar to how they exist in Snakemake
 * Comments reagarding Nextflow are added mainly in the preprocess workflow
*/
workflow {
    cube_channel = preprocess()

    // create spectral temporal metrics; since we only look at yearly aggregates, no additional config is needed here
    // also contains cropland detection related things
    higher_level(cube_channel)
}
