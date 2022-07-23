"""I should have learned how to use Numpy, but I was too lazy."""

import csv
import logging
from dataclasses import dataclass
from datetime import datetime

import matplotlib.pyplot as plt
import plotly.express as px

from helper_files.get_instructor import LecInfoGetter


def main() -> None:
    dps = DatePlotSystem()
    cur_data = dps.read_spreadsheet('MAT136H1-FCC.csv')
    dps.process_csv_data(cur_data)


def main_complex() -> None:
    lig = LecInfoGetter()
    dps2 = MultiDatePlotSystem(lig, '20229', False)
    dps2.sequence('coursedata2/CSC110Y1-F.csv')


class DatePlotSystem:
    plot_title: str
    course_cap: int
    y_enrol: list[int]  # unix time of
    # the 12AM on Y4...
    priority_end: int  # 12AM
    first_class: int  # 12AM
    waitlists_close: int
    last_enroll_day: datetime.date
    drop_date: datetime.date
    lwd_date: datetime.date

    def read_spreadsheet(self, path: str) -> list[list[str]]:
        with open(path, encoding='UTF-8') as f:
            reader = csv.reader(f)
            data = []
            for row in reader:
                data.append(row)
        return data

    def process_csv_data(self, cur_data: list[list[str]]) -> None:
        cur_data_transposed = list(map(list, zip(*cur_data)))
        dates_list = [datetime.fromtimestamp(int(x)) for x in cur_data_transposed[0]]
        values_list = cur_data_transposed[1]
        plt.plot_date(dates_list, values_list, linestyle='solid')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()


@dataclass
class LectureInstance:
    cap: int  # 260
    code: str  # LEC0101
    date_logs: list[datetime.date]
    enroll_logs: list[int]
    instructor: str

    def get_enroll_after(self, thedate: datetime.date) -> int:
        """Get the students enrolled after this date."""
        for i, dat in enumerate(self.date_logs):
            if dat > thedate:
                return self.enroll_logs[i]
        return self.enroll_logs[-1]

    def get_fy_final_enrolls(self) -> int:
        """Return the number of students who
        are enrolled in the section as of the
        earliest of today or the last day to
        enroll in F/Y courses"""
        return self.get_enroll_after(datetime(2022, 9, 21))

    def get_s_final_enrolls(self) -> int:
        """Return the number of students who are
        enrolled in the section as of the
        earliest of today or the last day
        to enroll in S courses"""
        return self.get_enroll_after(datetime(2023, 1, 22))

    def get_f_final_drop(self) -> int:
        """Return the number of students
        who are enrolled in the section
        as of the earliest of today
        or the last day to drop F courses"""
        return self.get_enroll_after(datetime(2022, 11, 16))

    def get_y_final_drop(self) -> int:
        """Return the number of students
        who are enrolled in the section
        as of the earliest of today
        or the last day to drop Y courses"""
        return self.get_enroll_after(datetime(2023, 2, 20))

    def get_s_final_drop(self) -> int:
        """Return the number of students
        who are enrolled in the section
        as of the earliest of today
        or the last day to drop S courses"""
        return self.get_enroll_after(datetime(2023, 3, 19))

    def get_f_final_lwd(self) -> int:
        """Return the number of students
        who are enrolled in the section
        as of the earliest of today
        or the last day to drop S courses"""
        return self.get_enroll_after(datetime(2022, 12, 7))

    def get_sy_final_lwd(self) -> int:
        """Return the number of students
        who are enrolled in the section
        as of the earliest of today
        or the last day to drop S courses"""
        return self.get_enroll_after(datetime(2022, 4, 6))


def mash_lecture_instances(lecs: dict[str, LectureInstance]) -> dict[str, LectureInstance]:
    """Mash up all lecture instances.

    Preconditions: every single lec is time-synced.
    """
    cap_so_far = 0
    enroll_log_lists: list[list[int]] = []
    date_logs = []
    for lec_num, lec_inst in lecs.items():
        if not date_logs:
            date_logs = lec_inst.date_logs
        cap_so_far += lec_inst.cap
        enroll_log_lists.append(lec_inst.enroll_logs)
    # squish them all!!!
    # enroll_log_squished = [sum(x) for x in enroll_log_lists]
    enroll_log_squished = enroll_log_lists[0].copy()
    for i in range(1, len(enroll_log_lists)):
        for j in range(len(enroll_log_squished)):
            enroll_log_squished[j] += enroll_log_lists[i][j]
    temp_lec_instance = LectureInstance(cap_so_far, 'ALL SECTIONS', date_logs, enroll_log_squished,
                                        'N/A')
    return {'ALL SECTIONS': temp_lec_instance}


