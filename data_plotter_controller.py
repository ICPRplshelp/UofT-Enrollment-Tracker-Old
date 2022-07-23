from datetime import datetime

from helper_files.date_plotter import MultiDatePlotSystem, PlotlyPlotter
from helper_files.get_instructor import LecInfoGetter

IMPORTANT_DATES = [
    ('St', datetime.fromtimestamp(1656907200), True),
    ('4th', datetime.fromtimestamp(1657512000), False),
    ('3rd', datetime.fromtimestamp(1657771200), False),
    ('2nd', datetime.fromtimestamp(1658116800), False),
    ('1st', datetime.fromtimestamp(1658376000), False),
    ('Gen', datetime.fromtimestamp(1659067200), True),
    # ('UTSG non-FAS enrollment', datetime.fromtimestamp(1659499200)),
    # ('UTM/UTSC enrollment', datetime.fromtimestamp(1659693600)),
    # ('Tuition fee deadline', datetime.fromtimestamp(1661918400), False),
    ('F/Y1st', datetime.fromtimestamp(1662609600), True),
    ('F/YW', datetime.fromtimestamp(1663387200), False),
    ('F/YE', datetime.fromtimestamp(1663819200), True),
    ('FD', datetime.fromtimestamp(1668571200), True),
    ('FLWD', datetime.fromtimestamp(1670385600), True),
    ('S1st', datetime.fromtimestamp(1673236800), True),
    ('SWLC', datetime.fromtimestamp(1674187200), False),
    ('SE', datetime.fromtimestamp(1674446400), True),
    ('YD', datetime.fromtimestamp(1676952000), True),
    ('SD', datetime.fromtimestamp(1679284800), True),
    ('Y/SLWD', datetime.fromtimestamp(1680753600), True),
    ('EOY', datetime.fromtimestamp(1682740800), True),
]

IMPORTANT_DATES_INFO = """
St: Enrollment start time
4th-1st: First day of course enrollment for these respective years
Gen: After the end of priority enrollment
F/Y1st: First day of classes (F/Y)
F/YW: Waitlists close
F/YE: Enrollment closes
FD: Last day to drop F courses
FLWD: Last day to LWD F courses
S1st: First day of S courses
SWLC: Waitlists close
SE: Enrollment closes
YD: Last day to drop Y courses
SD: Last day to drop S courses
Y/SLWD: Last day to LWD Y/S courses
EOY: Last day of the session
"""


class CoursePlotterWrapper:
    session: str
    ps: MultiDatePlotSystem
    plot_tool: str

    def __init__(self, session: str) -> None:
        self.lig = LecInfoGetter()
        self.session = session
        self.ps = MultiDatePlotSystem(self.lig, self.session,
                                      False)
        self.plot_tool = 'plt'
        self.ps.important_dates = IMPORTANT_DATES

    def change_plotting_tool(self, mode: str) -> None:
        if mode == 'plt' and self.plot_tool != 'plt':
            self.ps = MultiDatePlotSystem(self.lig, self.session, False)
        elif mode == 'px' and self.plot_tool != 'px':
            self.ps = PlotlyPlotter(self.lig, self.session, False)
        self.ps.important_dates = IMPORTANT_DATES

    def set_session(self, session: str) -> None:
        self.ps.session = session
        self.session = session

    def set_special_section_off_toggle(self, predicate: bool) -> None:
        self.ps.forbid_special_sections = predicate

    def plot_individual(self, course: str) -> None:
        """Plot all lectures at once for a course.
        One line for each lecture."""
        self.ps.sequence_single(self.get_course_path(course))

    def plot_combined(self, course: str) -> None:
        """Plot a single course. The line
        of that course will be the sum of enrollments
        for that lecture section."""
        self.ps.sequence_bulk(self.get_course_path(course))

    def get_course_path(self, course: str) -> str:
        return f'coursedata2/{course}.csv'


SESSION_CODE = '20229'


def main(course: str, individual: bool = True, plot_mode: str = 'plt', forbid_eng: bool = False, session: str = '20229') -> None:
    cpw = CoursePlotterWrapper(session)
    cpw.change_plotting_tool(plot_mode)
    cpw.set_special_section_off_toggle(forbid_eng)
    cpw.plot_individual(course) if individual else cpw.plot_combined(course)


if __name__ == '__main__':
    main('CSC343H1-S')
