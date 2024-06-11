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

### Query USGS Landsat-Data

**Input:** None  
**Output:** Landsat scenes with metadata files  
**Implementation:** Landsatxplore

### Generate Multi-Band Images

**Input:** Landsat scenes with metadata files  
**Output:** Multi-band images with metadata items set  
**Implementation:** Custom CLI Tool

### Mask Multi-Band Images

**Operation:** Apply gain and offset (remove from metadata afterwards)  
**Input:** Multi-band images with metadata items set + QAI-files  
**Output:** Masked and scaled multi-band scenes  
**Implementation:** Custom CLI Tool

### Generate Datacube

**Input:** All images  
**Output:** Gridded satellite scenes  
**Implementation:** FORCE

### Timeseries Processing and VI-Calculation

**Input:** Gridded satellite scenes  
**Output:** Temporal aggregation of Vegetation Index (VI)  
**Implementation:** Custom CLI Tool

### Generate (Training) Validation Data for Farmland

**Operation:** Human-in-the-loop  
**Input:** Gridded satellite scenes + high resolution aerial imagery  
**Output:** Spatial vector database  
**Implementation:** QGIS / Google Earth

### Train Machine Learning Model for Land Cover Classes

**Input:** Gridded satellite scenes  
**Output:** Pixel-wise classification of farmland/non-farmland  
**Implementation:** scikit-learn + custom script

### Circle/Half-Circle Detection

**Input:** Temporal aggregation of VI or Pixel-wise classification of farmland/non-farmland  
**Output:** Dataset containing circles in image coordinates  
**Implementation:** OpenCV + custom script

### Generate Output Map

**Input:** Dataset containing circles in image coordinates + background imagery  
**Output:** PNG  
**Implementation:** QGIS / R

### Accuracy Assessment

**Input:** Spatial vector database + Dataset containing circles in image coordinates  
**Output:** Accuracy metrics  
**Implementation:** scikit-learn

### Final Report

**Input:** Not yet set (PNG, accuracy metrics)  
**Output:** PDF  
**Implementation:** Quarto / R Markdown

## Additional Documentation

- [CONTRIBUTING.md](CONTRIBUTING.md)
- [LICENSE](LICENSE)
- [CONDUCT.md](CONDUCT.md)
- [citation.cff](citation.cff)

## Authors and Acknowledgments

Has to be updated.

## License

This project is licensed under the MIT License. For more details, refer to the [LICENSE](LICENSE) file.

## Project Status

The project is currently in progress. We have successfully set up the basic framework and worked out our next steps and goals. We welcome contributions and feedback to help us enhance the project's capabilities and accuracy.

## References

For more detailed information, refer to the attached documents and scripts provided in this repository.