class MultiDatePlotSystem(DatePlotSystem):
    dates: list[datetime.date] | None
    course_code: str
    bulk_mode: bool
    lec_info_getter: LecInfoGetter
    unused_names: set[str]
    session: str  # this may be set at any time. Please do.
    important_dates: list[tuple[str, datetime, bool]]
    forbid_special: bool

    def __init__(self, lec_info_getter: LecInfoGetter,
                 session: str,
                 bulk_mode: bool = False, forbid_special: bool = False) -> None:
        self.forbid_special_sections = forbid_special
        self.dates = None
        self.course_code = ""
        self.bulk_mode = bulk_mode
        self.lec_info_getter = lec_info_getter
        self.unused_names = {'N/A'}
        self.session = session

    def sequence(self, path_to_csv: str) -> None:
        # self.course_code = extract_course_code(path_to_csv) + f'-{self.session}'
        if self.bulk_mode:
            self.sequence_bulk(path_to_csv)
        else:
            self.sequence_single(path_to_csv)

    def sequence_single(self, path_to_csv: str) -> None:
        sp = self.read_spreadsheet(path_to_csv)
        s10 = self._process_csv_data_first(sp)
        if self.forbid_special_sections:
            try:
                s1 = {x: s10[x] for x in s10 if not (2000 <= int(x.split('-', 1)[1]) <= 2999)}
            except IndexError:
                s1 = s10
            except ValueError:
                s1 = s10
        else:
            s1 = s10
        self._process_csv_data_second(s1)

    def sequence_bulk(self, path_to_csv: str) -> None:
        sp = self.read_spreadsheet(path_to_csv)
        s1 = self._process_csv_data_first(sp)
        mashed = mash_lecture_instances(s1)
        self._process_csv_data_second(mashed)

    def _process_csv_data_first(self, cur_data: list[list[str]]) -> dict[str, LectureInstance]:
        cur_data_transposed = list(map(list, zip(*cur_data)))
        first_row = cur_data_transposed.pop(0)[2:]  # all dates
        self.dates = first_row
        self.course_code = cc_only(cur_data_transposed[0][0]) + f'-{self.session}'
        # print(self.course_code)
        lecture_instances: dict[str, LectureInstance] = {}
        for down_strip in cur_data_transposed:
            crs = down_strip[0]
            # print(down_strip[0])
            lecture_instances[code_only(crs)] = LectureInstance(
                int(down_strip[1]),
                code_only(down_strip[0]),
                [datetime.fromtimestamp(int(x)) for x in first_row],
                [int(x) for x in down_strip[2:]],
                "N/A"
                # self._determine_ins(code_only(down_strip[0]))
            )
        return lecture_instances

    def _process_csv_data_second(self, cur_data: dict[str, LectureInstance]) -> None:
        # plt.figure(dpi=1200)
        fig, ax = plt.subplots()
        # axes = plt.gca()
        # axes.set_aspect(1/66)
        # ax2 = plt.gca()
        # ax2.set_aspect(1/100)
        show_cap = False
        legend_outside = True
        # plt.figure(figsize=(8, 8))
        trans = ax.get_xaxis_transform()
        for i, (lec, lec_instance) in enumerate(cur_data.items()):
            # print(f'plotting {lec_instance.enroll_logs}')
            lec_instance: LectureInstance
            f_extra = f"({lec_instance.cap})" if show_cap else ""
            plt.plot_date(lec_instance.date_logs, lec_instance.enroll_logs, linestyle="solid",
                          label=f"{lec.replace('-', '')}{self._determine_ins(lec)}" + f_extra,
                          markersize=0,
                          linewidth=2.0, color=f'C{i}')
            plt.axhline(y=lec_instance.cap, linestyle="--", color=f'C{i}', alpha=0.6)

        for event, timing, show in self.important_dates:
            if timing > datetime.now():
                # print(f'didn\'t show {event} because it didn\'t happen yet')
                break

            plt.axvline(x=timing, linewidth=0.7)
            if not show:
                continue
            plt.text(timing, 0.013, event, transform=trans, rotation=90, fontsize=6)
        plt.legend(loc='upper right') if not legend_outside else plt.legend(bbox_to_anchor=(1, 0.95))
        plt.xticks(rotation=45)
        plt.title(f'Enrollment for {extract_course_code_2(self.course_code)}')

        fys = extract_course_code_2(self.course_code)[-1]
        if fys == "F":
            f_enrol = sum(x.get_fy_final_enrolls() for x in cur_data.values())
            drops = f_enrol - sum(x.get_f_final_drop() for x in cur_data.values())
            lwds = f_enrol - drops - sum(x.get_f_final_lwd() for x in cur_data.values())
        elif fys == "Y":
            f_enrol = sum(x.get_fy_final_enrolls() for x in cur_data.values())
            drops = f_enrol - sum(x.get_y_final_drop() for x in cur_data.values())
            lwds = f_enrol - drops - sum(x.get_sy_final_lwd() for x in cur_data.values())
        else:
            f_enrol = sum(x.get_s_final_enrolls() for x in cur_data.values())
            drops = f_enrol - sum(x.get_s_final_drop() for x in cur_data.values())
            lwds = f_enrol - drops - sum(x.get_sy_final_lwd() for x in cur_data.values())

        totcap = sum(x.cap for x in cur_data.values())
        totenrol = sum(x.enroll_logs[-1] for x in cur_data.values())
        if f_enrol == 0:
            f_enrol = 1

        dropstr = f"Drops: {drops} ({(drops / f_enrol) * 100:.1f}%)" if drops != 0 else ""
        lwdstr = f"LWDs: {lwds} ({(lwds / f_enrol) * 100:.1f}%)" if lwds != 0 else ""
        enrollstr = f"Enrollment: {totenrol}/{f_enrol}\n(cap: {totcap})" if \
            totenrol != f_enrol else f"Enrollment: {f_enrol}/{totcap}"

        plt.figtext(0.84, 0.04, '\n'.join([x for x in [dropstr, lwdstr, enrollstr] if x != ""]),
                    ha="center", fontsize=10,
                    bbox=dict(boxstyle='square,pad=1.70', fc='none', ec='none')


                    )
        plt.tight_layout()
        # plt.savefig('graph.svg')
        # plt.savefig('graph.pdf')
        plt.show()

    def _determine_ins(self, lec: str) -> str:
        """Determine the label to add."""
        ins_name = self.lec_info_getter.get_instructor(self.course_code + '-' + lec)
        logging.info(f'obtained instructor for {self.course_code}-{lec}, which ended up being {ins_name}')
        # print(ins_name)
        if ins_name in self.unused_names:
            return ''
        else:
            return f' - {long_name_trimmer(ins_name, 20)}'


