include { preprocess } from './module/preprocess.nf'
// include { higher_level } from './module/higher_level.nf'
// include { machine_learning } from './module/machine_learning.nf'
// include { reports } from './module/reports.nf'

workflow {
    cube_channel = preprocess()

    // create spectral temporal metrics; since we only look at yearly aggregates, no additional config is needed here
    // higher_level(cube_channel, params.vegetation_indices)

    // circle detection, accuaracy assessment
    // machine_learning()    
}