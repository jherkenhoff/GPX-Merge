import argparse
import glob
import gpxpy
import gpxpy.gpx
from os import listdir
from os.path import isfile, join


# Setup argument parser
parser = argparse.ArgumentParser(description='Merges multiple GPX files into one')
parser.add_argument('tracks', metavar='TRACKS', type=str, nargs='+',
                    help='path(s) to gpx-files to process')
parser.add_argument('merged', metavar='MERGED', type=str, nargs=1,
                    help='path to save the merged gpx-files to')
parser.add_argument('--split-threshold', dest='split_threshold', metavar='distance', type=float,
                    help='maximum distance between two points, before they get split into separate tracks')
parser.add_argument('--minimum-count', dest='minimum_point_count', metavar='count', type=int,
                    help='minimum number of points inside a track. Tracks with less points will not be merged')
parser.add_argument('--minimum-length', dest='minimum_length', metavar='length', type=float,
                    help='minimum total length of track. Shorter tracks will not be merged')
parser.add_argument('--simplify', dest='simplify', metavar='max-distance', type=float,
                    help='minimum total length of track. Shorter tracks will not be merged')
parser.add_argument('--reduce', dest='reduce', metavar='min-distance', type=float,
                    help='minimum total length of track. Shorter tracks will not be merged')

# Parse
args = parser.parse_args()

# Check input tracks
file_list = []
for track in args.tracks:
    file_list = file_list + glob.glob(track)

print("Found %d files" % len(file_list))

# Setup output file
merged_gpx = gpxpy.gpx.GPX()

# Initialize statistics
statistics = {
    "ignored_files": {
        "point_count": 0,
        "track_length": 0
    },
    "split_tracks": 0,
    "split_count": 0,
    "total_length": 0,
    "total_point_count": 0
}

for i, f in enumerate(file_list):
    gpxFile = open(f)
    gpx = gpxpy.parse(gpxFile)


    point_count = gpx.get_points_no()
    track_length = gpx.length_2d()
    print("Processing file %d of %d (%s) (%d points)" %(i, len(file_list), f, point_count))

    statistics["total_point_count"] = statistics["total_point_count"] + point_count
    if args.minimum_point_count:
        if point_count < args.minimum_point_count:
            print("Ignoring file %s (Point count %d < %d)" %(f, point_count, args.minimum_point_count))
            statistics["ignored_files"]["point_count"] = statistics["ignored_files"]["point_count"] + 1
            continue

    statistics["total_length"] = statistics["total_length"] + track_length
    if args.minimum_length:
        if track_length < args.minimum_length:
            print("Ignoring file %s (Track length %.2fm < %.2fm)" %(f, track_length, args.minimum_length))
            statistics["ignored_files"]["track_length"] = statistics["ignored_files"]["track_length"] + 1
            continue
    for track_idx, track in enumerate(gpx.tracks):

        # Do split and merge
        if args.split_threshold:
            split_track_segments = []
            for track_segment in track.segments:
                for j in range(track_segment.get_points_no()-1):
                    distance = track_segment.points[j].distance_2d(track_segment.points[j+1])
                    if (distance >= args.split_threshold):
                        segment_1, segment_2 = track_segment.split(j)
                        segment_1.remove_point(j)
                        split_track_segments.append(segment_1)
                        split_track_segments.append(segment_2)

            if (len(split_track_segments) > 0):
                statistics["split_tracks"] = statistics["split_tracks"] + 1
                statistics["split_count"] = statistics["split_count"] + len(split_track_segments)
                for i in split_track_segments:
                    merged_gpx.tracks.append(i)
            else:
                merged_gpx.tracks.append(track)
        else:
            merged_gpx.tracks.append(track)
    gpxFile.close()

print('Merging done. Writing to file \'%s\'' %args.merged[0])
merged_file = open(args.merged[0], "w")
merged_file.write(merged_gpx.to_xml())
merged_file.close()
print('Done')

print('\n#######################')
print('Statistics:')
print('#######################')
print('Ignored files: \t\t%d' %(statistics["ignored_files"]["point_count"] + statistics["ignored_files"]["track_length"]))
print('Split tracks: \t\t%d' %(statistics["split_tracks"]))
print('Split count: \t\t%d' %(statistics["split_count"]))
print('Total length: \t\t%.2f km' %(statistics["total_length"]/1e3))
print('Total point count: \t%d' %(statistics["total_point_count"]))
