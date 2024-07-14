# Center-Pivot Irrigation Analysis

## Project Overview

This project focuses on analyzing the development of center-pivot irrigation in Saudi Arabia using satellite imagery provided by the USGS. Center-pivot irrigation is a method where equipment rotates around a pivot point, watering crops with sprinklers. This is particularly beneficial in dryland areas, where water conservation and efficient irrigation are crucial. By analyzing the circular patterns created by center-pivot irrigation from satellite images, we can detect each irrigation field, providing information about its size at specific points in time and its development over the years.

## Getting Started

To get started with this project on GitLab, follow these steps:

### Add Your Files

- [ ] [Create](https://docs.gitlab.com/ee/user/project/repository/web_editor.html#create-a-file) or [upload](https://docs.gitlab.com/ee/user/project/repository/web_editor.html#upload-a-file) files.
- [ ] [Add files using the command line](https://docs.gitlab.com/ee/gitlab-basics/add-file.html#add-a-file-using-the-command-line) or push an existing Git repository with the following command:

```
cd existing_repo
git remote add origin https://gitup.uni-potsdam.de/ettenhofer/group_project_2.git
git branch -M main
git push -uf origin main
```

### Integrate with Your Tools

- [ ] [Set up project integrations](https://gitup.uni-potsdam.de/ettenhofer/group_project_2/-/settings/integrations)

### Collaborate with Your Team

- [ ] [Invite team members and collaborators](https://docs.gitlab.com/ee/user/project/members/)
- [ ] [Create a new merge request](https://docs.gitlab.com/ee/user/project/merge_requests/creating_merge_requests.html)
- [ ] [Automatically close issues from merge requests](https://docs.gitlab.com/ee/user/project/issues/managing_issues.html#closing-issues-automatically)
- [ ] [Enable merge request approvals](https://docs.gitlab.com/ee/user/project/merge_requests/approvals/)
- [ ] [Set auto-merge](https://docs.gitlab.com/ee/user/project/merge_requests/merge_when_pipeline_succeeds.html)

### Test and Deploy

Use the built-in continuous integration in GitLab.

- [ ] [Get started with GitLab CI/CD](https://docs.gitlab.com/ee/ci/quick_start/index.html)
- [ ] [Analyze your code for known vulnerabilities with Static Application Security Testing (SAST)](https://docs.gitlab.com/ee/user/application_security/sast/)
- [ ] [Deploy to Kubernetes, Amazon EC2, or Amazon ECS using Auto Deploy](https://docs.gitlab.com/ee/topics/autodevops/requirements.html)
- [ ] [Use pull-based deployments for improved Kubernetes management](https://docs.gitlab.com/ee/user/clusters/agent/)
- [ ] [Set up protected environments](https://docs.gitlab.com/ee/ci/environments/protected_environments.html)

## Project Components and Workflow

# Workflow Matched with Requirements File

## 1. Query USGS for raw Landsat data
**Requirements file:** Query USGS Landsat-Data
- **Details:** Query metadata (Cloud cover, time, location, sensor, processing level)

## 2. Unpack data
**Requirements file:** Not explicitly mentioned, but implied as a part of data handling.

## 3. Generate multi-band image
**Requirements file:** Generate multi-band images
- **Details:** Landsat scenes with metadata files, Multi-band images with metadata items set (Custom CLI Tool)

## 4. Mask according to quality band
**Requirements file:** Mask multi-band images, apply gain + offset
- **Details:** Masked and scaled multiband scenes

## 5. Generate datacube
**Requirements file:** Generate datacube
- **Details:** All images, Multi-band images with metadata items set + QAI-files, Gridded satellite scenes

## 6. Calculate spectral index (NDVI)
**Requirements file:** Timeseries processing + VI-calculation
- **Details:** Temporal aggregation of VI (Custom CLI Tool)

## 7. Aggregate NDVI on yearly basis
**Requirements file:** Implicit in Timeseries processing + VI-calculation

## 8. Circle (farmland) detection
**Requirements file:** Circle / half-circle detection
- **Details:** Dataset containing circles in images coordinates (OpenCV + custom script)

## 9. Generate validation data
**Requirements file:** ? human-in-the-loop?: Generate (training) validation data for farmland
- **Details:** Gridded satellite scenes + high resolution aerial imagery, Spatial vector database (QGIS / Google Earth)

## 10. Accuracy assessment
**Requirements file:** Accuracy Assessment
- **Details:** Spatial vector database + Dataset containing circles in images coordinates, Accuracy metrics (scikit-learn)


## Project Workflow Overview

This project leverages Nextflow for workflow management and includes various stages of data preprocessing, analysis, and validation. Below is a summary of the key updates and features implemented:

### Key Features and Updates

- **Workflow Outputs**: Added named outputs for the workflow and removed unnecessary channel names.
- **Git Management**: Updated `.gitignore` to exclude Nextflow-related files and other unnecessary directories.
- **Memory Management**: Adjusted memory allocation for processes requiring more resources.
- **Directory Management**: Moved directory publishes to the configuration file for better management.
- **Process Labeling**: Labeled processes based on their memory usage.
- **Parameter Updates**: Included new parameters for input and output directories, and updated paths accordingly.
- **NDVI Calculation**: Implemented NDVI (Normalized Difference Vegetation Index) calculation and aggregation.
- **Tool Conversion**: Converted scripts into CLI tools and moved from Snakemake to Nextflow for workflow management.
- **Data Downloading**: Finalized scripts for downloading and preprocessing data, including a prototype for cropland detection.
- **Docker Integration**: Added Dockerfile and updated dependencies for reproducible environments.
- **Circle Detection**: Implemented a feature for detecting circles, converting coordinates, and saving results as GeoPackage files.
- **Validation Data**: Digitized fields for validation and included a workflow for this purpose.
- **Bug Fixes and Improvements**: Addressed various bugs, linting issues, and improved code style for better readability and maintenance.

### Workflow Components

- **Preprocessing**: Initial data downloading, unpacking, and stacking processes.
- **Circle Detection**: Detecting circles in the images and transforming coordinates to spatial reference systems.
- **NDVI Calculation**: Calculating NDVI from the preprocessed images.
- **Cropland Detection**: Preliminary implementation for detecting croplands.
- **Validation**: Digitizing fields and validating the detected features.

### Future Improvements

- **Simultaneous Classification and Delineation**: Plan to implement simultaneous classification and tree crown delineation.
- **Pretraining with LiDAR Data**: Improving neural network performance by pretraining with LiDAR data.


## Additional Documentation

- [CONTRIBUTING.md](CONTRIBUTING.md)
- [LICENSE](LICENSE)
- [CONDUCT.md](CONDUCT.md)
- [citation.cff](citation.cff)
- [pyproject.toml] (pyproject.toml)

## Authors and Acknowledgments

## Authors

This project is a collaborative effort by the following contributors

- **Hasnain Mohi Ud Din** <mohiuddin1@uni-potsdam.de> 
- **Ayesha Shahzad** <shahzad@uni-potsdam.de>
- **Ann Zoe Thomas** <thomas6@uni-potsdam.de>
- **Florian Katerndahl** <florian.katerndahl@uni-potsdam.de>
- **Malin Ettenhofer** <ettenhofer@uni-potsdam.de>

Each author has brought unique expertise and dedication to this project, contributing significantly to its development and success.

## License

This project is licensed under the MIT License. For more details, refer to the [LICENSE](LICENSE) file.

## Project Status

The project is currently in progress. We have successfully set up the basic framework and worked out our next steps and goals. We came close to finishing the workflow, which takes 9 hours to render. Unfortunately, we cannot provide a full accuracy assessment at this moment but will be able to provide that and a full final report at project presentation.

## References

For more detailed information, refer to the attForached documents and scripts provided in this repository.

## Project Branches Structure

### Main Branch (`group_project_2-main-5`)

    group_project_2-main/
    ├── .gitignore
    ├── CONDUCT.md
    ├── CONTRIBUTING.md
    ├── LICENSE
    ├── README.md
    ├── citation.cff
    ├── pyproject.toml
    ├── bin/
    │   ├── apps/
    │   │   └── preprocess.py
    │   └── senseagronomy/
    │       ├── __init__.py
    │       ├── converter.py
    │       └── scene.py
    ├── data/
    │   └── validation/
    │       ├── validation_data.gpkg
    │       └── validation_data.qgz
    ├── docs/
    │   ├── RSE_project2_flowchart.pdf
    │   ├── raw-dag.uxf
    │   ├── requirements.md
    │   └── imgs/
    │       └── dag.png
    └── tests/
        └── test_converter.py

### Feature Snakemake Branch (`group_project_2-feature_snakemake`)

    group_project_2-feature_snakemake/
    ├── .dockerignore
    ├── .gitignore
    ├── CONDUCT.md
    ├── CONTRIBUTING.md
    ├── LICENSE
    ├── README.md
    ├── citation.cff
    ├── pyproject.toml
    ├── .docker/
    │   └── agrosense.Dockerfile
    ├── bin/
    │   └── senseagronomy/
    │       ├── __init__.py
    │       ├── converter.py
    │       ├── scene.py
    │       └── apps/
    │           └── preprocess.py
    ├── docs/
    │   ├── RSE_project2_flowchart.pdf
    │   ├── raw-dag.uxf
    │   ├── requirements.md
    │   └── imgs/
    │       └── dag.png
    └── workflow/
        └── Snakefile

### Feature Transform Coordinates Branch (`group_project_2-17_feature-transform-coordinates`)

    group_project_2-17_feature-transform-coordinates/
    ├── .dockerignore
    ├── .gitignore
    ├── CONDUCT.md
    ├── CONTRIBUTING.md
    ├── LICENSE
    ├── README.md
    ├── citation.cff
    ├── pyproject.toml
    ├── .docker/
    │   └── agrosense.Dockerfile
    ├── bin/
    │   └── senseagronomy/
    │       ├── __init__.py
    │       ├── circledetector.py
    │       ├── converter.py
    │       ├── downloader.py
    │       ├── scene.py
    │       ├── spatialtransformer.py
    │       └── apps/
    │           ├── detectcircle.py
    │           ├── download_data.py
    │           ├── preprocess.py
    │           └── transformcoordinates.py
    ├── data/
    │   └── validation/
    │       ├── validation_data.gpkg
    │       └── validation_data.qgz
    ├── docs/
    │   ├── RSE_project2_flowchart.pdf
    │   ├── raw-dag.uxf
    │   ├── requirements.md
    │   └── imgs/
    │       └── dag.png
    ├── tests/
    │   ├── test_converter.py
    │   └── test_download.py
    └── workflow/
        ├── main.nf
        ├── nextflow.config
        └── module/
            ├── cropland_detection.nf
            ├── higher_level.nf
            └── preprocess.nf

### Feature Nextflow Branch (`group_project_2-feature_nextflow-2`)

    group_project_2-feature_nextflow-2/
    ├── .dockerignore
    ├── .gitignore
    ├── CONDUCT.md
    ├── CONTRIBUTING.md
    ├── LICENSE
    ├── README.md
    ├── citation.cff
    ├── pyproject.toml
    ├── .docker/
    │   └── agrosense.Dockerfile
    ├── bin/
    │   └── senseagronomy/
    │       ├── __init__.py
    │       ├── circledetector.py
    │       ├── converter.py
    │       ├── downloader.py
    │       ├── scene.py
    │       ├── spatialtransformer.py
    │       └── apps/
    │           ├── detectcircle.py
    │           ├── download_data.py
    │           ├── preprocess.py
    │           └── transformcoordinates.py
    ├── data/
    │   └── validation/
    │       ├── validation_data.gpkg
    │       └── validation_data.qgz
    ├── docs/
    │   ├── RSE_project2_flowchart.pdf
    │   ├── raw-dag.uxf
    │   ├── requirements.md
    │   └── imgs/
    │       └── dag.png
    ├── tests/
    │   ├── test_converter.py
    │   └── test_download.py
    └── workflow/
        ├── main.nf
        ├── nextflow.config
        └── module/
            ├── cropland_detection.nf
            ├── higher_level.nf
            └── preprocess.nf

### Accuracy Assessment Branch (`group_project_2-accuracy_assessment`)

    group_project_2-accuracy_assessment/
    ├── .dockerignore
    ├── .gitignore
    ├── CONDUCT.md
    ├── CONTRIBUTING.md
    ├── LICENSE
    ├── README.md
    ├── citation.cff
    ├── pyproject.toml
    ├── workflow.md
    ├── .docker/
    │   └── agrosense.Dockerfile
    ├── bin/
    │   └── senseagronomy/
    │       ├── __init__.py
    │       ├── accuracy_assessment.py
    │       ├── circledetector.py
    │       ├── converter.py
    │       ├── downloader.py
    │       ├── scene.py
    │       ├── spatialtransformer.py
    │       └── apps/
    │           ├── accuracy_assessment_main.py
    │           ├── detectcircle.py
    │           ├── download_data.py
    │           ├── preprocess.py
    │           └── transformcoordinates.py
    ├── data/
    │   └── validation/
    │       ├── validation_data.gpkg
    │       └── validation_data.qgz
    ├── docs/
    │   ├── RSE_project2_flowchart.pdf
    │   ├── raw-dag.uxf
    │   ├── requirements.md
    │   └── imgs/
    │       └── dag.png
    ├── tests/
    │   ├── test_converter.py
    │   └── test_download.py
    └── workflow/
        ├── main.nf
        ├── nextflow.config
        └── module/
            ├── cropland_detection.nf
            ├── higher_level.nf
            └── preprocess.nf

