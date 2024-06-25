include { preprocess } from './module/preprocess.nf'
include { higher_level } from './module/higher_level.nf'
include { machine_learning } from './module/machine_learning.nf'
include { reports } from './module/reports.nf'

workflow {
    // downloading, unpacking, stacking, masking, cubing
    cube_channel = preprocess(params.data_range, params.raw_directory, params.cube_directory)

    // create spectral temporal metrics; since we only look at yearly aggregates, no additional config is needed here
    higher_level(cube_channel, params.vegetation_indices)

    // circle detection, accuaracy assessment
    machine_learning()

    // generate maps, potentially final report...
    reports()
}