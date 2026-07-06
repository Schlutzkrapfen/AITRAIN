**YOLO Auto-Split & Train**

An all-in-one Python utility designed to make YOLO dataset preparation and model training completely effortless. This tool handles everything from data curation to training execution: it splits your data, isolates specific classes from mixed images, and automatically launches the YOLO training pipeline. Features
- Smart Train/Val Splitting: Quickly partition your raw images and annotations into standard train and val configurations.

- Overfit/Full-Train Mode: Train on 100% of your dataset when validation isn't required.

- Automatic Class Isolation: If your raw dataset contains mixed labels (e.g., both a dog and a cat in the same frame), the tool can filter them out to create a clean, single-class dataset.

- End-to-End Automation: Automatically generates the required YOLO .yaml configuration files and kicks off the training process instantly using the Ultralytics API.
