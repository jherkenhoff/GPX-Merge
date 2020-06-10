import argparse
import glob
import gpxpy
import gpxpy.gpx
from os import listdir
from os.path import isfile, join

from gpx_split import gpx_split
from gpx_remove_short_segments import gpx_remove_short_segments
from gpx_simplify import gpx_simplify
from gpx_smooth import gpx_smooth


# Setup argument parser
parser = argparse.ArgumentParser(description="Merges multiple GPX files into one")
parser.add_argument("tracks", metavar="TRACKS", type=str, nargs="+",
                    help="path(s) to gpx-files to process")
parser.add_argument("merged", metavar="MERGED", type=str, nargs=1,
                    help="path to save the merged gpx-files to")

# Print iterations progress
def printProgressBar (iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█'):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print('\r%s |%s| %s%% %s' % (prefix, bar, percent, suffix), end = '\r')
    # Print New Line on Complete
    if iteration == total:
        print()

# Parse
args = parser.parse_args()

# Check input tracks
file_list = []
for track in args.tracks:
    file_list = file_list + glob.glob(track)

print("Found %d files" % len(file_list))

# Setup output file
merged_gpx = gpxpy.gpx.GPX()

for i, f in enumerate(file_list):
    print("\nProcessing file %d/%d (%s)" %(i+1, len(file_list), f), end="")

    with open(f) as gpx_file:
        gpx = gpxpy.parse(gpx_file)

    point_count = gpx.get_points_no()
    track_length = gpx.length_2d()
    print(" (%d points)" %(point_count), end="")

    if point_count < 50:
        print("\nIgnoring file %s (Point count %d < %d)" %(f, point_count, 50), end="")
        continue

    if track_length < 100:
        print("\nIgnoring file %s (Track length %.0fm < %.0fm)" %(f, track_length, 100), end="")
        continue

    tmp_gpx, split_count = gpx_split(gpx, 500)
    tmp_gpx, removed_segments = gpx_remove_short_segments(tmp_gpx, minimum_point_count=10, minimum_length=40)
    #tmp_gpx = gpx_smooth(tmp_gpx, smooth_count=1)
    tmp_gpx = gpx_simplify(tmp_gpx, 10)

    for track in tmp_gpx.tracks:
        merged_gpx.tracks.append(track)

print("\n\nMerging done. Generating XML")
xml = merged_gpx.to_xml(prettyprint=False)
xml_length = len(xml)
block_size = int(2**15)
print("Writing to file \"%s\"" %args.merged[0])
print("Blocksize: %d bytes" %block_size)

with open(args.merged[0], "w") as merged_file:
    for (i, block) in [(i, xml[i:i+block_size]) for i in range(0, xml_length, block_size)]:
        merged_file.write(block)
        printProgressBar(i, xml_length, prefix = 'Write:', suffix = 'Complete', length = 50)

print("\nDone")
