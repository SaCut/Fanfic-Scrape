# FANFIC-SCRAPE

A Python script for downloading WHOLE threads of fanfiction and original works from XenForo forums (only tested with SufficientVelocity and SpaceBattles). At this stage, it doesn't yet work for log-in protected forums like Questionable Questing.

# ------Description------
Fanfic Scrape is a simple executable python script that's intended mainly for downloading "story only" threads, or threads in "reader" mode. It will download a complete thread, find the threadmarks, and use those as chapter titles to create an html file for each chapter.

Plans for future versions include eventual bugfixes, adding the possibility to choose the output format of the download (at least epub), and maybe a small GUI. Making it into a plugin for Calibre is not excluded.

# ------Dependencies------
This script is written in Python 3.
I also requires beautifulsoup to run. You can install it from command line with:

$pip install beautifulsoup4

# ------Run------
The repository contains a file that can be run directly on linux systems. Also, FanfisScrape.py can be run from terminal.
