import argparse




def main():
    return

if __name__ == "__main__":

    # Parse command line args.
    cmdLineParser = argparse.ArgumentParser("Pragram Name")
    cmdLineParser.add_argument(
        "-p", "--varname",
        action="store",
        type=str,
        dest="varname_in_script",
        default="default_value",
        help="Describe the argument's purpose"
        )
    cmdLineParser.add_argument(
        "-C",
        "--flag-name",
        action="store_true",
        dest="flag_name_in_script",
        default=False,
        help="Describe the flag's purpose")
    args = cmdLineParser.parse_args()

    # Run the main program
    main()