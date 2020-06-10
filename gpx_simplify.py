import gpxpy
import gpxpy.gpx


def gpx_simplify(gpx, max_distance):
    gpx.simplify(max_distance)
    return gpx


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description="Splits tracks of a GPX file into multiple track segments, if a certain distance between two points is reached")
    parser.add_argument("input", metavar="INPUT", type=str, nargs=1,
                        help="path to input gpx-file")
    parser.add_argument("output", metavar="OUTPUT", type=str, nargs=1,
                        help="path to output gpx-file")
    parser.add_argument("--max-distance", metavar="max_distance", type=float,
                        help="the max separation in meters between points")

    args = parser.parse_args()

    with open(args.input[0]) as input_file:
        input_gpx = gpxpy.parse(input_file)

    output_gpx = gpx_simplify(input_gpx, args.max_distance)

    with open(args.output[0], "w") as output_file:
        output_file.write(output_gpx.to_xml(prettyprint=False))
