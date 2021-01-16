"""Implements smallest circle algorithm on chromosome movement data.

This script implements the smallest circle algorithm (from Project
Nayuki; see smallestenclosingcircle.py for details) on chromosome
movement data. It reads in excel files from folders where the data
are stored. The data are x,y coordinates of flourescently-tagged
chromosomes throughout a video recording. The make_circle function
in smallestenclosingcircle.py takes in a list of tuples, so these
coordinates were converted to that form.

The script returns graphs for each recording. These graphs visualize
the coordinates of the chromosomes as well as the smallest enclosing
circle. It also returns three excel files. One excel file is
generated for each recording; these files contain information about
the circle (the center's coordinates, as well as radius and area).
Excel files are also generated for all the recordings associated with
a particular chromosome. One of these excel files contains information
about each circle for all recordings associated with a particular
chromosome. The other contains information about the statistics of the
recordings associated with a particular chromosome (i.e. average circle
area, standard deviation, and standard error of the mean).
"""

import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import math
from smallestenclosingcircle import make_circle

TracksPath = "file/path/here"
os.chdir(TracksPath)

# Step 1: Retrieve all contents in Tracks_dots_lines_graphs directory.
all_directory_contents = os.listdir(TracksPath)

# Step 2: Retrieve ChrI and ChrX folders.
Chr_folders = []
for file_or_folder in all_directory_contents:
    if 'Chr' in file_or_folder:
        Chr_folders.append(file_or_folder)

# Step 3: Retrieve and analyze excel files in each Chr folder.
for Chr_folder in Chr_folders:

    x_column = 'x (\u03BCm)'
    y_column = 'y (\u03BCm)'
    radius = 'radius (\u03BCm)'
    area = 'area (\u03BCm^2)'
    summary_df = pd.DataFrame(columns=[x_column,
                                       y_column,
                                       radius,
                                       area
                                       ])

    # i. Move to current Chr folder.
    os.chdir(TracksPath)
    current_Chr_folder = os.path.join(TracksPath, Chr_folder)
    os.chdir(current_Chr_folder)

    # ii. Obtain excel files within the Chr folder.
    all_current_Chr_folder_contents = os.listdir(current_Chr_folder)
    xlsx_files_in_current_Chr_folder = []
    for file in all_current_Chr_folder_contents:
        if 'xlsx' in file:
            xlsx_files_in_current_Chr_folder.append(file)

    # iii. Obtain x and y coordinates from
    #      each xlsx file within Chr folder.
    for xlsx_file in xlsx_files_in_current_Chr_folder:

        df = pd.read_excel(xlsx_file, header=None, names=[x_column,
                                                          y_column
                                                          ])

        # a: Get the coordinates in "tuple" form,
        #    resulting in a list of tuples.
        coordinates = []
        for index, row in df.iterrows():
            coordinates.append((row[x_column], row[y_column]))

        # b: Obtain smallest circle and area using coordinates variable.
        smallest_circle = make_circle(coordinates)
        smallest_circle_area = np.asarray(math.pi*(smallest_circle[2]**2))

        # c: Write out smallest circle and area results
        #    into a pandas DataFrame.

        # 1: Create array of containing smallest circle specs and area.
        smallest_circle_array = np.asarray(smallest_circle)
        array_and_area = np.append(smallest_circle_array,
                                   smallest_circle_area)
        smallest_circle_array_and_area_2d = np.atleast_2d(array_and_area)

        # 2: Create pandas DataFrame from smallest_circle_array
        #    and save as excel file.
        results_df = pd.DataFrame(smallest_circle_array_and_area_2d,
                                  columns=[x_column,
                                           y_column,
                                           radius,
                                           area
                                           ],
                                  index=[xlsx_file[:-5]])
        results_df.to_excel(xlsx_file[:-5]+' circle.xlsx')

        # 3: Add results to summary file for Chr.
        summary_df = summary_df.append(results_df)

        # d. Plot x,y coordinates and smallest circle.
        ax = df.plot(x=0, y=1,
                     title=xlsx_file[:-5]+' smallest circle dots and lines',
                     xlim=[
                         smallest_circle[0]-0.7,
                         smallest_circle[0]+0.7
                         ],
                     ylim=[
                         smallest_circle[1]-0.7,
                         smallest_circle[1]+0.7
                         ],
                     c='steelblue', linestyle='solid', linewidth=1.0,
                     marker='o', markersize=3)
        ax.set_aspect('equal')
        circle = plt.Circle((smallest_circle[0], smallest_circle[1]),
                            smallest_circle[2], color='midnightblue',
                            alpha=0.8, clip_on=False, fill=False,
                            linewidth=1)

        fig = plt.gcf()
        ax_circle = fig.gca()

        ax_circle.add_artist(circle)

        # e. Save figure.
        fig.savefig(xlsx_file[:-5] + ' circle dots and lines' + '.jpeg')

    # iv. Compute basic summary statistics from summary DataFrame
    #     (summary_df).
    avg_area = summary_df.loc[:, area].mean()
    stdev_area = summary_df.loc[:, area].std()
    sem_area = summary_df.loc[:, area].sem()

    # v. Save summary and summary statistics as excel files.

    # a. Export summary DataFrame as excel file.
    summary_df.to_excel(Chr_folder + ' circle summary.xlsx')

    # b. Create summary statistics excel file.
    summary_statistics = np.asarray([avg_area, stdev_area, sem_area])
    summary_statistics_2d = np.atleast_2d(summary_statistics)

    summary_statistics_df = pd.DataFrame(summary_statistics_2d,
                                         columns=[
                                             'avg ' + area,
                                             'stdev',
                                             'sem'
                                             ])
    summary_statistics_df.to_excel(Chr_folder + ' area stats.xlsx')
