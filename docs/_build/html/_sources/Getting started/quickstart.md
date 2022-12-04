# Quickstart

Welcome to the getting started with the Root Viewer tutorial!

This tutorial assumes you have already installed the Root Viewer. For help with installation see the [installation tutorial](installation.md).

This tutorial will teach you all the different ways to launch the Root Viewer. By the end of the tutorial you should be able to launch the viewer and view all the images you want!

## Launching the Root Viewer
There are two ways to launch the viewer:

* command line
* python script

### Command line usage

To launch the viewer from the command line simply run
```
root-viewer
```
This command will launch an empty viewer:
```{image} ../images/blank_viewer.png
:name: main viewer
```

### Python script usage
To launch the viewer from a python script, inside your script you should import root-viewer, and then create the Viewer by adding some data.

For example, to add an image and some points inside your script you should include:
```
import root-viewer

# create a Viewer and add an image here
viewer = root-viewer.view_image(my_image_data)

# custom code to add data here
viewer.add_points(my_points_data)

# start the event loop and show the viewer
root-viewer.run()
```
```{image} ../images/astronaut_viewer.png
:name: main viewer with astronaut image
```