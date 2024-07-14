## Workflow Execution

### Prerequisites

The DAW is implemented using the Nextflow workflow manager. In order to execute the workflow on your machine, you need to install [Nextflow](https://www.nextflow.io/docs/latest/install.html) and [Docker](https://docs.docker.com/engine/install/) first.

Landsat 8 and 9 data are the basis for this workflow. The data can be downloaded from the U.S. Geological Survey which requires to [set up an account](https://ers.cr.usgs.gov/register). To follow along with this document, you also need access to the EarthExplorer `MACHINE` role. The respective application can be made from [your account settings](https://ers.cr.usgs.gov/profile/access).

Please note, that earth observation workflows like this one tend to be relatively resource heavy storage wise: Initially, approximately 334 GB of data were downloaded. During execution, another 1.5 TB of storage we needed for intermediate results.

#### Download Data

The data is downloaded via a CLI tool bundled with the here present Python module `senseagronomy`. The tool can be used either by cloning the repository and using poetry to create an appropriate virtual environment or using the associated docker image. From within the root of this repository, execute the following command:

```bash
 docker run -it --rm -v $PWD/resources/landsat:/download floriankaterndahl/agrosense:v0.1.8 \
    downloadlandsat --username <USGS_USERNAME> --password <USGS_PASSWORD> \
    --coordinates 24.5646 49.0965 24.5046 49.4907 24.2269 49.4591 24.0176 49.4501 23.9354 49.3671 23.7137 49.3753 23.4935 49.2579 23.2956 49.4501 23.1479 49.440 22.9887 49.5126 22.8445 49.2737 22.9230 49.1226 23.0696 49.1364 23.1883 48.8589 23.4506 48.8644 23.5917 48.9771 23.8959 48.6530 24.2920 48.6530 24.6046 48.8727 \
    --start-date 2015-01-01 --end-date 2020-12-31 --max-results 1000 --max-cloud-cover 10 --output-dir /download/
```

#### Update Directory Paths

Prior to workflow execution, two directory paths need to be updated in the configuration file: `input_data` and `output_directory`. You can either update them by editing the file `workflow/nextflow.config` or by overwriting them on the command line. The latter requires the addition of `--input_data <path> --output_directory <path` to the call shown below.

### Run the Workflow

To start the workflow, execute the following command from the root of this repository: `nextflow run workflow/main.nf`. You may want to add the `-resume` flag when re-starting the workflow to use cached results whereever possible.
