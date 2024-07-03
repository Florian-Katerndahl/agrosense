process DETECT_CIRCLES {
}

process TRANSFORM_COORDINATES {
}

process ACCURACY_ASSESSMENT{
    input:
    tuple ..., path(validation_data)

    output:

    when:
    validation_data.exists()

    script:
    """
    """
}

workflow cropland_detection {
    take:
    stm_chips
    validation_db

    main:

    emit:

}

