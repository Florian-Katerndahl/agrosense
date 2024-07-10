# Requirements

This document lists all functional, non-functional and possibly other forms of requirements for this project.

## Functional Requirements

![UML Workflow Diagram](./imgs/dag.png)

## Non-functional Requirements

- The system should be able to process the Landsat satellite images and detect farmland within a reasonable time frame.
- The system should be user-friendly for users to understand how to use the system and interpret the results without additional efforts.
- The system should be designed for easy updates, by using clean, modular code and best documentation practices.
- The system should adhere to the rules set by the USGS for using their satellite images.

## Other Requirements

### User Requirements

- User must be allowed to set a date range for which to download satellite products; the user must be informed if the endpoints are inclusive or exclusive.
- User must be allowed to set an AOI (Area of Interest) for which to download satellite imagery.
- User may be allowed to set a error handling strategy on their own (e.g. retry, fail, ignore).

### System Requirements

- The workflow must handle processing errors gracefully and according to user specification.
- The workflow must handle API errors gracefully.
- The workflow must potentially try to re-execute download requests. [requirement not yet met]
- The worklow should be able to run mostly independent of host operating system.
