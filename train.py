def main(args):
    ...
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--mood",
        type=str,
        help="mood category"
    )
    parser.add_argument(
        "--mode",
        type=str,
        help="major or minor mode"
    )
    parser.add_argument(
        "--timesig",
        type=int,
        help="the time signature beat count"
    )

    args = parser.parse_args()
    main(args)