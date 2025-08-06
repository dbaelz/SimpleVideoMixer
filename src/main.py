import argparse


PROGRAM_NAME = "Simple Video Mixer"
VERSION = "0.0.1"


def main() -> None:
    parser = argparse.ArgumentParser(description="Mix video and audio sources", add_help=True)
    parser.add_argument("-v", "--version", action="version", version=f"{PROGRAM_NAME} - version {VERSION}")
    
    


if __name__ == "__main__":
    main()