class PlotlyPlotter(MultiDatePlotSystem):
    def _process_csv_data_second(self, cur_data: dict[str, LectureInstance]) -> None:
        date_logs = []
        enroll_logs_all = []
        v_names = {}
        for i, (temp_key, temp_value) in enumerate(cur_data.items()):
            if not date_logs:
                date_logs = temp_value.date_logs
            enroll_logs_all.append(temp_value.enroll_logs)
            v_names[f'wide_variable_{i}'] = temp_value.code + self._determine_ins(temp_value.code)

        fig = px.line(x=date_logs, y=enroll_logs_all,
                      title=f'Enrollment for {extract_course_code_2(self.course_code)}')
        fig.for_each_trace(lambda t: t.update(name=v_names[t.name],
                                              hovertemplate=t.hovertemplate.replace(t.name, v_names[t.name])))
        fig.show()


def extract_course_code_2(cc: str) -> str:
    return cc[:10]


def extract_course_code(cc: str) -> str:
    """Extract the source code from something
    that looks like the source code. The course code
    must include the session number."""
    last_slash = cc.rfind('/')
    last_slash_2 = cc.rfind('\\')
    total_last_slash = max(last_slash, last_slash_2)
    if total_last_slash == -1:
        return cc[:cc.find('.csv')]
    else:
        total_last_slash += 1
        return cc[total_last_slash:cc.find('.csv')]


def long_name_trimmer(name: str, max_len: int) -> str:
    """Name too long? Trim it!!!"""
    if len(name) <= max_len:
        return name
    else:
        return name[:max_len + 1] + '...'


def cc_only(cc: str) -> str:
    return cc[:10]


def code_only(cc: str) -> str:
    return cc[-8:]


if __name__ == '__main__':
    # main()
    main_complex()
