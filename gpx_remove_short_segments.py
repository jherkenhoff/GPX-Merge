import gpxpy
import gpxpy.gpx


def gpx_remove_short_segments(gpx, minimum_point_count=None, minimum_length=None):

    def conditions_met(gpx_segment, minimum_point_count=False, minimum_length=False):
        if minimum_point_count:
            if gpx_segment.get_points_no() < minimum_point_count:
                conditions_met.removed_segments += 1
                return False
        if minimum_length:
            if gpx_segment.length_2d() < minimum_length:
                conditions_met.removed_segments += 1
                return False
        return True

    conditions_met.removed_segments = 0

    output_gpx = gpxpy.gpx.GPX()

    for track in gpx.tracks:
        output_track = gpxpy.gpx.GPXTrack()
        output_track.segments = [segment for segment in track.segments if conditions_met(segment, minimum_point_count, minimum_length)]
        output_gpx.tracks.append(output_track)

    return output_gpx, conditions_met.removed_segments


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description="Splits tracks of a GPX file into multiple track segments, if a certain distance between two points is reached")
    parser.add_argument("input", metavar="INPUT", type=str, nargs=1,
                        help="path to input gpx-file")
    parser.add_argument("output", metavar="OUTPUT", type=str, nargs=1,
                        help="path to output gpx-file")
    parser.add_argument("--minimum-point-count", metavar="minimum_point_count", type=float,
                        help="minimum number of points inside a segment. Segments with less points will be removed")
    parser.add_argument("--minimum-segment-length", metavar="minimum_segment_length", type=float,
                        help="minimum length of segment. Shorter segments will be removed")

    args = parser.parse_args()

    with open(args.input[0]) as input_file:
        input_gpx = gpxpy.parse(input_file)

    output_gpx, removed_segment_count = gpx_remove_short_segments(input_gpx, args.minimum_point_count, args.minimum_segment_length)
    print("Removed segments = %d"%removed_segment_count)

    with open(args.output[0], "w") as output_file:
        output_file.write(output_gpx.to_xml(prettyprint=False))
