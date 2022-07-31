# TimetableTracker

This program is used to track and display course enrollments for all of UofT's A&S courses for the Fall-Winter 2022-2023 session.

## Usage
run `runoptions_independent.py` on your computer if you want to use a GUI to use this.

## How to open Python files

The most straightforward way is to open this entire project with an IDE such as Pycharm. Otherwise, as long as you have Python installed, use command prompt to run them (`py runoptions_independent.py`) given the working directory is the directory the `py` folder is in (type `cmd` in the file search thing).

**This version of this program DOES NOT HAVE the tools to capture UofT timetable data - it just displays it.
I'll have to update this over time.**

## Definitions

- Enrollment: Actually enrolled + waitlisted students
- Drops: Students who've dropped the course after the last day to enroll in the course
- LWDs: Students who've dropped after the last day to drop the course

These values will be visible when applicable. The vertical lines signal important dates (typically, first day to enroll, end of priority period, last day to enroll, last day to drop, and last day to LWD).

## Dependencies

Use `pip` to install them. For instance, run `pip install <dependency>` for each dependency below after you have installed python.

```
matplotlib
pyplot
```

## Screenshots

![image](https://user-images.githubusercontent.com/93059453/180590777-e99ed38e-115e-432e-ab04-48b317e1091f.png)


![image](https://user-images.githubusercontent.com/93059453/180590744-67a56416-fbd8-4475-8aff-a4d6d6d4c2a2.png)

