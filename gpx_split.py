import gpxpy
import gpxpy.gpx

def gpx_split(gpx, split_threshold):
    for track_idx, track in enumerate(gpx.tracks):
        split_segments = []

        def recursive_split(segment):
            did_split=False
            for j in range(segment.get_points_no()-1):
                distance = segment.points[j].distance_2d(segment.points[j+1])
                if (distance >= split_threshold):
                    did_split=True
                    split_segments = []
                    segment_1, segment_2 = segment.split(j)
                    #segment_1.remove_point(j)
                    split_segments.append(segment_1)
                    segment_2 = recursive_split(segment_2)
                    return split_segments + segment_2
            if not did_split:
                return [segment]

        for segment in track.segments:
            split_segments = split_segments + recursive_split(segment)

        if (len(split_segments) > 1):
            split_gpx = gpxpy.gpx.GPX()
            split_gpx.tracks.append(gpxpy.gpx.GPXTrack())
            for split_segment in split_segments:
                split_gpx.tracks[0].segments.append(split_segment)
            return split_gpx, len(split_segments)-1
        else:
            return gpx, 0

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description="Splits tracks of a GPX file into multiple track segments, if a certain distance between two points is reached")
    parser.add_argument("input", metavar="INPUT", type=str, nargs=1,
                        help="path to input gpx-file")
    parser.add_argument("output", metavar="OUTPUT", type=str, nargs=1,
                        help="path to output gpx-file")
    parser.add_argument("distance", metavar="split-distance", type=float, nargs=1,
                        help="maximum distance between two points, after which they get split into separate tracks")

    args = parser.parse_args()

    with open(args.input[0]) as input_file:
        input_gpx = gpxpy.parse(input_file)

    output_gpx, split_count = gpx_split(input_gpx, args.distance[0])
    print("Split count = %d"%split_count)

    with open(args.output[0], "w") as output_file:
        output_file.write(output_gpx.to_xml(prettyprint=False))
