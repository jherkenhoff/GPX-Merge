from gpx_split import gpx_split
from gpx_remove_short_segments import gpx_remove_short_segments
from gpx_simplify import gpx_simplify
from gpx_smooth import gpx_smooth

if __name__ == '__main__':
    import argparse
    import gpxpy

    parser = argparse.ArgumentParser(description="Splits tracks of a GPX file into multiple track segments, if a certain distance between two points is reached")
    parser.add_argument("input", metavar="INPUT", type=str, nargs=1,
                        help="path to input gpx-file")
    parser.add_argument("output", metavar="OUTPUT", type=str, nargs=1,
                        help="path to output gpx-file")

    args = parser.parse_args()

    with open(args.input[0]) as input_file:
        input_gpx = gpxpy.parse(input_file)

    tmp_gpx, split_count = gpx_split(input_gpx, 500)
    tmp_gpx, removed_segments = gpx_remove_short_segments(tmp_gpx, minimum_point_count=10, minimum_length=40)
    #tmp_gpx = gpx_smooth(tmp_gpx, smooth_count=1)
    tmp_gpx = gpx_simplify(tmp_gpx, 10)

    with open(args.output[0], "w") as output_file:
        output_file.write(tmp_gpx.to_xml(prettyprint=False))
